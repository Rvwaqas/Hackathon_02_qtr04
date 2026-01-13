# Implementation Tasks: Todo AI Chatbot Integration with MCP Architecture

**Feature**: `003-ai-chatbot-mcp`
**Generated**: 2026-01-13
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Task Summary

| Phase | Description | Task Count |
|-------|-------------|------------|
| 1 | Setup & Configuration | 6 |
| 2 | Foundation (Database & MCP Tools) | 12 |
| 3 | US1: Natural Language Task Creation | 8 |
| 4 | US2: View and List Tasks | 5 |
| 5 | US3: Mark Tasks Complete | 4 |
| 6 | US4: Update Tasks | 4 |
| 7 | US5: Delete Tasks | 4 |
| 8 | US6: Compound Commands | 3 |
| 9 | US7: Conversation Persistence | 5 |
| 10 | US8: Clarification & Ambiguity | 3 |
| 11 | Frontend Integration | 8 |
| 12 | Polish & Documentation | 6 |
| **Total** | | **68** |

---

## Phase 1: Setup & Configuration

**Goal**: Initialize project dependencies and configuration

- [ ] T001 Install openai-agents SDK in phase3/backend: `pip install openai-agents`
- [ ] T002 Install python-dotenv in phase3/backend: `pip install python-dotenv`
- [ ] T003 [P] Verify COHERE_API_KEY is set in phase3/backend/.env
- [ ] T004 [P] Verify DATABASE_URL points to Neon PostgreSQL in phase3/backend/.env
- [ ] T005 Create agents directory structure at phase3/backend/src/agents/__init__.py
- [ ] T006 Create tools directory structure at phase3/backend/src/tools/__init__.py

**Validation Gate**: All dependencies installed, .env configured, directory structure created

---

## Phase 2: Foundation (Database & MCP Tools)

**Goal**: Create database models and MCP tools that all user stories depend on

### Database Models

- [ ] T007 [P] Create Conversation model in phase3/backend/src/models/conversation.py
- [ ] T008 [P] Create Message model in phase3/backend/src/models/message.py
- [ ] T009 Export new models in phase3/backend/src/models/__init__.py
- [ ] T010 Create ConversationService in phase3/backend/src/services/conversation.py
- [ ] T011 Run database migration to create conversations and messages tables
- [ ] T012 Create ChatRequest/ChatResponse schemas in phase3/backend/src/schemas/chat.py

### MCP Tools

- [ ] T013 [P] Create mcp_tools.py with add_task tool in phase3/backend/src/tools/mcp_tools.py
- [ ] T014 [P] Implement list_tasks tool with status filter in phase3/backend/src/tools/mcp_tools.py
- [ ] T015 [P] Implement complete_task tool in phase3/backend/src/tools/mcp_tools.py
- [ ] T016 [P] Implement update_task tool in phase3/backend/src/tools/mcp_tools.py
- [ ] T017 [P] Implement delete_task tool in phase3/backend/src/tools/mcp_tools.py
- [ ] T018 Add user_id ownership validation to all MCP tools in phase3/backend/src/tools/mcp_tools.py

**Validation Gate**: Models created, tables exist in database, all 5 MCP tools return valid responses

---

## Phase 3: User Story 1 - Natural Language Task Creation (P0)

**Story Goal**: Users can create tasks via natural language chat commands

**Independent Test**: Sign in, open chat, type "Add buy groceries", verify task created with confirmation

### Agent System for Task Creation

- [ ] T019 [US1] Create Cohere client configuration in phase3/backend/src/agents/config.py
- [ ] T020 [US1] Create IntentParser agent in phase3/backend/src/agents/intent_parser.py
- [ ] T021 [US1] Create MCPValidator agent in phase3/backend/src/agents/mcp_validator.py
- [ ] T022 [US1] Create TaskManager agent with add_task tool in phase3/backend/src/agents/task_manager.py
- [ ] T023 [US1] Create ResponseFormatter agent with add_task template in phase3/backend/src/agents/response_formatter.py
- [ ] T024 [US1] Create MainOrchestrator with handoffs in phase3/backend/src/agents/orchestrator.py

### API Endpoint for Task Creation

- [ ] T025 [US1] Create POST /api/{user_id}/chat endpoint in phase3/backend/src/api/chat.py
- [ ] T026 [US1] Register chat router in phase3/backend/src/main.py

**Validation Gate**: "Add buy groceries" creates task and returns confirmation message

---

## Phase 4: User Story 2 - View and List Tasks (P1)

**Story Goal**: Users can view their task list via chat commands

**Independent Test**: Type "Show my tasks", verify all tasks displayed with IDs and status

- [ ] T027 [US2] Add list_tasks intent patterns to IntentParser in phase3/backend/src/agents/intent_parser.py
- [ ] T028 [US2] Add list_tasks tool to TaskManager agent in phase3/backend/src/agents/task_manager.py
- [ ] T029 [US2] Add list_tasks formatting template to ResponseFormatter in phase3/backend/src/agents/response_formatter.py
- [ ] T030 [US2] Add empty state message "You have no tasks yet" in phase3/backend/src/agents/response_formatter.py
- [ ] T031 [US2] Add status filter support (pending/completed/all) to list_tasks in phase3/backend/src/tools/mcp_tools.py

**Validation Gate**: "Show my tasks" and "What's pending?" return correct task lists

---

## Phase 5: User Story 3 - Mark Tasks Complete (P2)

**Story Goal**: Users can mark tasks complete via chat

**Independent Test**: Type "Mark task 5 done", verify task status changes to completed

- [ ] T032 [US3] Add complete_task intent patterns to IntentParser in phase3/backend/src/agents/intent_parser.py
- [ ] T033 [US3] Add complete_task tool to TaskManager agent in phase3/backend/src/agents/task_manager.py
- [ ] T034 [US3] Add complete_task formatting template with celebration emoji in phase3/backend/src/agents/response_formatter.py
- [ ] T035 [US3] Add "already completed" handling in complete_task tool in phase3/backend/src/tools/mcp_tools.py

**Validation Gate**: "Mark task 5 done" completes task and shows celebration message

---

## Phase 6: User Story 4 - Update Tasks (P3)

**Story Goal**: Users can update task titles via chat

**Independent Test**: Type "Change task 3 to 'Call mom tonight'", verify title updated

- [ ] T036 [US4] Add update_task intent patterns to IntentParser in phase3/backend/src/agents/intent_parser.py
- [ ] T037 [US4] Add update_task tool to TaskManager agent in phase3/backend/src/agents/task_manager.py
- [ ] T038 [US4] Add update_task formatting template showing old/new title in phase3/backend/src/agents/response_formatter.py
- [ ] T039 [US4] Add empty title validation in update_task tool in phase3/backend/src/tools/mcp_tools.py

**Validation Gate**: "Change task 3 to 'new title'" updates task and shows confirmation

---

## Phase 7: User Story 5 - Delete Tasks (P4)

**Story Goal**: Users can delete tasks via chat

**Independent Test**: Type "Delete task 7", verify task removed from database

- [ ] T040 [US5] Add delete_task intent patterns to IntentParser in phase3/backend/src/agents/intent_parser.py
- [ ] T041 [US5] Add delete_task tool to TaskManager agent in phase3/backend/src/agents/task_manager.py
- [ ] T042 [US5] Add delete_task formatting template in phase3/backend/src/agents/response_formatter.py
- [ ] T043 [US5] Add "task not found" error handling in delete_task tool in phase3/backend/src/tools/mcp_tools.py

**Validation Gate**: "Delete task 7" removes task and shows confirmation

---

## Phase 8: User Story 6 - Compound Commands (P5)

**Story Goal**: Users can issue multiple commands in one message

**Independent Test**: Type "Add buy milk and show all my tasks", verify both operations execute

- [ ] T044 [US6] Add compound command detection to IntentParser in phase3/backend/src/agents/intent_parser.py
- [ ] T045 [US6] Enable TaskManager to execute multiple tools sequentially in phase3/backend/src/agents/task_manager.py
- [ ] T046 [US6] Add compound response formatting (combine multiple results) in phase3/backend/src/agents/response_formatter.py

**Validation Gate**: "Add eggs and show tasks" creates task AND displays list

---

## Phase 9: User Story 7 - Conversation Persistence (P6)

**Story Goal**: Conversation history persists across sessions

**Independent Test**: Create task, close browser, reopen, verify history preserved

- [ ] T047 [US7] Create ContextManager agent in phase3/backend/src/agents/context_manager.py
- [ ] T048 [US7] Implement load_conversation with 20-message limit in phase3/backend/src/services/conversation.py
- [ ] T049 [US7] Implement save_message for user and assistant messages in phase3/backend/src/services/conversation.py
- [ ] T050 [US7] Add conversation loading at request start in phase3/backend/src/api/chat.py
- [ ] T051 [US7] Add message saving after response in phase3/backend/src/api/chat.py

**Validation Gate**: Conversation history survives browser close and server restart

---

## Phase 10: User Story 8 - Clarification & Ambiguity (P7)

**Story Goal**: Chatbot asks for clarification when commands are ambiguous

**Independent Test**: Type "Delete the task" with multiple tasks, verify clarifying question asked

- [ ] T052 [US8] Add confidence threshold (0.7) to IntentParser in phase3/backend/src/agents/intent_parser.py
- [ ] T053 [US8] Add clarifying question logic when confidence < 0.7 in phase3/backend/src/agents/intent_parser.py
- [ ] T054 [US8] Add "didn't understand" fallback response in phase3/backend/src/agents/response_formatter.py

**Validation Gate**: Ambiguous commands trigger clarification requests

---

## Phase 11: Frontend Integration

**Goal**: Build chat UI and integrate with dashboard

### Chat Components

- [ ] T055 [P] Create ChatMessage component in phase3/frontend/components/chat/ChatMessage.tsx
- [ ] T056 [P] Create ChatInput component in phase3/frontend/components/chat/ChatInput.tsx
- [ ] T057 [P] Create ChatToggle floating button in phase3/frontend/components/chat/ChatToggle.tsx
- [ ] T058 Create ChatWidget container in phase3/frontend/components/chat/ChatWidget.tsx
- [ ] T059 Create chat API client in phase3/frontend/lib/chat-api.ts

### Dashboard Integration

- [ ] T060 Import and render ChatWidget in phase3/frontend/app/dashboard/page.tsx
- [ ] T061 Add responsive styles for chat widget (desktop 400x600, mobile fullscreen)
- [ ] T062 Add loading spinner and error message display in ChatWidget

**Validation Gate**: Chat widget opens from dashboard, messages send and display correctly

---

## Phase 12: Polish & Documentation

**Goal**: Final testing, optimization, and documentation

- [ ] T063 Add error handling for AI service unavailability in phase3/backend/src/api/chat.py
- [ ] T064 Add structured logging for all agent operations in phase3/backend/src/agents/orchestrator.py
- [ ] T065 Add database indexes on messages.conversation_id if not exists
- [ ] T066 Create README.md with setup instructions in phase3/specs/003-ai-chatbot-mcp/
- [ ] T067 Verify all 8 user stories work end-to-end
- [ ] T068 Measure and verify response time < 2s (p95)

**Validation Gate**: All user stories pass, documentation complete, performance targets met

---

## Dependency Graph

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundation: Database + MCP Tools)
    │
    ├──────────────────────────────────────────┐
    │                                          │
    ▼                                          ▼
Phase 3 (US1: Create)                    Phase 11 (Frontend)
    │                                          │
    ▼                                          │
Phase 4 (US2: List)                            │
    │                                          │
    ▼                                          │
Phase 5 (US3: Complete)                        │
    │                                          │
    ▼                                          │
Phase 6 (US4: Update)                          │
    │                                          │
    ▼                                          │
Phase 7 (US5: Delete)                          │
    │                                          │
    ▼                                          │
Phase 8 (US6: Compound)                        │
    │                                          │
    ▼                                          │
Phase 9 (US7: Persistence) ◄───────────────────┘
    │
    ▼
Phase 10 (US8: Clarification)
    │
    ▼
Phase 12 (Polish)
```

---

## Parallel Execution Opportunities

### Within Phase 2 (Foundation)
```
T007 (Conversation model) ─┬─ T009 (exports) ─► T010 (service)
T008 (Message model) ──────┘

T013 (add_task) ─┬─► T018 (ownership validation)
T014 (list_tasks) ─┤
T015 (complete_task) ─┤
T016 (update_task) ─┤
T017 (delete_task) ─┘
```

### Within Phase 11 (Frontend)
```
T055 (ChatMessage) ─┬─► T058 (ChatWidget)
T056 (ChatInput) ───┤
T057 (ChatToggle) ──┘
```

---

## MVP Scope (Recommended)

For minimum viable demonstration, complete through **Phase 5 (US3)**:

1. **Phase 1**: Setup (6 tasks)
2. **Phase 2**: Foundation (12 tasks)
3. **Phase 3**: US1 - Task Creation (8 tasks)
4. **Phase 4**: US2 - List Tasks (5 tasks)
5. **Phase 5**: US3 - Complete Tasks (4 tasks)
6. **Phase 11**: Frontend (8 tasks) - can be done in parallel with US2-US3

**MVP Total**: 43 tasks

This delivers a functional chatbot that can:
- Create tasks via natural language
- List tasks with status filtering
- Mark tasks as complete
- Display in a chat UI

---

## Deliverables Checklist

- [ ] Working FastAPI endpoint at POST /api/{user_id}/chat
- [ ] 5 MCP tools (add, list, complete, update, delete) fully functional
- [ ] 6 agents coordinating via sequential handoffs
- [ ] Chat widget integrated in Phase 2 dashboard
- [ ] Conversation persistence across sessions
- [ ] >90% intent recognition accuracy
- [ ] <2s response time (p95)
- [ ] Documentation complete
