# Tasks: AI-Powered Todo Chatbot with Cohere Integration

**Input**: Design documents from `/specs/003-ai-todo-chatbot/`
**Prerequisites**: plan.md (✅), spec.md (✅), data-model.md (✅), contracts/ (✅), quickstart.md (✅)
**Status**: Task breakdown complete — ready for implementation

**Tests**: OPTIONAL — included as reference; implement with TDD approach if desired

**Organization**: Tasks are grouped by user story (P1 first, then P2) to enable independent implementation and testing of each story

---

## Implementation Strategy

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 core
- Phase 1: Database & foundation (enable persistence)
- Phase 2: Agent & MCP tools (core AI logic)
- Phase 3: Chat endpoint (user-facing API)
- User Stories 1-5 (P1): Core functionality (add, list, complete, update, delete)

**Post-MVP**: User Stories 6-7 (P1), Phase 4-6

**Parallel Opportunities**:
- Backend Phase 1 + Frontend Phase 1 (independent)
- MCP tool implementation (5 tools are parallelizable)
- Unit tests for each tool (parallelizable)

---

## Phase 1: Setup & Foundation (Shared Infrastructure)

**Purpose**: Project initialization and database schema setup

- [ ] T001 Create project structure and verify existing Phase II setup (backend, frontend directories)
- [ ] T002 [P] Create Conversation model in `backend/src/models/conversation.py` with id, user_id (FK), created_at, updated_at, title
- [ ] T003 [P] Create Message model in `backend/src/models/message.py` with id, conversation_id (FK), role, content, created_at, metadata
- [ ] T004 Create database migration file `backend/migrations/001_add_chat_tables.sql` (conversations + messages tables with indexes)
- [ ] T005 Execute migration and verify tables created in PostgreSQL
- [ ] T006 Create ConversationService in `backend/src/services/conversation_service.py` with methods: create_conversation(), get_conversation(), add_message(), get_messages()
- [ ] T007 [P] Create Cohere client wrapper in `backend/src/agents/cohere_client.py` using AsyncOpenAI(api_key=COHERE_API_KEY, base_url="https://api.cohere.com/v1")
- [ ] T008 Update `backend/src/config.py` to add COHERE_API_KEY and COHERE_MODEL environment variables
- [ ] T009 Update `.env` and `.env.example` with new environment variables
- [ ] T010 Create agent configuration file `backend/src/agents/config.py` with system prompt and agent settings

**Checkpoint**: Foundation complete — database ready, Cohere client configured

---

## Phase 2: Foundational Prerequisites (Blocking)

**Purpose**: Core infrastructure that MUST be complete before user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 [P] Implement MCP tool: `add_task` in `backend/src/mcp/tools.py` — wrapper around TaskService.create_task() with user_id validation
- [ ] T012 [P] Implement MCP tool: `list_tasks` in `backend/src/mcp/tools.py` — retrieve tasks filtered by status (pending/completed/all)
- [ ] T013 [P] Implement MCP tool: `complete_task` in `backend/src/mcp/tools.py` — mark task complete with user_id isolation check
- [ ] T014 [P] Implement MCP tool: `update_task` in `backend/src/mcp/tools.py` — modify title/description/priority with validation
- [ ] T015 [P] Implement MCP tool: `delete_task` in `backend/src/mcp/tools.py` — remove task with user_id authorization
- [ ] T016 Create TodoAgent class in `backend/src/agents/todo_agent.py` with Cohere client and MCP tools attached
- [ ] T017 Implement agent execution logic with conversation history loading and message saving
- [ ] T018 Setup MCP tool registration with OpenAI Agents SDK format (tool definitions, parameter schemas)

**Checkpoint**: Agent & tools ready — ready for endpoint implementation

---

## Phase 3: User Story 1 - Add Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: User can type natural language to create a task without UI forms

**Independent Test**: Open chat → type "Add task: Buy groceries" → verify task appears in dashboard

### Tests for User Story 1 (OPTIONAL)

- [ ] T019 [P] Unit test for add_task tool in `backend/tests/unit/test_mcp_tools.py` — verify task creation with title extraction
- [ ] T020 [P] Integration test for chat endpoint in `backend/tests/integration/test_chat_endpoint.py` — send add task message, verify response contains ✅ emoji
- [ ] T021 Manual scenario test: "Add a task to buy groceries tomorrow" → verify task created with title "Buy groceries tomorrow"

### Implementation for User Story 1

- [ ] T022 [US1] Create chat route handler in `backend/src/api/routes/chat.py` — POST /api/{user_id}/chat endpoint
- [ ] T023 [US1] Implement request validation for ChatRequest model (message required, conversation_id optional)
- [ ] T024 [US1] Implement conversation lifecycle logic: create new if not provided, reuse if exists and belongs to user
- [ ] T025 [US1] Load conversation history from database and format for agent
- [ ] T026 [US1] Save user message to database (role: "user")
- [ ] T027 [US1] Execute agent with user message and conversation history
- [ ] T028 [US1] Save agent response to database (role: "assistant")
- [ ] T029 [US1] Return ChatResponse with response text, conversation_id, message_id
- [ ] T030 [US1] Add error handling for invalid conversation_id, database failures, Cohere API timeout
- [ ] T031 [US1] Add logging for all chat interactions (user_id, conversation_id, message, response, latency)
- [ ] T032 [P] [US1] Create ChatButton component in `frontend/src/components/chat/ChatButton.tsx` — floating icon button (bottom-right, Tailwind styled)
- [ ] T033 [P] [US1] Create ChatPanel component in `frontend/src/components/chat/ChatPanel.tsx` — modal/slide-in with message display
- [ ] T034 [P] [US1] Create chatApi.ts client in `frontend/src/lib/chatApi.ts` — wrapper around POST /api/{user_id}/chat
- [ ] T035 [P] [US1] Create useChat hook in `frontend/src/lib/useChat.ts` — React hook for chat state (messages, conversation_id, loading)
- [ ] T036 [US1] Integrate ChatButton + ChatPanel into dashboard `frontend/src/app/dashboard/page.tsx`
- [ ] T037 [US1] Style chat components with Tailwind CSS (match dashboard theme, loading states, error messages)
- [ ] T038 [US1] Test end-to-end: click chat button → type "Add task..." → verify task appears in dashboard

**Checkpoint**: User Story 1 fully functional and testable independently

---

## Phase 4: User Story 2 - View Tasks via Natural Language (Priority: P1)

**Goal**: User can query tasks and see results with friendly formatting

**Independent Test**: Open chat → type "Show my pending tasks" → verify all pending tasks listed with IDs

### Tests for User Story 2 (OPTIONAL)

- [ ] T039 Unit test for list_tasks tool in `backend/tests/unit/test_mcp_tools.py` — verify filtering by status (pending/completed/all)
- [ ] T040 Integration test for list query in `backend/tests/integration/test_chat_endpoint.py` — send "Show pending tasks" message, verify task list format
- [ ] T041 Manual scenario test: User with 3 pending tasks → "Show my pending tasks" → all 3 tasks displayed

### Implementation for User Story 2

- [ ] T042 [US2] Update agent instructions in `backend/src/agents/config.py` to include task list formatting guidance
- [ ] T043 [US2] Test agent tool selection for list_tasks (ensure agent calls correct tool for queries)
- [ ] T044 [US2] Test task list formatting in agent response (grouped by status, with IDs and titles)
- [ ] T045 [US2] Verify no code changes needed in frontend (reuses existing ChatPanel from US1)
- [ ] T046 [US2] Manual test: type variations ("List tasks", "What tasks do I have?", "Show completed tasks") → verify all work

**Checkpoint**: User Story 2 fully functional

---

## Phase 5: User Story 3 - Complete Task via Natural Language (Priority: P1)

**Goal**: User can mark tasks complete using natural language references (ID or description)

**Independent Test**: Have pending task → type "Mark task 1 as complete" → verify status changes in dashboard

### Tests for User Story 3 (OPTIONAL)

- [ ] T047 Unit test for complete_task tool in `backend/tests/unit/test_mcp_tools.py` — verify status update and error handling (not found, already complete)
- [ ] T048 Integration test for complete action in `backend/tests/integration/test_chat_endpoint.py` — send "Mark task 1 complete", verify 🎉 confirmation
- [ ] T049 Manual scenario test: "Mark task 1 as complete" → verify dashboard shows task as completed

### Implementation for User Story 3

- [ ] T050 [US3] Test agent tool selection for complete_task (ensure agent recognizes complete intent)
- [ ] T051 [US3] Test agent parameter extraction (extract task_id from natural language)
- [ ] T052 [US3] Test agent error handling (ambiguous reference, missing task, already completed)
- [ ] T053 [US3] Test agent response formatting (include emoji confirmation ✅, task title)
- [ ] T054 [US3] Manual test: "Mark the grocery task as done" (by description, not ID) → verify agent finds correct task
- [ ] T055 [US3] Manual test: "Complete task 999" (non-existent) → verify graceful error response

**Checkpoint**: User Story 3 fully functional

---

## Phase 6: User Story 4 - Update Task via Natural Language (Priority: P2)

**Goal**: User can modify task properties (title, priority, etc.) via natural language

**Independent Test**: Have existing task → type "Change task 2 to high priority" → verify priority updated in dashboard

### Tests for User Story 4 (OPTIONAL)

- [ ] T056 Unit test for update_task tool in `backend/tests/unit/test_mcp_tools.py` — verify partial updates, error handling
- [ ] T057 Integration test for update action in `backend/tests/integration/test_chat_endpoint.py` — send "Change task 2 to...", verify ✏️ response
- [ ] T058 Manual scenario test: "Change task 2 to 'Buy groceries and cook dinner'" → verify title updated

### Implementation for User Story 4

- [ ] T059 [US4] Test agent parameter extraction for update (title, priority, description)
- [ ] T060 [US4] Test agent handling of partial updates (only some fields provided)
- [ ] T061 [US4] Test agent clarification when update is ambiguous
- [ ] T062 [US4] Manual test: "Set task 3 priority to high" → verify priority field updated
- [ ] T063 [US4] Manual test: "Update task description" (incomplete) → verify agent asks for clarification

**Checkpoint**: User Story 4 fully functional

---

## Phase 7: User Story 5 - Delete Task via Natural Language (Priority: P2)

**Goal**: User can remove tasks via natural language with confirmation

**Independent Test**: Have task → type "Delete task 3" → verify task no longer appears

### Tests for User Story 5 (OPTIONAL)

- [ ] T064 Unit test for delete_task tool in `backend/tests/unit/test_mcp_tools.py` — verify deletion, error handling (not found)
- [ ] T065 Integration test for delete action in `backend/tests/integration/test_chat_endpoint.py` — send "Delete task 3", verify ✂️ response
- [ ] T066 Manual scenario test: "Delete the milk task" (by description) → verify agent finds and deletes task

### Implementation for User Story 5

- [ ] T067 [US5] Test agent parameter extraction for delete (task_id from ID or description)
- [ ] T068 [US5] Test agent clarification for ambiguous deletions
- [ ] T069 [US5] Test agent confirmation message (task deleted, no accidental loses)
- [ ] T070 [US5] Manual test: "Remove the first task" (ambiguous) → verify agent asks which task user means
- [ ] T071 [US5] Manual test: "Delete task 999" (non-existent) → verify graceful error response

**Checkpoint**: User Story 5 fully functional

---

## Phase 8: User Story 6 - Conversation Persistence (Priority: P1)

**Goal**: Chat history persists across page refresh and server restart

**Independent Test**: Send 5 messages → refresh page → verify all 5 messages reload

### Tests for User Story 6 (OPTIONAL)

- [ ] T072 Integration test for persistence in `backend/tests/integration/test_conversation_flow.py` — send multiple messages, reload, verify history intact
- [ ] T073 Integration test for server restart resilience — restart server, reopen chat, verify conversation loads
- [ ] T074 Manual scenario test: Send 5 messages → F5 refresh → verify messages reappear in order

### Implementation for User Story 6

- [ ] T075 [US6] Implement conversation history loading on chat open (fetch from DB on demand)
- [ ] T076 [US6] Test conversation ID persistence (created on first message, reused on subsequent messages)
- [ ] T077 [US6] Test message ordering (load messages ASC by created_at)
- [ ] T078 [US6] Test frontend state management (store conversation_id in session/context, reuse across page refreshes)
- [ ] T079 [US6] Manual test: Close chat panel → reopen → verify conversation still visible
- [ ] T080 [US6] Manual test: Refresh entire page → reopen chat → verify full history loaded

**Checkpoint**: User Story 6 fully functional — conversation persistence guaranteed

---

## Phase 9: User Story 7 - Chat UI Integration (Priority: P1)

**Goal**: Prominent chatbot icon visible on dashboard; clicking opens chat panel

**Independent Test**: Log in → navigate to dashboard → verify chat icon visible → click → panel opens

### Tests for User Story 7 (OPTIONAL)

- [ ] T081 Component test for ChatButton in `frontend/tests/unit/test_chat_components.tsx` — verify button renders, click toggles panel open/close
- [ ] T082 Component test for ChatPanel in `frontend/tests/unit/test_chat_components.tsx` — verify message display, input field, send button work
- [ ] T083 E2E test for UI integration in `frontend/tests/integration/test_chat_integration.tsx` — navigate dashboard, click chat button, send message, verify response appears

### Implementation for User Story 7

- [ ] T084 [US7] Verify ChatButton component renders on dashboard (already created in US1)
- [ ] T085 [US7] Test chat icon visibility (bottom-right, not obscuring dashboard)
- [ ] T086 [US7] Test panel open/close animation (smooth slide or fade)
- [ ] T087 [US7] Test message input focus (click input, type, send with Enter or button)
- [ ] T088 [US7] Test loading state (show "Thinking..." while waiting for response)
- [ ] T089 [US7] Test error state (network error, Cohere API timeout, display user-friendly message)
- [ ] T090 [US7] Manual test: Chat button visible, clickable, panel opens, can type and send messages

**Checkpoint**: User Story 7 complete — chat UI fully accessible and integrated

---

## Phase 10: Cross-Cutting Concerns & Testing

**Purpose**: User isolation validation, error handling verification, performance, documentation

- [ ] T091 [P] Implement user isolation test in `backend/tests/integration/test_user_isolation.py` — verify User A cannot access User B's conversations or tasks
- [ ] T092 [P] Implement error handling tests in `backend/tests/integration/test_chat_endpoint.py` — test 401 (auth), 404 (conversation), 500 (Cohere API failure)
- [ ] T093 [P] Create manual test scenarios file `backend/tests/scenarios/manual_scenarios.md` with all examples from spec.md
- [ ] T094 [P] Verify existing Phase II features still work (regression test: dashboard, task REST API, authentication)
- [ ] T095 Implement rate limiting in chat endpoint (optional: 10 messages/min per user)
- [ ] T096 Add performance monitoring/logging for chat latency (measure agent execution time, database queries)
- [ ] T097 Create deployment checklist (environment variables, database migrations, dependency installation)
- [ ] T098 Update backend README with new chat API documentation
- [ ] T099 Update frontend README with ChatKit setup and customization
- [ ] T100 Document all environment variables required (COHERE_API_KEY, domain allowlist key, etc.)

**Checkpoint**: All tests passing, documentation complete

---

## Phase 11: Optimization & Production Readiness

**Purpose**: Performance tuning, security hardening, deployment preparation

- [ ] T101 Optimize conversation history queries (add pagination if >50 messages per conversation)
- [ ] T102 Add request/response logging with timestamps and latency tracking
- [ ] T103 Verify Cohere API error handling (rate limiting, timeout, invalid responses)
- [ ] T104 Add CORS configuration for ChatKit domain allowlist
- [ ] T105 Test with real Cohere API in staging environment
- [ ] T106 Load test: simulate 100+ concurrent users, measure p95 latency
- [ ] T107 Security audit: verify user_id validation in all MCP tools, no SQL injection, XSS prevention
- [ ] T108 Database backup verification (conversations and messages tables)
- [ ] T109 Create runbook for common issues (high latency, Cohere API errors, database connection issues)
- [ ] T110 Prepare production deployment plan (rolling out chat feature without downtime)

**Checkpoint**: Production ready — all systems validated

---

## Task Dependency Graph

```
Phase 1 (Foundation)
├─ T001-T010: Database, config, Cohere client setup
└─ Blocks: All user stories

Phase 2 (Foundational)
├─ T011-T018: MCP tools and agent
└─ Blocks: All user stories

Phase 3-7 (User Stories 1-5, core functionality)
├─ T022-T071: Add, List, Complete, Update, Delete tasks
├─ User Stories independent of each other (can implement in parallel after Phase 2)
└─ Blocks: User Stories 6-7

Phase 8-9 (User Stories 6-7, polish)
├─ T072-T090: Persistence and UI integration
└─ Depends on: User Stories 1-5 (feature-complete)

Phase 10-11 (Testing and production)
├─ T091-T110: Validation, optimization, deployment
└─ Depends on: All prior phases
```

---

## Parallel Execution Opportunities

**After Phase 2 complete, can execute in parallel**:

1. **Backend: User Story 3 (Complete)** + **Frontend: US1 Chat UI** → different files, no dependencies
2. **Backend: US4 (Update)** + **Backend: US5 (Delete)** → different tools, parallelizable
3. **All MCP tool unit tests** (T019, T039, T047, etc.) → independent tests for each tool
4. **Regression testing Phase II** (T094) → can run in parallel with US implementations

**Example Parallel Execution Schedule**:
```
Day 1-2:   Phase 1 (Foundation) — sequential
Day 3:     Phase 2 (Agent & Tools) — sequential
Day 4-5:   Phase 3 (US1 backend) + Phase 4-5 (US2-3 backend) + Phase 3 (US1 frontend) — parallel
Day 5-6:   Phase 6-7 (US4-5 backend) + Phase 8-9 (Persistence + UI tests) — parallel
Day 7-8:   Phase 10-11 (Testing, optimization, deployment) — final validation
```

---

## MVP Scope Checklist

**Minimum Viable Product includes**:

- [x] Phase 1: Database and foundation
- [x] Phase 2: Agent and MCP tools
- [x] Phase 3: Chat endpoint (POST /api/{user_id}/chat)
- [x] User Story 1: Add task
- [x] User Story 2: List tasks
- [x] User Story 3: Complete task
- [x] User Story 4: Update task (P2, optional but prioritized)
- [x] User Story 5: Delete task (P2, optional but prioritized)
- [x] User Story 6: Conversation persistence
- [x] User Story 7: Chat UI integration
- [x] Phase 10: Testing and user isolation
- [ ] Phase 11: Production optimization (post-MVP)

**MVP Deliverable**: Fully functional chatbot that handles all 5 task operations via natural language, persists conversations, integrates with Phase II, and maintains user isolation.

---

## Format Validation

✅ **All tasks follow required checklist format**:
- Each task has checkbox: `- [ ]`
- Each task has Task ID: `T001`, `T002`, etc.
- [P] marker included only for parallelizable tasks
- [Story] label (e.g., `[US1]`) included only for user story phase tasks
- Each task includes exact file path for reference

**Example verified**:
- ✅ `- [ ] T001 Create project structure and verify existing Phase II setup (backend, frontend directories)`
- ✅ `- [ ] T032 [P] [US1] Create ChatButton component in frontend/src/components/chat/ChatButton.tsx`
- ✅ `- [ ] T011 [P] Implement MCP tool: add_task in backend/src/mcp/tools.py`

---

## Next Steps

1. **Start Phase 1**: Setup database and foundation infrastructure
2. **Run unit tests as you go**: Use TDD approach if desired (tests already outlined)
3. **Validate user isolation**: Critical security requirement (test in Phase 10)
4. **Test with real Cohere API**: After Phase 2 complete, try end-to-end with real API
5. **Deploy to staging**: After Phase 10, validate in staging environment
6. **Production rollout**: Use Phase 11 deployment plan for zero-downtime release

---

**Total Task Count**: 110 implementation tasks
- **Phase 1 (Setup)**: 10 tasks
- **Phase 2 (Foundation)**: 8 tasks
- **User Stories (P1)**: 48 tasks (US1-3, US6-7)
- **User Stories (P2)**: 24 tasks (US4-5)
- **Testing & Polish**: 20 tasks
- **Parallel Opportunities**: 5+ opportunities identified

**Estimated Implementation Time**: 2-3 weeks with full team

**Status**: ✅ READY FOR IMPLEMENTATION

