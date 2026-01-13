"""Notification model."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Notification(SQLModel, table=True):
    """Notification model for task reminders."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    task_id: int = Field(foreign_key="task.id", index=True)
    message: str = Field(max_length=500)
    read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "task_id": 1,
                "message": "Reminder: Buy groceries in 1 hour",
                "read": False,
                "created_at": "2026-01-13T12:00:00"
            }
        }
