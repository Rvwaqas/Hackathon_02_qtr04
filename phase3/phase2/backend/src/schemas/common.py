"""Common schemas."""

from typing import Any, Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    data: Optional[Any] = None
    status_code: int = 400

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Task not found",
                "data": None,
                "status_code": 404
            }
        }


class SuccessResponse(BaseModel):
    """Success response schema."""

    success: bool = True
    data: Any
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "title": "Buy groceries"},
                "message": "Task created successfully"
            }
        }
