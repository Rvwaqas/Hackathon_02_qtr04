"""Task schemas."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict


class TaskCreate(BaseModel):
    """Task creation schema."""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: str = Field(default="none", pattern="^(high|medium|low|none)$")
    tags: List[str] = Field(default=[])
    recurrence: Optional[Dict] = None
    due_date: Optional[datetime] = None
    reminder_offset_minutes: Optional[int] = Field(default=None, ge=0)


class TaskUpdate(BaseModel):
    """Task update schema."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[str] = Field(default=None, pattern="^(high|medium|low|none)$")
    tags: Optional[List[str]] = None
    recurrence: Optional[Dict] = None
    due_date: Optional[datetime] = None
    reminder_offset_minutes: Optional[int] = Field(default=None, ge=0)


class TaskResponse(BaseModel):
    """Task response schema."""

    id: int
    user_id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    tags: List[str]
    recurrence: Optional[Dict]
    due_date: Optional[datetime]
    reminder_offset_minutes: Optional[int]
    parent_task_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
