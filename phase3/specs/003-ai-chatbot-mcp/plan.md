# Implementation Plan: Todo AI Chatbot Integration with MCP Architecture

**Branch**: `003-ai-chatbot-mcp` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `phase3/specs/003-ai-chatbot-mcp/spec.md`

## Summary

Build an AI-powered chat interface for natural language task management using OpenAI Agents SDK with Cohere API backend. The system implements a multi-agent architecture with 6 specialized agents (Orchestrator, IntentParser, MCPValidator, TaskManager, ContextManager, ResponseFormatter) coordinating via sequential handoffs. MCP tools (add_task, list_tasks, complete_task, update_task, delete_task) operate on the existing Phase 2 tasks table. Conversation state persists in PostgreSQL for stateless server design.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js (frontend)
**Primary Dependencies**:
- openai-agents-sdk (agent orchestration)
- FastAPI (API framework, existing)
- SQLModel (ORM, existing)
- asyncpg (async PostgreSQL, existing)

**Storage**: Neon PostgreSQL (existing Phase 2 database + 2 new tables)
**Testing**: pytest with async support, jest for frontend
**Target Platform**: Web (browser-based chat interface)
**Project Type**: Web application (extends Phase 2 monorepo)
**Performance Goals**: <2s response time (p95), 50+ concurrent users
**Constraints**: 20-message context window, 1000 char max message, 5 max tool calls per turn
**Scale/Scope**: Single-user conversations, basic CRUD operations

## Constitution Check

*GATE: Constitution template not fully configured - proceeding with standard best practices*

| Principle | Status | Notes |
|-----------|--------|-------|
| Test-First | FOLLOW | Write tests before implementation |
| Simplicity | FOLLOW | Sequential agent handoffs (simplest viable) |
| Observability | FOLLOW | Structured logging for all agents |
| Error Handling | FOLLOW | Graceful degradation with user-friendly messages |

## Project Structure

### Documentation (this feature)

```text
phase3/specs/003-ai-chatbot-mcp/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Technical decisions
├── data-model.md        # Database schema
├── quickstart.md        # Setup guide
├── contracts/
│   ├── chat-api.yaml    # OpenAPI specification
│   └── mcp-tools.md     # MCP tool contracts
├── checklists/
│   ├── requirements.md  # Spec quality checklist
│   └── plan-quality-checklist.md  # Plan quality checklist
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (extends Phase 2)

```text
phase3/backend/
├── src/
│   ├── api/
│   │   ├── auth.py          # Existing
│   │   ├── tasks.py         # Existing
│   │   └── chat.py          # NEW: Chat endpoint
│   ├── agents/              # NEW: Agent system
│   │   ├── __init__.py
│   │   ├── config.py        # Cohere client setup
│   │   ├── orchestrator.py  # Main orchestrator agent
│   │   ├── intent_parser.py # Intent extraction
│   │   ├── task_manager.py  # MCP tool execution
│   │   ├── context_manager.py # Conversation persistence
│   │   ├── response_formatter.py # Response templates
│   │   └── mcp_validator.py # Input validation
│   ├── tools/               # NEW: MCP tools
│   │   ├── __init__.py
│   │   └── mcp_tools.py     # add_task, list_tasks, etc.
│   ├── models/
│   │   ├── user.py          # Existing
│   │   ├── task.py          # Existing
│   │   ├── conversation.py  # NEW
│   │   └── message.py       # NEW
│   ├── schemas/
│   │   ├── auth.py          # Existing
│   │   ├── task.py          # Existing
│   │   └── chat.py          # NEW: ChatRequest/Response
│   └── services/
│       ├── task.py          # Existing
│       └── conversation.py  # NEW: Conversation CRUD
└── tests/
    ├── test_auth.py         # Existing
    ├── test_tasks.py        # Existing
    ├── test_mcp_tools.py    # NEW
    ├── test_agents.py       # NEW
    └── test_chat_api.py     # NEW

phase3/frontend/
├── components/
│   ├── tasks/               # Existing
│   └── chat/                # NEW
│       ├── ChatWidget.tsx   # Main container
│       ├── ChatMessage.tsx  # Message display
│       ├── ChatInput.tsx    # Input with send
│       └── ChatToggle.tsx   # Floating button
├── lib/
│   ├── api.ts               # Existing (extend)
│   └── chat-api.ts          # NEW: Chat API client
└── app/
    └── dashboard/
        └── page.tsx         # Existing (add chat)
```

**Structure Decision**: Extends existing Phase 2 monorepo structure. New code organized in dedicated directories (`agents/`, `tools/`, `chat/`) to maintain separation while integrating with existing infrastructure.

## Implementation Phases

### Phase 1: Database & Models

**Goal**: Add conversation persistence layer

**Tasks**:
1. Create `Conversation` model in `src/models/conversation.py`
2. Create `Message` model in `src/models/message.py`
3. Add models to `src/models/__init__.py` exports
4. Create `ConversationService` in `src/services/conversation.py`
5. Run migration to create tables
6. Write unit tests for models

**Files**:
- `src/models/conversation.py` (new)
- `src/models/message.py` (new)
- `src/services/conversation.py` (new)
- `tests/test_models.py` (new)

**Validation Gate**: All model tests pass

---

### Phase 2: MCP Tools

**Goal**: Implement 5 task management tools

**Tasks**:
1. Set up `src/tools/mcp_tools.py` with `@function_tool` decorators
2. Implement `add_task` tool
3. Implement `list_tasks` tool with status filter
4. Implement `complete_task` tool
5. Implement `update_task` tool
6. Implement `delete_task` tool
7. Add ownership validation to all tools
8. Write unit tests for each tool

**Files**:
- `src/tools/__init__.py` (new)
- `src/tools/mcp_tools.py` (new)
- `tests/test_mcp_tools.py` (new)

**Validation Gate**: All tool tests pass, ownership validation verified

---

### Phase 3: Agent System

**Goal**: Build multi-agent orchestration

**Tasks**:
1. Set up Cohere client in `src/agents/config.py`
2. Create IntentParser agent
3. Create MCPValidator agent
4. Create TaskManager agent with MCP tools
5. Create ContextManager agent
6. Create ResponseFormatter agent
7. Create MainOrchestrator with handoffs
8. Write agent routing tests

**Agent Definitions**:

```python
# IntentParser
intent_parser = Agent(
    name="IntentParser",
    instructions="""Parse natural language into structured todo operations.

    Intents: add_task, list_tasks, complete_task, update_task, delete_task

    Extract:
    - intent: the operation type
    - title: task title (for add/update)
    - task_id: numeric ID (for complete/update/delete)
    - status: all/pending/completed (for list)
    - confidence: 0.0-1.0

    If confidence < 0.7, ask clarifying question.""",
    model=model
)

# TaskManager
task_manager = Agent(
    name="TaskManager",
    instructions="""Execute task operations using MCP tools.

    Available tools: add_task, list_tasks, complete_task, update_task, delete_task

    Always pass user_id from context.
    For ambiguous references like "delete the meeting", first list_tasks to find task_id.

    Always confirm actions with task details.""",
    model=model,
    tools=[add_task_tool, list_tasks_tool, complete_task_tool,
           update_task_tool, delete_task_tool],
    model_settings=ModelSettings(tool_choice="required")
)

# ContextManager
context_manager = Agent(
    name="ContextManager",
    instructions="""Manage conversation persistence.

    Load: Fetch last 20 messages from database for conversation_id
    Save: Store user and assistant messages after each turn
    Create: Generate new conversation if conversation_id not provided

    Return conversation_id and messages array for agent runner.""",
    model=model
)

# ResponseFormatter
response_formatter = Agent(
    name="ResponseFormatter",
    instructions="""Format MCP tool results into friendly messages.

    Templates:
    - add_task: "✅ Added: '{title}' (Task #{id})"
    - list_tasks: "📝 Your {status} tasks:\n{numbered_list}"
    - complete_task: "🎉 Completed: '{title}'"
    - update_task: "✏️ Updated Task #{id}: '{new_title}'"
    - delete_task: "🗑️ Deleted: '{title}'"
    - error: "❌ {friendly_message}\n💡 {suggestion}"
    - empty_list: "You're all caught up! 🎉"

    Use emojis, be encouraging, suggest next actions.""",
    model=model
)

# MCPValidator
mcp_validator = Agent(
    name="MCPValidator",
    instructions="""Validate parameters before MCP tool execution.

    Checks:
    - user_id is valid integer
    - task_id is positive integer
    - title is 1-200 characters
    - status is valid enum
    - description is max 2000 characters

    Sanitize inputs to prevent injection.
    Return validation_error if invalid.""",
    model=model
)

# MainOrchestrator
main_orchestrator = Agent(
    name="MainOrchestrator",
    instructions="""Coordinate todo chatbot workflow.

    Workflow:
    1. Load conversation history (ContextManager)
    2. Parse user intent (IntentParser)
    3. Validate parameters (MCPValidator)
    4. Execute operations (TaskManager with MCP tools)
    5. Format response (ResponseFormatter)
    6. Save messages (ContextManager)

    Handle errors at each stage.
    Provide fallback responses if agents fail.
    Maintain user_id context across all operations.""",
    model=model,
    handoffs=[context_manager, intent_parser, mcp_validator,
              task_manager, response_formatter]
)
```

**Files**:
- `src/agents/__init__.py` (new)
- `src/agents/config.py` (new)
- `src/agents/intent_parser.py` (new)
- `src/agents/mcp_validator.py` (new)
- `src/agents/task_manager.py` (new)
- `src/agents/context_manager.py` (new)
- `src/agents/response_formatter.py` (new)
- `src/agents/orchestrator.py` (new)
- `tests/test_agents.py` (new)

**Validation Gate**: Agent routing works for 10 test scenarios

---

### Phase 4: FastAPI Endpoint

**Goal**: Create chat API endpoint

**Tasks**:
1. Create `ChatRequest` and `ChatResponse` schemas
2. Implement `POST /api/{user_id}/chat` endpoint
3. Add JWT authentication dependency
4. Implement conversation loading/saving
5. Add error handling and logging
6. Write integration tests

**Endpoint Implementation**:

```python
@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: int,
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    # Validate ownership
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Load or create conversation
    if request.conversation_id:
        conversation = await ConversationService.get_conversation(
            session, request.conversation_id, user_id
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = await ConversationService.create_conversation(session, user_id)

    # Save user message
    await ConversationService.save_message(
        session, conversation.id, user_id, "user", request.message
    )

    # Run agent
    try:
        result = await Runner.run(
            main_orchestrator,
            request.message,
            context={"user_id": user_id, "conversation_id": conversation.id}
        )
        response_text = result.final_output
        tool_calls = [call.name for call in result.tool_calls]
    except Exception as e:
        logger.error(f"Agent error: {e}")
        response_text = "I'm having trouble right now. Please try again."
        tool_calls = []

    # Save assistant response
    await ConversationService.save_message(
        session, conversation.id, user_id, "assistant", response_text
    )

    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text,
        tool_calls=tool_calls
    )
```

**Files**:
- `src/api/chat.py` (new)
- `src/schemas/chat.py` (new)
- `src/main.py` (modify - add router)
- `tests/test_chat_api.py` (new)

**Validation Gate**: Endpoint returns <2s for 95% of requests

---

### Phase 5: Frontend Chat Component

**Goal**: Build chat UI integrated with dashboard

**Tasks**:
1. Create `ChatWidget` component
2. Create `ChatMessage` component
3. Create `ChatInput` component
4. Create `ChatToggle` floating button
5. Add chat API client functions
6. Integrate into dashboard page
7. Style for responsive design
8. Write component tests

**Component Structure**:

```tsx
// ChatWidget.tsx
export default function ChatWidget({ userId }: { userId: number }) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [conversationId, setConversationId] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = async (content: string) => {
        setIsLoading(true);
        const userMessage: Message = { role: 'user', content, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);

        try {
            const response = await chatApi.sendMessage(userId, content, conversationId);
            setConversationId(response.conversation_id);

            const assistantMessage: Message = {
                role: 'assistant',
                content: response.response,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage: Message = {
                role: 'assistant',
                content: 'Sorry, something went wrong. Please try again.',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <ChatToggle onClick={() => setIsOpen(!isOpen)} isOpen={isOpen} />
            {isOpen && (
                <div className="chat-widget">
                    <div className="chat-messages">
                        {messages.map((msg, i) => (
                            <ChatMessage key={i} message={msg} />
                        ))}
                        {isLoading && <LoadingIndicator />}
                    </div>
                    <ChatInput onSend={sendMessage} disabled={isLoading} />
                </div>
            )}
        </>
    );
}
```

**Files**:
- `components/chat/ChatWidget.tsx` (new)
- `components/chat/ChatMessage.tsx` (new)
- `components/chat/ChatInput.tsx` (new)
- `components/chat/ChatToggle.tsx` (new)
- `lib/chat-api.ts` (new)
- `app/dashboard/page.tsx` (modify)

**Validation Gate**: Chat displays correctly on desktop and mobile

---

### Phase 6: Testing & Refinement

**Goal**: Ensure quality and performance

**Tasks**:
1. Run full test suite
2. Test natural language variations (50+ commands)
3. Verify intent recognition accuracy (>90% target)
4. Load test with 50 concurrent users
5. Verify conversation persistence after restart
6. Fix bugs found during testing
7. Optimize slow queries if needed

**Test Scenarios**:

```python
test_commands = [
    ("Add buy groceries", "add_task"),
    ("Remind me to call mom", "add_task"),
    ("I need to pay bills", "add_task"),
    ("Show my tasks", "list_tasks"),
    ("What's pending?", "list_tasks"),
    ("List completed todos", "list_tasks"),
    ("Mark task 3 done", "complete_task"),
    ("I finished the meeting", "complete_task"),
    ("Complete buy milk", "complete_task"),
    ("Delete task 2", "delete_task"),
    ("Remove the meeting", "delete_task"),
    ("Change task 1 to 'Call mom tonight'", "update_task"),
    ("Add buy milk and show my tasks", "compound"),
    # ... 40+ more variations
]
```

**Validation Gates**:
- [ ] All unit tests pass
- [ ] Intent recognition accuracy > 90%
- [ ] Load test passes (50 concurrent users)
- [ ] Conversation persists after server restart
- [ ] Response time < 2s (p95)

---

## Quality Validation Gates Summary

| Phase | Gate | Criteria |
|-------|------|----------|
| 1 | Models | All model tests pass |
| 2 | MCP Tools | All tool tests pass, ownership verified |
| 3 | Agents | Routing works for 10 scenarios |
| 4 | API | <2s response (p95) |
| 5 | Frontend | Displays correctly desktop/mobile |
| 6 | Testing | >90% intent accuracy, 50 users load test |

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cohere API rate limits | Service degradation | Retry with exponential backoff |
| Agent handoffs fail | Broken workflow | max_handoff_depth=5, explicit conditions |
| Intent misinterpretation | Wrong actions | Confidence threshold 0.7, clarifying questions |
| Database conflicts | Data corruption | Row-level locking, test concurrency |
| Token overflow | Failed responses | Limit to 20 messages context |
| Slow responses | Poor UX | Query optimization, indexes |

---

## Performance Targets

| Metric | Target | Implementation |
|--------|--------|----------------|
| Intent parsing | < 200ms | LLM structured output |
| MCP tool execution | < 500ms | Indexed queries |
| Total response | < 2s (p95) | Async throughout |
| Concurrent users | 50+ | Connection pooling |
| Database pool | 20 max | Existing config |

---

## Dependencies

- **Internal**: Phase 2 backend (auth, tasks API)
- **Internal**: Phase 2 frontend (dashboard)
- **External**: Cohere API (command-r-plus model)
- **External**: Neon PostgreSQL (existing)

---

## Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent orchestration | Sequential handoffs | Predictable, debuggable |
| AI provider | Cohere | User specified, OpenAI SDK compatible |
| Persistence | Database | Stateless servers, zero data loss |
| Frontend | Custom React | Full control, no external deps |
| Context window | 20 messages | Balance: context vs performance |

See [research.md](./research.md) for detailed decision rationale.
