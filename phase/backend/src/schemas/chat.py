"""Chat API request/response schemas."""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class ChatRequest(BaseModel):
    """Request for chat endpoint."""

    message: str
    conversation_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add a task to buy groceries",
                "conversation_id": None
            }
        }


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    conversation_id: str
    message: str
    role: str = "assistant"

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "Task 'buy groceries' added! [COMPLETED]",
                "role": "assistant"
            }
        }
