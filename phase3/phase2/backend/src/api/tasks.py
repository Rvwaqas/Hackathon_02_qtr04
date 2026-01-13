"""Task API routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from ..database import get_session
from ..middleware.jwt_auth import get_current_user
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from ..services.task_service import TaskService

router = APIRouter(prefix="/api", tags=["tasks"])


@router.post("/{user_id}/tasks", response_model=TaskResponse)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    current_user: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Task:
    """
    Create a new task.

    Args:
        user_id: User ID (from path)
        task_data: Task creation data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Created task
    """
    # Verify user owns this user_id
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create tasks for yourself"
        )

    task = await TaskService.create_task(session, user_id, task_data)
    return task


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: int,
    current_user: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    completed: Optional[bool] = Query(None),
    priority: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort: str = Query("created_at"),
    order: str = Query("desc")
) -> dict:
    """
    List user's tasks with filtering and sorting.

    Args:
        user_id: User ID (from path)
        current_user: Current authenticated user
        session: Database session
        completed: Filter by completion status
        priority: Filter by priority
        tag: Filter by tag
        search: Search in title and description
        sort: Sort field
        order: Sort order (asc/desc)

    Returns:
        List of tasks
    """
    # Verify user owns this user_id
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tasks"
        )

    tasks = await TaskService.list_tasks(
        session,
        user_id,
        completed=completed,
        priority=priority,
        tag=tag,
        search=search,
        sort_by=sort,
        sort_order=order
    )

    return {
        "tasks": tasks,
        "total": len(tasks),
        "status": "completed" if completed is True else "pending" if completed is False else None,
        "priority_filter": priority,
        "tag_filter": tag
    }


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: int,
    task_id: int,
    current_user: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Task:
    """
    Get a single task.

    Args:
        user_id: User ID (from path)
        task_id: Task ID (from path)
        current_user: Current authenticated user
        session: Database session

    Returns:
        Task details
    """
    # Verify user owns this user_id
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tasks"
        )

    task = await TaskService.get_task(session, user_id, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Task:
    """
    Update a task.

    Args:
        user_id: User ID (from path)
        task_id: Task ID (from path)
        task_data: Update data
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated task
    """
    # Verify user owns this user_id
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )

    task = await TaskService.update_task(session, user_id, task_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task


@router.delete("/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: int,
    task_id: int,
    current_user: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Delete a task.

    Args:
        user_id: User ID (from path)
        task_id: Task ID (from path)
        current_user: Current authenticated user
        session: Database session

    Returns:
        Success message
    """
    # Verify user owns this user_id
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tasks"
        )

    success = await TaskService.delete_task(session, user_id, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return {
        "success": True,
        "message": f"Task {task_id} deleted successfully"
    }


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    user_id: int,
    task_id: int,
    current_user: int = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Task:
    """
    Toggle task completion status.

    Args:
        user_id: User ID (from path)
        task_id: Task ID (from path)
        current_user: Current authenticated user
        session: Database session

    Returns:
        Updated task
    """
    # Verify user owns this user_id
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own tasks"
        )

    task = await TaskService.toggle_complete(session, user_id, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task
