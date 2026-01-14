"""Conversation model for chat history."""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Conversation(SQLModel, table=True):
    """Conversation model to group related messages."""

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default="New Conversation", max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
