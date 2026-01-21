"""Notification service."""

from sqlmodel import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timedelta

from src.models import Notification, Task


class NotificationService:
    """Notification service for reminders."""

    @classmethod
    async def create_notification(
        cls,
        session: AsyncSession,
        user_id: int,
        task_id: int,
        message: str,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            task_id=task_id,
            message=message,
        )
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    @classmethod
    async def get_notifications(
        cls,
        session: AsyncSession,
        user_id: int,
        read: bool = None,
    ) -> List[Notification]:
        """Get all notifications for a user."""
        query = select(Notification).where(Notification.user_id == user_id)

        if read is not None:
            query = query.where(Notification.read == read)

        query = query.order_by(Notification.created_at.desc())
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def mark_as_read(
        cls, session: AsyncSession, notification_id: int, user_id: int
    ) -> bool:
        """Mark a notification as read."""
        result = await session.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id,
                )
            )
        )
        notification = result.scalar_one_or_none()

        if not notification:
            return False

        notification.read = True
        await session.commit()
        return True

    @classmethod
    async def check_and_create_reminders(cls, session: AsyncSession):
        """Check for tasks needing reminders and create notifications."""
        now = datetime.utcnow()

        # Find tasks with due dates and reminders
        query = select(Task).where(
            and_(
                Task.completed == False,
                Task.due_date != None,
                Task.reminder_offset_minutes != None,
            )
        )

        result = await session.execute(query)
        tasks = result.scalars().all()

        for task in tasks:
            if not task.due_date or not task.reminder_offset_minutes:
                continue

            # Calculate reminder time
            reminder_time = task.due_date - timedelta(
                minutes=task.reminder_offset_minutes
            )

            # Check if it's time to send reminder
            if now >= reminder_time and now < task.due_date:
                # Check if notification already exists
                existing = await session.execute(
                    select(Notification).where(
                        and_(
                            Notification.task_id == task.id,
                            Notification.read == False,
                        )
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                # Create notification
                message = f"⏰ '{task.title}' is due soon!"
                await cls.create_notification(
                    session, task.user_id, task.id, message
                )

        await session.commit()
