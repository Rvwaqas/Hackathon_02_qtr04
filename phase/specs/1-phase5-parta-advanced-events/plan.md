# Implementation Plan: Phase V Part A - Advanced Features & Event-Driven Logic

**Feature Branch**: `1-phase5-parta-advanced-events`
**Created**: 2026-01-31
**Status**: Draft
**Spec Reference**: [spec.md](./spec.md)

## Architecture Sketch (Part A – Code & Logic Level)

Extension of existing Phase III/IV application with new fields, extended APIs/tools/agent, and Dapr Pub/Sub event publishing.

```
Existing App (FastAPI + Next.js + Cohere Agent + MCP)
├── Task Model Extension (priority, tags, due_date, recurring...)
├── API / MCP Tools Extension (new params in add/update/list)
├── UI Extension (dashboard + chatbot)
└── Cohere Agent Extension (new intents & tool calls)
│
▼
Dapr Pub/Sub Calls (HTTP to localhost:3500)
│
▼
Kafka Topics (prepared for Part B): task-events, reminders
```

- All publishing via Dapr sidecar (code only in Part A)
- No runtime Dapr/Kafka here — only httpx.post patterns
- Future consumers (recurring, notification) will subscribe in Part B

## Component Breakdown & Section Structure

### Backend (/backend)

| File | Changes |
|------|---------|
| `models.py` | Extend Task with new fields (priority, tags, due_date, remind_before, recurring_interval, recurring_end) |
| `schemas.py` | Extend Pydantic models (CreateTask, UpdateTask, TaskOut) with new optional fields |
| `routes/tasks.py` | Accept new fields in POST/PUT, add query params (priority, tags, sort_by, search, due_before, due_after) |
| `mcp/tools.py` | Extend add_task, update_task, list_tasks params and descriptions |
| `agents/todo_agent.py` | Update Cohere instructions + tool descriptions for new intents |
| `services/event_publisher.py` | NEW: httpx.post to Dapr Pub/Sub with CloudEvents format |

### Frontend (/frontend)

| File | Changes |
|------|---------|
| `components/TaskForm.tsx` | Priority dropdown, tags input, date picker, recurring options |
| `components/TaskList.tsx` | Filter/sort UI, priority badges, tag pills, overdue indicators |
| `lib/api.ts` | Extend API calls with new query params and body fields |
| ChatKit | No change — Cohere handles new intents via existing chat endpoint |

### Database

| Change | Description |
|--------|-------------|
| Migration | Add columns to tasks table: priority (VARCHAR), tags (TEXT[]), due_date (TIMESTAMP), remind_before (INT), recurring_interval (VARCHAR), recurring_end (TIMESTAMP) |

### Event Publishing

| Action | Topic | Event Type |
|--------|-------|------------|
| Task created | task-events | com.taskmanager.task.created |
| Task updated | task-events | com.taskmanager.task.updated |
| Task completed | task-events | com.taskmanager.task.completed |
| Task deleted | task-events | com.taskmanager.task.deleted |
| Due date set | reminders | com.taskmanager.reminder.scheduled |

## Key Decisions & Tradeoffs

| Decision | Chosen Option | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| Priority Field | str enum (high/medium/low) | int (1-3) | Readable in DB/UI/chatbot, natural language friendly |
| Tags Storage | PostgreSQL ARRAY(String) | JSONB, separate table | Native Postgres support, easy query with ANY() |
| Recurring Logic | Event publish on complete | Immediate DB insert | Decoupled — Part B will consume and create next instance |
| Reminder Trigger | Publish to reminders topic | Dapr Jobs in code | Part B will use Jobs API for exact timing delivery |
| Dapr Pub/Sub | httpx.post to localhost:3500 | Direct Kafka client | Part A code only — Dapr runtime deployed in Part B |
| Event Schema | CloudEvents with full snapshot | Delta changes only | Simpler for consumers, enables idempotency |
| Date Parsing | Python dateparser library | Manual regex | Handles "tomorrow", "next Friday at 3pm" naturally |

## Implementation Sequence (High-Level Phases)

| Phase | Agent Responsible | Description | Dependencies |
|-------|-------------------|-------------|--------------|
| 1 | FeatureAgent | Database schema extension - Add new fields to Task model + migration | None |
| 2 | FeatureAgent | API & Pydantic extension - Update endpoints, schemas, query params | Phase 1 |
| 3 | FeatureAgent | MCP tools extension - Add params to add_task, update_task, list_tasks | Phase 2 |
| 4 | FeatureAgent | Cohere agent update - Extend instructions + tool descriptions | Phase 3 |
| 5 | DaprAgent + KafkaAgent | Event publishing logic - Create event schemas + Dapr publish service | Phase 2 |
| 6 | FeatureAgent | Dashboard UI extensions - Priority/tags/date/recurring inputs + filter/sort | Phase 2 |
| 7 | FeatureAgent | Chatbot natural language support - Test new commands end-to-end | Phase 4 |
| 8 | OrchestratorAgent | Local testing & validation - Verify backward compatibility + event logs | All |
| 9 | OrchestratorAgent | Documentation update - README section for new features & events | Phase 8 |

## Testing/Validation Strategy (Part A only)

| Check | Validation Method | Agent | Pass Criteria |
|-------|-------------------|-------|---------------|
| New fields save/retrieve | DB query + API response | FeatureAgent | All 6 new fields persist and return correctly |
| Filter/sort/search work | API calls + UI test | FeatureAgent | Filtered results match criteria, sort order correct |
| Recurring/due date event publish | Logs show httpx.post | KafkaAgent/DaprAgent | Event JSON visible in logs with correct format |
| Chatbot commands | "add high priority task due tomorrow recur weekly" | FeatureAgent | Task created with all attributes |
| Backward compatibility | Old basic commands still work | OrchestratorAgent | "add buy milk", "list tasks" unchanged |
| Event schema valid | JSON matches CloudEvents structure | KafkaAgent | specversion, type, source, id, time, data present |

## Technical Details & Patterns

### Priority Enum
```python
from typing import Literal

PriorityType = Literal["high", "medium", "low"]
```

### Tags Storage (PostgreSQL ARRAY)
```python
from sqlalchemy import ARRAY, String
from sqlmodel import Field

tags: list[str] | None = Field(default=None, sa_column=Column(ARRAY(String)))
```

### CloudEvents Schema
```json
{
  "specversion": "1.0",
  "type": "com.taskmanager.task.created",
  "source": "/tasks/backend-service",
  "id": "uuid-v4",
  "time": "2026-01-31T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": "user-abc",
    "title": "Buy milk",
    "priority": "high",
    "tags": ["shopping"],
    "due_date": "2026-02-01T15:00:00Z",
    "recurring_interval": "weekly"
  }
}
```

### Dapr Publish Pattern
```python
import httpx
import uuid
from datetime import datetime

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

async def publish_event(topic: str, event_type: str, data: dict) -> bool:
    """Publish event via Dapr sidecar. Graceful degradation if unavailable."""
    event = {
        "specversion": "1.0",
        "type": f"com.taskmanager.{event_type}",
        "source": "/tasks/backend-service",
        "id": str(uuid.uuid4()),
        "time": datetime.utcnow().isoformat() + "Z",
        "datacontenttype": "application/json",
        "data": data
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}",
                json=event,
                timeout=5.0
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Event publish failed (Dapr not running): {e}")
        return False
```

### Filter Query Pattern
```python
# GET /api/tasks?priority=high&tags=work&sort_by=due_date&search=milk

@router.get("/tasks")
async def list_tasks(
    priority: str | None = None,
    tags: str | None = None,  # comma-separated
    sort_by: str | None = None,  # due_date, priority, created_at
    search: str | None = None,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    # ... existing params
):
    query = select(Task).where(Task.user_id == user_id)

    if priority:
        query = query.where(Task.priority == priority)
    if tags:
        tag_list = tags.split(",")
        query = query.where(Task.tags.overlap(tag_list))
    if search:
        query = query.where(
            or_(
                Task.title.ilike(f"%{search}%"),
                Task.description.ilike(f"%{search}%")
            )
        )
    if due_before:
        query = query.where(Task.due_date <= due_before)
    if due_after:
        query = query.where(Task.due_date >= due_after)
    if sort_by == "due_date":
        query = query.order_by(Task.due_date.asc().nulls_last())
    elif sort_by == "priority":
        # Custom order: high > medium > low > null
        query = query.order_by(
            case(
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                (Task.priority == "low", 3),
                else_=4
            )
        )

    return await session.exec(query).all()
```

### Cohere Agent Instructions Update
```python
SYSTEM_INSTRUCTIONS = """
You are a task management assistant. You can:

1. Add tasks with optional priority, tags, due dates, and recurring settings
   - "add high priority task Meeting"
   - "add task Buy groceries tagged shopping due tomorrow"
   - "add urgent task Report due Friday at 5pm recur weekly until December 2026"

2. List and filter tasks
   - "show all tasks"
   - "show high priority tasks"
   - "show tasks tagged work"
   - "show overdue tasks"
   - "sort tasks by due date"

3. Search tasks
   - "find tasks with grocery"
   - "search for meeting"

4. Update tasks
   - "mark task 5 complete"
   - "set task 3 priority to high"
   - "add tag urgent to task 2"
   - "make task 1 recur monthly"

5. Delete tasks
   - "delete task 4"

Priority levels: high, medium, low
Recurring intervals: daily, weekly, monthly
"""
```

## Constitution Check

| Principle | Compliance |
|-----------|------------|
| I. Strictly Spec-Driven | All changes traced to spec.md requirements FR-001 to FR-037 |
| II. Event-Driven Priority | Every CRUD publishes events via Dapr Pub/Sub |
| III. Backward Compatibility | All new fields optional, existing behavior unchanged |
| IV. Dapr-Exclusive | No direct Kafka imports, only httpx to localhost:3500 |
| V. Stateless & Scalable | No in-memory state, all persisted to Neon PostgreSQL |
| VI. Tech Stack | FastAPI, Next.js, Cohere, Neon, Dapr Pub/Sub |

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| PostgreSQL ARRAY not supported on Neon | High | Test early; fallback to JSONB if needed |
| Date parsing ambiguity | Medium | Use dateparser library with explicit timezone |
| Dapr logs noisy when sidecar absent | Low | Wrap in try/except, log at DEBUG level |
| Tags filter performance with many tags | Low | Add GIN index on tags column |

## Dependencies & Assumptions

**Dependencies:**
- Phase III codebase functional (FastAPI, Next.js, Cohere, MCP)
- Phase IV Docker/Helm not modified in Part A
- Neon PostgreSQL supports ARRAY type (verify)
- httpx library available in backend

**Assumptions:**
- All dates stored in UTC
- Tags are case-insensitive for filtering
- remind_before=0 means no reminder
- recurring_end=null means indefinite recurring
- Event consumers not present in Part A (logs only)

## Success Metrics (Part A)

| Metric | Target | Validation |
|--------|--------|------------|
| New fields work | 100% | All 6 fields save/retrieve correctly |
| Filters work | 100% | Priority, tags, due date filters return correct results |
| Search works | 100% | Keyword search matches title/description |
| Events published | 100% | All CRUD ops show event in logs |
| Chatbot commands | 90%+ | Standard phrases interpreted correctly |
| Backward compat | 100% | Phase III commands unchanged |
| No runtime errors | 0 | No crashes when Dapr unavailable |

## Next Steps

1. Run `/sp.tasks` to generate detailed task list
2. Execute tasks in order (Phase 1-9)
3. Validate each phase before proceeding
4. Run `/sp.analyze` after tasks completion
5. Prepare for Part B (Dapr deployment)
