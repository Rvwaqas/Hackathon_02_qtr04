"""MCP tools for AI chatbot task operations."""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import TaskService
from src.schemas import TaskCreate, TaskUpdate


async def add_task(
    session: AsyncSession,
    user_id: int,
    title: str,
    description: str = ""
) -> Dict[str, Any]:
    """
    Add a new task for the user.

    Args:
        session: Database session
        user_id: The authenticated user's ID
        title: Task title (required, 1-200 characters)
        description: Optional task description

    Returns:
        Success status with task_id and confirmation message
    """
    try:
        if not title or len(title.strip()) == 0:
            return {
                "success": False,
                "error": "Title is required"
            }

        if len(title) > 200:
            return {
                "success": False,
                "error": "Title must be 200 characters or less"
            }

        task_data = TaskCreate(
            title=title.strip(),
            description=description.strip() if description else None
        )

        task = await TaskService.create_task(
            session=session,
            user_id=user_id,
            data=task_data
        )

        return {
            "success": True,
            "task_id": task.id,
            "message": f"Task '{title}' added!"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }


async def list_tasks(
    session: AsyncSession,
    user_id: int,
    status: str = "all"
) -> Dict[str, Any]:
    """
    List tasks for the user.

    Args:
        session: Database session
        user_id: The authenticated user's ID
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        List of tasks with count and summary message
    """
    try:
        # Map status filter
        status_filter = None
        if status == "pending":
            status_filter = "pending"
        elif status == "completed":
            status_filter = "completed"

        tasks = await TaskService.get_tasks(
            session=session,
            user_id=user_id,
            status=status_filter
        )

        task_list = [
            {
                "id": t.id,
                "title": t.title,
                "status": "completed" if t.completed else "pending",
                "completed": t.completed,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None
            }
            for t in tasks
        ]

        count = len(task_list)
        if count == 0:
            message = "You have no tasks yet" if status == "all" else f"You have no {status} tasks"
        else:
            message = f"Found {count} {'task' if count == 1 else 'tasks'}"

        return {
            "success": True,
            "tasks": task_list,
            "count": count,
            "message": message
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list tasks: {str(e)}",
            "tasks": [],
            "count": 0
        }


async def complete_task(
    session: AsyncSession,
    user_id: int,
    task_id: int
) -> Dict[str, Any]:
    """
    Mark a task as complete.

    Args:
        session: Database session
        user_id: The authenticated user's ID
        task_id: ID of the task to mark complete

    Returns:
        Success status with task details and confirmation
    """
    try:
        task = await TaskService.get_task(session, task_id, user_id)

        if not task:
            return {
                "success": False,
                "error": "Task not found",
                "task_id": task_id
            }

        if task.completed:
            return {
                "success": True,
                "task_id": task_id,
                "title": task.title,
                "message": f"Task '{task.title}' is already complete!"
            }

        result = await TaskService.toggle_complete(session, task_id, user_id)

        if not result:
            return {
                "success": False,
                "error": "Failed to complete task",
                "task_id": task_id
            }

        current_task, _ = result

        return {
            "success": True,
            "task_id": task_id,
            "title": current_task.title,
            "message": f"Task '{current_task.title}' marked as complete!"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to complete task: {str(e)}",
            "task_id": task_id
        }


async def update_task(
    session: AsyncSession,
    user_id: int,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update task title or description.

    Args:
        session: Database session
        user_id: The authenticated user's ID
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Success status with updated task details
    """
    try:
        task = await TaskService.get_task(session, task_id, user_id)

        if not task:
            return {
                "success": False,
                "error": "Task not found",
                "task_id": task_id
            }

        old_title = task.title

        update_data = TaskUpdate()
        if title is not None:
            if len(title.strip()) == 0:
                return {
                    "success": False,
                    "error": "Title cannot be empty"
                }
            update_data.title = title.strip()
        if description is not None:
            update_data.description = description.strip() if description else None

        updated_task = await TaskService.update_task(
            session=session,
            task_id=task_id,
            user_id=user_id,
            data=update_data
        )

        if not updated_task:
            return {
                "success": False,
                "error": "Failed to update task",
                "task_id": task_id
            }

        return {
            "success": True,
            "task_id": task_id,
            "title": updated_task.title,
            "message": f"Task updated to '{updated_task.title}'!"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}",
            "task_id": task_id
        }


async def delete_task(
    session: AsyncSession,
    user_id: int,
    task_id: int
) -> Dict[str, Any]:
    """
    Delete a task.

    Args:
        session: Database session
        user_id: The authenticated user's ID
        task_id: ID of the task to delete

    Returns:
        Success status with deleted task details
    """
    try:
        task = await TaskService.get_task(session, task_id, user_id)

        if not task:
            return {
                "success": False,
                "error": "Task not found",
                "task_id": task_id
            }

        task_title = task.title

        deleted = await TaskService.delete_task(session, task_id, user_id)

        if not deleted:
            return {
                "success": False,
                "error": "Failed to delete task",
                "task_id": task_id
            }

        return {
            "success": True,
            "task_id": task_id,
            "title": task_title,
            "message": f"Deleted '{task_title}' successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}",
            "task_id": task_id
        }


def get_mcp_tools() -> List[Dict[str, Any]]:
    """
    Get tool definitions for the OpenAI Agents SDK.

    Returns:
        List of tool definitions in OpenAI function calling format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a new task for the user. Use when user wants to create, add, or remind about something.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (required, 1-200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List tasks for the user. Use when user asks to show, list, see, or view their tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter by status - all (default), pending, or completed"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete. Use when user says done, complete, finish, or mark done.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to mark complete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update task title or description. Use when user says change, rename, update, or modify.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description (optional)"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task. Use when user says delete, remove, or cancel.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]
