"""JWT authentication middleware."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "your-secret-key-here")
ALGORITHM = "HS256"

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> int:
    """
    Get current user from JWT token.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        User ID

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
