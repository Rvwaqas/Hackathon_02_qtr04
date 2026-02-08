# Event Schema Contract: Phase V Part A

**Version**: 1.0.0
**Last Updated**: 2026-01-31
**Format**: CloudEvents 1.0 Specification

---

## Overview

All events in the Phase V Part A system follow the [CloudEvents 1.0](https://cloudevents.io/) specification. Events are published via Dapr Pub/Sub to Kafka topics.

---

## Topics

| Topic Name | Purpose | Event Types |
|------------|---------|-------------|
| `task-events` | All task lifecycle events | created, updated, completed, deleted |
| `reminders` | Reminder and recurring triggers | reminder.due, recurring.triggered |

---

## Base CloudEvent Structure

All events MUST include these required fields:

```json
{
  "specversion": "1.0",
  "type": "<event-type>",
  "source": "<source-path>",
  "id": "<uuid-v4>",
  "time": "<iso-8601-timestamp>",
  "datacontenttype": "application/json",
  "data": { ... }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| specversion | string | Yes | Always "1.0" |
| type | string | Yes | Event type identifier (see below) |
| source | string | Yes | Origin path, e.g., "/api/tasks" |
| id | string | Yes | Unique event ID (UUID v4) |
| time | string | Yes | ISO 8601 timestamp with timezone |
| datacontenttype | string | Yes | Always "application/json" |
| data | object | Yes | Event-specific payload |

---

## Event Types

### com.todo.task.created

**Trigger**: New task created via API or chatbot
**Topic**: `task-events`

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/api/tasks",
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "time": "2026-01-31T12:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Review quarterly report",
    "description": "Q4 financial review",
    "priority": "high",
    "tags": ["work", "reports"],
    "due_date": "2026-02-07T17:00:00Z",
    "reminder_offset_minutes": 60,
    "recurrence": {
      "type": "weekly",
      "interval": 1,
      "end_date": null
    },
    "completed": false,
    "created_at": "2026-01-31T12:00:00Z"
  }
}
```

**Data Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | integer | Yes | Unique task identifier |
| user_id | integer | Yes | Owner user ID |
| title | string | Yes | Task title |
| description | string | No | Task description |
| priority | string | Yes | high/medium/low/none |
| tags | array[string] | Yes | Category tags (may be empty) |
| due_date | string/null | No | ISO 8601 datetime |
| reminder_offset_minutes | integer/null | No | Minutes before due_date |
| recurrence | object/null | No | Recurrence configuration |
| completed | boolean | Yes | Completion status |
| created_at | string | Yes | ISO 8601 creation timestamp |

---

### com.todo.task.updated

**Trigger**: Existing task modified (any field)
**Topic**: `task-events`

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.updated",
  "source": "/api/tasks",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "time": "2026-01-31T14:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "changes": {
      "priority": {
        "old": "medium",
        "new": "high"
      },
      "tags": {
        "old": ["work"],
        "new": ["work", "urgent"]
      }
    },
    "task_snapshot": {
      "title": "Review quarterly report",
      "description": "Q4 financial review",
      "priority": "high",
      "tags": ["work", "urgent"],
      "due_date": "2026-02-07T17:00:00Z",
      "completed": false
    },
    "updated_at": "2026-01-31T14:30:00Z"
  }
}
```

**Data Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | integer | Yes | Task identifier |
| user_id | integer | Yes | Owner user ID |
| changes | object | Yes | Changed fields with old/new values |
| task_snapshot | object | Yes | Current state of full task |
| updated_at | string | Yes | ISO 8601 update timestamp |

---

### com.todo.task.completed

**Trigger**: Task marked as complete
**Topic**: `task-events`

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.completed",
  "source": "/api/tasks",
  "id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
  "time": "2026-01-31T16:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Review quarterly report",
    "completed_at": "2026-01-31T16:00:00Z",
    "was_recurring": true,
    "next_occurrence_id": 124
  }
}
```

**Data Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | integer | Yes | Completed task ID |
| user_id | integer | Yes | Owner user ID |
| title | string | Yes | Task title |
| completed_at | string | Yes | ISO 8601 completion timestamp |
| was_recurring | boolean | Yes | Had recurrence settings |
| next_occurrence_id | integer/null | No | New task ID if recurring |

---

### com.todo.task.deleted

**Trigger**: Task permanently deleted
**Topic**: `task-events`

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.deleted",
  "source": "/api/tasks",
  "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
  "time": "2026-01-31T18:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Review quarterly report",
    "deleted_at": "2026-01-31T18:00:00Z"
  }
}
```

---

### com.todo.recurring.triggered

**Trigger**: Recurring task creates next occurrence
**Topic**: `reminders`

```json
{
  "specversion": "1.0",
  "type": "com.todo.recurring.triggered",
  "source": "/api/tasks",
  "id": "d4e5f6a7-b8c9-0123-defg-456789012345",
  "time": "2026-01-31T16:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "parent_task_id": 123,
    "new_task_id": 124,
    "user_id": 456,
    "title": "Review quarterly report",
    "recurrence_type": "weekly",
    "previous_due_date": "2026-01-31T17:00:00Z",
    "next_due_date": "2026-02-07T17:00:00Z"
  }
}
```

---

### com.todo.reminder.due

**Trigger**: Reminder time reached (reminder_offset_minutes before due_date)
**Topic**: `reminders`

```json
{
  "specversion": "1.0",
  "type": "com.todo.reminder.due",
  "source": "/services/scheduler",
  "id": "e5f6a7b8-c9d0-1234-efgh-567890123456",
  "time": "2026-02-07T16:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": 456,
    "title": "Review quarterly report",
    "due_date": "2026-02-07T17:00:00Z",
    "reminder_offset_minutes": 60,
    "reminder_time": "2026-02-07T16:00:00Z"
  }
}
```

---

## Dapr Publishing

### HTTP Endpoint

```
POST http://localhost:3500/v1.0/publish/{pubsub-name}/{topic}
Content-Type: application/cloudevents+json

{event-body}
```

### Example Request

```bash
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/cloudevents+json" \
  -d '{
    "specversion": "1.0",
    "type": "com.todo.task.created",
    "source": "/api/tasks",
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "time": "2026-01-31T12:00:00Z",
    "datacontenttype": "application/json",
    "data": {
      "task_id": 123,
      "user_id": 456,
      "title": "New task"
    }
  }'
```

### Response Codes

| Code | Meaning |
|------|---------|
| 204 | Event published successfully |
| 400 | Invalid event format |
| 403 | Pub/Sub component not configured |
| 500 | Internal error |

---

## Python Implementation

```python
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

import httpx

class EventPublisher:
    """Publishes events to Dapr Pub/Sub."""

    DAPR_HOST = "http://localhost:3500"
    PUBSUB_NAME = "kafka-pubsub"

    TOPIC_TASK_EVENTS = "task-events"
    TOPIC_REMINDERS = "reminders"

    @staticmethod
    def _create_cloud_event(
        event_type: str,
        source: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create CloudEvents 1.0 compliant event."""
        return {
            "specversion": "1.0",
            "type": event_type,
            "source": source,
            "id": str(uuid.uuid4()),
            "time": datetime.utcnow().isoformat() + "Z",
            "datacontenttype": "application/json",
            "data": data
        }

    async def publish(
        self,
        topic: str,
        event_type: str,
        source: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Publish event to Dapr. Returns True if successful.
        Fails gracefully - logs error but doesn't raise.
        """
        event = self._create_cloud_event(event_type, source, data)
        url = f"{self.DAPR_HOST}/v1.0/publish/{self.PUBSUB_NAME}/{topic}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    json=event,
                    headers={"Content-Type": "application/cloudevents+json"}
                )
                if response.status_code == 204:
                    return True
                else:
                    # Log error but don't fail
                    print(f"Event publish failed: {response.status_code}")
                    return False
        except Exception as e:
            # Log error but don't fail
            print(f"Event publish error: {e}")
            return False
```

---

## Validation Rules

1. **specversion**: Must be exactly "1.0"
2. **type**: Must match one of the defined event types
3. **source**: Must be a valid URI path
4. **id**: Must be a valid UUID v4
5. **time**: Must be ISO 8601 with timezone
6. **datacontenttype**: Must be "application/json"
7. **data**: Must be valid JSON object with required fields

---

## Testing

### Mock Dapr for Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_dapr():
    """Mock Dapr HTTP endpoint for testing."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        client.post.return_value.status_code = 204
        mock.return_value.__aenter__.return_value = client
        yield client

async def test_event_published(mock_dapr):
    publisher = EventPublisher()
    result = await publisher.publish(
        topic="task-events",
        event_type="com.todo.task.created",
        source="/api/tasks",
        data={"task_id": 1, "user_id": 1, "title": "Test"}
    )
    assert result is True
    mock_dapr.post.assert_called_once()
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-31 | Initial event schema specification |
