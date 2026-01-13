"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, EmailStr
from ..database import get_session
from ..models.user import User
from ..services.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


class SignUpRequest(BaseModel):
    """Sign up request schema."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8)


class SignInRequest(BaseModel):
    """Sign in request schema."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Authentication response schema."""
    id: int
    email: str
    name: str
    access_token: str
    token_type: str = "bearer"


@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignUpRequest,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Register a new user.

    Args:
        request: Sign up data
        session: Database session

    Returns:
        User data with access token
    """
    result = await AuthService.register_user(
        session,
        request.email,
        request.name,
        request.password,
        User
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error")
        )

    user = result["user"]
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "access_token": result["access_token"],
        "token_type": "bearer"
    }


@router.post("/signin", response_model=AuthResponse)
async def signin(
    request: SignInRequest,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Login a user.

    Args:
        request: Sign in data
        session: Database session

    Returns:
        User data with access token
    """
    result = await AuthService.login_user(
        session,
        request.email,
        request.password,
        User
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get("error")
        )

    user = result["user"]
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "access_token": result["access_token"],
        "token_type": "bearer"
    }


@router.post("/signout")
async def signout():
    """
    Sign out a user.

    Returns:
        Success message
    """
    return {
        "success": True,
        "message": "Signed out successfully"
    }
