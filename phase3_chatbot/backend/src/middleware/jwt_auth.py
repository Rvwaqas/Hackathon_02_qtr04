"""JWT authentication middleware."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.services import AuthService
from src.models import User

security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """
    Get current user ID from JWT token.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        int: User ID

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    user_id = AuthService.decode_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Get current user from JWT token.

    Args:
        user_id: User ID from token
        session: Database session

    Returns:
        User: Current user

    Raises:
        HTTPException: If user not found
    """
    user = await AuthService.get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
