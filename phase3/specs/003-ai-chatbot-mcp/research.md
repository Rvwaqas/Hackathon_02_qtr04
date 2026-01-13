# Research: Todo AI Chatbot Integration with MCP Architecture

**Feature**: `003-ai-chatbot-mcp`
**Date**: 2026-01-13
**Status**: Complete

## Technical Decisions

### 1. AI Service Provider

**Decision**: Cohere API via OpenAI SDK Compatibility Layer

**Rationale**:
- User specified Cohere API with command-r-plus model
- OpenAI SDK compatibility allows using familiar openai-agents-sdk patterns
- Cohere's compatibility endpoint at `https://api.cohere.ai/compatibility/v1`
- Model: `command-r-plus-08-2024` for optimal reasoning and tool use

**Alternatives Considered**:
- OpenAI GPT-4: More expensive, not specified by user
- Gemini 2.0 Flash: Originally mentioned but user provided Cohere config
- Local LLM: Higher latency, requires GPU infrastructure

**Configuration**:
```python
client = AsyncOpenAI(
    api_key=COHERE_API_KEY,
    base_url="https://api.cohere.ai/compatibility/v1"
)
model = OpenAIChatCompletionsModel(
    model="command-r-plus-08-2024",
    openai_client=client
)
```

---

### 2. Agent Orchestration Pattern

**Decision**: Sequential Handoffs with Main Orchestrator

**Rationale**:
- Predictable execution flow for debugging
- Clear responsibility chain: Context → Intent → Validator → TaskManager → Formatter
- Error isolation: failures at one stage don't corrupt others
- Easier to test individual agents
- Matches OpenAI Agents SDK handoff pattern

**Alternatives Considered**:
- Parallel execution: Faster but complex error handling, state conflicts
- Single monolithic agent: Harder to test, debug, and modify
- Event-driven: Overkill for simple todo operations

**Workflow**:
```
User Message → ContextManager (load history)
            → IntentParser (extract operation)
            → MCPValidator (validate params)
            → TaskManager (execute MCP tools)
            → ResponseFormatter (friendly message)
            → ContextManager (save messages)
```

---

### 3. MCP Tool Implementation

**Decision**: Function Tools with OpenAI Agents SDK `@function_tool` decorator

**Rationale**:
- Native integration with openai-agents-sdk
- Automatic schema generation from type hints
- Async support for database operations
- Clean separation of tool logic

**Tool Signatures**:
```python
@function_tool
async def add_task(user_id: int, title: str, description: str = "") -> dict

@function_tool
async def list_tasks(user_id: int, status: str = "all") -> dict

@function_tool
async def complete_task(user_id: int, task_id: int) -> dict

@function_tool
async def update_task(user_id: int, task_id: int, title: str) -> dict

@function_tool
async def delete_task(user_id: int, task_id: int) -> dict
```

---

### 4. Conversation Persistence Strategy

**Decision**: Database-backed persistence with 20-message context window

**Rationale**:
- Stateless server design: any instance handles any request
- Survives server restarts (zero data loss)
- 20-message limit prevents token overflow and maintains performance
- Simple relational schema (conversations → messages)

**Alternatives Considered**:
- Redis session store: Fast but volatile, data loss on restart
- In-memory with replication: Complex, requires sticky sessions
- Full history: Token limits, slow responses, expensive

**Schema**:
- `conversations`: id, user_id, created_at, updated_at
- `messages`: id, conversation_id, user_id, role, content, created_at

---

### 5. Frontend Integration Approach

**Decision**: Custom React Chat Component (not OpenAI ChatKit)

**Rationale**:
- OpenAI ChatKit requires OpenAI API key and domain allowlist
- Custom component integrates directly with FastAPI backend
- Full control over styling to match Phase 2 design system
- No external service dependency for UI

**Alternatives Considered**:
- OpenAI ChatKit: Requires OpenAI platform setup, domain allowlist complexity
- Third-party chat UI: Additional dependency, style conflicts
- Headless chat library: Good but custom is simpler for this scope

**Component Structure**:
```
components/
├── chat/
│   ├── ChatWidget.tsx       # Main container
│   ├── ChatMessage.tsx      # Individual message
│   ├── ChatInput.tsx        # Input field with send
│   └── ChatToggle.tsx       # Floating button
```

---

### 6. API Endpoint Design

**Decision**: Single `/api/{user_id}/chat` endpoint with conversation_id parameter

**Rationale**:
- Explicit user_id in path for ownership validation
- Optional conversation_id for continuing conversations
- Returns structured response with tool_calls for debugging
- Consistent with Phase 2 API patterns

**Request/Response**:
```python
# Request
POST /api/{user_id}/chat
{
    "conversation_id": 123,  # optional
    "message": "Add buy groceries"
}

# Response
{
    "conversation_id": 123,
    "response": "✅ Added: 'buy groceries' (Task #45)",
    "tool_calls": ["add_task"]
}
```

---

### 7. Error Handling Strategy

**Decision**: Graceful degradation with user-friendly messages

**Rationale**:
- Never expose stack traces or internal errors
- AI service down: Friendly fallback message
- Database error: Retry once, then apologize
- Invalid input: Helpful suggestions

**Error Response Templates**:
```python
ERROR_TEMPLATES = {
    "ai_unavailable": "Chat service temporarily unavailable. Please use the task list directly or try again later.",
    "task_not_found": "Task #{id} not found. Type 'show my tasks' to see your task list.",
    "empty_title": "Please provide a task title. Example: 'Add buy groceries'",
    "invalid_command": "I didn't understand that. Try 'Add [task]', 'Show tasks', 'Complete [task]', or 'Delete [task]'"
}
```

---

### 8. Authentication Integration

**Decision**: Reuse Phase 2 JWT middleware with `get_current_user_id` dependency

**Rationale**:
- No duplication of auth logic
- Consistent security model
- User context automatically available in request

**Integration**:
```python
from src.middleware import get_current_user_id

@router.post("/{user_id}/chat")
async def chat_endpoint(
    user_id: int,
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user_id)
):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
```

---

## Performance Targets

| Metric | Target | Implementation |
|--------|--------|----------------|
| Intent parsing | < 200ms | LLM with structured output |
| MCP tool execution | < 500ms | Indexed database queries |
| Total response | < 2s (p95) | Async processing throughout |
| Concurrent users | 50+ | Connection pooling, stateless design |
| Database pool | 20 connections max | Existing Phase 2 config |

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Agent handoffs fail | max_handoff_depth=5, explicit conditions |
| Database conflicts | Row-level locking, test concurrency |
| Intent misinterpretation | Lower confidence threshold (0.7), ask clarifying questions |
| MCP timeout | Query timeouts (5s), optimized indexes |
| Cohere API rate limits | Implement retry with exponential backoff |
| Token overflow | Limit context to 20 messages |

---

## Dependencies Verified

- **Python**: 3.11+ (Phase 2 uses 3.13)
- **openai-agents-sdk**: Install via pip
- **SQLModel**: Already in Phase 2
- **asyncpg**: Already in Phase 2
- **FastAPI**: Already in Phase 2
- **Cohere API**: Requires `COHERE_API_KEY` environment variable
