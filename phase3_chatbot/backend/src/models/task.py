"""Task model."""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Index
from datetime import datetime
from typing import Optional, Dict, List


class Task(SQLModel, table=True):
    """Task model with all features."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(default="none", max_length=20)
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    recurrence: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    due_date: Optional[datetime] = Field(default=None, index=True)
    reminder_offset_minutes: Optional[int] = Field(default=None)
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("ix_tasks_user_completed", "user_id", "completed"),
        Index("ix_tasks_user_priority", "user_id", "priority"),
    )
