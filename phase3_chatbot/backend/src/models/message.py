"""Message model for storing chat messages."""

from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4

from sqlalchemy import JSON
from sqlmodel import SQLModel, Field


class Message(SQLModel, table=True):
    """Represents a single message in a conversation."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(index=True, foreign_key="conversation.id")
    role: str = Field(index=True)  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    msg_metadata: Optional[dict] = Field(default=None, sa_type=JSON)  # JSON field for extensibility

    class Config:
        """SQLModel config."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Add a task to buy groceries tomorrow",
                "created_at": "2026-01-15T10:05:00",
                "metadata": None,
            }
        }
