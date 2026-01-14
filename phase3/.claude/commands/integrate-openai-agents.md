# Integrate OpenAI Agents

Setup OpenAI Agents SDK in FastAPI endpoint with MCP tools and conversation persistence.

## Core Architecture

```
User Message → Load History → Build Messages → Run Agent → Execute Tools → Save → Stream Response
```

## FastAPI Endpoint

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

app = FastAPI()

@app.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1. Validate JWT and extract user
    user = await verify_jwt(request.token)

    # 2. Load conversation history from DB
    messages = await load_conversation_history(db, user_id, request.conversation_id)

    # 3. Append new user message
    messages.append({"role": "user", "content": request.message})

    # 4. Run agent with MCP tools
    response = await run_agent_with_tools(user_id, messages)

    # 5. Save conversation to DB
    await save_conversation(db, user_id, request.conversation_id, messages, response)

    # 6. Return response (streaming or regular)
    if request.stream:
        return StreamingResponse(stream_response(response), media_type="text/event-stream")
    return {"response": response.content, "conversation_id": request.conversation_id}
```

## Message Array from DB History

```python
from sqlmodel import select
from models import Message, Conversation

async def load_conversation_history(
    db: AsyncSession,
    user_id: str,
    conversation_id: str | None
) -> list[dict]:
    """Build message array from DB history."""

    if not conversation_id:
        # New conversation
        return []

    # Fetch messages ordered by timestamp
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.user_id == user_id)  # User isolation
        .order_by(Message.created_at)
        .limit(20)  # Context window limit
    )

    result = await db.execute(query)
    db_messages = result.scalars().all()

    # Convert to OpenAI format
    messages = []
    for msg in db_messages:
        messages.append({
            "role": msg.role,  # "user", "assistant", "tool"
            "content": msg.content,
            **({"tool_call_id": msg.tool_call_id} if msg.tool_call_id else {}),
            **({"name": msg.tool_name} if msg.tool_name else {})
        })

    return messages
```

## Agent Setup with MCP Tools

```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

async def run_agent_with_tools(user_id: str, messages: list[dict]) -> AgentResponse:
    """Run agent with MCP tools attached."""

    # Setup MCP server connection
    async with MCPServerStdio(
        command="python",
        args=["mcp_server.py"],
        env={"USER_ID": user_id}  # Pass user context
    ) as mcp_server:

        # Create agent with tools
        agent = Agent(
            name="TodoAssistant",
            instructions="""You are a helpful task management assistant.
            Use the available tools to help users manage their tasks.
            Always confirm actions and be friendly.""",
            mcp_servers=[mcp_server]
        )

        # Run agent
        runner = Runner()
        result = await runner.run(
            agent=agent,
            messages=messages
        )

        return result
```

## Tool Call Execution

```python
async def execute_tool_calls(tool_calls: list, user_id: str) -> list[dict]:
    """Execute tool calls and return results."""

    results = []

    # Group independent calls for parallel execution
    parallel_calls = []
    sequential_calls = []

    for call in tool_calls:
        if is_independent(call):
            parallel_calls.append(call)
        else:
            sequential_calls.append(call)

    # Execute parallel calls
    if parallel_calls:
        parallel_results = await asyncio.gather(*[
            execute_single_tool(call, user_id)
            for call in parallel_calls
        ])
        results.extend(parallel_results)

    # Execute sequential calls
    for call in sequential_calls:
        result = await execute_single_tool(call, user_id)
        results.append(result)

    return results

async def execute_single_tool(call: ToolCall, user_id: str) -> dict:
    """Execute a single tool call."""

    tool_name = call.function.name
    arguments = json.loads(call.function.arguments)

    # Inject user_id into all tool calls
    arguments["user_id"] = user_id

    # Execute via MCP
    result = await mcp_tools[tool_name](**arguments)

    return {
        "tool_call_id": call.id,
        "role": "tool",
        "name": tool_name,
        "content": json.dumps(result)
    }
```

## Save Conversation to DB

```python
async def save_conversation(
    db: AsyncSession,
    user_id: str,
    conversation_id: str | None,
    messages: list[dict],
    response: AgentResponse
):
    """Save full conversation to database."""

    # Create conversation if new
    if not conversation_id:
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(conversation)
        conversation_id = conversation.id

    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=messages[-1]["content"]  # Latest user message
    )
    db.add(user_msg)

    # Save tool call messages if any
    for tool_result in response.tool_results:
        tool_msg = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="tool",
            content=tool_result["content"],
            tool_call_id=tool_result["tool_call_id"],
            tool_name=tool_result["name"]
        )
        db.add(tool_msg)

    # Save assistant response
    assistant_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=response.content
    )
    db.add(assistant_msg)

    await db.commit()

    return conversation_id
```

## Streaming Response

```python
async def stream_response(response: AgentResponse):
    """Stream response to ChatKit frontend."""

    async for chunk in response.stream():
        # SSE format
        yield f"data: {json.dumps({'content': chunk.content, 'done': False})}\n\n"

    # Final message
    yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

# Frontend consumption (ChatKit)
# const eventSource = new EventSource('/api/user123/chat?stream=true')
# eventSource.onmessage = (e) => appendMessage(JSON.parse(e.data))
```

## Graceful Fallback

```python
async def run_agent_with_fallback(user_id: str, messages: list[dict]) -> dict:
    """Run agent with graceful error handling."""

    try:
        response = await run_agent_with_tools(user_id, messages)
        return {
            "success": True,
            "content": response.content,
            "tool_calls": response.tool_calls
        }

    except MCPConnectionError as e:
        logger.error(f"MCP connection failed: {e}")
        return {
            "success": False,
            "content": "I'm having trouble connecting to my tools. Please try again.",
            "error": "mcp_connection"
        }

    except AgentTimeoutError as e:
        logger.error(f"Agent timeout: {e}")
        return {
            "success": False,
            "content": "That took too long. Let me try a simpler approach.",
            "error": "timeout"
        }

    except Exception as e:
        logger.error(f"Agent failed: {e}")
        return {
            "success": False,
            "content": "Something went wrong. Please try again or rephrase your request.",
            "error": "unknown"
        }
```

## Checklist

- [ ] FastAPI endpoint at `/api/{user_id}/chat`
- [ ] Load conversation history from DB (20 message limit)
- [ ] Build proper message array (role/content format)
- [ ] Agent configured with MCP tools
- [ ] Tool calls executed with user_id injection
- [ ] Parallel tool execution where possible
- [ ] Full conversation saved (user + assistant + tool)
- [ ] Streaming response support (SSE)
- [ ] Graceful fallback on errors
- [ ] Proper error messages for frontend
