# Feature Specification: Phase V Part A - Advanced Features & Event-Driven Logic

**Feature Branch**: `1-phase5-parta-advanced-events`
**Created**: 2026-01-31
**Status**: Draft → Ready for Implementation
**Constitution Reference**: `.specify/memory/constitution.md` v3.0.0

---

## 1. Executive Summary

This specification defines the implementation of intermediate and advanced todo features with event-driven architecture for the Hackathon II Evolution of Todo application. Phase V Part A focuses exclusively on **code and logic** — no deployment or infrastructure changes.

### Scope Overview

| Category | Features |
|----------|----------|
| **Intermediate** | Priorities, Tags/Categories, Search, Filter, Sort |
| **Advanced** | Recurring Tasks, Due Dates, Reminders |
| **Architecture** | Event publishing via Dapr Pub/Sub (code patterns only) |

### Current State Assessment

Based on codebase exploration, the following components are **already implemented**:

| Component | Status | Notes |
|-----------|--------|-------|
| Task Model | ✅ Complete | All fields (priority, tags, due_date, recurrence, reminder_offset_minutes) |
| API Routes | ✅ Complete | All endpoints with filter/sort/search query params |
| Pydantic Schemas | ✅ Complete | TaskCreate, TaskUpdate, TaskResponse |
| TaskService | ✅ Complete | Filter logic, recurring task creation |
| Frontend TaskForm | ✅ Complete | All inputs including advanced options |
| Chat Infrastructure | ✅ Complete | Conversation persistence, message history |

### Remaining Implementation

| Component | Status | Required Work |
|-----------|--------|---------------|
| MCP Tool Definitions | ⚠️ Partial | Add tags, recurrence, search, sort, order params |
| System Prompt | ⚠️ Partial | Add new intent recognition |
| TodoToolsHandler | ⚠️ Partial | Extend method signatures |
| Event Publishing | ❌ Missing | Create Dapr Pub/Sub service |
| Integration Tests | ⚠️ Partial | Add filter/event tests |

---

## 2. User Scenarios & Stories

### US-001: Advanced Task Creation (P1 - Critical)

**As a** user managing complex tasks,
**I want to** create tasks with priority, tags, due date, and recurrence settings,
**So that** I can organize my work effectively and ensure important tasks are highlighted.

**Acceptance Criteria**:
- [ ] AC-001.1: Can create task with priority (high/medium/low/none) via API
- [ ] AC-001.2: Can create task with multiple tags via API
- [ ] AC-001.3: Can create task with due date via API
- [ ] AC-001.4: Can create task with reminder offset via API
- [ ] AC-001.5: Can create task with recurrence (daily/weekly/monthly) via API
- [ ] AC-001.6: Event published to `task-events` topic on creation
- [ ] AC-001.7: Dashboard form supports all fields
- [ ] AC-001.8: Chatbot understands "add high priority task X due tomorrow"

**Test Cases**:
```gherkin
Scenario: Create task with all advanced fields
  Given I am authenticated user "user123"
  When I POST /api/tasks with:
    | title | "Weekly report" |
    | priority | "high" |
    | tags | ["work", "reports"] |
    | due_date | "2026-02-07T17:00:00Z" |
    | reminder_offset_minutes | 60 |
    | recurrence | {"type": "weekly", "interval": 1} |
  Then response status is 201
  And task has all fields saved correctly
  And event published to task-events with type "com.todo.task.created"

Scenario: Create task via chatbot with natural language
  Given I am authenticated user "user123"
  When I send message "add high priority task Review PR due Friday tagged work"
  Then agent creates task with:
    | priority | "high" |
    | title | "Review PR" |
    | tags | ["work"] |
  And response confirms task creation with details
```

---

### US-002: Task Filtering & Search (P1 - Critical)

**As a** user with many tasks,
**I want to** filter tasks by status, priority, and tags, and search by keywords,
**So that** I can quickly find specific tasks without scrolling.

**Acceptance Criteria**:
- [ ] AC-002.1: Filter by status (pending/completed/all)
- [ ] AC-002.2: Filter by priority (high/medium/low)
- [ ] AC-002.3: Filter by tag (single tag match)
- [ ] AC-002.4: Search by keyword in title/description
- [ ] AC-002.5: Combine multiple filters
- [ ] AC-002.6: Chatbot understands "show high priority tasks tagged work"

**Test Cases**:
```gherkin
Scenario: Filter tasks by priority
  Given user has tasks:
    | title | priority |
    | Task A | high |
    | Task B | low |
    | Task C | high |
  When I GET /api/tasks?priority=high
  Then response contains 2 tasks (A and C)

Scenario: Search tasks by keyword
  Given user has tasks:
    | title | description |
    | Buy groceries | milk, eggs |
    | Meeting notes | project review |
  When I GET /api/tasks?search=milk
  Then response contains 1 task (Buy groceries)

Scenario: Combined filter via chatbot
  Given user has tasks with various priorities and tags
  When I send message "show pending high priority tasks tagged work"
  Then agent lists only matching tasks
```

---

### US-003: Task Sorting (P2 - High)

**As a** user viewing task lists,
**I want to** sort tasks by different fields,
**So that** I can prioritize my view based on urgency or recency.

**Acceptance Criteria**:
- [ ] AC-003.1: Sort by created_at (default)
- [ ] AC-003.2: Sort by due_date
- [ ] AC-003.3: Sort by priority (custom order: high > medium > low > none)
- [ ] AC-003.4: Sort by title (alphabetical)
- [ ] AC-003.5: Support ascending and descending order
- [ ] AC-003.6: Chatbot understands "sort tasks by due date"

**Test Cases**:
```gherkin
Scenario: Sort tasks by due date ascending
  Given user has tasks:
    | title | due_date |
    | Task A | 2026-02-01 |
    | Task B | 2026-01-15 |
    | Task C | 2026-03-01 |
  When I GET /api/tasks?sort=due_date&order=asc
  Then tasks are ordered: B, A, C

Scenario: Sort by priority
  Given user has tasks with priorities high, low, medium
  When I GET /api/tasks?sort=priority&order=desc
  Then tasks ordered: high first, then medium, then low
```

---

### US-004: Recurring Tasks (P2 - High)

**As a** user with repetitive tasks,
**I want to** set tasks to recur daily, weekly, or monthly,
**So that** completing one creates the next occurrence automatically.

**Acceptance Criteria**:
- [ ] AC-004.1: Set recurrence on task creation
- [ ] AC-004.2: Set recurrence on existing task via update
- [ ] AC-004.3: On completion, create next occurrence with updated due date
- [ ] AC-004.4: New occurrence links to parent via parent_task_id
- [ ] AC-004.5: Recurrence respects end_date if specified
- [ ] AC-004.6: Event published for recurring trigger
- [ ] AC-004.7: Chatbot understands "make task 1 recur weekly until Dec 2026"

**Test Cases**:
```gherkin
Scenario: Complete recurring task creates next instance
  Given task exists:
    | id | 1 |
    | title | "Weekly standup" |
    | due_date | 2026-02-03 |
    | recurrence | {"type": "weekly", "interval": 1} |
  When I PATCH /api/tasks/1/complete
  Then task 1 is marked completed
  And new task created with:
    | title | "Weekly standup" |
    | due_date | 2026-02-10 |
    | parent_task_id | 1 |
  And event published with type "com.todo.recurring.triggered"

Scenario: Recurrence stops at end_date
  Given task has recurrence ending 2026-02-01
  And task due_date is 2026-01-31
  When I complete the task
  Then no new occurrence is created
```

---

### US-005: Due Dates & Reminders (P2 - High)

**As a** user with deadlines,
**I want to** set due dates and reminder offsets,
**So that** I'm notified before tasks are due.

**Acceptance Criteria**:
- [ ] AC-005.1: Set due_date on task creation/update
- [ ] AC-005.2: Set reminder_offset_minutes (e.g., 60 = 1 hour before)
- [ ] AC-005.3: Event published when reminder time reaches
- [ ] AC-005.4: Tasks sortable/filterable by due_date
- [ ] AC-005.5: Chatbot understands "due tomorrow" and "remind me 1 hour before"

**Test Cases**:
```gherkin
Scenario: Create task with due date via chatbot
  When I send "add task Submit report due Friday at 5pm"
  Then task created with due_date = next Friday 17:00 local time
  And response confirms due date

Scenario: Set reminder offset
  When I send "remind me 30 minutes before"
  Then task updated with reminder_offset_minutes = 30
```

---

### US-006: Event Publishing via Dapr (P1 - Critical)

**As the** system architecture,
**Events MUST** be published for all state-changing operations,
**So that** future services (notifications, analytics) can react to changes.

**Acceptance Criteria**:
- [ ] AC-006.1: Event published on task creation
- [ ] AC-006.2: Event published on task update
- [ ] AC-006.3: Event published on task completion
- [ ] AC-006.4: Event published on task deletion
- [ ] AC-006.5: Events follow CloudEvents 1.0 specification
- [ ] AC-006.6: Events sent via HTTP POST to Dapr sidecar
- [ ] AC-006.7: Graceful degradation if Dapr unavailable (log error, don't fail)
- [ ] AC-006.8: All events include task_id, user_id, timestamp, event_type

**Test Cases**:
```gherkin
Scenario: Task creation publishes event
  When I create a new task
  Then HTTP POST sent to http://localhost:3500/v1.0/publish/kafka-pubsub/task-events
  And request body is valid CloudEvents JSON
  And event type is "com.todo.task.created"

Scenario: Graceful degradation when Dapr unavailable
  Given Dapr sidecar is not running
  When I create a task
  Then task is saved successfully
  And error is logged "Failed to publish event: connection refused"
  And API response is still 201 Created
```

---

### US-007: Chatbot Natural Language Support (P1 - Critical)

**As a** user interacting via chat,
**I want to** use natural language for all new features,
**So that** I don't need to learn special syntax.

**Acceptance Criteria**:
- [ ] AC-007.1: Recognize priority keywords (high, urgent, low, important)
- [ ] AC-007.2: Recognize tag syntax ("tagged X", "with tag X")
- [ ] AC-007.3: Recognize search intent ("find", "search for")
- [ ] AC-007.4: Recognize filter intent ("show only", "filter by")
- [ ] AC-007.5: Recognize sort intent ("sort by", "order by")
- [ ] AC-007.6: Recognize recurrence ("repeat daily", "make recurring", "every week")
- [ ] AC-007.7: Recognize due date ("due tomorrow", "by Friday", "deadline")
- [ ] AC-007.8: Recognize reminder ("remind me", "notify me")
- [ ] AC-007.9: Backward compatible with Phase III commands

**Test Cases**:
```gherkin
Scenario Outline: Natural language intent recognition
  When I send message "<input>"
  Then agent interprets as "<intent>" with parameters "<params>"

  Examples:
    | input | intent | params |
    | add high priority task meeting | add_task | priority=high, title=meeting |
    | show tasks tagged work | list_tasks | tag=work |
    | find tasks about groceries | list_tasks | search=groceries |
    | sort by due date | list_tasks | sort=due_date |
    | complete task 5 | complete_task | task_id=5 |
    | make task 3 repeat weekly | update_task | task_id=3, recurrence.type=weekly |
```

---

## 3. Functional Requirements

### FR-001: MCP Tool Definition Updates

**Description**: Extend existing MCP tool definitions to support new parameters.

**Requirements**:

| Tool | New Parameters | Type | Required |
|------|----------------|------|----------|
| add_task | tags | array[string] | No |
| add_task | recurrence | object | No |
| add_task | reminder_offset_minutes | integer | No |
| update_task | tags | array[string] | No |
| update_task | recurrence | object | No |
| update_task | reminder_offset_minutes | integer | No |
| list_tasks | search | string | No |
| list_tasks | tag | string | No |
| list_tasks | sort | enum(created_at, due_date, priority, title) | No |
| list_tasks | order | enum(asc, desc) | No |

**Validation**:
- tags: max 10 items, each max 50 characters
- recurrence.type: enum(daily, weekly, monthly)
- recurrence.interval: integer >= 1
- recurrence.end_date: ISO datetime or null
- reminder_offset_minutes: integer >= 0
- sort: must be valid field name
- order: must be "asc" or "desc"

---

### FR-002: System Prompt Updates

**Description**: Update Cohere agent system prompt to recognize new intents.

**New Intent Patterns**:

```
PRIORITY RECOGNITION:
- "high priority", "urgent", "important" → priority="high"
- "medium priority", "normal" → priority="medium"
- "low priority", "minor" → priority="low"

TAG RECOGNITION:
- "tagged X", "tag X", "with tag X", "label X" → tags=["X"]
- "tags X and Y" → tags=["X", "Y"]

SEARCH RECOGNITION:
- "find X", "search for X", "look for X", "containing X" → search="X"

FILTER RECOGNITION:
- "show only X priority" → priority filter
- "show tasks tagged X" → tag filter
- "pending tasks", "completed tasks" → status filter

SORT RECOGNITION:
- "sort by X", "order by X", "organized by X" → sort="X"
- "ascending", "oldest first" → order="asc"
- "descending", "newest first" → order="desc"

RECURRENCE RECOGNITION:
- "repeat daily", "every day" → recurrence.type="daily"
- "repeat weekly", "every week" → recurrence.type="weekly"
- "repeat monthly", "every month" → recurrence.type="monthly"
- "until DATE" → recurrence.end_date=DATE

DUE DATE RECOGNITION:
- "due tomorrow", "by tomorrow" → due_date = tomorrow
- "due Friday", "by Friday" → due_date = next Friday
- "due DATE" → due_date = DATE

REMINDER RECOGNITION:
- "remind me X minutes before" → reminder_offset_minutes=X
- "remind me 1 hour before" → reminder_offset_minutes=60
```

---

### FR-003: TodoToolsHandler Method Updates

**Description**: Extend handler methods to accept and process new parameters.

**add_task Updates**:
```python
async def add_task(
    self,
    title: str,
    description: str = None,
    priority: str = "none",
    due_date: str = None,
    tags: List[str] = None,           # NEW
    recurrence: Dict = None,           # NEW
    reminder_offset_minutes: int = None, # NEW
    **kwargs
) -> Dict[str, Any]:
```

**list_tasks Updates**:
```python
async def list_tasks(
    self,
    status: str = "all",
    priority: str = None,
    tag: str = None,                   # NEW
    search: str = None,                # NEW
    sort: str = "created_at",          # NEW
    order: str = "desc",               # NEW
    **kwargs
) -> Dict[str, Any]:
```

**update_task Updates**:
```python
async def update_task(
    self,
    task_id: int,
    title: str = None,
    description: str = None,
    priority: str = None,
    status: str = None,
    due_date: str = None,
    tags: List[str] = None,            # NEW
    recurrence: Dict = None,           # NEW
    reminder_offset_minutes: int = None, # NEW
    **kwargs
) -> Dict[str, Any]:
```

---

### FR-004: Event Publishing Service

**Description**: Create service for publishing events to Dapr Pub/Sub.

**File**: `backend/src/services/event_publisher.py`

**Interface**:
```python
class EventPublisher:
    DAPR_HOST = "http://localhost:3500"
    PUBSUB_NAME = "kafka-pubsub"
    TOPIC_TASK_EVENTS = "task-events"
    TOPIC_REMINDERS = "reminders"

    async def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        user_id: int,
        task_data: dict
    ) -> bool:
        """Publish task event to Dapr. Returns True if successful."""

    async def publish_reminder_event(
        self,
        task_id: int,
        user_id: int,
        due_date: datetime,
        reminder_time: datetime
    ) -> bool:
        """Publish reminder event to Dapr. Returns True if successful."""
```

**Event Types**:
- `com.todo.task.created`
- `com.todo.task.updated`
- `com.todo.task.completed`
- `com.todo.task.deleted`
- `com.todo.recurring.triggered`
- `com.todo.reminder.due`

**CloudEvents Schema**:
```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/api/tasks",
  "id": "uuid-v4",
  "time": "2026-01-31T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Task title",
    "priority": "high",
    "tags": ["work"],
    "due_date": "2026-02-01T09:00:00Z",
    "completed": false,
    "created_at": "2026-01-31T12:00:00Z"
  }
}
```

---

### FR-005: TaskService Event Integration

**Description**: Call event publisher after each CRUD operation in TaskService.

**Integration Points**:

| Method | Event Type | When |
|--------|------------|------|
| create_task | com.todo.task.created | After successful DB insert |
| update_task | com.todo.task.updated | After successful DB update |
| toggle_complete | com.todo.task.completed | After marking complete |
| toggle_complete | com.todo.recurring.triggered | After creating next occurrence |
| delete_task | com.todo.task.deleted | After successful DB delete |

**Error Handling**:
- Event publishing failures MUST NOT cause API request failures
- Log errors with full context (event_type, task_id, error message)
- Return API response regardless of event publishing result

---

## 4. Non-Functional Requirements

### NFR-001: Performance

- Filter/sort queries must complete in < 100ms for up to 1000 tasks
- Event publishing must be non-blocking (fire-and-forget with logging)
- Chatbot response time unchanged from Phase III baseline

### NFR-002: Reliability

- API must return success even if Dapr unavailable
- All events must include correlation ID for tracing
- Failed events must be logged with sufficient detail for debugging

### NFR-003: Backward Compatibility

- All Phase III chatbot commands must work unchanged
- Existing API endpoints must accept requests without new fields
- New fields must have sensible defaults (priority="none", tags=[])

### NFR-004: Security

- User isolation enforced on all queries (user can only see own tasks)
- Tags and search terms must be sanitized to prevent injection
- No sensitive data in event payloads beyond what's in the task

---

## 5. Key Entities

### Task (Extended)

| Field | Type | Description | New? |
|-------|------|-------------|------|
| id | int | Primary key | No |
| user_id | int | Foreign key to users | No |
| title | string | Task title (max 200) | No |
| description | string | Task description (max 2000) | No |
| completed | bool | Completion status | No |
| priority | string | high/medium/low/none | Already exists |
| tags | array[string] | Category labels | Already exists |
| due_date | datetime | Deadline | Already exists |
| reminder_offset_minutes | int | Minutes before due_date | Already exists |
| recurrence | object | {type, interval, end_date} | Already exists |
| parent_task_id | int | Link to recurring parent | Already exists |
| created_at | datetime | Creation timestamp | No |
| updated_at | datetime | Last update timestamp | No |

### CloudEvent

| Field | Type | Description |
|-------|------|-------------|
| specversion | string | "1.0" |
| type | string | Event type identifier |
| source | string | "/api/tasks" |
| id | string | UUID v4 |
| time | string | ISO 8601 timestamp |
| datacontenttype | string | "application/json" |
| data | object | Event payload |

---

## 6. Success Criteria

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| SC-001 | All intermediate features (priority, tags, filter, sort, search) functional via API | API integration tests |
| SC-002 | All advanced features (recurring, due dates, reminders) functional via API | API integration tests |
| SC-003 | Chatbot recognizes all new intents and executes correctly | Chat integration tests |
| SC-004 | Events published on all CRUD operations | Log inspection / mock Dapr tests |
| SC-005 | Events follow CloudEvents 1.0 schema | Schema validation tests |
| SC-006 | Graceful degradation when Dapr unavailable | Fault injection test |
| SC-007 | Phase III chatbot commands still work | Regression tests |
| SC-008 | Combined filters work correctly | Parameterized API tests |
| SC-009 | Recurring task completion creates next occurrence | Recurring task tests |
| SC-010 | All new chatbot commands documented | Documentation review |

---

## 7. Constraints

| Constraint | Rationale |
|------------|-----------|
| No deployment changes | Part A is code only per constitution |
| No direct Kafka client | Must use Dapr Pub/Sub exclusively |
| No new API endpoints | Extend existing endpoints |
| No breaking changes | Backward compatibility required |
| No UI redesign | Additive changes only |
| Must use existing tools | Extend MCP tools, don't create new |

---

## 8. Out of Scope

- Dapr sidecar deployment or configuration
- Kafka cluster setup
- Cloud deployment (Part C)
- Actual reminder notifications (consumers not built yet)
- Real-time WebSocket updates
- Task sharing between users
- File attachments
- Subtasks hierarchy

---

## 9. Assumptions

| Assumption | Impact if False |
|------------|-----------------|
| Task model already has all required fields | Would need migration |
| Frontend TaskForm already supports all inputs | Would need UI updates |
| Cohere API supports tool updates | Would need prompt engineering |
| httpx is available for async HTTP | Would need to add dependency |
| Phase III tests still pass | Would need fixes first |

---

## 10. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cohere doesn't recognize new intents well | Medium | High | Add more examples to prompt, test extensively |
| Event publishing adds latency | Low | Medium | Make async/fire-and-forget |
| Filter combinations have edge cases | Medium | Medium | Add comprehensive parameterized tests |
| Recurring date calculation bugs | Medium | High | Use dateutil, add edge case tests |
| Breaking existing chatbot | Low | High | Run regression tests before merge |

---

## 11. Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| Phase III implementation | Internal | ✅ Complete |
| Phase IV deployment | Internal | ✅ Complete |
| httpx library | External | ✅ Available |
| Cohere API | External | ✅ Available |
| PostgreSQL (Neon) | External | ✅ Available |

---

## 12. Appendices

### A. Example Chatbot Interactions

```
User: add high priority task "Review quarterly report" due Friday tagged work, reports
Agent: Created task #47 "Review quarterly report" with priority HIGH, due 2026-02-07, tagged [work, reports]

User: show pending tasks tagged work
Agent: Found 3 pending tasks tagged "work":
1. #47 Review quarterly report (HIGH) - due Feb 7
2. #32 Update documentation (MEDIUM) - no due date
3. #28 Team meeting prep (LOW) - due Feb 3

User: sort by due date ascending
Agent: Tasks sorted by due date (earliest first):
1. #28 Team meeting prep - due Feb 3
2. #47 Review quarterly report - due Feb 7
3. #32 Update documentation - no due date

User: make task 47 recur weekly until end of March
Agent: Updated task #47 to repeat weekly until March 31, 2026

User: complete task 28
Agent: Completed task #28 "Team meeting prep". Next occurrence created as task #48 due Feb 10.
```

### B. Event Flow Diagram

```
[User Action] → [API Endpoint] → [TaskService] → [Database]
                                       ↓
                              [EventPublisher]
                                       ↓
                    [HTTP POST to Dapr Sidecar]
                                       ↓
                         [Kafka: task-events topic]
                                       ↓
                       [Future: Consumer Services]
```

### C. Files to Modify

| File | Changes |
|------|---------|
| `backend/src/agents/config.py` | Update TOOL_DEFINITIONS, SYSTEM_PROMPT |
| `backend/src/mcp/tools.py` | Extend method signatures |
| `backend/src/services/event_publisher.py` | NEW - Create event service |
| `backend/src/services/task.py` | Add event publishing calls |
| `backend/tests/test_filters.py` | NEW - Filter tests |
| `backend/tests/test_events.py` | NEW - Event publishing tests |
| `backend/tests/test_chatbot_intents.py` | NEW - Intent recognition tests |

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-31
**Author**: Claude Code Agent
**Reviewers**: Pending
