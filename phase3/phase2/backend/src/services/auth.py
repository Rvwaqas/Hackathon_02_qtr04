"""Authentication service."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlmodel import SQLModel
from jose import jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    @staticmethod
    async def register_user(
        session: AsyncSession,
        email: str,
        name: str,
        password: str,
        User: type
    ) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            session: Database session
            email: User email
            name: User name
            password: User password (plain text)
            User: User model class

        Returns:
            Dict with user data and access token
        """
        # Check if user already exists
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            return {
                "success": False,
                "error": "Email already registered"
            }

        # Create new user
        hashed_password = AuthService.hash_password(password)
        user = User(
            email=email,
            name=name,
            password_hash=hashed_password
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Create access token
        access_token = AuthService.create_access_token({"sub": user.id})

        return {
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            },
            "access_token": access_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def login_user(
        session: AsyncSession,
        email: str,
        password: str,
        User: type
    ) -> Dict[str, Any]:
        """
        Login a user.

        Args:
            session: Database session
            email: User email
            password: User password (plain text)
            User: User model class

        Returns:
            Dict with user data and access token
        """
        # Find user by email
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return {
                "success": False,
                "error": "Invalid email or password"
            }

        # Verify password
        if not AuthService.verify_password(password, user.password_hash):
            return {
                "success": False,
                "error": "Invalid email or password"
            }

        # Create access token
        access_token = AuthService.create_access_token({"sub": user.id})

        return {
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
