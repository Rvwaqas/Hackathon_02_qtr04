# Implementation Plan: AI-Powered Todo Chatbot

**Spec Reference**: `specs/003-ai-todo-chatbot/spec.md`
**Created**: 2026-01-14
**Status**: Approved
**Constitution Check**: Verified against `.specify/memory/constitution.md` v1.0.0

---

## Overview

Extension of Phase II full-stack monorepo with a stateless AI chatbot layer. The chatbot integrates Cohere LLM via OpenAI Agents SDK with 5 MCP tools for task operations. Frontend uses a floating chat icon opening ChatKit panel; backend exposes stateless chat endpoint with conversation persistence.

```
┌─────────────────┐                              ┌─────────────────┐
│   Frontend      │   POST /api/{user_id}/chat   │    Backend      │
│   (Next.js)     │ <─────────────────────────>  │   (FastAPI)     │
│ - Dashboard     │   JWT + conversation_id      │ - Existing CRUD │
│ - ChatKit UI    │                              │ - JWT Middleware│
│ - Chat Icon     │                              │ - Chat Endpoint │
└─────────────────┘                              │ - Cohere Agent  │
         ↑                                       │ - MCP Tools (5) │
         │                                       └─────────────────┘
         │                                                │
    Neon PostgreSQL ◄─────────────────────────────────────┘
    (conversations + messages + tasks)
```

---

## Architecture Decisions

### Decision 1: LLM Provider - Cohere via OpenAI-Compatible Client

**Context**: Need to integrate LLM for natural language understanding and tool selection.

**Options Considered**:
1. Direct Cohere SDK - Native but different API patterns
2. OpenAI Agents SDK with Cohere - Familiar patterns, easy tool calling

**Decision**: OpenAI Agents SDK with custom AsyncOpenAI client pointing to Cohere API

**Rationale**:
- Hackathon requires Cohere (not OpenAI)
- OpenAI Agents SDK provides excellent tool calling patterns
- Cohere offers OpenAI-compatible API endpoint
- Model: `command-r-plus` or latest available

**Constitution Alignment**: P5 (Cohere-Only LLM)

**Implementation**:
```python
from openai import AsyncOpenAI

cohere_client = AsyncOpenAI(
    api_key=os.getenv("COHERE_API_KEY"),
    base_url="https://api.cohere.com/v1"
)
```

---

### Decision 2: MCP Tools Wrap Existing Service Layer

**Context**: Need to implement 5 tools for task operations.

**Options Considered**:
1. Duplicate CRUD logic in MCP tools - Simple but violates DRY
2. MCP tools call existing TaskService - Reusable, single source of truth

**Decision**: MCP tools wrap existing TaskService methods

**Rationale**:
- Existing `TaskService` already handles all CRUD operations
- Single source of truth for business logic
- Reduces bugs from duplicated code
- Changes propagate to both web UI and chat

**Constitution Alignment**: P6 (MCP Tool Design)

---

### Decision 3: Single Conversation Thread Per User

**Context**: How to manage conversation history.

**Options Considered**:
1. Multiple conversation threads - More complex, not required
2. Single thread per user - Simplest, meets requirements

**Decision**: Single active conversation thread per user

**Rationale**:
- Spec explicitly states single thread is sufficient
- Reduces complexity in DB queries
- No UI needed for conversation switching
- New conversation can be started by user request (future)

**Constitution Alignment**: P7 (Conversation Persistence)

---

### Decision 4: Floating Chat Icon with Slide-In Panel

**Context**: How to integrate chat UI into existing dashboard.

**Options Considered**:
1. Separate /chat page only - Less discoverable
2. Floating icon on dashboard - Always accessible, better UX

**Decision**: Floating chat icon in bottom-right corner, opens slide-in panel

**Rationale**:
- Quick access from any dashboard view
- Standard UX pattern for chat widgets
- Doesn't interfere with existing dashboard layout
- ChatKit fits well in panel/modal format

**Constitution Alignment**: P9 (ChatKit Frontend)

---

## Component Breakdown

### Backend Components

#### 1. Database Models (`backend/src/models/`)

**New Files**:
- `conversation.py` - Conversation model
- `message.py` - Message model

**Modified Files**:
- `__init__.py` - Export new models

---

#### 2. MCP Tools (`backend/src/mcp/`)

**New Directory**: `backend/src/mcp/`

**Files**:
- `__init__.py` - Package init
- `tools.py` - 5 MCP tools implementation

**Tool Signatures**:
```python
@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict

@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> dict

@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> dict

@mcp.tool()
async def update_task(user_id: str, task_id: int, title: str = None, description: str = None) -> dict

@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict
```

---

#### 3. Agent Service (`backend/src/services/`)

**New Files**:
- `agent.py` - Todo agent with Cohere client
- `conversation.py` - Conversation CRUD service

**Agent Configuration**:
```python
agent = Agent(
    name="TodoAssistant",
    instructions="""You are a friendly todo assistant.
    Help users manage their tasks using natural language.
    Always confirm actions with friendly messages and emojis.
    When tasks are ambiguous, ask for clarification.""",
    model="command-r-plus",
    tools=[add_task, list_tasks, complete_task, update_task, delete_task]
)
```

---

#### 4. Chat API Route (`backend/src/api/`)

**New Files**:
- `chat.py` - Chat endpoint implementation

**Endpoint**: `POST /api/users/{user_id}/chat`

**Request Cycle**:
1. Validate JWT, extract user_id
2. Load/create conversation
3. Load message history (last 20-30)
4. Append user message
5. Run agent with Cohere
6. Execute tool calls if any
7. Save all messages to DB
8. Return response

---

### Frontend Components

#### 1. Chat UI Components (`frontend/components/`)

**New Files**:
- `ChatIcon.tsx` - Floating chat button
- `ChatPanel.tsx` - Slide-in chat panel
- `ChatMessages.tsx` - Message list display

---

#### 2. Chat Page/Route (`frontend/app/`)

**New Files**:
- `chat/page.tsx` - Optional dedicated chat page

**Modified Files**:
- `dashboard/page.tsx` - Add ChatIcon component

---

#### 3. API Integration (`frontend/lib/`)

**New Files**:
- `chat-api.ts` - Chat API client functions

---

## Implementation Sequence

### Phase 1: Database & Models (Backend)
1. Create Conversation model with SQLModel
2. Create Message model with SQLModel
3. Add migration for new tables
4. Create composite indexes

### Phase 2: MCP Tools (Backend)
5. Create `mcp/` directory structure
6. Implement `add_task` tool
7. Implement `list_tasks` tool
8. Implement `complete_task` tool
9. Implement `update_task` tool
10. Implement `delete_task` tool
11. Add tool logging

### Phase 3: Agent & Conversation Service (Backend)
12. Create Cohere client wrapper
13. Create ConversationService (CRUD)
14. Create TodoAgent with instructions
15. Attach MCP tools to agent

### Phase 4: Chat Endpoint (Backend)
16. Create chat.py route file
17. Implement stateless request cycle
18. Add JWT validation
19. Integrate with existing auth middleware
20. Add error handling

### Phase 5: Frontend Chat UI
21. Create ChatIcon component (floating button)
22. Create ChatPanel component (slide-in)
23. Integrate ChatKit for messages
24. Create chat-api.ts client
25. Add ChatIcon to dashboard layout

### Phase 6: Integration & Testing
26. End-to-end testing with Cohere
27. Test all 5 natural language operations
28. Test conversation persistence
29. Test user isolation
30. Update environment variables

---

## Data Model

See `data-model.md` for complete schema.

**Summary**:
- `conversations`: id (UUID), user_id, title, created_at, updated_at
- `messages`: id, conversation_id, user_id, role, content, tool_call_id, tool_name, created_at

---

## API Contracts

See `contracts/chat-api.yaml` for OpenAPI specification.

**Summary**:

```yaml
POST /api/users/{user_id}/chat
Request:
  message: string (required)
  conversation_id: string (optional)
Response:
  response: string
  conversation_id: string
```

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cohere API rate limits | Medium | High | Implement retry logic, error messages |
| Tool calling accuracy | Medium | Medium | Strong tool descriptions, confirmation pattern |
| Token limits with long history | Low | Medium | Limit to 20-30 messages |
| ChatKit domain config | Low | High | Configure early in development |

---

## Testing Strategy

### Unit Tests
- [ ] ConversationService CRUD operations
- [ ] MCP tool parameter validation
- [ ] Message history loading with limit

### Integration Tests
- [ ] Chat endpoint with mock Cohere
- [ ] Tool execution with real database
- [ ] User isolation verification

### End-to-End Tests
- [ ] Full chat flow: add → list → complete → delete
- [ ] Conversation persistence after refresh
- [ ] Multiple users isolation
- [ ] Error handling scenarios

---

## Constitution Compliance Checklist

- [x] P1: Spec reference included (`specs/003-ai-todo-chatbot/spec.md`)
- [x] P2: Backward compatibility verified (no changes to existing endpoints)
- [x] P3: User isolation in all queries (user_id filtering)
- [x] P4: No in-memory state (DB persistence)
- [x] P5: Cohere API only (via OpenAI-compatible client)
- [x] P6: MCP tools follow spec (5 tools, stateless)
- [x] P7: Conversation persistence implemented (conversations + messages tables)
- [x] P8: JWT auth reused (existing middleware)
- [x] P9: ChatKit integration planned (floating icon + panel)
- [x] P10: Graceful error handling planned (friendly messages)

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `COHERE_API_KEY` | Cohere API key | Yes |
| `DATABASE_URL` | Neon PostgreSQL connection | Yes (existing) |
| `JWT_SECRET` | JWT signing secret | Yes (existing) |
| `CHATKIT_DOMAIN` | Domain allowlist for ChatKit | Production only |

---

## ADR Suggestions

📋 Architectural decision detected: **Cohere via OpenAI-compatible client pattern**
   Document reasoning and tradeoffs? Run `/sp.adr cohere-openai-adapter`

📋 Architectural decision detected: **MCP tools wrapping existing service layer**
   Document reasoning and tradeoffs? Run `/sp.adr mcp-service-wrapper`
