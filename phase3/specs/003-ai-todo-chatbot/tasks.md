# Implementation Tasks: AI-Powered Todo Chatbot

**Spec Reference**: `specs/003-ai-todo-chatbot/spec.md`
**Plan Reference**: `specs/003-ai-todo-chatbot/plan.md`
**Created**: 2026-01-14
**Status**: Implementation Complete (41/42 tasks)
**Constitution Check**: Verified against `.specify/memory/constitution.md` v1.0.0

---

## Task Summary

| Status | Count |
|--------|-------|
| ⬜ Not Started | 1 |
| 🔄 In Progress | 0 |
| ✅ Complete | 41 |
| **Total** | **42** |

| Phase | Tasks | User Story |
|-------|-------|------------|
| Phase 1: Setup | 5 | - |
| Phase 2: Foundation | 8 | US7 (Conversation Persistence) |
| Phase 3: Chat Interface | 6 | US1 (Access Chatbot) |
| Phase 4: Add Task | 3 | US2 |
| Phase 5: List Tasks | 3 | US3 |
| Phase 6: Complete Task | 3 | US4 |
| Phase 7: Update Task | 3 | US5 |
| Phase 8: Delete Task | 3 | US6 |
| Phase 9: Polish | 8 | US8 (Error Handling) |

---

## Phase 1: Setup

**Goal**: Project initialization and environment configuration.

- [x] T001 Add COHERE_API_KEY to backend/.env file
- [x] T002 [P] Install openai package in backend via `pip install openai` or add to requirements.txt
- [x] T003 [P] Install mcp package in backend via `pip install mcp` or add to requirements.txt
- [ ] T004 [P] Install @openai/chatkit in frontend via `npm install @openai/chatkit`
- [x] T005 Create backend/src/mcp/ directory structure with __init__.py

---

## Phase 2: Foundation (US7 - Conversation Persistence)

**Goal**: Database models and conversation service for persistence.

**Story**: As an authenticated user, I expect my chat history to persist so that I can continue conversations across sessions.

**Independent Test**: Have a conversation, refresh the page, reopen chat, verify all previous messages are loaded.

### Database Models

- [x] T006 [US7] Create Conversation model in backend/src/models/conversation.py per data-model.md
- [x] T007 [P] [US7] Create Message model in backend/src/models/message.py per data-model.md
- [x] T008 [US7] Export Conversation and Message from backend/src/models/__init__.py
- [x] T009 [US7] Run database migration to create conversations and messages tables

### Conversation Service

- [x] T010 [US7] Create ConversationService class in backend/src/services/conversation.py
- [x] T011 [US7] Implement get_or_create_conversation method in ConversationService
- [x] T012 [US7] Implement load_history method with 20-30 message limit in ConversationService
- [x] T013 [US7] Implement save_message method in ConversationService

---

## Phase 3: Chat Interface (US1 - Access Chatbot)

**Goal**: Frontend chat UI and backend chat endpoint.

**Story**: As an authenticated user, I can access the chatbot from the dashboard so that I can manage tasks via natural language.

**Independent Test**: Log in to dashboard, verify floating chat icon visible in bottom-right corner, click icon, verify chat panel opens with ChatKit UI.

### Backend Chat Endpoint

- [x] T014 [US1] Create chat.py route file in backend/src/api/chat.py
- [x] T015 [US1] Implement POST /api/users/{user_id}/chat endpoint with JWT validation
- [x] T016 [US1] Register chat router in backend/src/main.py

### Frontend Chat Components

- [x] T017 [P] [US1] Create ChatIcon.tsx floating button component in frontend/components/chat/ChatIcon.tsx
- [x] T018 [US1] Create ChatPanel.tsx slide-in panel component in frontend/components/chat/ChatPanel.tsx
- [x] T019 [US1] Add ChatIcon component to dashboard layout in frontend/app/dashboard/page.tsx

---

## Phase 4: Add Task via Chat (US2)

**Goal**: Implement add_task MCP tool and agent integration.

**Story**: As an authenticated user, I can tell the chatbot to add a task so that I can create tasks using natural language.

**Independent Test**: Open chat, type "Add a task to buy groceries tomorrow", verify chatbot responds with confirmation, verify task appears in dashboard.

- [x] T020 [US2] Implement add_task MCP tool in backend/src/mcp/tools.py
- [x] T021 [US2] Create Cohere client wrapper in backend/src/services/agent.py
- [x] T022 [US2] Create TodoAgent with add_task tool attached in backend/src/services/agent.py

---

## Phase 5: List Tasks via Chat (US3)

**Goal**: Implement list_tasks MCP tool.

**Story**: As an authenticated user, I can ask the chatbot to show my tasks so that I can see what I need to do.

**Independent Test**: Create 3 tasks via dashboard, open chat, type "Show me my tasks", verify chatbot lists all 3 tasks with IDs.

- [x] T023 [US3] Implement list_tasks MCP tool with status filter in backend/src/mcp/tools.py
- [x] T024 [US3] Add list_tasks tool to TodoAgent in backend/src/services/agent.py
- [x] T025 [US3] Verify list_tasks returns tasks in formatted response

---

## Phase 6: Complete Task via Chat (US4)

**Goal**: Implement complete_task MCP tool.

**Story**: As an authenticated user, I can tell the chatbot to mark a task as complete so that I can track my progress.

**Independent Test**: Create task via dashboard, open chat, type "Mark task 1 as complete", verify chatbot confirms, verify task shows completed in dashboard.

- [x] T026 [US4] Implement complete_task MCP tool in backend/src/mcp/tools.py
- [x] T027 [US4] Add complete_task tool to TodoAgent in backend/src/services/agent.py
- [x] T028 [US4] Verify complete_task returns confirmation with task title

---

## Phase 7: Update Task via Chat (US5)

**Goal**: Implement update_task MCP tool.

**Story**: As an authenticated user, I can tell the chatbot to update a task so that I can modify task details.

**Independent Test**: Create task "Buy milk", open chat, type "Change task 1 to 'Buy groceries'", verify chatbot confirms update.

- [x] T029 [US5] Implement update_task MCP tool in backend/src/mcp/tools.py
- [x] T030 [US5] Add update_task tool to TodoAgent in backend/src/services/agent.py
- [x] T031 [US5] Verify update_task returns confirmation with old and new title

---

## Phase 8: Delete Task via Chat (US6)

**Goal**: Implement delete_task MCP tool.

**Story**: As an authenticated user, I can tell the chatbot to delete a task so that I can remove tasks I no longer need.

**Independent Test**: Create task, open chat, type "Delete task 1", verify chatbot confirms deletion with task title.

- [x] T032 [US6] Implement delete_task MCP tool in backend/src/mcp/tools.py
- [x] T033 [US6] Add delete_task tool to TodoAgent in backend/src/services/agent.py
- [x] T034 [US6] Verify delete_task returns confirmation with deleted task title

---

## Phase 9: Polish & Error Handling (US8)

**Goal**: Graceful error handling and UI polish.

**Story**: As an authenticated user, I expect the chatbot to handle errors gracefully so that I always understand what happened.

**Independent Test**: Try various error scenarios (invalid task ID, ambiguous commands), verify chatbot responds helpfully.

### Error Handling

- [x] T035 [US8] Add task not found error handling in all MCP tools in backend/src/mcp/tools.py
- [x] T036 [US8] Add friendly error messages to agent instructions in backend/src/services/agent.py
- [x] T037 [US8] Add Cohere API error handling with retry in backend/src/services/agent.py
- [x] T038 [US8] Add frontend error toast notifications in frontend/components/chat/ChatPanel.tsx

### UI Polish

- [x] T039 [P] [US8] Add loading spinner while waiting for chat response in frontend/components/chat/ChatPanel.tsx
- [x] T040 [P] [US8] Add welcome message for empty conversation in frontend/components/chat/ChatPanel.tsx
- [x] T041 [US8] Style ChatPanel with Tailwind CSS to match dashboard theme

### Final Integration

- [x] T042 Verify all 5 natural language operations work end-to-end and update README with COHERE_API_KEY

---

## Dependency Graph

```
Phase 1: Setup
    │
    ▼
Phase 2: Foundation (US7)
    │
    ├─────────────────────────────────────────┐
    ▼                                         │
Phase 3: Chat Interface (US1) ◄───────────────┘
    │
    ├───────┬───────┬───────┬───────┐
    ▼       ▼       ▼       ▼       ▼
Phase 4  Phase 5  Phase 6  Phase 7  Phase 8
(US2)    (US3)    (US4)    (US5)    (US6)
Add      List     Complete Update   Delete
    │       │       │       │       │
    └───────┴───────┴───────┴───────┘
                    │
                    ▼
            Phase 9: Polish (US8)
```

**Key Dependencies**:
- Phase 2 (Foundation) MUST complete before Phase 3+
- Phase 3 (Chat Interface) MUST complete before Phases 4-8
- Phases 4-8 (CRUD operations) can run in PARALLEL after Phase 3
- Phase 9 (Polish) runs AFTER all CRUD operations

---

## Parallel Execution Opportunities

### Phase 1 Parallel Tasks
```
T002, T003, T004 can run in parallel (different package managers)
```

### Phase 2 Parallel Tasks
```
T006, T007 can run in parallel (different model files)
```

### Phases 4-8 Full Parallel
```
After Phase 3 completes, ALL of these can run in parallel:
- Phase 4: T020, T021, T022 (add_task)
- Phase 5: T023, T024, T025 (list_tasks)
- Phase 6: T026, T027, T028 (complete_task)
- Phase 7: T029, T030, T031 (update_task)
- Phase 8: T032, T033, T034 (delete_task)
```

### Phase 9 Parallel Tasks
```
T039, T040 can run in parallel (different UI components)
```

---

## Implementation Strategy

### MVP Scope (Recommended First Milestone)

Complete Phases 1-4 for minimal working chatbot:
1. **Phase 1**: Setup environment
2. **Phase 2**: Database models and conversation service
3. **Phase 3**: Chat UI and endpoint
4. **Phase 4**: add_task tool

**MVP Test**: User can open chat and add a task via natural language.

### Incremental Delivery

| Milestone | Phases | Capability |
|-----------|--------|------------|
| MVP | 1-4 | Add tasks via chat |
| Core CRUD | 5-8 | Full task management |
| Production | 9 | Error handling, polish |

---

## Files to Create/Modify

### New Files (Backend)
- `backend/src/models/conversation.py`
- `backend/src/models/message.py`
- `backend/src/mcp/__init__.py`
- `backend/src/mcp/tools.py`
- `backend/src/services/conversation.py`
- `backend/src/services/agent.py`
- `backend/src/api/chat.py`

### New Files (Frontend)
- `frontend/components/ChatIcon.tsx`
- `frontend/components/ChatPanel.tsx`

### Modified Files
- `backend/src/models/__init__.py` - Export new models
- `backend/src/main.py` - Register chat router
- `frontend/app/dashboard/page.tsx` - Add ChatIcon
- `backend/.env` - Add COHERE_API_KEY
- `README.md` - Document new env vars

---

## Definition of Done

All tasks are considered complete when:

- [ ] All 42 tasks marked complete
- [ ] All 5 natural language operations work (add, list, complete, update, delete)
- [ ] Conversation persists after page refresh
- [ ] Conversation persists after server restart
- [ ] User isolation verified (User A can't see User B's data)
- [ ] Existing dashboard and REST API still functional
- [ ] Chat UI opens/closes smoothly with ChatKit
- [ ] Cohere API is used for all LLM calls (verified via logs)
- [ ] Error handling shows friendly messages
- [ ] Constitution compliance verified (10/10 principles)
