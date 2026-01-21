"""Notification model."""

from sqlmodel import SQLModel, Field, Index
from datetime import datetime
from typing import Optional


class Notification(SQLModel, table=True):
    """Notification model for reminders."""

    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    task_id: int = Field(foreign_key="tasks.id")
    message: str = Field(max_length=500)
    read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "read"),
    )
