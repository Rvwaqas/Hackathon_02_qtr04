"""Task schemas for API validation."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


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


class TaskCreate(BaseModel):
    """Schema for creating a task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    priority: Priority = Field(default=Priority.NONE)
    tags: List[str] = Field(default_factory=list)
    recurrence: RecurrenceType = Field(default=RecurrenceType.NONE)
    recurrence_days: List[int] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    reminder_offset_minutes: Optional[int] = None

    @field_validator("tags")
    def validate_tags(cls, v):
        """Validate tags."""
        if len(v) > 10:
            raise ValueError("Maximum 10 tags per task")
        return [tag.lower().strip() for tag in v if tag.strip()]

    @field_validator("recurrence_days")
    def validate_recurrence_days(cls, v):
        """Validate recurrence days."""
        for day in v:
            if day < 0 or day > 6:
                raise ValueError("Recurrence days must be 0-6 (Monday-Sunday)")
        return v


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    completed: Optional[bool] = None
    priority: Optional[Priority] = None
    tags: Optional[List[str]] = None
    recurrence: Optional[RecurrenceType] = None
    recurrence_days: Optional[List[int]] = None
    due_date: Optional[datetime] = None
    reminder_offset_minutes: Optional[int] = None

    @field_validator("tags")
    def validate_tags(cls, v):
        """Validate tags."""
        if v and len(v) > 10:
            raise ValueError("Maximum 10 tags per task")
        return [tag.lower().strip() for tag in v if tag and tag.strip()] if v else None


class TaskResponse(BaseModel):
    """Schema for task responses."""

    id: int
    user_id: int
    title: str
    description: str
    completed: bool
    priority: Priority
    tags: List[str]
    recurrence: RecurrenceType
    recurrence_days: List[int]
    due_date: Optional[datetime]
    reminder_offset_minutes: Optional[int]
    parent_task_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list responses."""

    tasks: List[TaskResponse]
    total: int
    status: Optional[str] = None
    priority_filter: Optional[str] = None
    tag_filter: Optional[str] = None
