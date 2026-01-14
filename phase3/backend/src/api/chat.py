"""Chat API endpoint for AI chatbot."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any

from src.database import get_session
from src.middleware.jwt_auth import get_current_user_id
from src.services import ConversationService
from src.services.agent import get_agent

router = APIRouter(prefix="/api/users", tags=["Chat"])


class ChatRequest(BaseModel):
    """Chat request schema."""

    message: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema."""

    response: str
    conversation_id: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ConversationMessage(BaseModel):
    """Message in conversation history."""

    id: int
    role: str
    content: str
    created_at: str


class ConversationResponse(BaseModel):
    """Conversation with message history."""

    conversation_id: str
    title: Optional[str] = None
    messages: List[ConversationMessage]
    created_at: str
    updated_at: str


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    code: str
    details: Optional[Dict[str, Any]] = None


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def chat(
    user_id: int,
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Send a chat message to the AI todo assistant.

    The agent will understand intent, execute MCP tools if needed,
    and return a friendly response.
    """
    # Validate user_id matches JWT
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        # Get or create conversation
        conversation = await ConversationService.get_or_create_conversation(
            session=session,
            user_id=user_id,
            conversation_id=request.conversation_id
        )

        # Load conversation history
        history = await ConversationService.load_history(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id,
            limit=20
        )

        # Save user message
        await ConversationService.save_message(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=request.message
        )

        # Get agent and process message
        agent = get_agent()
        result = await agent.chat(
            session=session,
            user_id=user_id,
            message=request.message,
            history=history
        )

        # Save assistant response
        await ConversationService.save_message(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=result["response"]
        )

        # Update conversation title if it's the first message
        if not conversation.title and len(history) == 0:
            title = request.message[:50]
            await ConversationService.update_conversation_title(
                session=session,
                conversation_id=conversation.id,
                user_id=user_id,
                title=title
            )

        return ChatResponse(
            response=result["response"],
            conversation_id=conversation.id,
            tool_calls=result.get("tool_calls")
        )

    except ValueError as e:
        # Configuration errors (e.g., missing API key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        # General errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong. Please try again."
        )


@router.get(
    "/{user_id}/conversations",
    response_model=ConversationResponse,
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    }
)
async def get_conversation(
    user_id: int,
    limit: int = 20,
    current_user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session)
):
    """
    Get conversation history.

    Returns the most recent conversation for the user with message history.
    """
    # Validate user_id matches JWT
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Limit validation
    if limit < 1:
        limit = 1
    elif limit > 50:
        limit = 50

    try:
        # Get most recent conversation
        conversation = await ConversationService.get_or_create_conversation(
            session=session,
            user_id=user_id
        )

        # Load messages
        from sqlmodel import select
        from src.models import Message

        result = await session.execute(
            select(Message)
            .where(
                Message.conversation_id == conversation.id,
                Message.user_id == user_id
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()

        # Format messages (reverse to chronological order)
        formatted_messages = [
            ConversationMessage(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at.isoformat()
            )
            for m in reversed(messages)
        ]

        return ConversationResponse(
            conversation_id=conversation.id,
            title=conversation.title,
            messages=formatted_messages,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load conversation"
        )
