"""Common schemas."""

from pydantic import BaseModel
from typing import Optional, Any


class ErrorDetail(BaseModel):
    """Error detail schema."""

    message: str
    code: str


class ErrorResponse(BaseModel):
    """Standard error response."""

    data: None = None
    error: ErrorDetail


class SuccessResponse(BaseModel):
    """Standard success response."""

    data: Any
    error: None = None
