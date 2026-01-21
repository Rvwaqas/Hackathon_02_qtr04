"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.services import AuthService
from src.schemas import SignupRequest, SigninRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    data: SignupRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Register a new user.

    Args:
        data: Signup request data
        session: Database session

    Returns:
        TokenResponse: JWT token and user data

    Raises:
        HTTPException: If email already exists
    """
    try:
        user = await AuthService.signup(session, data)
        access_token = AuthService.create_access_token(user.id)

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(user),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/signin", response_model=TokenResponse)
async def signin(
    data: SigninRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Sign in a user.

    Args:
        data: Signin request data
        session: Database session

    Returns:
        TokenResponse: JWT token and user data

    Raises:
        HTTPException: If credentials are invalid
    """
    user = await AuthService.signin(session, data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = AuthService.create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/signout")
async def signout():
    """
    Sign out a user (client-side token removal).

    Returns:
        dict: Success message
    """
    return {"message": "Signed out successfully"}
