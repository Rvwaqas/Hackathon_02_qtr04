"""Chat API endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
from src.database import get_session
from src.agents import get_openai_client, MainOrchestrator
from jose import jwt, JWTError
import os

router = APIRouter(prefix="/api", tags=["chat"])

# JWT configuration (matching phase2 backend)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-minimum-32-characters-for-development-only")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str = Field(..., description="User message", min_length=1)
    conversation_id: Optional[int] = Field(None, description="Conversation ID (optional)")


class ChatResponse(BaseModel):
    """Chat response schema."""
    conversation_id: int = Field(..., description="Conversation ID")
    response: str = Field(..., description="Assistant response")
    tool_calls: List[str] = Field(default_factory=list, description="Tools that were called")
    success: bool = Field(..., description="Success status")


def verify_token(authorization: str = Header(...)) -> int:
    """
    Verify JWT token and extract user_id.

    Args:
        authorization: Authorization header (Bearer TOKEN)

    Returns:
        User ID from token

    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Extract token from "Bearer TOKEN"
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization.replace("Bearer ", "")

        # Decode JWT
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return user_id

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: int,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    token_user_id: int = Depends(verify_token)
):
    """
    Chat endpoint for natural language task management.

    Args:
        user_id: User ID from path
        request: Chat request with message and optional conversation_id
        session: Database session
        token_user_id: User ID from JWT token

    Returns:
        ChatResponse with assistant response and metadata

    Raises:
        HTTPException: If user_id doesn't match token or other errors occur
    """
    # Verify user_id matches token
    if user_id != token_user_id:
        raise HTTPException(
            status_code=403,
            detail="User ID does not match authentication token"
        )

    try:
        # Initialize OpenAI client
        openai_client = get_openai_client()

        # Initialize orchestrator
        orchestrator = MainOrchestrator(
            session=session,
            openai_client=openai_client
        )

        # Process message through agent pipeline
        result = await orchestrator.process_message(
            user_message=request.message,
            user_id=user_id,
            conversation_id=request.conversation_id
        )

        return ChatResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            tool_calls=result["tool_calls"],
            success=result["success"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/{user_id}/conversations")
async def list_conversations(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    token_user_id: int = Depends(verify_token)
):
    """
    List all conversations for a user.

    Args:
        user_id: User ID from path
        session: Database session
        token_user_id: User ID from JWT token

    Returns:
        List of conversations

    Raises:
        HTTPException: If user_id doesn't match token
    """
    # Verify user_id matches token
    if user_id != token_user_id:
        raise HTTPException(
            status_code=403,
            detail="User ID does not match authentication token"
        )

    try:
        from src.services.conversation import ConversationService

        conversations = await ConversationService.list_user_conversations(
            session=session,
            user_id=user_id,
            limit=50
        )

        return {
            "conversations": [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list conversations: {str(e)}"
        )
