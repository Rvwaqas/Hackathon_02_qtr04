"""Authentication service."""

from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.config import settings
from src.models import User
from src.schemas import SignupRequest, SigninRequest


class AuthService:
    """Authentication service with JWT."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password (bcrypt truncates to 72 bytes)."""
        # Bcrypt has a 72 byte limit, truncate password
        password_bytes = password.encode('utf-8')[:72]
        return cls.pwd_context.hash(password_bytes.decode('utf-8'))

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(cls, user_id: int) -> str:
        """Create a JWT access token."""
        expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRATION_DAYS)
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @classmethod
    def decode_access_token(cls, token: str) -> Optional[int]:
        """Decode a JWT access token and return user_id."""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return int(user_id)
        except JWTError:
            return None

    @classmethod
    async def signup(cls, session: AsyncSession, data: SignupRequest) -> User:
        """Register a new user."""
        # Check if email already exists
        result = await session.execute(
            select(User).where(User.email == data.email)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValueError("Email already registered")

        # Create new user
        hashed_password = cls.hash_password(data.password)
        user = User(
            email=data.email,
            name=data.name,
            password_hash=hashed_password,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def signin(cls, session: AsyncSession, data: SigninRequest) -> Optional[User]:
        """Authenticate a user."""
        result = await session.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()

        if not user or not cls.verify_password(data.password, user.password_hash):
            return None

        return user

    @classmethod
    async def get_user_by_id(cls, session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
