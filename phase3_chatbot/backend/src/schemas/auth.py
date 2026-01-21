"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class SignupRequest(BaseModel):
    """Signup request schema."""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)


class SigninRequest(BaseModel):
    """Signin request schema."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
