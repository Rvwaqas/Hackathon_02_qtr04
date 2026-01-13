"""Task model."""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, JSON
from sqlalchemy import Column


class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class RecurrenceType(str, Enum):
    """Task recurrence types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NONE = "none"


class Task(SQLModel, table=True):
    """Task model with all features."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=200, index=True)
    description: str = Field(default="", max_length=2000)
    completed: bool = Field(default=False, index=True)
    priority: Priority = Field(default=Priority.NONE)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    recurrence: RecurrenceType = Field(default=RecurrenceType.NONE)
    recurrence_days: List[int] = Field(default_factory=list, sa_column=Column(JSON))  # For weekly: [0-6]
    due_date: Optional[datetime] = Field(default=None, index=True)
    reminder_offset_minutes: Optional[int] = Field(default=None)
    parent_task_id: Optional[int] = Field(default=None, foreign_key="task.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "high",
                "tags": ["shopping", "urgent"],
                "recurrence": "weekly",
                "recurrence_days": [0, 3, 5],
                "due_date": "2026-01-15T09:00:00",
                "reminder_offset_minutes": 60,
                "parent_task_id": None,
                "created_at": "2026-01-13T12:00:00",
                "updated_at": "2026-01-13T12:00:00"
            }
        }
