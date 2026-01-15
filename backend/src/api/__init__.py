"""API routes."""

from .auth import router as auth_router
from .tasks import router as tasks_router
from .notifications import router as notifications_router
from .chat import router as chat_router

__all__ = ["auth_router", "tasks_router", "notifications_router", "chat_router"]
