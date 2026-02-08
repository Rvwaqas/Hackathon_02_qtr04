# Implementation Tasks: Phase V Part A - Advanced Features & Event-Driven Logic

**Feature Branch**: `1-phase5-parta-advanced-events`
**Created**: 2026-01-31
**Status**: Ready for Implementation
**Spec Reference**: [spec.md](./spec.md)
**Plan Reference**: [plan.md](./plan.md)

## Task Breakdown

All tasks are atomic, sequential, and assigned to specific agents.
Implementation must follow this exact order. No step without agent involvement.

---

### T-501: Extend Task database model with new fields

**Agent**: FeatureAgent
**Priority**: P1
**Estimated Complexity**: Medium
**Dependencies**: None

**File**: `backend/models.py`

**Changes**:
Add to Task class (SQLModel):
```python
from sqlalchemy import Column, String, DateTime, Integer, ARRAY
from sqlmodel import Field
from datetime import datetime

class Task(SQLModel, table=True):
    # Existing fields...

    # NEW: Phase V Part A fields
    priority: str | None = Field(default=None, sa_column=Column(String, nullable=True))
    tags: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    due_date: datetime | None = Field(default=None, sa_column=Column(DateTime, nullable=True))
    remind_before: int | None = Field(default=None, sa_column=Column(Integer, nullable=True))  # minutes
    recurring_interval: str | None = Field(default=None, sa_column=Column(String, nullable=True))
    recurring_end: datetime | None = Field(default=None, sa_column=Column(DateTime, nullable=True))
```

**Migration**: Generate Alembic migration or manual SQL:
```sql
ALTER TABLE tasks
ADD COLUMN priority VARCHAR,
ADD COLUMN tags TEXT[],
ADD COLUMN due_date TIMESTAMP,
ADD COLUMN remind_before INTEGER,
ADD COLUMN recurring_interval VARCHAR,
ADD COLUMN recurring_end TIMESTAMP;
```

**Acceptance Criteria**:
- [ ] New columns added to tasks table
- [ ] Existing tasks still load correctly (null values for new fields)
- [ ] Verify with DB tool: `SELECT * FROM tasks LIMIT 1;`

**Test Cases**:
1. Create task with only title → new fields are null
2. Create task with priority="high" → saves correctly
3. Create task with tags=["work", "urgent"] → array saves correctly

---

### T-502: Extend Pydantic schemas for API

**Agent**: FeatureAgent
**Priority**: P1
**Estimated Complexity**: Medium
**Dependencies**: T-501

**File**: `backend/schemas.py`

**Changes**:
```python
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal

PriorityType = Literal["high", "medium", "low"]
RecurringType = Literal["daily", "weekly", "monthly"]

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    # NEW fields
    priority: PriorityType | None = None
    tags: list[str] = Field(default_factory=list)
    due_date: datetime | None = None
    remind_before: int | None = None  # minutes before due_date
    recurring_interval: RecurringType | None = None
    recurring_end: datetime | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    # NEW fields
    priority: PriorityType | None = None
    tags: list[str] | None = None
    due_date: datetime | None = None
    remind_before: int | None = None
    recurring_interval: RecurringType | None = None
    recurring_end: datetime | None = None

class TaskOut(BaseModel):
    id: int
    user_id: str
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
    # NEW fields
    priority: str | None
    tags: list[str]
    due_date: datetime | None
    remind_before: int | None
    recurring_interval: str | None
    recurring_end: datetime | None

class TaskListParams(BaseModel):
    priority: PriorityType | None = None
    tags: str | None = None  # comma-separated
    search: str | None = None
    sort_by: Literal["created_at", "due_date", "priority", "title"] | None = None
    sort_order: Literal["asc", "desc"] = "asc"
    due_before: datetime | None = None
    due_after: datetime | None = None
```

**Acceptance Criteria**:
- [ ] Schemas validate new fields with correct types
- [ ] API docs (Swagger) show updated schemas
- [ ] Invalid priority value rejected (e.g., "urgent" → validation error)

**Test Cases**:
1. TaskCreate with priority="invalid" → ValidationError
2. TaskCreate with tags=["work"] → passes
3. TaskUpdate with partial fields → only provided fields present

---

### T-503: Update REST API endpoints

**Agent**: FeatureAgent
**Priority**: P1
**Estimated Complexity**: High
**Dependencies**: T-501, T-502

**File**: `backend/routes/tasks.py`

**Changes**:

```python
from sqlalchemy import case, or_
from sqlmodel import select

@router.post("/tasks", response_model=TaskOut)
async def create_task(
    task: TaskCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_task = Task(
        user_id=current_user.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        tags=task.tags or [],
        due_date=task.due_date,
        remind_before=task.remind_before,
        recurring_interval=task.recurring_interval,
        recurring_end=task.recurring_end
    )
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    # Event publishing added in T-508
    return db_task

@router.get("/tasks", response_model=list[TaskOut])
async def list_tasks(
    priority: str | None = None,
    tags: str | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    query = select(Task).where(Task.user_id == current_user.id)

    # Filters
    if priority:
        query = query.where(Task.priority == priority)
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
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

    # Sorting
    if sort_by == "due_date":
        order = Task.due_date.asc() if sort_order == "asc" else Task.due_date.desc()
        query = query.order_by(order.nulls_last())
    elif sort_by == "priority":
        priority_order = case(
            (Task.priority == "high", 1),
            (Task.priority == "medium", 2),
            (Task.priority == "low", 3),
            else_=4
        )
        query = query.order_by(priority_order if sort_order == "asc" else priority_order.desc())
    elif sort_by == "title":
        order = Task.title.asc() if sort_order == "asc" else Task.title.desc()
        query = query.order_by(order)
    else:
        order = Task.created_at.asc() if sort_order == "asc" else Task.created_at.desc()
        query = query.order_by(order)

    result = await session.exec(query)
    return result.all()

@router.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    task = await session.get(Task, task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(404, "Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)
    # Event publishing added in T-508
    return task
```

**Acceptance Criteria**:
- [ ] POST /tasks accepts all new fields
- [ ] GET /tasks with ?priority=high returns only high priority tasks
- [ ] GET /tasks with ?tags=work,urgent returns tasks with either tag
- [ ] GET /tasks with ?search=milk returns matching tasks
- [ ] GET /tasks with ?sort_by=due_date&sort_order=asc returns sorted
- [ ] PUT /tasks/{id} accepts partial updates for new fields
- [ ] Existing behavior unchanged when no new params provided

**Test Cases**:
1. POST /tasks with priority, tags, due_date → task created with all fields
2. GET /tasks?priority=high → only high priority returned
3. GET /tasks?tags=work → tasks containing "work" tag returned
4. GET /tasks (no params) → all tasks returned (backward compat)

---

### T-504: Extend MCP tools with new parameters

**Agent**: FeatureAgent
**Priority**: P1
**Estimated Complexity**: Medium
**Dependencies**: T-503

**File**: `backend/mcp/tools.py`

**Changes**:
```python
@mcp_tool(
    name="add_task",
    description="""Add a new task with optional priority, tags, due date, reminder, and recurring settings.

    Parameters:
    - title (required): Task title
    - description (optional): Task description
    - priority (optional): "high", "medium", or "low"
    - tags (optional): List of tags like ["work", "urgent"]
    - due_date (optional): ISO datetime string like "2026-02-01T15:00:00Z"
    - remind_before (optional): Minutes before due_date to remind (e.g., 60 for 1 hour)
    - recurring_interval (optional): "daily", "weekly", or "monthly"
    - recurring_end (optional): ISO datetime string for when recurring stops

    Examples:
    - add_task(title="Buy milk")
    - add_task(title="Meeting", priority="high", tags=["work"])
    - add_task(title="Report", due_date="2026-02-01T17:00:00Z", remind_before=60)
    - add_task(title="Standup", recurring_interval="daily")
    """
)
async def add_task(
    title: str,
    description: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
    remind_before: int | None = None,
    recurring_interval: str | None = None,
    recurring_end: str | None = None
) -> dict:
    # Parse dates
    parsed_due = datetime.fromisoformat(due_date.replace("Z", "+00:00")) if due_date else None
    parsed_end = datetime.fromisoformat(recurring_end.replace("Z", "+00:00")) if recurring_end else None

    # Create task via API or direct DB
    task = await create_task_in_db(
        title=title,
        description=description,
        priority=priority,
        tags=tags or [],
        due_date=parsed_due,
        remind_before=remind_before,
        recurring_interval=recurring_interval,
        recurring_end=parsed_end
    )
    return {"success": True, "task": task.model_dump()}

@mcp_tool(
    name="list_tasks",
    description="""List tasks with optional filtering and sorting.

    Parameters:
    - priority (optional): Filter by "high", "medium", or "low"
    - tags (optional): Filter by tags (comma-separated string)
    - search (optional): Search in title and description
    - sort_by (optional): "created_at", "due_date", "priority", or "title"
    - completed (optional): true/false to filter by completion status

    Examples:
    - list_tasks()  # all tasks
    - list_tasks(priority="high")
    - list_tasks(tags="work,urgent")
    - list_tasks(search="grocery", sort_by="due_date")
    """
)
async def list_tasks(
    priority: str | None = None,
    tags: str | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    completed: bool | None = None
) -> dict:
    tasks = await get_tasks_filtered(
        priority=priority,
        tags=tags,
        search=search,
        sort_by=sort_by,
        completed=completed
    )
    return {"success": True, "tasks": [t.model_dump() for t in tasks]}

@mcp_tool(
    name="update_task",
    description="""Update an existing task. All fields are optional - only provided fields are updated.

    Parameters:
    - task_id (required): ID of the task to update
    - title, description, completed, priority, tags, due_date, remind_before, recurring_interval, recurring_end (all optional)

    Examples:
    - update_task(task_id=1, completed=true)
    - update_task(task_id=2, priority="high", tags=["urgent"])
    - update_task(task_id=3, recurring_interval="weekly", recurring_end="2026-12-31T00:00:00Z")
    """
)
async def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    completed: bool | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
    remind_before: int | None = None,
    recurring_interval: str | None = None,
    recurring_end: str | None = None
) -> dict:
    update_data = {k: v for k, v in locals().items() if v is not None and k != "task_id"}
    task = await update_task_in_db(task_id, update_data)
    return {"success": True, "task": task.model_dump()}
```

**Acceptance Criteria**:
- [ ] add_task accepts all new parameters
- [ ] list_tasks accepts filter/sort parameters
- [ ] update_task accepts partial updates for new fields
- [ ] Tool descriptions updated with examples
- [ ] Existing calls without new params still work

**Test Cases**:
1. add_task(title="Test", priority="high") → task with priority created
2. list_tasks(priority="high") → filtered results
3. update_task(task_id=1, tags=["new"]) → tags updated

---

### T-505: Update Cohere agent instructions & tool usage

**Agent**: FeatureAgent
**Priority**: P1
**Estimated Complexity**: Medium
**Dependencies**: T-504

**File**: `backend/agents/todo_agent.py`

**Changes**:
```python
SYSTEM_INSTRUCTIONS = """
You are a helpful task management assistant. You help users manage their todo list using natural language.

## Capabilities

### 1. Add Tasks
Create new tasks with optional priority, tags, due dates, reminders, and recurring settings.

Examples:
- "Add task buy milk" → add_task(title="Buy milk")
- "Add high priority task meeting" → add_task(title="Meeting", priority="high")
- "Add task report tagged work due tomorrow" → add_task(title="Report", tags=["work"], due_date="<tomorrow's date>")
- "Add urgent task call mom due Friday at 3pm remind me 1 hour before" → add_task(title="Call mom", priority="high", due_date="<Friday 3pm>", remind_before=60)
- "Add task standup recur daily" → add_task(title="Standup", recurring_interval="daily")
- "Add task weekly review recur weekly until December 2026" → add_task(title="Weekly review", recurring_interval="weekly", recurring_end="2026-12-31T00:00:00Z")

Priority keywords: high, urgent, important → priority="high"; medium, normal → priority="medium"; low → priority="low"
Tag keywords: "tagged X", "with tag X", "tag X" → tags=["X"]

### 2. List Tasks
View tasks with optional filtering and sorting.

Examples:
- "Show all tasks" → list_tasks()
- "Show my tasks" → list_tasks()
- "Show high priority tasks" → list_tasks(priority="high")
- "Show tasks tagged work" → list_tasks(tags="work")
- "Show urgent work tasks" → list_tasks(priority="high", tags="work")
- "Sort tasks by due date" → list_tasks(sort_by="due_date")
- "Show overdue tasks" → list_tasks with due_date filter
- "Show pending tasks" → list_tasks(completed=false)
- "Show completed tasks" → list_tasks(completed=true)

### 3. Search Tasks
Find tasks by keyword in title or description.

Examples:
- "Find tasks with grocery" → list_tasks(search="grocery")
- "Search for meeting" → list_tasks(search="meeting")

### 4. Update Tasks
Modify existing tasks including marking complete and changing attributes.

Examples:
- "Mark task 5 complete" → update_task(task_id=5, completed=true)
- "Complete task 3" → update_task(task_id=3, completed=true)
- "Set task 2 priority to high" → update_task(task_id=2, priority="high")
- "Add tag urgent to task 1" → update_task(task_id=1, tags=["urgent"])
- "Make task 4 recur weekly" → update_task(task_id=4, recurring_interval="weekly")
- "Set due date for task 6 to next Monday" → update_task(task_id=6, due_date="<next Monday>")

### 5. Delete Tasks
Remove tasks from the list.

Examples:
- "Delete task 4" → delete_task(task_id=4)
- "Remove task 7" → delete_task(task_id=7)

## Important Notes
- When user says "tomorrow", calculate the actual date
- When user says "next Friday at 3pm", calculate the ISO datetime
- Priority "urgent" or "important" maps to "high"
- Always confirm actions with the user
- If task ID is ambiguous, list tasks first to clarify
"""

# Update tool registration with new descriptions from T-504
tools = [
    add_task,      # Updated with new params
    list_tasks,    # Updated with filter/sort
    update_task,   # Updated with new fields
    delete_task,   # No change
    complete_task, # No change (calls update_task internally)
]
```

**Acceptance Criteria**:
- [ ] Agent understands priority keywords (high, urgent, important)
- [ ] Agent understands tag syntax ("tagged work", "with tag personal")
- [ ] Agent understands due date phrases ("due tomorrow", "due next Friday at 3pm")
- [ ] Agent understands recurring phrases ("recur weekly", "repeat daily until Dec 2026")
- [ ] Agent understands filter commands ("show high priority", "show tagged work")
- [ ] Agent understands sort commands ("sort by due date")
- [ ] Basic commands still work ("add buy milk", "show tasks", "complete 1")

**Test Cases**:
1. "Add high priority task meeting" → add_task(title="Meeting", priority="high")
2. "Show tasks tagged work" → list_tasks(tags="work")
3. "Add task report due tomorrow" → add_task with correct due_date
4. "Make task 1 recur weekly" → update_task(task_id=1, recurring_interval="weekly")
5. "Add buy milk" → still works (backward compat)

---

### T-506: Define event schemas for Kafka topics

**Agent**: KafkaAgent
**Priority**: P1
**Estimated Complexity**: Low
**Dependencies**: None (can run in parallel with T-501-T-505)

**File**: `backend/events/schemas.py`

**Changes**:
```python
from datetime import datetime
from typing import Literal
from pydantic import BaseModel
import uuid

EventType = Literal[
    "task.created",
    "task.updated",
    "task.completed",
    "task.deleted",
    "reminder.scheduled"
]

class CloudEvent(BaseModel):
    """CloudEvents 1.0 specification base"""
    specversion: str = "1.0"
    type: str
    source: str = "/tasks/backend-service"
    id: str
    time: str
    datacontenttype: str = "application/json"
    data: dict

    @classmethod
    def create(cls, event_type: str, data: dict) -> "CloudEvent":
        return cls(
            type=f"com.taskmanager.{event_type}",
            id=str(uuid.uuid4()),
            time=datetime.utcnow().isoformat() + "Z",
            data=data
        )

class TaskEventData(BaseModel):
    """Data payload for task-events topic"""
    task_id: int
    user_id: str
    title: str
    description: str | None = None
    completed: bool = False
    priority: str | None = None
    tags: list[str] = []
    due_date: str | None = None
    remind_before: int | None = None
    recurring_interval: str | None = None
    recurring_end: str | None = None
    created_at: str
    updated_at: str

class ReminderEventData(BaseModel):
    """Data payload for reminders topic"""
    task_id: int
    user_id: str
    title: str
    due_date: str
    remind_at: str  # Calculated: due_date - remind_before minutes

# Example event structures
TASK_CREATED_EXAMPLE = {
    "specversion": "1.0",
    "type": "com.taskmanager.task.created",
    "source": "/tasks/backend-service",
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "time": "2026-01-31T10:00:00Z",
    "datacontenttype": "application/json",
    "data": {
        "task_id": 123,
        "user_id": "user-abc",
        "title": "Buy milk",
        "priority": "high",
        "tags": ["shopping"],
        "due_date": "2026-02-01T15:00:00Z",
        "remind_before": 60,
        "recurring_interval": None,
        "created_at": "2026-01-31T10:00:00Z",
        "updated_at": "2026-01-31T10:00:00Z"
    }
}

REMINDER_SCHEDULED_EXAMPLE = {
    "specversion": "1.0",
    "type": "com.taskmanager.reminder.scheduled",
    "source": "/tasks/backend-service",
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "time": "2026-01-31T10:00:00Z",
    "datacontenttype": "application/json",
    "data": {
        "task_id": 123,
        "user_id": "user-abc",
        "title": "Buy milk",
        "due_date": "2026-02-01T15:00:00Z",
        "remind_at": "2026-02-01T14:00:00Z"
    }
}
```

**Acceptance Criteria**:
- [ ] CloudEvent base class follows spec 1.0
- [ ] TaskEventData contains all task fields
- [ ] ReminderEventData contains reminder-specific fields
- [ ] Example events documented for reference
- [ ] Schemas importable by event_publisher.py

**Test Cases**:
1. CloudEvent.create("task.created", data) → valid CloudEvents structure
2. TaskEventData validates all fields correctly
3. ReminderEventData calculates remind_at from due_date and remind_before

---

### T-507: Implement Dapr Pub/Sub event publishing service

**Agent**: DaprAgent + KafkaAgent
**Priority**: P1
**Estimated Complexity**: Medium
**Dependencies**: T-506

**File**: `backend/services/event_publisher.py`

**Changes**:
```python
import httpx
import logging
from datetime import datetime, timedelta
from backend.events.schemas import CloudEvent, TaskEventData, ReminderEventData

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"
TASK_EVENTS_TOPIC = "task-events"
REMINDERS_TOPIC = "reminders"

async def publish_event(topic: str, event: CloudEvent) -> bool:
    """
    Publish event via Dapr sidecar.
    Graceful degradation: logs warning if Dapr unavailable, does not fail operation.
    """
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=event.model_dump(),
                headers={"Content-Type": "application/cloudevents+json"},
                timeout=5.0
            )
            response.raise_for_status()
            logger.info(f"Event published: {event.type} to {topic}")
            return True
    except httpx.ConnectError:
        logger.warning(f"Dapr sidecar not available. Event not published: {event.type}")
        return False
    except httpx.HTTPStatusError as e:
        logger.error(f"Event publish failed: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Event publish error: {e}")
        return False

async def publish_task_event(event_type: str, task) -> bool:
    """Publish task lifecycle event to task-events topic."""
    data = TaskEventData(
        task_id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        priority=task.priority,
        tags=task.tags or [],
        due_date=task.due_date.isoformat() if task.due_date else None,
        remind_before=task.remind_before,
        recurring_interval=task.recurring_interval,
        recurring_end=task.recurring_end.isoformat() if task.recurring_end else None,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat()
    )

    event = CloudEvent.create(event_type, data.model_dump())
    return await publish_event(TASK_EVENTS_TOPIC, event)

async def publish_reminder_event(task) -> bool:
    """Publish reminder scheduled event when task has due_date and remind_before."""
    if not task.due_date or not task.remind_before:
        return False

    remind_at = task.due_date - timedelta(minutes=task.remind_before)

    data = ReminderEventData(
        task_id=task.id,
        user_id=task.user_id,
        title=task.title,
        due_date=task.due_date.isoformat(),
        remind_at=remind_at.isoformat()
    )

    event = CloudEvent.create("reminder.scheduled", data.model_dump())
    return await publish_event(REMINDERS_TOPIC, event)
```

**Acceptance Criteria**:
- [ ] publish_event sends POST to Dapr Pub/Sub endpoint
- [ ] CloudEvents format used with correct content-type header
- [ ] Connection errors logged but don't raise exceptions
- [ ] HTTP errors logged with response details
- [ ] publish_task_event creates correct event structure
- [ ] publish_reminder_event calculates remind_at correctly

**Test Cases**:
1. Dapr running → event published successfully, returns True
2. Dapr not running → warning logged, returns False, no exception
3. publish_reminder_event with due_date and remind_before → remind_at calculated

---

### T-508: Integrate event publishing in task operations

**Agent**: DaprAgent + FeatureAgent
**Priority**: P1
**Estimated Complexity**: Medium
**Dependencies**: T-503, T-507

**Files**: `backend/routes/tasks.py`, `backend/mcp/tools.py`

**Changes**:
```python
# In routes/tasks.py
from backend.services.event_publisher import publish_task_event, publish_reminder_event

@router.post("/tasks", response_model=TaskOut)
async def create_task(...):
    # ... existing create logic ...
    await session.commit()
    await session.refresh(db_task)

    # Publish events (fire-and-forget, don't await result)
    await publish_task_event("task.created", db_task)
    if db_task.due_date and db_task.remind_before:
        await publish_reminder_event(db_task)

    return db_task

@router.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(...):
    # ... existing update logic ...

    # Determine event type
    was_completed = task.completed and not update_data.get("completed", task.completed)
    is_completed = update_data.get("completed", False) and not task.completed

    # Apply updates
    for key, value in update_data.items():
        setattr(task, key, value)
    task.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)

    # Publish events
    if is_completed:
        await publish_task_event("task.completed", task)
    else:
        await publish_task_event("task.updated", task)

    # If due_date or remind_before changed, publish reminder event
    if "due_date" in update_data or "remind_before" in update_data:
        if task.due_date and task.remind_before:
            await publish_reminder_event(task)

    return task

@router.delete("/tasks/{task_id}")
async def delete_task(...):
    # ... existing delete logic ...

    # Publish event before deleting
    await publish_task_event("task.deleted", task)

    await session.delete(task)
    await session.commit()
    return {"success": True}

# Similar changes in mcp/tools.py for add_task, update_task, delete_task
```

**Acceptance Criteria**:
- [ ] Task creation publishes task.created event
- [ ] Task update publishes task.updated event
- [ ] Task completion publishes task.completed event
- [ ] Task deletion publishes task.deleted event
- [ ] Due date + remind_before triggers reminder.scheduled event
- [ ] Event publish failures don't block CRUD operations
- [ ] Logs show event publishing attempts

**Test Cases**:
1. Create task → logs show "Event published: task.created"
2. Update task → logs show "Event published: task.updated"
3. Complete task → logs show "Event published: task.completed"
4. Delete task → logs show "Event published: task.deleted"
5. Create task with due_date + remind_before → both task.created and reminder.scheduled

---

### T-509: Extend frontend UI for new features

**Agent**: FeatureAgent
**Priority**: P1
**Estimated Complexity**: High
**Dependencies**: T-503

**Files**:
- `frontend/components/TaskForm.tsx`
- `frontend/components/TaskList.tsx`
- `frontend/components/TaskFilters.tsx` (new)
- `frontend/lib/api.ts`

**Changes**:

**TaskForm.tsx**:
```tsx
// Add priority dropdown
<select name="priority" value={task.priority || ""} onChange={handleChange}>
  <option value="">No Priority</option>
  <option value="high">High</option>
  <option value="medium">Medium</option>
  <option value="low">Low</option>
</select>

// Add tags input
<TagInput
  tags={task.tags || []}
  onChange={(tags) => setTask({...task, tags})}
/>

// Add date picker for due date
<input
  type="datetime-local"
  name="due_date"
  value={task.due_date || ""}
  onChange={handleChange}
/>

// Add remind before dropdown
<select name="remind_before" value={task.remind_before || ""} onChange={handleChange}>
  <option value="">No Reminder</option>
  <option value="15">15 minutes before</option>
  <option value="60">1 hour before</option>
  <option value="1440">1 day before</option>
</select>

// Add recurring options
<select name="recurring_interval" value={task.recurring_interval || ""} onChange={handleChange}>
  <option value="">Not Recurring</option>
  <option value="daily">Daily</option>
  <option value="weekly">Weekly</option>
  <option value="monthly">Monthly</option>
</select>
```

**TaskList.tsx**:
```tsx
// Display priority badge
{task.priority && (
  <span className={`priority-badge priority-${task.priority}`}>
    {task.priority}
  </span>
)}

// Display tags
{task.tags?.map(tag => (
  <span key={tag} className="tag-pill">{tag}</span>
))}

// Display due date with overdue indicator
{task.due_date && (
  <span className={isOverdue(task.due_date) ? "overdue" : ""}>
    Due: {formatDate(task.due_date)}
  </span>
)}

// Display recurring indicator
{task.recurring_interval && (
  <span className="recurring-icon">🔁 {task.recurring_interval}</span>
)}
```

**TaskFilters.tsx** (new):
```tsx
export function TaskFilters({ onFilterChange }) {
  return (
    <div className="task-filters">
      <select name="priority" onChange={onFilterChange}>
        <option value="">All Priorities</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>

      <input
        type="text"
        name="search"
        placeholder="Search tasks..."
        onChange={onFilterChange}
      />

      <select name="sort_by" onChange={onFilterChange}>
        <option value="created_at">Sort by Created</option>
        <option value="due_date">Sort by Due Date</option>
        <option value="priority">Sort by Priority</option>
      </select>
    </div>
  );
}
```

**api.ts**:
```typescript
interface TaskFilters {
  priority?: string;
  tags?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
  due_before?: string;
  due_after?: string;
}

export async function getTasks(filters: TaskFilters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });

  const response = await fetch(`/api/tasks?${params}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.json();
}
```

**Acceptance Criteria**:
- [ ] Priority dropdown shows high/medium/low options
- [ ] Tags input allows adding/removing multiple tags
- [ ] Date picker works for due_date selection
- [ ] Remind before dropdown shows time options
- [ ] Recurring dropdown shows daily/weekly/monthly
- [ ] Task list shows priority badges with colors
- [ ] Task list shows tag pills
- [ ] Task list shows due date with overdue styling
- [ ] Filter controls filter task list
- [ ] Sort controls reorder task list
- [ ] Search input filters by keyword

**Test Cases**:
1. Create task with all new fields → task displays correctly
2. Filter by priority=high → only high priority shown
3. Search for "grocery" → matching tasks shown
4. Sort by due_date → tasks ordered correctly
5. Overdue task shows red styling

---

### T-510: Final validation & backward compatibility testing

**Agent**: OrchestratorAgent
**Priority**: P1
**Estimated Complexity**: Medium
**Dependencies**: T-501 through T-509

**Validation Checklist**:

**Database & Model**:
- [ ] New fields save and retrieve correctly
- [ ] Existing tasks load without errors (null new fields)
- [ ] Field validation works (invalid priority rejected)

**API**:
- [ ] POST /tasks with new fields creates task correctly
- [ ] GET /tasks with filters returns correct results
- [ ] PUT /tasks with partial updates works
- [ ] All endpoints return new fields in response

**MCP Tools**:
- [ ] add_task with new params works
- [ ] list_tasks with filters works
- [ ] update_task with new fields works

**Chatbot**:
- [ ] "add high priority task buy milk" → correct task
- [ ] "show tasks tagged work" → filtered list
- [ ] "add task due tomorrow" → correct due_date
- [ ] "make task 1 recur weekly" → recurring set

**Event Publishing**:
- [ ] task.created event in logs
- [ ] task.updated event in logs
- [ ] task.completed event in logs
- [ ] task.deleted event in logs
- [ ] reminder.scheduled event when due_date+remind_before set

**Backward Compatibility**:
- [ ] "add buy milk" still works
- [ ] "show tasks" still works
- [ ] "complete 1" still works
- [ ] "delete 2" still works
- [ ] Dashboard basic flow unchanged
- [ ] Phase III chatbot commands work
- [ ] Phase IV Docker build still works (if tested)

**Acceptance Criteria**:
- [ ] All validation checks pass
- [ ] No regressions in existing functionality
- [ ] Event logs visible for all state changes
- [ ] Graceful handling when Dapr unavailable

---

### T-511: Documentation update

**Agent**: OrchestratorAgent
**Priority**: P2
**Estimated Complexity**: Low
**Dependencies**: T-510

**Files**: `README.md`, `docs/phase5-parta.md`

**Changes**:

Add Phase V Part A section to README:
```markdown
## Phase V Part A: Advanced Features & Event-Driven Logic

### New Features
- **Priority**: Tasks can have high/medium/low priority
- **Tags**: Tasks can have multiple tags for categorization
- **Due Dates**: Tasks can have due dates with reminders
- **Recurring**: Tasks can repeat daily/weekly/monthly
- **Filtering**: Filter tasks by priority, tags, due date
- **Sorting**: Sort tasks by due date, priority, title
- **Search**: Search tasks by keyword

### Event-Driven Architecture
All task operations publish events via Dapr Pub/Sub:
- `task-events` topic: task.created, task.updated, task.completed, task.deleted
- `reminders` topic: reminder.scheduled

Events use CloudEvents 1.0 format.

### Chatbot Commands
New natural language commands:
- "add high priority task [title]"
- "add task [title] due tomorrow"
- "add task [title] tagged [tag]"
- "show high priority tasks"
- "sort tasks by due date"
- "make task [id] recur weekly"
```

**Acceptance Criteria**:
- [ ] README updated with new features
- [ ] Event schema documented
- [ ] Chatbot commands documented
- [ ] API changes documented

---

## Task Summary

| Task ID | Title | Agent | Priority | Dependencies |
|---------|-------|-------|----------|--------------|
| T-501 | Extend Task database model | FeatureAgent | P1 | None |
| T-502 | Extend Pydantic schemas | FeatureAgent | P1 | T-501 |
| T-503 | Update REST API endpoints | FeatureAgent | P1 | T-501, T-502 |
| T-504 | Extend MCP tools | FeatureAgent | P1 | T-503 |
| T-505 | Update Cohere agent | FeatureAgent | P1 | T-504 |
| T-506 | Define event schemas | KafkaAgent | P1 | None |
| T-507 | Implement event publisher | DaprAgent + KafkaAgent | P1 | T-506 |
| T-508 | Integrate event publishing | DaprAgent + FeatureAgent | P1 | T-503, T-507 |
| T-509 | Extend frontend UI | FeatureAgent | P1 | T-503 |
| T-510 | Final validation | OrchestratorAgent | P1 | T-501-T-509 |
| T-511 | Documentation update | OrchestratorAgent | P2 | T-510 |

## Execution Order

```
T-501 (Model) ─┬─► T-502 (Schemas) ─► T-503 (API) ─┬─► T-504 (MCP) ─► T-505 (Agent)
               │                                    │
               │                                    └─► T-509 (UI)
               │
T-506 (Events) ─► T-507 (Publisher) ─────────────────► T-508 (Integration)

All ──────────────────────────────────────────────────► T-510 (Validation) ─► T-511 (Docs)
```

## Constitution Compliance

| Principle | Task Coverage |
|-----------|---------------|
| I. Spec-Driven | All tasks traced to spec.md FRs |
| II. Event-Driven | T-506, T-507, T-508 |
| III. Backward Compat | T-510 validation checklist |
| IV. Dapr-Exclusive | T-507 uses only httpx to localhost:3500 |
| V. Stateless | All state in Neon PostgreSQL |
| VI. Tech Stack | FastAPI, Next.js, Cohere, Neon, Dapr |
