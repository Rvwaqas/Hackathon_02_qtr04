"""Notification API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.database import get_session
from src.middleware import get_current_user_id
from src.services import NotificationService
from src.schemas import NotificationResponse

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    read: Optional[bool] = Query(None),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Get all notifications for the authenticated user."""
    notifications = await NotificationService.get_notifications(
        session, user_id, read
    )
    return [NotificationResponse.model_validate(notif) for notif in notifications]


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
):
    """Mark a notification as read."""
    success = await NotificationService.mark_as_read(
        session, notification_id, user_id
    )

    if not success:
        return {"data": None, "error": {"message": "Notification not found", "code": "NOT_FOUND"}}

    return {"data": {"message": "Notification marked as read"}, "error": None}
