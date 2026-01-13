"""Notification schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Schema for notification responses."""

    id: int
    user_id: int
    task_id: int
    message: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for notification list responses."""

    notifications: list[NotificationResponse]
    total: int
    unread_count: int
