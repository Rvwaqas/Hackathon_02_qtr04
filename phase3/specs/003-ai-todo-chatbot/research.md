# Research: AI-Powered Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Created**: 2026-01-14
**Status**: Complete

---

## Research Topics

### 1. Cohere API Integration with OpenAI Agents SDK

**Question**: How to use Cohere LLM with OpenAI Agents SDK?

**Decision**: Use AsyncOpenAI client with Cohere's OpenAI-compatible endpoint

**Rationale**:
- Cohere provides OpenAI-compatible API at `https://api.cohere.com/v1`
- OpenAI Agents SDK works with any OpenAI-compatible provider
- Minimal code changes required - just change base_url and api_key
- Tool calling works natively with Cohere Command R+ models

**Alternatives Considered**:
1. Direct Cohere SDK (`cohere-ai`) - Different API patterns, would need custom adapter
2. LangChain with Cohere - Additional dependency, more complex
3. Custom HTTP client - Too low-level, reinventing the wheel

**Implementation Pattern**:
```python
from openai import AsyncOpenAI
import os

cohere_client = AsyncOpenAI(
    api_key=os.getenv("COHERE_API_KEY"),
    base_url="https://api.cohere.com/v1"
)

# Use with OpenAI Agents SDK
from agents import Agent, Runner

agent = Agent(
    name="TodoAssistant",
    model="command-r-plus",  # Cohere model
    client=cohere_client,
    tools=[...]
)
```

---

### 2. MCP Tool Implementation Pattern

**Question**: How to implement MCP tools that wrap existing service?

**Decision**: Create thin wrapper functions that call TaskService methods

**Rationale**:
- Existing `TaskService` already implements all CRUD logic
- Single source of truth - changes propagate everywhere
- Tools just handle parameter conversion and response formatting
- Maintains clean separation of concerns

**Alternatives Considered**:
1. Duplicate logic in tools - Violates DRY, maintenance burden
2. Pass TaskService directly - Tight coupling, harder to test
3. Event-based system - Overkill for this use case

**Implementation Pattern**:
```python
from mcp.server import Server
from mcp.types import Tool

server = Server("todo-mcp-server")

@server.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Add a new task for the user."""
    async with get_session() as session:
        task = await TaskService.create_task(
            session=session,
            user_id=int(user_id),
            data=TaskCreate(title=title, description=description)
        )
        return {
            "success": True,
            "task_id": task.id,
            "message": f"Task '{title}' added!"
        }
```

---

### 3. Conversation Persistence Strategy

**Question**: How to store and retrieve conversation history efficiently?

**Decision**: Two tables (conversations, messages) with composite indexes

**Rationale**:
- Normalized schema for flexibility
- Composite index on (conversation_id, user_id) for fast lookups
- Single thread per user simplifies queries
- Limit to 20-30 messages for context window

**Alternatives Considered**:
1. Single table with JSON - Less queryable, harder to paginate
2. Redis cache - Violates stateless requirement, data loss risk
3. File-based storage - Not scalable, no transactions

**Schema Design**:
```sql
-- conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL REFERENCES users(id),
    title VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_conv_user ON conversations(user_id);

-- messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    user_id VARCHAR NOT NULL,
    role VARCHAR NOT NULL,  -- 'user', 'assistant', 'tool', 'system'
    content TEXT NOT NULL,
    tool_call_id VARCHAR,
    tool_name VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_msg_conv_user ON messages(conversation_id, user_id);
CREATE INDEX idx_msg_created ON messages(conversation_id, created_at);
```

---

### 4. ChatKit Integration

**Question**: How to integrate OpenAI ChatKit with Next.js?

**Decision**: Use ChatKit React component with custom API handler

**Rationale**:
- ChatKit provides production-ready UI components
- Works with any backend via adapter pattern
- Domain allowlist ensures security in production
- Tailwind CSS compatible for styling

**Alternatives Considered**:
1. Custom chat UI - More work, less polished
2. Streamlit - Python only, doesn't fit Next.js
3. Third-party chat widgets - Less control, vendor lock-in

**Implementation Pattern**:
```tsx
// components/ChatPanel.tsx
import { Chat } from '@openai/chatkit';

export function ChatPanel({ userId }: { userId: string }) {
  const handleSend = async (message: string) => {
    const response = await fetch(`/api/users/${userId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return response.json();
  };

  return (
    <Chat
      onSend={handleSend}
      placeholder="Ask me to manage your tasks..."
    />
  );
}
```

---

### 5. Stateless Chat Endpoint Design

**Question**: How to implement stateless chat with conversation context?

**Decision**: Load history from DB on each request, no server-side session

**Rationale**:
- Fully stateless enables horizontal scaling
- No data loss on server restart
- Conversation context loaded fresh each request
- Meets constitution requirement (P4)

**Request Cycle**:
```
1. Receive POST /api/{user_id}/chat
2. Validate JWT, extract user_id
3. Load/create conversation (conversation_id from body or new)
4. Load last 20-30 messages from DB
5. Build messages array for agent
6. Run agent with Cohere
7. Execute any tool calls
8. Save user message + assistant response + tool results to DB
9. Return response with conversation_id
```

**Alternatives Considered**:
1. WebSocket with server state - Violates stateless requirement
2. Redis session cache - Adds complexity, data loss risk
3. Cookie-based context - Size limits, security concerns

---

## Technology Versions

| Technology | Version | Notes |
|------------|---------|-------|
| Cohere API | v1 | OpenAI-compatible endpoint |
| Command R+ | Latest | Tool calling capable |
| OpenAI Agents SDK | Latest | Python async support |
| MCP SDK | Official Python | Tool definition patterns |
| ChatKit | Latest | React components |
| SQLModel | 0.0.x | Async support required |
| FastAPI | 0.100+ | Async endpoints |
| Next.js | 16+ | App Router |

---

## Key Findings

1. **Cohere Integration is Straightforward** - OpenAI-compatible API makes SDK reuse trivial
2. **MCP Tools Should Be Thin Wrappers** - Reuse existing TaskService for consistency
3. **Single Thread Simplifies Everything** - No need for conversation selection UI
4. **ChatKit Works with Any Backend** - Just needs adapter for API calls
5. **Stateless Design is Clean** - Each request self-contained, scales horizontally

---

## Resolved Clarifications

All technical unknowns have been resolved:

| Topic | Resolution |
|-------|------------|
| Cohere API pattern | OpenAI-compatible client |
| Tool implementation | Wrap TaskService |
| Conversation storage | Two-table normalized schema |
| Chat UI | ChatKit with custom adapter |
| Stateless design | DB-loaded context each request |

---

## Next Steps

1. Proceed to `data-model.md` for detailed schema
2. Generate API contracts in `contracts/`
3. Create `quickstart.md` for setup guide
