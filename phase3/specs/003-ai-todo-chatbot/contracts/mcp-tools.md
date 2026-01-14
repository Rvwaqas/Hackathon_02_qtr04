# MCP Tools Contract: AI Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Created**: 2026-01-14
**Status**: Complete

---

## Overview

5 MCP tools for AI agent to manage todo tasks. All tools are stateless and receive `user_id` from authenticated context.

---

## Tool Definitions

### 1. add_task

**Description**: Add a new task for the user.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user ID from JWT |
| `title` | string | Yes | Task title (1-200 chars) |
| `description` | string | No | Task description (max 1000 chars) |

**Returns**:
```json
{
  "success": true,
  "task_id": 5,
  "message": "Task 'Buy groceries' added!"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Title is required"
}
```

**Tool Definition**:
```python
@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = ""
) -> dict:
    """
    Add a new task for the user.

    Args:
        user_id: The authenticated user's ID
        title: Task title (required, 1-200 characters)
        description: Optional task description

    Returns:
        Success status with task_id and confirmation message
    """
```

---

### 2. list_tasks

**Description**: List tasks for the user with optional status filter.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user ID from JWT |
| `status` | string | No | Filter: "all" (default), "pending", "completed" |

**Returns**:
```json
{
  "success": true,
  "tasks": [
    {"id": 1, "title": "Buy groceries", "status": "pending", "completed": false},
    {"id": 2, "title": "Call mom", "status": "completed", "completed": true}
  ],
  "count": 2,
  "message": "Found 2 tasks"
}
```

**Empty Response**:
```json
{
  "success": true,
  "tasks": [],
  "count": 0,
  "message": "You have no tasks yet"
}
```

**Tool Definition**:
```python
@mcp.tool()
async def list_tasks(
    user_id: str,
    status: str = "all"
) -> dict:
    """
    List tasks for the user.

    Args:
        user_id: The authenticated user's ID
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        List of tasks with count and summary message
    """
```

---

### 3. complete_task

**Description**: Mark a task as complete.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user ID from JWT |
| `task_id` | integer | Yes | ID of task to complete |

**Returns**:
```json
{
  "success": true,
  "task_id": 3,
  "title": "Buy groceries",
  "message": "Task 'Buy groceries' marked as complete!"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Task not found",
  "task_id": 99
}
```

**Tool Definition**:
```python
@mcp.tool()
async def complete_task(
    user_id: str,
    task_id: int
) -> dict:
    """
    Mark a task as complete.

    Args:
        user_id: The authenticated user's ID
        task_id: ID of the task to mark complete

    Returns:
        Success status with task details and confirmation
    """
```

---

### 4. update_task

**Description**: Update task title or description.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user ID from JWT |
| `task_id` | integer | Yes | ID of task to update |
| `title` | string | No | New title (if changing) |
| `description` | string | No | New description (if changing) |

**Returns**:
```json
{
  "success": true,
  "task_id": 1,
  "title": "Call mom tonight",
  "message": "Task updated to 'Call mom tonight'!"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Task not found",
  "task_id": 99
}
```

**Tool Definition**:
```python
@mcp.tool()
async def update_task(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None
) -> dict:
    """
    Update task title or description.

    Args:
        user_id: The authenticated user's ID
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Success status with updated task details
    """
```

---

### 5. delete_task

**Description**: Delete a task.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user ID from JWT |
| `task_id` | integer | Yes | ID of task to delete |

**Returns**:
```json
{
  "success": true,
  "task_id": 2,
  "title": "Old meeting",
  "message": "Deleted 'Old meeting' successfully"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Task not found",
  "task_id": 99
}
```

**Tool Definition**:
```python
@mcp.tool()
async def delete_task(
    user_id: str,
    task_id: int
) -> dict:
    """
    Delete a task.

    Args:
        user_id: The authenticated user's ID
        task_id: ID of the task to delete

    Returns:
        Success status with deleted task details
    """
```

---

## Tool Implementation Pattern

All tools follow this pattern:

```python
from mcp.server import Server
from src.services.task import TaskService
from src.database import get_session

server = Server("todo-mcp-server")

@server.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Add a new task for the user."""
    try:
        async with get_session() as session:
            task = await TaskService.create_task(
                session=session,
                user_id=int(user_id),
                data=TaskCreate(title=title, description=description)
            )
            return {
                "success": True,
                "task_id": task.id,
                "message": f"Task '{title}' added!"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

---

## Agent Instructions for Tool Use

```python
agent_instructions = """
You are a friendly todo assistant. Help users manage their tasks using natural language.

When to use each tool:
- add_task: When user wants to create, add, or remind about something
- list_tasks: When user asks to show, list, see, or view tasks
- complete_task: When user says done, complete, finish, mark done
- update_task: When user says change, rename, update, modify
- delete_task: When user says delete, remove, cancel

Always:
- Confirm actions with friendly messages and emojis
- Include task titles in confirmations
- Ask for clarification if the request is ambiguous
- Show available tasks if referenced task not found
"""
```

---

## Error Handling

All tools MUST handle these error cases:

| Error | Response |
|-------|----------|
| Task not found | `{"success": false, "error": "Task not found", "task_id": X}` |
| Invalid user_id | `{"success": false, "error": "Invalid user ID"}` |
| Missing required param | `{"success": false, "error": "Title is required"}` |
| Database error | `{"success": false, "error": "Service unavailable"}` |

---

## User Isolation

Every tool MUST:
1. Accept `user_id` as first parameter
2. Filter database queries by `user_id`
3. Never return data from other users
4. Log tool calls with user context

```python
# Example: Always filter by user_id
async def get_task(session, task_id: int, user_id: str):
    result = await session.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == int(user_id)  # User isolation
        )
    )
    return result.scalar_one_or_none()
```
