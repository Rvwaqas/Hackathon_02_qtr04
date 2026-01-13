"""Task service for business logic."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlmodel import SQLModel
from ..models.task import Task, RecurrenceType
from ..schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Service for task operations."""

    @staticmethod
    async def create_task(
        session: AsyncSession,
        user_id: int,
        task_data: TaskCreate
    ) -> Dict[str, Any]:
        """
        Create a new task.

        Args:
            session: Database session
            user_id: User ID
            task_data: Task creation data

        Returns:
            Created task data
        """
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            tags=task_data.tags,
            recurrence=task_data.recurrence,
            recurrence_days=task_data.recurrence_days,
            due_date=task_data.due_date,
            reminder_offset_minutes=task_data.reminder_offset_minutes
        )

        session.add(task)
        await session.commit()
        await session.refresh(task)

        return task

    @staticmethod
    async def get_task(
        session: AsyncSession,
        user_id: int,
        task_id: int
    ) -> Optional[Task]:
        """Get a task by ID with ownership validation."""
        stmt = select(Task).where(
            and_(Task.id == task_id, Task.user_id == user_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_tasks(
        session: AsyncSession,
        user_id: int,
        completed: Optional[bool] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Task]:
        """
        List tasks with filtering and sorting.

        Args:
            session: Database session
            user_id: User ID
            completed: Filter by completion status
            priority: Filter by priority
            tag: Filter by tag
            search: Search in title and description
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            List of tasks
        """
        stmt = select(Task).where(Task.user_id == user_id)

        # Apply filters
        if completed is not None:
            stmt = stmt.where(Task.completed == completed)

        if priority and priority != "none":
            stmt = stmt.where(Task.priority == priority)

        if tag:
            stmt = stmt.where(Task.tags.contains([tag]))

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    func.lower(Task.title).ilike(search_pattern),
                    func.lower(Task.description).ilike(search_pattern)
                )
            )

        # Apply sorting
        if sort_by == "priority":
            # Custom priority order
            priority_order = {"high": 1, "medium": 2, "low": 3, "none": 4}
            # This is simplified; real implementation would use CASE statement
            sort_col = Task.priority
        elif sort_by == "due_date":
            sort_col = Task.due_date
        elif sort_by == "title":
            sort_col = Task.title
        else:
            sort_col = Task.created_at

        if sort_order == "asc":
            stmt = stmt.order_by(sort_col.asc())
        else:
            stmt = stmt.order_by(sort_col.desc())

        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_task(
        session: AsyncSession,
        user_id: int,
        task_id: int,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """
        Update a task.

        Args:
            session: Database session
            user_id: User ID
            task_id: Task ID
            task_data: Update data

        Returns:
            Updated task
        """
        task = await TaskService.get_task(session, user_id, task_id)
        if not task:
            return None

        # Update fields if provided
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.completed is not None:
            task.completed = task_data.completed
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.tags is not None:
            task.tags = task_data.tags
        if task_data.recurrence is not None:
            task.recurrence = task_data.recurrence
        if task_data.recurrence_days is not None:
            task.recurrence_days = task_data.recurrence_days
        if task_data.due_date is not None:
            task.due_date = task_data.due_date
        if task_data.reminder_offset_minutes is not None:
            task.reminder_offset_minutes = task_data.reminder_offset_minutes

        task.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(task)

        return task

    @staticmethod
    async def delete_task(
        session: AsyncSession,
        user_id: int,
        task_id: int
    ) -> bool:
        """
        Delete a task.

        Args:
            session: Database session
            user_id: User ID
            task_id: Task ID

        Returns:
            True if deleted, False if not found
        """
        task = await TaskService.get_task(session, user_id, task_id)
        if not task:
            return False

        await session.delete(task)
        await session.commit()
        return True

    @staticmethod
    async def toggle_complete(
        session: AsyncSession,
        user_id: int,
        task_id: int
    ) -> Optional[Task]:
        """
        Toggle task completion status.

        Args:
            session: Database session
            user_id: User ID
            task_id: Task ID

        Returns:
            Updated task
        """
        task = await TaskService.get_task(session, user_id, task_id)
        if not task:
            return None

        task.completed = not task.completed
        task.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(task)

        return task

    @staticmethod
    def calculate_next_recurrence(
        task: Task,
        current_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Calculate next recurrence date for a task.

        Args:
            task: Task object
            current_date: Current date (defaults to now)

        Returns:
            Next occurrence date or None
        """
        if task.recurrence == RecurrenceType.NONE:
            return None

        if current_date is None:
            current_date = datetime.utcnow()

        if task.recurrence == RecurrenceType.DAILY:
            return current_date + timedelta(days=1)

        elif task.recurrence == RecurrenceType.WEEKLY:
            if not task.recurrence_days:
                return current_date + timedelta(weeks=1)
            # Find next weekday
            days_ahead = 7
            for day in sorted(task.recurrence_days):
                if day > current_date.weekday():
                    days_ahead = day - current_date.weekday()
                    break
            return current_date + timedelta(days=days_ahead)

        elif task.recurrence == RecurrenceType.MONTHLY:
            # Handle month-end dates
            year = current_date.year
            month = current_date.month + 1
            day = current_date.day

            if month > 12:
                month = 1
                year += 1

            # Handle month-end (e.g., Jan 31 -> Feb 28)
            try:
                return datetime(year, month, day)
            except ValueError:
                # Get last day of month
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                return datetime(year, month, last_day)

        return None
