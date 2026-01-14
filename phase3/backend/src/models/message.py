"""Message model for AI chatbot."""

from sqlmodel import SQLModel, Field, Index
from datetime import datetime
from typing import Optional


class Message(SQLModel, table=True):
    """Message model for storing chat messages."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    user_id: int = Field(index=True)
    role: str = Field(max_length=20)  # "user", "assistant", "tool", "system"
    content: str
    tool_call_id: Optional[str] = Field(default=None, max_length=100)
    tool_name: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("idx_messages_conv_user", "conversation_id", "user_id"),
        Index("idx_messages_created", "conversation_id", "created_at"),
    )
