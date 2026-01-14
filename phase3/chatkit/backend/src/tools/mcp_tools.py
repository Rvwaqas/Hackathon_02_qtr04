"""MCP Tools for task operations.

These tools are used by the TaskManager agent to perform task operations
on behalf of the user. All tools validate user ownership via user_id.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import models from phase2 backend (we'll use the same database)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../phase2/backend"))

from src.models.task import Task


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
        user_id: User ID (from JWT)
        title: Task title (max 200 chars)
        description: Task description (max 2000 chars, optional)

    Returns:
        Dict with success status, task details, or error message
    """
    try:
        # Validate title length
        if len(title) > 200:
            return {
                "success": False,
                "error": "Title must be 200 characters or less",
                "task": None
            }

        # Create task
        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else "",
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            },
            "message": f"Task #{task.id} '{task.title}' created successfully"
        }

    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}",
            "task": None
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
        user_id: User ID (from JWT)
        status: Filter by status ("all", "pending", "completed")

    Returns:
        Dict with success status and list of tasks
    """
    try:
        # Build query
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)
        # "all" returns everything

        # Order by created_at descending (newest first)
        query = query.order_by(Task.created_at.desc())

        # Execute query
        result = await session.execute(query)
        tasks = result.scalars().all()

        # Format tasks
        task_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ]

        return {
            "success": True,
            "tasks": task_list,
            "count": len(task_list),
            "status_filter": status
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list tasks: {str(e)}",
            "tasks": []
        }


async def complete_task(
    session: AsyncSession,
    user_id: int,
    task_id: int
) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        session: Database session
        user_id: User ID (from JWT)
        task_id: Task ID to complete

    Returns:
        Dict with success status and task details
    """
    try:
        # Get task with ownership check
        stmt = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return {
                "success": False,
                "error": f"Task #{task_id} not found or you don't have permission",
                "task": None
            }

        # Check if already completed
        if task.completed:
            return {
                "success": False,
                "error": f"Task #{task_id} is already completed",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed
                }
            }

        # Mark as completed
        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            },
            "message": f"Task #{task.id} '{task.title}' marked as completed"
        }

    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": f"Failed to complete task: {str(e)}",
            "task": None
        }


async def update_task(
    session: AsyncSession,
    user_id: int,
    task_id: int,
    title: str
) -> Dict[str, Any]:
    """
    Update a task's title.

    Args:
        session: Database session
        user_id: User ID (from JWT)
        task_id: Task ID to update
        title: New title (max 200 chars)

    Returns:
        Dict with success status and updated task details
    """
    try:
        # Validate title length
        if len(title) > 200:
            return {
                "success": False,
                "error": "Title must be 200 characters or less",
                "task": None
            }

        # Get task with ownership check
        stmt = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return {
                "success": False,
                "error": f"Task #{task_id} not found or you don't have permission",
                "task": None
            }

        # Update title
        old_title = task.title
        task.title = title.strip()
        task.updated_at = datetime.utcnow()
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            },
            "message": f"Task #{task.id} updated from '{old_title}' to '{task.title}'"
        }

    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}",
            "task": None
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
        user_id: User ID (from JWT)
        task_id: Task ID to delete

    Returns:
        Dict with success status
    """
    try:
        # Get task with ownership check
        stmt = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()

        if not task:
            return {
                "success": False,
                "error": f"Task #{task_id} not found or you don't have permission"
            }

        # Store task info before deletion
        task_title = task.title
        task_id_copy = task.id

        # Delete task
        await session.delete(task)
        await session.commit()

        return {
            "success": True,
            "message": f"Task #{task_id_copy} '{task_title}' deleted successfully"
        }

    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}"
        }
