# Skill: OpenAI Agents SDK Development

## Purpose
Build stateless, production-ready AI agents using OpenAI Agents SDK with automatic conversation history management, tool calling, and MCP integration.

## Tech Stack
- **OpenAI Agents SDK**: `openai-agents`
- **Python**: 3.9+
- **FastAPI**: For chat API endpoints
- **SQLModel**: For conversation persistence
- **MCP**: Model Context Protocol for tools

## Core Concepts

### Key Primitives

1. **Agent**: LLM with instructions and tools
2. **Runner**: Executes agents (sync or async)
3. **Session**: Automatic conversation history management
4. **Handoffs**: Delegate between agents
5. **Guardrails**: Input/output validation
6. **Tracing**: Built-in observability

## Installation

```bash
pip install openai-agents
# or with UV
uv add openai-agents
```

## Architecture for Hackathon Phase III

```
┌─────────────────────────────────────────────────────────────┐
│                    Chat API Endpoint                         │
│  POST /api/{user_id}/chat                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Fetch conversation history from DB               │    │
│  │ 2. Build messages array (history + new message)     │    │
│  │ 3. Run agent with MCP tools                         │    │
│  │ 4. Agent calls tools → MCP executes                 │    │
│  │ 5. Save messages to DB                              │    │
│  │ 6. Return response (STATELESS - no memory in RAM)   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
               ┌────────────────────────┐
               │   MCP Server (Tools)   │
               │  - add_task           │
               │  - list_tasks         │
               │  - complete_task      │
               │  - delete_task        │
               │  - update_task        │
               └────────────────────────┘
```

## Basic Agent Setup

### 1. Simple Agent (Hello World)

```python
"""
Basic agent example
[Task]: T-060
[From]: plan.md §7.3 - OpenAI Agents SDK Setup
"""

from agents import Agent, Runner
import asyncio

# Define agent
agent = Agent(
    name="Todo Assistant",
    instructions="""
    You are a helpful todo assistant. You help users manage their tasks
    through natural language. Always be friendly and confirm actions.
    """
)

# Run agent (async)
async def main():
    result = await Runner.run(
        agent,
        "What can you help me with?"
    )
    print(result.final_output)

# Run agent (sync)
result = Runner.run_sync(agent, "Hello!")
print(result.final_output)
```

## Agent with MCP Tools

### 2. Connect Agent to MCP Server

```python
"""
Agent with MCP tools for task management
[Task]: T-061
[From]: plan.md §7.3 - Agent + MCP Integration
"""

from agents import Agent, Runner
from mcp import MCPClient
import asyncio

# Initialize MCP client
mcp_client = MCPClient("http://localhost:8000/mcp")

# Define agent with MCP tools
todo_agent = Agent(
    name="Todo Manager",
    instructions="""
    You are a todo management assistant. Help users manage their tasks
    through natural language commands.
    
    Available capabilities:
    - Create new tasks
    - List all tasks (with filtering)
    - Mark tasks as complete
    - Delete tasks
    - Update task details
    
    Always confirm what action you took and provide clear feedback.
    """,
    tools=mcp_client.get_tools()  # Get all MCP tools
)

async def chat(user_id: str, message: str):
    """
    Single chat turn with agent.
    
    [Spec]: plan.md §7.3 - Stateless Agent Pattern
    """
    result = await Runner.run(
        todo_agent,
        message,
        context={"user_id": user_id}  # Pass user context
    )
    
    return result.final_output

# Example usage
async def main():
    response = await chat("user123", "Add a task to buy groceries")
    print(response)
    # Output: "I've created a new task 'Buy groceries' for you. Task ID: 5"

asyncio.run(main())
```

## Stateless Chat Endpoint with Database Persistence

### 3. FastAPI Endpoint with Session Management

```python
"""
Stateless chat API endpoint
[Task]: T-062
[From]: plan.md §7.3 - Stateless Chat Architecture
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from agents import Agent, Runner
from db import get_session
from models import Conversation, Message
from mcp import MCPClient
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

# Initialize MCP client
mcp_client = MCPClient("http://localhost:8000/mcp")

# Define agent
todo_agent = Agent(
    name="Todo Assistant",
    instructions="""
    You are a helpful todo assistant. Help users manage tasks through
    natural language. Always confirm actions clearly.
    """,
    tools=mcp_client.get_tools()
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list[dict] | None = None

@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Stateless chat endpoint.
    Server holds NO state - everything from/to database.
    
    [Task]: T-062
    [Spec]: plan.md §7.3 - Stateless Request Cycle
    """
    
    # Step 1: Get or create conversation
    conversation_id = request.conversation_id
    if not conversation_id:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        conversation_id = conversation.id
        history = []
    else:
        # Fetch conversation history from database
        history = await get_conversation_history(session, conversation_id)
    
    # Step 2: Save user message to database
    user_message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    await session.commit()
    
    # Step 3: Build messages array for agent
    messages = history + [{"role": "user", "content": request.message}]
    
    # Step 4: Run agent with context
    result = await Runner.run(
        todo_agent,
        messages,  # Full conversation history
        context={"user_id": user_id}
    )
    
    # Step 5: Extract response
    assistant_message = result.final_output
    tool_calls = result.tool_calls if hasattr(result, 'tool_calls') else None
    
    # Step 6: Save assistant response to database
    assistant_msg = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=assistant_message
    )
    session.add(assistant_msg)
    await session.commit()
    
    # Step 7: Return response (server is now stateless again)
    return ChatResponse(
        conversation_id=conversation_id,
        response=assistant_message,
        tool_calls=tool_calls
    )

async def get_conversation_history(
    session: AsyncSession,
    conversation_id: int
) -> list[dict]:
    """
    Fetch conversation history from database.
    
    [Task]: T-063
    """
    from sqlmodel import select
    
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    # Convert to OpenAI format
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
```

## Agent with Sessions (Alternative Pattern)

### 4. Using Built-in Session Management

```python
"""
Agent with built-in session management
[Task]: T-064
[From]: OpenAI Agents SDK - Sessions Documentation
"""

from agents import Agent, Runner, Session
from sqlalchemy import create_engine

# Create agent
agent = Agent(
    name="Todo Assistant",
    instructions="Help users manage their tasks"
)

# Setup session with database backend
engine = create_engine("postgresql://...")

# Create session (automatically persists to DB)
session = Session(
    agent=agent,
    session_id="user123_conversation_456",
    engine=engine
)

# Run with session (automatic history management)
async def chat_with_session(message: str):
    """
    Chat with automatic session persistence.
    
    [Note]: This pattern auto-manages history but requires
    session state in memory. For stateless servers, use the
    pattern in example #3 above.
    """
    result = await Runner.run(
        agent,
        message,
        session=session  # SDK handles history automatically
    )
    
    return result.final_output

# Usage
await chat_with_session("Add a task to call mom")
await chat_with_session("What tasks do I have?")
# Session automatically maintains context
```

## Multi-Agent with Handoffs

### 5. Triage Agent Pattern

```python
"""
Multi-agent with handoffs
[Task]: T-065
[From]: OpenAI Agents SDK - Handoffs Documentation
"""

from agents import Agent, Runner

# Define specialized agents
task_agent = Agent(
    name="Task Manager",
    instructions="Manage tasks: create, update, delete, complete",
    tools=mcp_client.get_tools()
)

calendar_agent = Agent(
    name="Calendar Manager",
    instructions="Handle scheduling and calendar queries"
)

# Triage agent that routes to specialists
triage_agent = Agent(
    name="Triage Assistant",
    instructions="""
    You are a triage assistant. Analyze user requests and route to:
    - Task Manager: for todo items, task management
    - Calendar Manager: for scheduling, dates, appointments
    
    Always explain which agent you're handing off to.
    """,
    handoffs=[task_agent, calendar_agent]  # Available agents
)

async def chat_with_handoff(message: str):
    """
    Agent can hand off to specialists.
    
    [Spec]: OpenAI Agents SDK - Handoff Pattern
    """
    result = await Runner.run(triage_agent, message)
    
    # Result includes which agent handled it
    print(f"Handled by: {result.agent.name}")
    return result.final_output

# Examples
await chat_with_handoff("Add a task to buy milk")
# → Hands off to Task Manager

await chat_with_handoff("What's my schedule for tomorrow?")
# → Hands off to Calendar Manager
```

## Guardrails (Input Validation)

### 6. Guardrail Functions

```python
"""
Input guardrails
[Task]: T-066
[From]: OpenAI Agents SDK - Guardrails Documentation
"""

from agents import Agent, Runner, GuardrailFunctionOutput, InputGuardrail
from pydantic import BaseModel

class ValidationOutput(BaseModel):
    is_valid: bool
    reason: str

# Guardrail agent
validation_agent = Agent(
    name="Input Validator",
    instructions="Check if user input is appropriate for a todo app",
    output_type=ValidationOutput
)

async def validate_input(ctx, agent, input_data):
    """
    Guardrail function to validate input.
    
    [Spec]: OpenAI Agents SDK - Guardrail Pattern
    """
    # Run validation agent
    result = await Runner.run(
        validation_agent,
        f"Is this appropriate for a todo app: {input_data}"
    )
    
    validation = result.final_output_as(ValidationOutput)
    
    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=not validation.is_valid
    )

# Agent with guardrail
protected_agent = Agent(
    name="Todo Assistant",
    instructions="Help with tasks",
    input_guardrails=[
        InputGuardrail(guardrail_function=validate_input)
    ]
)

try:
    result = await Runner.run(
        protected_agent,
        "What's the weather?"  # Invalid for todo app
    )
except Exception as e:
    print(f"Guardrail blocked: {e}")
```

## Natural Language Understanding

### 7. Agent Behavior Examples

```python
"""
Natural language command handling
[Task]: T-067
[From]: specify.md §3.3 - Natural Language Commands
"""

# The agent automatically understands various phrasings:

examples = [
    # Creating tasks
    "Add a task to buy groceries",
    "Remind me to call mom",
    "I need to finish the report",
    
    # Listing tasks
    "What's on my todo list?",
    "Show me all my tasks",
    "What do I need to do?",
    
    # Completing tasks
    "Mark task 3 as done",
    "I finished the meeting task",
    "Complete the groceries item",
    
    # Filtering
    "What tasks are pending?",
    "Show completed items",
    "What have I not done yet?",
    
    # Updating
    "Change task 5 to 'Call mom tonight'",
    "Update the meeting description",
    
    # Deleting
    "Remove the old task",
    "Delete task number 7"
]

# Agent handles all these naturally without explicit rules!
for example in examples:
    result = await Runner.run(todo_agent, example)
    print(result.final_output)
```

## Tracing and Debugging

### 8. Built-in Tracing

```python
"""
View agent execution traces
[Task]: T-068
[From]: OpenAI Agents SDK - Tracing Documentation
"""

from agents import Agent, Runner, set_trace_processors
from agents.tracing import PrintProcessor

# Enable trace printing (for development)
set_trace_processors([PrintProcessor()])

agent = Agent(
    name="Todo Assistant",
    instructions="Help with tasks",
    tools=mcp_client.get_tools()
)

result = await Runner.run(agent, "Add a task to buy milk")

# Trace output shows:
# - Agent called
# - Tool called: add_task
# - Tool result
# - Final response generated
# - Total time, tokens used
```

## Environment Setup

```bash
# .env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
MCP_SERVER_URL=http://localhost:8000/mcp
```

```python
import os
from agents import Agent

# SDK automatically reads OPENAI_API_KEY from environment
agent = Agent(
    name="Assistant",
    instructions="You are helpful"
)
```

## Best Practices

### 1. Always Use Async

```python
# ✅ Good
result = await Runner.run(agent, message)

# ❌ Bad (blocking)
result = Runner.run_sync(agent, message)  # Use only for scripts
```

### 2. Pass User Context

```python
# ✅ Good - Tools can access user_id
result = await Runner.run(
    agent,
    message,
    context={"user_id": user_id}
)

# ❌ Bad - Tools don't know which user
result = await Runner.run(agent, message)
```

### 3. Persist Conversations to Database

```python
# ✅ Good - Stateless, scalable
# Fetch history from DB → Run agent → Save to DB

# ❌ Bad - State in memory, not scalable
# Keep history in Python dict/list
```

### 4. Clear Instructions

```python
# ✅ Good
Agent(
    name="Todo Assistant",
    instructions="""
    You help users manage tasks. Available actions:
    - Create tasks with add_task(title, description)
    - List tasks with list_tasks(status)
    - Mark complete with complete_task(task_id)
    
    Always confirm actions clearly.
    """
)

# ❌ Bad
Agent(name="Assistant", instructions="Help with stuff")
```

## Testing Agents

```python
"""
Test agent behavior
[Task]: T-069
"""

import pytest
from agents import Agent, Runner

@pytest.mark.asyncio
async def test_agent_creates_task():
    """Test agent can create task via MCP tool"""
    
    result = await Runner.run(
        todo_agent,
        "Add a task to buy milk",
        context={"user_id": "test_user"}
    )
    
    # Check response mentions creation
    assert "created" in result.final_output.lower()
    assert "buy milk" in result.final_output.lower()

@pytest.mark.asyncio
async def test_agent_lists_tasks():
    """Test agent can list tasks"""
    
    result = await Runner.run(
        todo_agent,
        "What are my tasks?",
        context={"user_id": "test_user"}
    )
    
    # Should call list_tasks tool
    assert len(result.tool_calls) > 0
    assert result.tool_calls[0].name == "list_tasks"
```

## Key Differences: OpenAI SDK vs Agents SDK

| Feature | OpenAI SDK | Agents SDK |
|---------|-----------|------------|
| Tool Calling | Manual loop | Automatic agent loop |
| History | Manual management | Session auto-manages |
| Multi-Agent | Custom logic | Built-in handoffs |
| Validation | Custom code | Built-in guardrails |
| Tracing | External | Built-in |
| Complexity | Low-level | High-level abstractions |

## Summary

This skill provides:
- ✅ Stateless agent architecture (Phase III requirement)
- ✅ Automatic tool calling with MCP
- ✅ Conversation persistence to database
- ✅ Natural language understanding
- ✅ Multi-agent handoffs (optional)
- ✅ Input validation with guardrails
- ✅ Built-in tracing and debugging
- ✅ Production-ready patterns
- ✅ Scalable, horizontal-scaling compatible

**For Hackathon Phase III**: Use the stateless chat endpoint pattern (example #3) with MCP tools for task management.