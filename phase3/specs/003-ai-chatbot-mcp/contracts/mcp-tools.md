# MCP Tools Contract

**Feature**: `003-ai-chatbot-mcp`
**Date**: 2026-01-13

## Overview

Five MCP tools exposed via OpenAI Agents SDK `@function_tool` decorator for task management operations.

---

## Tool: add_task

**Purpose**: Create a new task for the authenticated user.

### Signature

```python
@function_tool
async def add_task(
    user_id: int,
    title: str,
    description: str = ""
) -> dict
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | int | Yes | Authenticated user ID |
| title | str | Yes | Task title (1-200 characters) |
| description | str | No | Task description (max 2000 characters) |

### Response

```json
{
    "success": true,
    "task": {
        "id": 45,
        "title": "buy groceries",
        "description": "",
        "completed": false,
        "created_at": "2026-01-13T10:30:00Z"
    }
}
```

### Errors

```json
{
    "success": false,
    "error": "title_required",
    "message": "Task title cannot be empty"
}
```

---

## Tool: list_tasks

**Purpose**: Retrieve user's tasks with optional status filter.

### Signature

```python
@function_tool
async def list_tasks(
    user_id: int,
    status: str = "all"
) -> dict
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | int | Yes | Authenticated user ID |
| status | str | No | Filter: "all", "pending", "completed" |

### Response

```json
{
    "success": true,
    "count": 3,
    "status_filter": "pending",
    "tasks": [
        {
            "id": 45,
            "title": "buy groceries",
            "completed": false,
            "created_at": "2026-01-13T10:30:00Z"
        },
        {
            "id": 44,
            "title": "call mom",
            "completed": false,
            "created_at": "2026-01-13T09:00:00Z"
        }
    ]
}
```

### Errors

```json
{
    "success": false,
    "error": "invalid_status",
    "message": "Status must be 'all', 'pending', or 'completed'"
}
```

---

## Tool: complete_task

**Purpose**: Mark a task as completed.

### Signature

```python
@function_tool
async def complete_task(
    user_id: int,
    task_id: int
) -> dict
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | int | Yes | Authenticated user ID |
| task_id | int | Yes | ID of task to complete |

### Response

```json
{
    "success": true,
    "task": {
        "id": 45,
        "title": "buy groceries",
        "completed": true,
        "completed_at": "2026-01-13T11:00:00Z"
    }
}
```

### Errors

```json
{
    "success": false,
    "error": "task_not_found",
    "message": "Task #999 not found"
}
```

```json
{
    "success": false,
    "error": "already_completed",
    "message": "Task #45 is already completed"
}
```

---

## Tool: update_task

**Purpose**: Update task title or description.

### Signature

```python
@function_tool
async def update_task(
    user_id: int,
    task_id: int,
    title: str = None,
    description: str = None
) -> dict
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | int | Yes | Authenticated user ID |
| task_id | int | Yes | ID of task to update |
| title | str | No | New title (1-200 characters) |
| description | str | No | New description (max 2000 characters) |

### Response

```json
{
    "success": true,
    "task": {
        "id": 45,
        "title": "buy groceries and fruits",
        "description": "",
        "completed": false,
        "updated_at": "2026-01-13T11:30:00Z"
    },
    "changes": {
        "title": {
            "old": "buy groceries",
            "new": "buy groceries and fruits"
        }
    }
}
```

### Errors

```json
{
    "success": false,
    "error": "task_not_found",
    "message": "Task #999 not found"
}
```

```json
{
    "success": false,
    "error": "empty_title",
    "message": "Task title cannot be empty"
}
```

---

## Tool: delete_task

**Purpose**: Permanently delete a task.

### Signature

```python
@function_tool
async def delete_task(
    user_id: int,
    task_id: int
) -> dict
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | int | Yes | Authenticated user ID |
| task_id | int | Yes | ID of task to delete |

### Response

```json
{
    "success": true,
    "deleted_task": {
        "id": 45,
        "title": "buy groceries"
    }
}
```

### Errors

```json
{
    "success": false,
    "error": "task_not_found",
    "message": "Task #999 not found"
}
```

---

## Security Requirements

All tools MUST:

1. **Validate user_id**: Ensure task belongs to authenticated user
2. **Sanitize inputs**: Prevent SQL injection and XSS
3. **Return safe errors**: Never expose internal details
4. **Log operations**: Audit trail for all modifications

---

## Response Templates (for ResponseFormatter Agent)

```python
RESPONSE_TEMPLATES = {
    "add_task_success": "✅ Added: '{title}' (Task #{id})",
    "list_tasks_header": "📝 Your {status} tasks:",
    "list_tasks_empty": "You're all caught up! 🎉 No {status} tasks.",
    "complete_task_success": "🎉 Completed: '{title}'",
    "update_task_success": "✏️ Updated Task #{id}: '{old_title}' → '{new_title}'",
    "delete_task_success": "🗑️ Deleted: '{title}'",
    "task_not_found": "❌ Task #{id} not found. Type 'show my tasks' to see your task list.",
    "error_generic": "❌ {message}\n💡 {suggestion}"
}
```
