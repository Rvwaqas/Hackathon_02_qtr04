"""Notification schemas."""

from pydantic import BaseModel
from datetime import datetime


class NotificationResponse(BaseModel):
    """Notification response schema."""

    id: int
    user_id: int
    task_id: int
    message: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True
