# Tasks: Phase V Part A - Advanced Features & Event-Driven Logic

**Input**: Design documents from `/specs/005-phase5-parta-advanced-events/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: pytest for backend, manual verification for chatbot intents

**Key Finding**: Database model, API routes, schemas, and frontend are **already complete**. Tasks focus on remaining gaps: MCP tools, system prompt, event publishing, and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- Include exact file paths and agent assignments
- Each task is atomic and independently verifiable

## Path Conventions

- **Backend**: `backend/src/`
- **Agents**: `backend/src/agents/`
- **MCP Tools**: `backend/src/mcp/`
- **Services**: `backend/src/services/`
- **Tests**: `backend/tests/`
- **Contracts**: `specs/005-phase5-parta-advanced-events/contracts/`

---

## Phase 1: Event Publishing Foundation (Critical Path)

**Purpose**: Create the event-driven architecture foundation
**Agent**: DaprAgent
**User Story Reference**: US-006 (Event Publishing via Dapr)

### Event Publisher Service

- [X] T501 [US6] Create `backend/src/services/event_publisher.py` with EventPublisher class
  - Import: httpx, uuid, datetime, typing, logging
  - Constants: DAPR_HOST, PUBSUB_NAME, topics
  - Method: `_create_cloud_event(event_type, source, data)` → CloudEvents 1.0 format
  - Method: `async publish(topic, event_type, source, data)` → HTTP POST to Dapr
  - Error handling: Log error on failure, don't raise (graceful degradation)
  - **Acceptance**: Class instantiates without error, methods defined

- [X] T502 [US6] Implement `publish_task_event()` helper method
  - Parameters: event_type, task_id, user_id, task_data dict
  - Builds CloudEvents envelope with task snapshot
  - Publishes to TOPIC_TASK_EVENTS ("task-events")
  - **Acceptance**: Method accepts all parameters, returns bool

- [X] T503 [US6] Implement `publish_reminder_event()` helper method
  - Parameters: task_id, user_id, due_date, reminder_time
  - Builds CloudEvents envelope for reminder trigger
  - Publishes to TOPIC_REMINDERS ("reminders")
  - **Acceptance**: Method accepts all parameters, returns bool

- [X] T504 [US6] Add logging configuration for event publishing
  - Logger named "event_publisher"
  - Log INFO on successful publish
  - Log ERROR on failure with full context
  - **Acceptance**: Logs visible during operation

### TaskService Integration

- [X] T505 [US6] Import EventPublisher in `backend/src/services/task.py`
  - Add import at top of file
  - Instantiate EventPublisher in methods or as class attribute
  - **Acceptance**: Import successful, no errors

- [X] T506 [US6] Add event publishing to `create_task()` method
  - After successful DB commit, call `publish_task_event("com.todo.task.created", ...)`
  - Include full task data in event
  - **Acceptance**: Event published on task creation

- [X] T507 [US6] Add event publishing to `update_task()` method
  - After successful DB commit, call `publish_task_event("com.todo.task.updated", ...)`
  - Include changed fields and current state
  - **Acceptance**: Event published on task update

- [X] T508 [US6] Add event publishing to `toggle_complete()` method
  - After marking complete, call `publish_task_event("com.todo.task.completed", ...)`
  - If recurring, also publish "com.todo.recurring.triggered"
  - **Acceptance**: Completion event published, recurring trigger if applicable

- [X] T509 [US6] Add event publishing to `delete_task()` method
  - After successful DB delete, call `publish_task_event("com.todo.task.deleted", ...)`
  - Include deleted task_id and user_id
  - **Acceptance**: Event published on task deletion

**Checkpoint**: Event publishing integrated with all CRUD operations. Verify with logs.

---

## Phase 2: MCP Tool Definitions (Critical Path)

**Purpose**: Enable chatbot to understand and use new parameters
**Agent**: FeatureAgent
**User Story Reference**: US-001, US-002, US-003, US-004, US-005, US-007

### Update TOOL_DEFINITIONS

- [X] T510 [US1] [US7] Add `tags` parameter to `add_task` tool definition in `backend/src/agents/config.py`
  ```python
  "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Category tags for the task (e.g., ['work', 'personal'])"
  }
  ```
  - **Acceptance**: Tool definition includes tags parameter

- [X] T511 [US4] [US7] Add `recurrence` parameter to `add_task` tool definition
  ```python
  "recurrence": {
      "type": "object",
      "properties": {
          "type": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
          "interval": {"type": "integer", "description": "Number of periods"},
          "end_date": {"type": "string", "description": "ISO 8601 end date"}
      },
      "description": "Make task recurring (daily/weekly/monthly)"
  }
  ```
  - **Acceptance**: Tool definition includes recurrence object

- [X] T512 [US5] [US7] Add `reminder_offset_minutes` parameter to `add_task` tool definition
  ```python
  "reminder_offset_minutes": {
      "type": "integer",
      "description": "Remind user this many minutes before due_date (e.g., 60 for 1 hour)"
  }
  ```
  - **Acceptance**: Tool definition includes reminder parameter

- [X] T513 [US2] [US7] Add `search` parameter to `list_tasks` tool definition
  ```python
  "search": {
      "type": "string",
      "description": "Search keyword to find in task titles or descriptions"
  }
  ```
  - **Acceptance**: Tool definition includes search parameter

- [X] T514 [US2] [US7] Add `tag` parameter to `list_tasks` tool definition
  ```python
  "tag": {
      "type": "string",
      "description": "Filter to show only tasks with this tag"
  }
  ```
  - **Acceptance**: Tool definition includes tag filter

- [X] T515 [US3] [US7] Add `sort` parameter to `list_tasks` tool definition
  ```python
  "sort": {
      "type": "string",
      "enum": ["created_at", "due_date", "priority", "title", "updated_at"],
      "description": "Field to sort results by (default: created_at)"
  }
  ```
  - **Acceptance**: Tool definition includes sort parameter

- [X] T516 [US3] [US7] Add `order` parameter to `list_tasks` tool definition
  ```python
  "order": {
      "type": "string",
      "enum": ["asc", "desc"],
      "description": "Sort order: 'asc' for ascending, 'desc' for descending"
  }
  ```
  - **Acceptance**: Tool definition includes order parameter

- [X] T517 [US1] [US4] [US5] Add new parameters to `update_task` tool definition
  - Add: tags, recurrence, reminder_offset_minutes, due_date
  - Same schemas as add_task
  - **Acceptance**: Update tool supports all new parameters

- [X] T518 [US1-US7] Update tool descriptions to be more helpful for intent recognition
  - add_task: "Create a new task. Supports priority, tags, due dates, reminders, and recurring schedules."
  - list_tasks: "List tasks with filtering by status, priority, tags, and keyword search. Supports sorting."
  - update_task: "Modify task properties including priority, tags, recurrence, and reminders."
  - **Acceptance**: Descriptions clear and comprehensive

**Checkpoint**: All tool definitions updated. Run `python -c "from src.agents.config import TOOL_DEFINITIONS; print('OK')"` to verify.

---

## Phase 3: System Prompt Updates (Critical Path)

**Purpose**: Enable chatbot to recognize new natural language intents
**Agent**: FeatureAgent
**User Story Reference**: US-007 (Chatbot Natural Language Support)

### Update SYSTEM_PROMPT

- [X] T519 [US7] Add priority recognition patterns to SYSTEM_PROMPT
  ```
  PRIORITY RECOGNITION:
  - "high priority", "urgent", "important", "critical" → use priority="high"
  - "medium priority", "normal" → use priority="medium"
  - "low priority", "minor", "can wait" → use priority="low"
  ```
  - **Acceptance**: Prompt includes priority patterns

- [X] T520 [US7] Add tag recognition patterns to SYSTEM_PROMPT
  ```
  TAG RECOGNITION:
  - "tagged X", "tag X", "with tag X", "label X" → include tags=["X"]
  - "tags X and Y", "tagged X, Y" → include tags=["X", "Y"]
  ```
  - **Acceptance**: Prompt includes tag patterns

- [X] T521 [US7] Add search/filter recognition patterns to SYSTEM_PROMPT
  ```
  SEARCH & FILTER:
  - "find X", "search for X", "look for X" → use search="X"
  - "show only high priority" → use priority="high"
  - "show tasks tagged X" → use tag="X"
  - "pending tasks" → use status="pending"
  ```
  - **Acceptance**: Prompt includes search/filter patterns

- [X] T522 [US7] Add sort recognition patterns to SYSTEM_PROMPT
  ```
  SORTING:
  - "sort by due date" → use sort="due_date"
  - "sort by priority" → use sort="priority"
  - "oldest first" → use sort="created_at", order="asc"
  - "newest first" → use sort="created_at", order="desc"
  ```
  - **Acceptance**: Prompt includes sort patterns

- [X] T523 [US7] Add recurrence recognition patterns to SYSTEM_PROMPT
  ```
  RECURRENCE:
  - "repeat daily", "every day" → recurrence={type: "daily", interval: 1}
  - "repeat weekly", "every week" → recurrence={type: "weekly", interval: 1}
  - "repeat monthly", "every month" → recurrence={type: "monthly", interval: 1}
  - "until DATE" → add end_date to recurrence
  ```
  - **Acceptance**: Prompt includes recurrence patterns

- [X] T524 [US7] Add due date recognition patterns to SYSTEM_PROMPT
  ```
  DUE DATES:
  - "due tomorrow", "by tomorrow" → calculate tomorrow's date
  - "due Friday", "by Friday" → calculate next Friday
  - "due in 3 days" → calculate date + 3 days
  ```
  - **Acceptance**: Prompt includes due date patterns

- [X] T525 [US7] Add reminder recognition patterns to SYSTEM_PROMPT
  ```
  REMINDERS:
  - "remind me 30 minutes before" → reminder_offset_minutes=30
  - "remind me 1 hour before" → reminder_offset_minutes=60
  - "remind me 1 day before" → reminder_offset_minutes=1440
  ```
  - **Acceptance**: Prompt includes reminder patterns

- [X] T526 [US7] Add example interactions to SYSTEM_PROMPT
  ```
  EXAMPLE INTERACTIONS:
  User: "add high priority task meeting due Friday tagged work"
  → Call add_task with title="meeting", priority="high", due_date=<next_friday>, tags=["work"]

  User: "show pending tasks tagged work sorted by due date"
  → Call list_tasks with status="pending", tag="work", sort="due_date"
  ```
  - **Acceptance**: Prompt includes helpful examples

**Checkpoint**: System prompt fully updated. Test with sample messages.

---

## Phase 4: TodoToolsHandler Extension

**Purpose**: Handler methods accept and process new parameters
**Agent**: FeatureAgent
**User Story Reference**: US-001, US-002, US-003, US-004, US-005

### Extend add_task Method

- [X] T527 [US1] Update `add_task` signature in `backend/src/mcp/tools.py`
  - Add parameters: tags, recurrence, reminder_offset_minutes
  - Update docstring with new parameters
  - **Acceptance**: Method accepts new parameters

- [X] T528 [US1] Pass tags to TaskCreate in `add_task`
  - Extract from kwargs or direct parameter
  - Default to empty list if not provided
  - **Acceptance**: Tags saved with task

- [X] T529 [US4] Pass recurrence to TaskCreate in `add_task`
  - Extract recurrence dict from kwargs
  - Pass to TaskCreate schema
  - **Acceptance**: Recurrence saved with task

- [X] T530 [US5] Pass reminder_offset_minutes to TaskCreate in `add_task`
  - Extract from kwargs
  - Pass to TaskCreate schema
  - **Acceptance**: Reminder offset saved with task

- [X] T531 [US1] Update success message in `add_task` to include new fields
  - Include priority, tags (if any), due date (if set)
  - Example: "Task 'Meeting' added with priority HIGH, tagged [work], due Feb 7!"
  - **Acceptance**: Message shows relevant details

### Extend list_tasks Method

- [X] T532 [US2] Update `list_tasks` signature in `backend/src/mcp/tools.py`
  - Add parameters: search, tag, sort, order
  - Update docstring
  - **Acceptance**: Method accepts new parameters

- [X] T533 [US2] Pass search parameter to TaskService.get_tasks()
  - Extract from kwargs
  - Pass to service method
  - **Acceptance**: Search filtering works

- [X] T534 [US2] Pass tag parameter to TaskService.get_tasks()
  - Extract from kwargs
  - Pass to service method
  - **Acceptance**: Tag filtering works

- [X] T535 [US3] Pass sort and order parameters to TaskService.get_tasks()
  - Extract from kwargs
  - Default: sort="created_at", order="desc"
  - Pass to service method
  - **Acceptance**: Sorting works

- [X] T536 [US2] [US3] Update formatted_tasks output in `list_tasks`
  - Include: tags, due_date, priority badge
  - Format due_date as human-readable
  - **Acceptance**: Output shows all relevant fields

- [X] T537 [US2] [US3] Update success message in `list_tasks`
  - Include filter/sort context
  - Example: "Found 3 high-priority tasks tagged 'work' sorted by due date"
  - **Acceptance**: Message describes results accurately

### Extend update_task Method

- [X] T538 [US1] [US4] [US5] Update `update_task` signature in `backend/src/mcp/tools.py`
  - Add parameters: tags, recurrence, reminder_offset_minutes, due_date
  - Update docstring
  - **Acceptance**: Method accepts new parameters

- [X] T539 [US1] [US4] [US5] Build update_fields with new parameters
  - Check each new parameter and add to update dict
  - Pass to TaskUpdate schema
  - **Acceptance**: All new fields updateable

- [X] T540 [US1] [US4] [US5] Update success message in `update_task`
  - Include what was changed
  - Example: "Task 5 updated: now recurring weekly, due Feb 14"
  - **Acceptance**: Message describes changes

**Checkpoint**: All handler methods extended. Unit test each method.

---

## Phase 5: Integration Testing

**Purpose**: Verify all features work correctly together
**Agent**: FeatureAgent
**User Story Reference**: All (US-001 through US-007)

### API Filter/Sort Tests

- [X] T541 [US2] Create `backend/tests/test_filters.py`
  - Setup: pytest fixtures for test user and tasks
  - **Acceptance**: Test file created with fixtures

- [X] T542 [P] [US2] Test priority filter
  - Create tasks with different priorities
  - GET /api/tasks?priority=high
  - Assert only high priority tasks returned
  - **Acceptance**: Test passes

- [X] T543 [P] [US2] Test tag filter
  - Create tasks with different tags
  - GET /api/tasks?tag=work
  - Assert only tasks with "work" tag returned
  - **Acceptance**: Test passes

- [X] T544 [P] [US2] Test search by keyword
  - Create tasks with specific keywords
  - GET /api/tasks?search=meeting
  - Assert tasks matching keyword returned
  - **Acceptance**: Test passes

- [X] T545 [P] [US3] Test sort by due_date
  - Create tasks with different due dates
  - GET /api/tasks?sort=due_date&order=asc
  - Assert correct order
  - **Acceptance**: Test passes

- [X] T546 [P] [US3] Test sort by priority
  - Create tasks with different priorities
  - GET /api/tasks?sort=priority&order=desc
  - Assert high → medium → low order
  - **Acceptance**: Test passes

- [X] T547 [US2] [US3] Test combined filters
  - GET /api/tasks?status=pending&priority=high&tag=work&sort=due_date
  - Assert all filters applied correctly
  - **Acceptance**: Test passes

### Event Publishing Tests

- [X] T548 [US6] Create `backend/tests/test_events.py`
  - Setup: Mock httpx for Dapr endpoint
  - **Acceptance**: Test file created with mocks

- [X] T549 [P] [US6] Test event published on task creation
  - Mock Dapr response
  - Create task via service
  - Assert HTTP POST called with CloudEvents JSON
  - Assert event type is "com.todo.task.created"
  - **Acceptance**: Test passes

- [X] T550 [P] [US6] Test event published on task update
  - Mock Dapr response
  - Update task via service
  - Assert event type is "com.todo.task.updated"
  - **Acceptance**: Test passes

- [X] T551 [P] [US6] Test event published on task completion
  - Mock Dapr response
  - Complete task via service
  - Assert event type is "com.todo.task.completed"
  - **Acceptance**: Test passes

- [X] T552 [P] [US6] Test event published on task deletion
  - Mock Dapr response
  - Delete task via service
  - Assert event type is "com.todo.task.deleted"
  - **Acceptance**: Test passes

- [X] T553 [US6] Test CloudEvents schema validation
  - Capture published event
  - Validate: specversion, type, source, id, time, datacontenttype, data
  - **Acceptance**: Schema validation passes

- [X] T554 [US6] Test graceful degradation when Dapr unavailable
  - Mock httpx to raise connection error
  - Create task
  - Assert task created successfully (DB commit)
  - Assert error logged
  - **Acceptance**: Test passes

### Chatbot Intent Tests

- [X] T555 [US7] Create `backend/tests/test_chatbot_intents.py`
  - Setup: Test agent with mocked Cohere client
  - **Acceptance**: Test file created

- [X] T556 [P] [US7] Test priority intent recognition
  - Message: "add high priority task meeting"
  - Assert: add_task called with priority="high"
  - **Acceptance**: Test passes

- [X] T557 [P] [US7] Test tag intent recognition
  - Message: "add task report tagged work"
  - Assert: add_task called with tags=["work"]
  - **Acceptance**: Test passes

- [X] T558 [P] [US7] Test search intent recognition
  - Message: "find tasks about groceries"
  - Assert: list_tasks called with search="groceries"
  - **Acceptance**: Test passes

- [X] T559 [P] [US7] Test filter intent recognition
  - Message: "show high priority tasks"
  - Assert: list_tasks called with priority="high"
  - **Acceptance**: Test passes

- [X] T560 [P] [US7] Test sort intent recognition
  - Message: "sort by due date"
  - Assert: list_tasks called with sort="due_date"
  - **Acceptance**: Test passes

- [X] T561 [P] [US7] Test recurrence intent recognition
  - Message: "make task 1 repeat weekly"
  - Assert: update_task called with recurrence object
  - **Acceptance**: Test passes

- [X] T562 [US7] Test backward compatibility with Phase III commands
  - Messages: "add task buy milk", "show tasks", "complete task 1"
  - Assert: All work as before
  - **Acceptance**: Test passes

### Recurring Task Tests

- [X] T563 [US4] Create `backend/tests/test_recurring.py`
  - Setup: Test fixtures for recurring tasks
  - **Acceptance**: Test file created

- [X] T564 [P] [US4] Test recurrence data storage
  - Create task with recurrence={type: "weekly", interval: 1}
  - Assert: Recurrence saved correctly in DB
  - **Acceptance**: Test passes

- [X] T565 [P] [US4] Test completion creates next occurrence
  - Complete recurring task
  - Assert: New task created with updated due_date
  - Assert: parent_task_id links to original
  - **Acceptance**: Test passes

- [X] T566 [P] [US4] Test due date calculation (daily)
  - Task due Jan 31, recurrence="daily"
  - Complete task
  - Assert: Next task due Feb 1
  - **Acceptance**: Test passes

- [X] T567 [P] [US4] Test due date calculation (weekly)
  - Task due Jan 31, recurrence="weekly"
  - Complete task
  - Assert: Next task due Feb 7
  - **Acceptance**: Test passes

- [X] T568 [P] [US4] Test due date calculation (monthly)
  - Task due Jan 31, recurrence="monthly"
  - Complete task
  - Assert: Next task due Feb 28 (month-end handling)
  - **Acceptance**: Test passes

- [X] T569 [US4] Test recurrence end_date respected
  - Task with recurrence ending Feb 1
  - Task due Jan 31
  - Complete task
  - Assert: No new occurrence created
  - **Acceptance**: Test passes

- [X] T570 [US4] [US6] Test recurring.triggered event published
  - Complete recurring task
  - Assert: "com.todo.recurring.triggered" event published
  - **Acceptance**: Test passes

**Checkpoint**: All tests written and passing. Run `pytest backend/tests/ -v`.

---

## Phase 6: Documentation & Validation

**Purpose**: Ensure complete documentation and backward compatibility
**Agent**: OrchestratorAgent
**User Story Reference**: All

### Documentation

- [X] T571 [ALL] Create `specs/005-phase5-parta-advanced-events/checklists/requirements.md`
  - Checklist of all requirements from spec
  - Track completion status
  - **Acceptance**: Checklist complete

- [X] T572 [US7] Document all new chatbot commands in README section
  - Priority commands
  - Tag commands
  - Search/filter commands
  - Sort commands
  - Recurrence commands
  - Due date commands
  - Reminder commands
  - **Acceptance**: Commands documented with examples

- [X] T573 [US6] Document event schema in README section
  - Reference to event-schema.md contract
  - Summary of event types
  - Dapr configuration notes (for Part B)
  - **Acceptance**: Events documented

- [X] T574 [ALL] Add "Phase V Part A Features" section to main README
  - Summary of new features
  - Links to spec and contracts
  - **Acceptance**: README updated

### Backward Compatibility Verification

- [X] T575 [ALL] Run Phase III regression tests
  - Execute existing chatbot tests
  - Verify basic CRUD still works
  - **Acceptance**: All Phase III tests pass

- [X] T576 [ALL] Manual test: Basic task commands
  - "add task buy milk" → works
  - "show tasks" → works
  - "complete task 1" → works
  - "delete task 1" → works
  - **Acceptance**: All basic commands work

- [X] T577 [ALL] Manual test: Conversation history
  - Send multiple messages
  - Refresh page
  - Verify history loads
  - **Acceptance**: History persists

- [X] T578 [ALL] Manual test: User isolation
  - Create two users
  - Verify tasks isolated
  - **Acceptance**: No cross-user access

### Final Validation

- [X] T579 [ALL] Manual E2E: Advanced task creation via chatbot
  - "add high priority task quarterly review due Friday tagged work reports remind me 1 hour before"
  - Verify all fields saved
  - **Acceptance**: Full command works

- [X] T580 [ALL] Manual E2E: Filtering and sorting via chatbot
  - "show pending high priority tasks tagged work sorted by due date"
  - Verify correct results
  - **Acceptance**: Combined filters work

- [X] T581 [ALL] Manual E2E: Recurring task via chatbot
  - "make task 1 recur weekly until end of March"
  - Complete task 1
  - Verify next occurrence created
  - **Acceptance**: Recurrence works

- [X] T582 [ALL] Verify event publishing logs
  - Perform CRUD operations
  - Check logs for event publish messages
  - **Acceptance**: Events logged correctly

- [X] T583 [ALL] Verify all success criteria from spec
  - SC-001 through SC-010
  - Mark each as PASS/FAIL
  - **Acceptance**: All criteria pass

**Checkpoint**: Phase V Part A complete. Ready for Part B deployment work.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Event Publishing) → Phase 2 (Tool Definitions) → Phase 3 (System Prompt)
                                                                    ↓
                                                         Phase 4 (Handler Extension)
                                                                    ↓
                                                         Phase 5 (Testing)
                                                                    ↓
                                                         Phase 6 (Documentation)
```

### Task Dependencies

| Task | Depends On |
|------|------------|
| T505-T509 | T501-T504 (EventPublisher must exist) |
| T527-T540 | T510-T518 (Tool definitions must exist) |
| T541-T570 | T527-T540 (Handlers must be extended) |
| T575-T583 | T541-T570 (Tests must pass first) |

### Parallel Opportunities

- **Phase 1**: T502, T503 can run in parallel
- **Phase 2**: T510-T517 can run in parallel (same file, different additions)
- **Phase 3**: T519-T526 can run in parallel
- **Phase 5**: All test groups (T542-T546, T549-T552, T556-T561, T564-T569) can run in parallel within groups

---

## Task Summary

| Phase | Focus | Task Count | Agent |
|-------|-------|------------|-------|
| 1 | Event Publishing | 9 | DaprAgent |
| 2 | MCP Tool Definitions | 9 | FeatureAgent |
| 3 | System Prompt | 8 | FeatureAgent |
| 4 | Handler Extension | 14 | FeatureAgent |
| 5 | Integration Testing | 30 | FeatureAgent |
| 6 | Documentation & Validation | 13 | OrchestratorAgent |
| **Total** | | **83** | |

---

## Implementation Strategy

### MVP First (Phases 1-4)

1. Complete Phase 1: Event Publishing Service
2. Complete Phase 2: MCP Tool Definitions
3. Complete Phase 3: System Prompt
4. Complete Phase 4: Handler Extension
5. **STOP and VALIDATE**: Manual test key chatbot commands

### Full Implementation

1. MVP + Phase 5: All automated tests pass
2. Phase 6: Documentation complete
3. Final validation against success criteria

### Strict Sequential Order (Critical Path)

```
T501 → T502-T504 → T505-T509 → T510-T518 → T519-T526 → T527-T540 → T541-T570 → T571-T583
```

---

## Success Criteria Mapping

| Success Criterion | Primary Tasks |
|-------------------|---------------|
| SC-001: Intermediate features via API | T541-T547 |
| SC-002: Advanced features via API | T563-T570 |
| SC-003: Chatbot recognizes intents | T555-T562 |
| SC-004: Events on all CRUD | T506-T509, T549-T552 |
| SC-005: CloudEvents 1.0 schema | T501, T553 |
| SC-006: Graceful degradation | T554 |
| SC-007: Phase III still works | T562, T575-T578 |
| SC-008: Combined filters | T547 |
| SC-009: Recurring creates next | T565 |
| SC-010: Commands documented | T572 |

---

## Notes

- All tasks traceable to spec user stories (US1-US7)
- Event publishing is fire-and-forget (non-blocking)
- Chatbot backward compatibility is critical - test early
- No database migrations needed (fields exist)
- No frontend changes needed (UI complete)
- Focus is on backend logic and chatbot intelligence
