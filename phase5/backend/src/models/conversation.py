"""Conversation model for storing chat sessions."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class Conversation(SQLModel, table=True):
    """Represents a chat session for an authenticated user."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)  # Removed foreign key - auth system uses email as user_id
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    title: Optional[str] = Field(default=None, max_length=255)

    class Config:
        """SQLModel config."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-123",
                "created_at": "2026-01-15T10:00:00",
                "updated_at": "2026-01-15T10:30:00",
                "title": "Grocery Tasks",
            }
        }
