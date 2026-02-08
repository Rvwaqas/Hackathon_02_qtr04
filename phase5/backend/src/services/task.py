"""Task service with event publishing via Dapr Pub/Sub.

Phase V Part A: Integrated event publishing for all CRUD operations.
"""

from sqlmodel import select, or_, and_
from sqlalchemy import literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import logging

from src.models import Task
from src.schemas import TaskCreate, TaskUpdate
from src.services.event_publisher import event_publisher

logger = logging.getLogger(__name__)


class TaskService:
    """Task service with CRUD and recurring task logic."""

    @classmethod
    async def create_task(
        cls, session: AsyncSession, user_id: int, data: TaskCreate
    ) -> Task:
        """Create a new task."""
        task = Task(
            user_id=user_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            tags=data.tags,
            recurrence=data.recurrence,
            due_date=data.due_date,
            reminder_offset_minutes=data.reminder_offset_minutes,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Publish event (fire-and-forget)
        await event_publisher.publish_task_event(
            event_type=event_publisher.EVENT_TASK_CREATED,
            task_id=task.id,
            user_id=user_id,
            task_data={
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "tags": task.tags,
                "due_date": task.due_date.isoformat() + "Z" if task.due_date else None,
                "recurrence": task.recurrence,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() + "Z" if task.created_at else None,
            }
        )

        return task

    @classmethod
    async def get_tasks(
        cls,
        session: AsyncSession,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> List[Task]:
        """Get all tasks for a user with optional filters."""
        query = select(Task).where(Task.user_id == user_id)

        # Status filter
        if status == "completed":
            query = query.where(Task.completed == True)
        elif status == "pending":
            query = query.where(Task.completed == False)

        # Priority filter
        if priority and priority != "all":
            query = query.where(Task.priority == priority)

        # Tag filter (literal_column bypasses JSON type handling for SQLite compatibility)
        if tag:
            query = query.where(literal_column("tags").like(f'%"{tag}"%'))

        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term),
                )
            )

        # Sort
        sort_column = getattr(Task, sort, Task.created_at)
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_task(
        cls, session: AsyncSession, task_id: int, user_id: int
    ) -> Optional[Task]:
        """Get a single task by ID (with ownership check)."""
        result = await session.execute(
            select(Task).where(and_(Task.id == task_id, Task.user_id == user_id))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def update_task(
        cls, session: AsyncSession, task_id: int, user_id: int, data: TaskUpdate
    ) -> Optional[Task]:
        """Update a task."""
        task = await cls.get_task(session, task_id, user_id)
        if not task:
            return None

        # Update fields
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.priority is not None:
            task.priority = data.priority
        if data.completed is not None:
            task.completed = data.completed
        if data.tags is not None:
            task.tags = data.tags
        if data.recurrence is not None:
            task.recurrence = data.recurrence
        if data.due_date is not None:
            task.due_date = data.due_date
        if data.reminder_offset_minutes is not None:
            task.reminder_offset_minutes = data.reminder_offset_minutes

        task.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(task)

        # Publish event (fire-and-forget)
        await event_publisher.publish_task_event(
            event_type=event_publisher.EVENT_TASK_UPDATED,
            task_id=task.id,
            user_id=user_id,
            task_data={
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "tags": task.tags,
                "due_date": task.due_date.isoformat() + "Z" if task.due_date else None,
                "recurrence": task.recurrence,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat() + "Z" if task.updated_at else None,
            }
        )

        return task

    @classmethod
    async def delete_task(
        cls, session: AsyncSession, task_id: int, user_id: int
    ) -> bool:
        """Delete a task."""
        task = await cls.get_task(session, task_id, user_id)
        if not task:
            return False

        # Capture task info before deletion for event
        task_title = task.title

        await session.delete(task)
        await session.commit()

        # Publish event (fire-and-forget)
        await event_publisher.publish_task_event(
            event_type=event_publisher.EVENT_TASK_DELETED,
            task_id=task_id,
            user_id=user_id,
            task_data={
                "title": task_title,
                "deleted_at": datetime.utcnow().isoformat() + "Z",
            }
        )

        return True

    @classmethod
    async def toggle_complete(
        cls, session: AsyncSession, task_id: int, user_id: int
    ) -> Optional[tuple[Task, Optional[Task]]]:
        """
        Toggle task completion status.
        Returns tuple of (current_task, next_task if recurring).
        """
        task = await cls.get_task(session, task_id, user_id)
        if not task:
            return None

        # Toggle completion
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        # If completing a recurring task, create next occurrence
        next_task = None
        if task.completed and task.recurrence:
            next_task = await cls.create_next_occurrence(session, task)

        await session.commit()
        await session.refresh(task)
        if next_task:
            await session.refresh(next_task)

        # Publish completion event
        await event_publisher.publish_task_event(
            event_type=event_publisher.EVENT_TASK_COMPLETED,
            task_id=task.id,
            user_id=user_id,
            task_data={
                "title": task.title,
                "completed_at": task.updated_at.isoformat() + "Z" if task.updated_at else None,
                "was_recurring": bool(task.recurrence),
                "next_occurrence_id": next_task.id if next_task else None,
            }
        )

        # If recurring, also publish recurring triggered event
        if next_task and task.recurrence:
            await event_publisher.publish_recurring_triggered(
                parent_task_id=task.id,
                new_task_id=next_task.id,
                user_id=user_id,
                title=task.title,
                recurrence_type=task.recurrence.get("type", "unknown"),
                previous_due_date=task.due_date,
                next_due_date=next_task.due_date,
            )

        return (task, next_task)

    @classmethod
    async def create_next_occurrence(
        cls, session: AsyncSession, task: Task
    ) -> Optional[Task]:
        """Create the next occurrence of a recurring task."""
        if not task.recurrence:
            return None

        recurrence = task.recurrence
        rec_type = recurrence.get("type")
        interval = recurrence.get("interval", 1)

        # Calculate next due date
        if task.due_date:
            next_due = cls.calculate_next_due_date(
                task.due_date, rec_type, interval
            )
        else:
            next_due = cls.calculate_next_due_date(
                datetime.utcnow(), rec_type, interval
            )

        # Create new task
        next_task = Task(
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            tags=task.tags,
            recurrence=task.recurrence,
            due_date=next_due,
            reminder_offset_minutes=task.reminder_offset_minutes,
            parent_task_id=task.id,
            completed=False,
        )

        session.add(next_task)
        return next_task

    @staticmethod
    def calculate_next_due_date(
        current_date: datetime, rec_type: str, interval: int
    ) -> datetime:
        """Calculate the next due date based on recurrence type."""
        if rec_type == "daily":
            return current_date + timedelta(days=interval)
        elif rec_type == "weekly":
            return current_date + timedelta(weeks=interval)
        elif rec_type == "monthly":
            # Handle month-end edge cases
            next_date = current_date + relativedelta(months=interval)
            # If current day doesn't exist in next month, use last day of month
            if current_date.day > calendar.monthrange(next_date.year, next_date.month)[1]:
                next_date = next_date.replace(
                    day=calendar.monthrange(next_date.year, next_date.month)[1]
                )
            return next_date
        else:
            return current_date + timedelta(days=interval)
