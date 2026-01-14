"""Message model for chat messages."""

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Text
from datetime import datetime
from typing import Optional, List, Dict, Any


class Message(SQLModel, table=True):
    """Message model for storing chat messages."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20, index=True)  # "user" or "assistant"
    content: str = Field(sa_column=Column(Text))
    tool_calls: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
