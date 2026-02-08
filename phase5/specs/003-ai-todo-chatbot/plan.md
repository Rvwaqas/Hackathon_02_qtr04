# Implementation Plan: AI-Powered Todo Chatbot with Cohere Integration

**Branch**: `003-ai-todo-chatbot` | **Date**: 2026-01-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-ai-todo-chatbot/spec.md`

## Summary

Extend Phase II full-stack todo application with a stateless AI-powered chatbot that allows authenticated users to manage tasks via natural language. The chatbot integrates with the existing database and authentication system, using Cohere LLM powered by OpenAI Agents SDK, with conversation history persisted in PostgreSQL. The implementation maintains strict user data isolation, operates entirely stateless on the backend, and provides a seamless UX via floating chatbot UI powered by OpenAI ChatKit.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Neon PostgreSQL, OpenAI Agents SDK, Official MCP SDK (Python), AsyncOpenAI (Cohere-compatible client)
- Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS, OpenAI ChatKit, Better Auth
**Storage**: PostgreSQL (Neon) — extensions to existing schema: `conversations` and `messages` tables
**Testing**: pytest (backend), Jest/Vitest (frontend) — scenarios-based manual testing for chat interactions
**Target Platform**: Web application (browser) — no mobile/PWA in scope
**Project Type**: Web application — monorepo structure with `/frontend` and `/backend` directories
**Performance Goals**:
- Chat endpoint p95 latency: under 3 seconds (network + Cohere)
- Chat UI interactions: under 500ms (button click, panel open/close)
- Conversation history load: under 2 seconds
- Concurrent users supported: 100+ (stateless architecture allows horizontal scaling)

**Constraints**:
- Cohere API must be the exclusive LLM provider (no OpenAI direct calls)
- Stateless backend only — all conversation state in database
- No in-memory caching or Redis — database is single source of truth
- REST POST only — no WebSockets or real-time streaming
- User isolation mandatory — user_id from JWT required for all operations
- Existing Phase II features must remain fully functional (zero breaking changes)

**Scale/Scope**:
- Data: single conversation thread per user; messages stored in DB
- Feature scope: 7 user stories (5 P1, 2 P2); 18 functional requirements
- Implementation: ~2-3 weeks with the architecture outlined

## Constitution Check

✅ **GATE PASSED**: Plan aligns with all Phase III Constitution principles:

1. **Strictly Spec-Driven Development**: ✅ This plan is generated directly from spec.md; implementation will follow spec-driven workflow
2. **Seamless Backend Integration**: ✅ Reuses existing database (PostgreSQL), authentication (Better Auth + JWT), and task service layer; new tables only extend schema
3. **User Data Isolation & Security (NON-NEGOTIABLE)**: ✅ user_id from JWT mandatory for all MCP tools; conversation_id tied to user_id; no cross-user access possible
4. **Stateless Server Architecture**: ✅ Conversation history stored in database; no in-memory state; each request is independent; horizontal scaling enabled
5. **Tech Stack Standardization**: ✅ Mandatory use of Cohere API, OpenAI Agents SDK, Official MCP SDK, OpenAI ChatKit as specified

**No Constitution violations detected**. Plan fully compliant with all core principles.

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-todo-chatbot/
├── spec.md                 # ✅ Feature specification (complete)
├── plan.md                 # ✅ This file (implementation plan)
├── research.md             # (Phase 0 - TBD if clarifications needed)
├── data-model.md           # (Phase 1 - to be generated)
├── quickstart.md           # (Phase 1 - to be generated)
├── contracts/              # (Phase 1 - API contracts)
│   ├── chat-api.yaml       # POST /api/{user_id}/chat endpoint
│   └── mcp-tools.md        # MCP tool contracts
└── checklists/
    └── requirements.md     # ✅ Quality validation (passed)
```

### Source Code Structure (Monorepo)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py                    # (existing)
│   │   ├── user.py                    # (existing)
│   │   ├── conversation.py            # (NEW) Conversation entity
│   │   └── message.py                 # (NEW) Message entity
│   ├── services/
│   │   ├── task_service.py            # (existing - reused)
│   │   ├── conversation_service.py    # (NEW) Manage conversations & messages
│   │   └── user_service.py            # (existing)
│   ├── api/
│   │   ├── routes/
│   │   │   ├── tasks.py               # (existing)
│   │   │   ├── auth.py                # (existing)
│   │   │   └── chat.py                # (NEW) POST /api/{user_id}/chat
│   │   └── middleware/
│   │       └── jwt_auth.py            # (existing - extended for chat)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── todo_agent.py              # (NEW) Agent with Cohere + MCP tools
│   │   └── config.py                  # (NEW) Agent configuration
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── tools.py                   # (NEW) 5 MCP tools (add, list, complete, update, delete)
│   │   └── cohere_client.py           # (NEW) AsyncOpenAI wrapper for Cohere
│   ├── database.py                    # (existing - migrations for new tables)
│   ├── config.py                      # (existing - new env vars: COHERE_API_KEY)
│   └── main.py                        # (existing - register new chat endpoint)
└── tests/
    ├── unit/
    │   ├── test_mcp_tools.py          # Unit tests for MCP tools
    │   └── test_agent.py              # Unit tests for agent logic
    ├── integration/
    │   ├── test_chat_endpoint.py      # Integration tests for /api/{user_id}/chat
    │   ├── test_conversation_flow.py  # Multi-turn conversation tests
    │   └── test_user_isolation.py     # User data isolation tests
    └── scenarios/
        └── manual_scenarios.md        # Manual test scenarios (all examples from spec)

frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   └── page.tsx               # (existing - add chat icon here)
│   │   └── chat/
│   │       └── page.tsx               # (NEW) Chat page (optional, if needed)
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatButton.tsx         # (NEW) Floating chatbot icon button
│   │   │   ├── ChatPanel.tsx          # (NEW) Chat panel (slide-in/modal)
│   │   │   ├── ChatKitWrapper.tsx     # (NEW) OpenAI ChatKit integration
│   │   │   └── ChatMessage.tsx        # (NEW) Message display
│   │   └── ui/
│   │       ├── Button.tsx             # (existing)
│   │       └── Modal.tsx              # (existing - reused for chat panel)
│   ├── lib/
│   │   ├── api.ts                     # (existing - add chatAPI client)
│   │   ├── chatApi.ts                 # (NEW) Chat API wrapper for /api/{user_id}/chat
│   │   └── useChat.ts                 # (NEW) React hook for chat state management
│   └── types/
│       ├── api.ts                     # (existing)
│       └── chat.ts                    # (NEW) Chat-specific types (Message, Conversation)
└── tests/
    ├── unit/
    │   └── test_chat_components.tsx   # Component tests
    └── integration/
        └── test_chat_integration.tsx  # E2E chat flow tests
```

**Structure Decision**: Web application (monorepo) with separate `/backend` and `/frontend` directories. Backend extends existing Phase II structure with new MCP agent layer. Frontend adds chat UI as floating component on dashboard.

## Key Architectural Decisions

### 1. LLM Provider: Cohere via OpenAI-Compatible Client
- **Choice**: Cohere Command R+ via AsyncOpenAI(base_url="https://api.cohere.com/v1")
- **Rationale**: Required by constitution; excellent tool-calling capabilities; OpenAI Agents SDK supports custom clients seamlessly
- **Alternatives Rejected**: Direct OpenAI (not allowed), Anthropic (not allowed), LLaMA (local deployment complexity)

### 2. Agent Framework: OpenAI Agents SDK
- **Choice**: OpenAI Agents SDK with custom AsyncOpenAI client for Cohere
- **Rationale**: Matches hackathon pattern; excellent tool calling; minimal custom code needed
- **Alternatives Rejected**: LangChain (heavier), LlamaIndex (RAG-focused), custom implementation (risk)

### 3. Conversation Storage: Database Only (Single Thread per User)
- **Choice**: PostgreSQL tables (conversations, messages) — no Redis or in-memory cache
- **Rationale**: Stateless architecture; meets requirements; simplest implementation
- **Alternatives Rejected**: Redis (requires cache invalidation; adds complexity), Multiple threads (out of scope)

### 4. Tool Implementation: Wrap Existing Task Service
- **Choice**: MCP tools call existing TaskService layer
- **Rationale**: Single source of truth; reuse tested logic; minimal duplication
- **Alternatives Rejected**: Duplicate CRUD logic (maintenance burden), Direct DB access (skips validation)

### 5. Chat UI: OpenAI ChatKit Component
- **Choice**: OpenAI ChatKit (hosted/self-hosted with domain key)
- **Rationale**: Production-ready; beautiful UI; handles history; domain allowlist security
- **Alternatives Rejected**: Custom chat bubbles (dev time), Streamlit (not web-native)

### 6. Chat Access: Floating Icon on Dashboard
- **Choice**: Bottom-right floating button; click opens slide-in/modal panel
- **Rationale**: Always accessible; non-intrusive; matches modern UX patterns
- **Alternatives Rejected**: Separate page only (less accessible), always-open sidebar (space waste)

## Implementation Sequence (Phases)

### Phase 1: Foundation (Database & Infrastructure)
1. Create Conversation and Message models (SQLModel) — enable persistence
2. Create database migrations for new tables
3. Implement ConversationService (CRUD operations)
4. Setup Cohere client (AsyncOpenAI wrapper with base_url + api_key)
5. Create environment variable configuration (COHERE_API_KEY, domain key)

### Phase 2: Agent & MCP Tools
6. Implement 5 MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)
   - Each tool wraps existing TaskService
   - Each tool receives user_id and validates access
7. Create TodoAgent with Cohere model and attach MCP tools
8. Setup agent instructions ("You are a friendly todo assistant...")

### Phase 3: Chat Endpoint
9. Implement POST /api/{user_id}/chat endpoint
   - Accept: {message, conversation_id?}
   - Load conversation history (if conversation_id provided)
   - Run agent with Cohere LLM and MCP tools
   - Save user message and assistant response to database
   - Return: {response, conversation_id}
10. Add error handling and logging
11. Add rate limiting (if needed)

### Phase 4: Frontend Integration
12. Create ChatButton component (floating icon, bottom-right)
13. Create ChatPanel component (modal/slide-in)
14. Integrate OpenAI ChatKit (conversation display, input, send)
15. Create chatApi.ts client (wrapper around /api/{user_id}/chat)
16. Create useChat hook (state management: messages, conversation_id, loading)
17. Connect ChatPanel to chat endpoint via hook
18. Add Tailwind styling (match dashboard theme)

### Phase 5: Testing & Validation
19. Unit tests for MCP tools (task CRUD operations)
20. Integration tests for chat endpoint (multi-turn conversations)
21. User isolation tests (verify user A cannot access user B's tasks)
22. Manual scenario testing (all examples from spec.md)
23. Persistence testing (refresh page → history loads)
24. Error handling tests (missing task, ambiguous reference, API failure)

### Phase 6: Polish & Deployment
25. Update README with new features and setup instructions
26. Add environment variable documentation (COHERE_API_KEY, domain key)
27. Verify existing Phase II features still work (regression test)
28. Optimize performance (cache conversation list? batch updates?)
29. Deploy to staging and test with real Cohere API
30. Deploy to production

## Testing & Validation Strategy

### Manual Scenario Tests (from spec.md)

| Scenario | Test Command | Expected Outcome |
|----------|--------------|------------------|
| Add task | "Add a task to buy groceries tomorrow" | "Task 'Buy groceries tomorrow' added! ✅" |
| List tasks | "Show my pending tasks" | Lists all pending tasks with IDs |
| Complete task | "Mark task 1 as complete" | "Task 1 marked as complete! 🎉" |
| Update task | "Change task 2 to 'High priority'" | "Task 2 updated! ✏️" |
| Delete task | "Delete task 3" | "Task 3 deleted. ✂️" |
| Persistence | Refresh page after 5 messages | All 5 messages reappear |
| Restart resilience | Server restart during conversation | Conversation loads correctly |
| User isolation | User A and B chat simultaneously | No cross-user data leakage |
| Error handling | "Mark task 999 complete" | "I couldn't find task 999..." |
| Out of domain | "What's the weather?" | "I'm a todo assistant..." |

### Automated Tests

- **Unit Tests**: MCP tools (task CRUD), agent initialization
- **Integration Tests**: /api/{user_id}/chat endpoint, multi-turn conversation flow, conversation persistence
- **Contract Tests**: API request/response format matches spec
- **E2E Tests** (optional): Chat panel UI interactions, message send/receive, history reload

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Cohere tool calling inconsistency | Agent may not select correct tool | Provide clear tool descriptions; test with multiple tool use scenarios |
| Conversation history grows large | Performance degradation on load | Implement pagination (load last N messages); consider archival |
| User mistypes ambiguous references | Agent error or confusion | Implement clarification logic; list options with IDs |
| Cohere API latency | Slow chat response (>3s) | Implement timeout with fallback message; cache recent tool results |
| Cross-user data leakage (security) | CRITICAL: Privacy violation | Enforce user_id in all MCP tools; add integration tests for isolation |
| Existing Phase II features break | Regression failure | Run full Phase II test suite before deployment |

## Out of Scope

The following are explicitly OUT OF SCOPE for Phase III:

- Multiple conversation threads per user
- Voice input/output or audio
- File attachments or image handling
- Advanced agent memory (vector embeddings, RAG)
- Real-time multi-user collaborative chat
- Custom LLM training or fine-tuning
- Mobile app or PWA changes
- Browser-specific optimizations
- Analytics or usage tracking beyond conversation logging

---

## Next Steps (for /sp.tasks)

After this plan is approved, run `/sp.tasks` to generate `tasks.md` with:
- Detailed task breakdown organized by user story (P1 first, then P2)
- Each task with exact file paths and dependencies
- Parallel execution opportunities identified
- Independent test criteria for each user story
- MVP scope (likely: Phase 1 + Phase 2 + Phase 3 for core functionality)

**Status**: ✅ Plan Complete — Ready for Task Generation

