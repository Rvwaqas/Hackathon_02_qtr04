"""MCP Tools for AI Chatbot using OpenAI Agents SDK pattern."""

from typing import List, Dict, Any, Optional
from agents import function_tool, RunContextWrapper

from src.services.task import TaskService
from src.schemas.task import TaskCreate, TaskUpdate


@function_tool
async def add_task(
    ctx: RunContextWrapper,
    title: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        title: The title of the task (required)
        description: Optional description of the task

    Returns:
        task_id, status, and title of created task
    """
    user_id = ctx.context.get("user_id")
    session = ctx.context.get("session")

    task_data = TaskCreate(
        title=title,
        description=description,
        priority="medium",
        tags=[]
    )

    task = await TaskService.create_task(session, user_id, task_data)

    return {
        "task_id": task.id,
        "status": "created",
        "title": task.title
    }


@function_tool
async def list_tasks(
    ctx: RunContextWrapper,
    status: str = "all"
) -> List[Dict[str, Any]]:
    """
    Retrieve tasks from the user's list.

    Args:
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        Array of task objects with id, title, completed status
    """
    user_id = ctx.context.get("user_id")
    session = ctx.context.get("session")

    tasks = await TaskService.get_user_tasks(session, user_id)

    # Filter by status
    if status == "pending":
        tasks = [t for t in tasks if not t.completed]
    elif status == "completed":
        tasks = [t for t in tasks if t.completed]

    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "completed": t.completed
        }
        for t in tasks
    ]


@function_tool
async def complete_task(
    ctx: RunContextWrapper,
    task_id: int
) -> Dict[str, Any]:
    """
    Mark a task as complete.

    Args:
        task_id: The ID of the task to complete

    Returns:
        task_id, status, and title of completed task
    """
    user_id = ctx.context.get("user_id")
    session = ctx.context.get("session")

    task = await TaskService.get_task(session, task_id, user_id)

    if not task:
        return {"task_id": task_id, "status": "error", "message": "Task not found"}

    result = await TaskService.toggle_complete(session, task_id, user_id)

    return {
        "task_id": result["current_task"].id,
        "status": "completed",
        "title": result["current_task"].title
    }


@function_tool
async def delete_task(
    ctx: RunContextWrapper,
    task_id: int
) -> Dict[str, Any]:
    """
    Remove a task from the list.

    Args:
        task_id: The ID of the task to delete

    Returns:
        task_id, status, and title of deleted task
    """
    user_id = ctx.context.get("user_id")
    session = ctx.context.get("session")

    task = await TaskService.get_task(session, task_id, user_id)

    if not task:
        return {"task_id": task_id, "status": "error", "message": "Task not found"}

    title = task.title
    await TaskService.delete_task(session, task_id, user_id)

    return {
        "task_id": task_id,
        "status": "deleted",
        "title": title
    }


@function_tool
async def update_task(
    ctx: RunContextWrapper,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Modify task title or description.

    Args:
        task_id: The ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)

    Returns:
        task_id, status, and title of updated task
    """
    user_id = ctx.context.get("user_id")
    session = ctx.context.get("session")

    task = await TaskService.get_task(session, task_id, user_id)

    if not task:
        return {"task_id": task_id, "status": "error", "message": "Task not found"}

    update_data = {}
    if title:
        update_data["title"] = title
    if description:
        update_data["description"] = description

    if not update_data:
        return {"task_id": task_id, "status": "error", "message": "No updates provided"}

    task_update = TaskUpdate(**update_data)
    updated_task = await TaskService.update_task(session, task_id, user_id, task_update)

    return {
        "task_id": updated_task.id,
        "status": "updated",
        "title": updated_task.title
    }


def get_mcp_tools():
    """Get list of MCP tools for the agent."""
    return [add_task, list_tasks, complete_task, delete_task, update_task]
