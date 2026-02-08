# MCP Tools Contract: Phase V Part A Updates

**Version**: 2.0.0
**Last Updated**: 2026-01-31
**Base Version**: 1.0.0 (Phase III)

---

## Overview

This document specifies the updated MCP tool definitions for Phase V Part A. Changes from Phase III are marked with `[NEW]`.

---

## Tool: add_task

**Purpose**: Create a new task for the authenticated user.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| title | string | Yes | - | Task title (1-200 chars) |
| description | string | No | null | Task description (max 2000 chars) |
| priority | enum | No | "none" | Priority level |
| due_date | string | No | null | ISO 8601 datetime |
| tags | array[string] | No | [] | `[NEW]` Category tags (max 10, each max 50 chars) |
| recurrence | object | No | null | `[NEW]` Recurrence settings |
| reminder_offset_minutes | integer | No | null | `[NEW]` Minutes before due_date to remind |

### Priority Enum

```json
["high", "medium", "low", "none"]
```

### Recurrence Object Schema

```json
{
  "type": "string",      // "daily" | "weekly" | "monthly"
  "interval": "integer", // >= 1, default 1
  "end_date": "string"   // ISO 8601 datetime or null
}
```

### Tool Definition (for Cohere)

```json
{
  "name": "add_task",
  "description": "Create a new task. Use this when the user wants to add, create, or make a new task. Supports priority levels (high/medium/low), tags for categorization, due dates, reminders, and recurring schedules.",
  "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "The task title or name. Required."
      },
      "description": {
        "type": "string",
        "description": "Optional longer description of the task."
      },
      "priority": {
        "type": "string",
        "enum": ["high", "medium", "low", "none"],
        "description": "Task priority level. Use 'high' for urgent/important tasks, 'medium' for normal tasks, 'low' for minor tasks, 'none' for no priority."
      },
      "due_date": {
        "type": "string",
        "description": "When the task is due. ISO 8601 format (e.g., '2026-02-15T17:00:00Z') or relative like 'tomorrow', 'next Friday'."
      },
      "tags": {
        "type": "array",
        "items": {"type": "string"},
        "description": "[NEW] Category tags for the task. Examples: ['work', 'personal', 'urgent']."
      },
      "recurrence": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": ["daily", "weekly", "monthly"],
            "description": "How often the task repeats."
          },
          "interval": {
            "type": "integer",
            "description": "Number of periods between occurrences. Default 1."
          },
          "end_date": {
            "type": "string",
            "description": "When recurrence stops. ISO 8601 format."
          }
        },
        "description": "[NEW] Make the task recurring. Set type to 'daily', 'weekly', or 'monthly'."
      },
      "reminder_offset_minutes": {
        "type": "integer",
        "description": "[NEW] Remind user this many minutes before due_date. E.g., 60 for 1 hour before."
      }
    },
    "required": ["title"]
  }
}
```

### Response Schema

```json
{
  "success": true,
  "task_id": 123,
  "message": "Created task 'Review report' with priority HIGH, due Feb 15, tagged [work]"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Title is required"
}
```

---

## Tool: list_tasks

**Purpose**: List tasks for the authenticated user with optional filtering and sorting.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| status | enum | No | "all" | Filter by completion status |
| priority | enum | No | null | Filter by priority level |
| tag | string | No | null | `[NEW]` Filter by tag (single tag) |
| search | string | No | null | `[NEW]` Search in title/description |
| sort | enum | No | "created_at" | `[NEW]` Sort field |
| order | enum | No | "desc" | `[NEW]` Sort direction |

### Status Enum

```json
["pending", "completed", "all"]
```

### Sort Enum

```json
["created_at", "due_date", "priority", "title", "updated_at"]
```

### Order Enum

```json
["asc", "desc"]
```

### Tool Definition (for Cohere)

```json
{
  "name": "list_tasks",
  "description": "List the user's tasks with optional filters. Use this when the user wants to see, show, view, list, find, or search their tasks. Supports filtering by status (pending/completed), priority (high/medium/low), tags, and keyword search. Can sort by various fields.",
  "parameters": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["pending", "completed", "all"],
        "description": "Filter by task status. 'pending' for incomplete tasks, 'completed' for done tasks, 'all' for everything."
      },
      "priority": {
        "type": "string",
        "enum": ["high", "medium", "low", "none"],
        "description": "Filter to only show tasks with this priority level."
      },
      "tag": {
        "type": "string",
        "description": "[NEW] Filter to only show tasks with this tag. Example: 'work' to show work-related tasks."
      },
      "search": {
        "type": "string",
        "description": "[NEW] Search keyword to find in task titles or descriptions. Example: 'meeting' to find meeting-related tasks."
      },
      "sort": {
        "type": "string",
        "enum": ["created_at", "due_date", "priority", "title", "updated_at"],
        "description": "[NEW] Field to sort results by. Default is 'created_at'."
      },
      "order": {
        "type": "string",
        "enum": ["asc", "desc"],
        "description": "[NEW] Sort order. 'asc' for ascending (oldest/lowest first), 'desc' for descending (newest/highest first)."
      }
    },
    "required": []
  }
}
```

### Response Schema

```json
{
  "success": true,
  "tasks": [
    {
      "id": 123,
      "title": "Review report",
      "description": "Q4 review",
      "priority": "high",
      "tags": ["work"],
      "due_date": "2026-02-15T17:00:00Z",
      "completed": false,
      "created_at": "2026-01-31T12:00:00Z"
    }
  ],
  "count": 1,
  "message": "Found 1 pending high-priority task tagged 'work'"
}
```

---

## Tool: complete_task

**Purpose**: Mark a task as complete.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | integer | Yes | ID of task to complete |

### Tool Definition (for Cohere)

```json
{
  "name": "complete_task",
  "description": "Mark a task as complete/done. Use when user says 'complete', 'finish', 'done', 'mark as done', 'check off' a task. If the task is recurring, a new occurrence will be created automatically.",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "The ID number of the task to mark as complete."
      }
    },
    "required": ["task_id"]
  }
}
```

### Response Schema

```json
{
  "success": true,
  "task_id": 123,
  "message": "Completed task 'Review report'. Next occurrence created as task #124 due Feb 22."
}
```

---

## Tool: update_task

**Purpose**: Update an existing task's fields.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| task_id | integer | Yes | - | ID of task to update |
| title | string | No | null | New title |
| description | string | No | null | New description |
| priority | enum | No | null | New priority |
| status | enum | No | null | New status (pending/completed) |
| due_date | string | No | null | New due date |
| tags | array[string] | No | null | `[NEW]` New tags (replaces existing) |
| recurrence | object | No | null | `[NEW]` New recurrence settings |
| reminder_offset_minutes | integer | No | null | `[NEW]` New reminder offset |

### Tool Definition (for Cohere)

```json
{
  "name": "update_task",
  "description": "Update an existing task. Use when user wants to change, modify, edit, update, set, or adjust task properties. Can update title, description, priority, status, due date, tags, recurrence, and reminder settings.",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "The ID number of the task to update. Required."
      },
      "title": {
        "type": "string",
        "description": "New title for the task."
      },
      "description": {
        "type": "string",
        "description": "New description for the task."
      },
      "priority": {
        "type": "string",
        "enum": ["high", "medium", "low", "none"],
        "description": "New priority level for the task."
      },
      "status": {
        "type": "string",
        "enum": ["pending", "completed"],
        "description": "New status. Use 'completed' to mark done, 'pending' to reopen."
      },
      "due_date": {
        "type": "string",
        "description": "New due date. ISO 8601 format or relative like 'tomorrow'."
      },
      "tags": {
        "type": "array",
        "items": {"type": "string"},
        "description": "[NEW] New tags for the task. Replaces existing tags."
      },
      "recurrence": {
        "type": "object",
        "properties": {
          "type": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
          "interval": {"type": "integer"},
          "end_date": {"type": "string"}
        },
        "description": "[NEW] New recurrence settings. Set to make task repeat, or null to stop recurring."
      },
      "reminder_offset_minutes": {
        "type": "integer",
        "description": "[NEW] New reminder offset in minutes before due date."
      }
    },
    "required": ["task_id"]
  }
}
```

### Response Schema

```json
{
  "success": true,
  "task_id": 123,
  "message": "Updated task 'Review report': priority changed to HIGH, now recurring weekly"
}
```

---

## Tool: delete_task

**Purpose**: Permanently delete a task.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| task_id | integer | Yes | ID of task to delete |

### Tool Definition (for Cohere)

```json
{
  "name": "delete_task",
  "description": "Permanently delete a task. Use when user wants to delete, remove, discard, or get rid of a task. This action cannot be undone.",
  "parameters": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "integer",
        "description": "The ID number of the task to delete."
      }
    },
    "required": ["task_id"]
  }
}
```

### Response Schema

```json
{
  "success": true,
  "task_id": 123,
  "message": "Deleted task 'Review report'"
}
```

---

## System Prompt Updates

The following intents MUST be recognized by the system prompt:

### Priority Recognition

| User Language | Mapped Priority |
|---------------|-----------------|
| "high priority", "urgent", "important", "critical" | high |
| "medium priority", "normal", "moderate" | medium |
| "low priority", "minor", "can wait" | low |
| no priority mentioned | none |

### Tag Recognition

| User Language | Action |
|---------------|--------|
| "tagged X", "tag X", "with tag X", "label X" | Add tag X |
| "tagged X and Y", "tags: X, Y" | Add tags X and Y |
| "remove tag X" | Remove tag (via update) |

### Search Recognition

| User Language | Action |
|---------------|--------|
| "find X", "search for X", "look for X" | search=X |
| "containing X", "with X in name" | search=X |
| "tasks about X", "tasks related to X" | search=X |

### Filter Recognition

| User Language | Action |
|---------------|--------|
| "show only high priority" | priority=high |
| "show tasks tagged X" | tag=X |
| "pending tasks", "incomplete tasks" | status=pending |
| "completed tasks", "done tasks" | status=completed |
| "all tasks" | status=all |

### Sort Recognition

| User Language | Action |
|---------------|--------|
| "sort by due date", "order by deadline" | sort=due_date |
| "sort by priority" | sort=priority |
| "sort by created", "oldest first" | sort=created_at, order=asc |
| "newest first" | sort=created_at, order=desc |
| "alphabetical", "by name" | sort=title, order=asc |

### Recurrence Recognition

| User Language | Mapped Recurrence |
|---------------|-------------------|
| "repeat daily", "every day" | {type: "daily", interval: 1} |
| "repeat weekly", "every week" | {type: "weekly", interval: 1} |
| "every 2 weeks", "biweekly" | {type: "weekly", interval: 2} |
| "repeat monthly", "every month" | {type: "monthly", interval: 1} |
| "until DATE", "ending DATE" | end_date: DATE |

### Due Date Recognition

| User Language | Mapped Due Date |
|---------------|-----------------|
| "due tomorrow" | tomorrow at end of day |
| "due Friday", "by Friday" | next Friday at end of day |
| "due Feb 15", "deadline Feb 15" | Feb 15 at end of day |
| "due in 3 days" | current date + 3 days |

### Reminder Recognition

| User Language | Mapped Offset |
|---------------|---------------|
| "remind me 30 minutes before" | 30 |
| "remind me 1 hour before" | 60 |
| "remind me 1 day before" | 1440 |
| "no reminder" | null |

---

## Example Interactions

### Create Advanced Task

**User**: "add high priority task 'Quarterly review' due next Friday tagged work and reports, remind me 1 hour before, repeat monthly"

**Agent Action**:
```json
{
  "tool": "add_task",
  "parameters": {
    "title": "Quarterly review",
    "priority": "high",
    "due_date": "2026-02-07T17:00:00Z",
    "tags": ["work", "reports"],
    "reminder_offset_minutes": 60,
    "recurrence": {
      "type": "monthly",
      "interval": 1
    }
  }
}
```

### Filter and Sort

**User**: "show me pending high priority tasks tagged work, sorted by due date"

**Agent Action**:
```json
{
  "tool": "list_tasks",
  "parameters": {
    "status": "pending",
    "priority": "high",
    "tag": "work",
    "sort": "due_date",
    "order": "asc"
  }
}
```

### Search

**User**: "find tasks about quarterly report"

**Agent Action**:
```json
{
  "tool": "list_tasks",
  "parameters": {
    "search": "quarterly report"
  }
}
```

### Update Recurrence

**User**: "make task 5 repeat weekly until end of March"

**Agent Action**:
```json
{
  "tool": "update_task",
  "parameters": {
    "task_id": 5,
    "recurrence": {
      "type": "weekly",
      "interval": 1,
      "end_date": "2026-03-31T23:59:59Z"
    }
  }
}
```

---

## Backward Compatibility

All Phase III commands MUST continue to work:

| Phase III Command | Behavior |
|-------------------|----------|
| "add task X" | Creates task with title X, priority=none |
| "show tasks" | Lists all pending tasks |
| "show all tasks" | Lists all tasks (pending + completed) |
| "complete task N" | Marks task N as complete |
| "delete task N" | Deletes task N |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-20 | Phase III initial tools |
| 2.0.0 | 2026-01-31 | Phase V Part A extensions (tags, recurrence, search, sort) |
