"""Chat API endpoint for AI Chatbot - Stateless with DB persistence."""

from typing import List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_session
from src.middleware.jwt_auth import get_current_user
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.services.agent import get_agent


router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request model."""
    conversation_id: Optional[int] = None
    message: str


class ToolCall(BaseModel):
    """Tool call model."""
    name: str
    arguments: dict


class ChatResponse(BaseModel):
    """Chat response model."""
    conversation_id: int
    response: str
    tool_calls: List[Any] = []


async def get_or_create_conversation(
    session: AsyncSession,
    user_id: int,
    conversation_id: Optional[int] = None
) -> Conversation:
    """Get existing conversation or create a new one."""
    if conversation_id:
        # Try to find existing conversation
        result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            return conversation

    # Create new conversation
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


async def get_conversation_history(
    session: AsyncSession,
    conversation_id: int,
    limit: int = 20
) -> List[dict]:
    """Fetch conversation history from database."""
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    # Reverse to get chronological order
    return [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(messages)
    ]


async def save_message(
    session: AsyncSession,
    conversation_id: int,
    user_id: int,
    role: str,
    content: str
) -> Message:
    """Save a message to the database."""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )
    session.add(message)
    await session.commit()
    return message


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def send_message(
    user_id: int,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Send a message to the AI chatbot.

    Stateless endpoint that:
    1. Receives user message
    2. Fetches conversation history from database
    3. Stores user message in database
    4. Runs agent with MCP tools
    5. Stores assistant response in database
    6. Returns response to client
    """
    # Verify user_id matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        # Step 1: Get or create conversation
        conversation = await get_or_create_conversation(
            session, user_id, request.conversation_id
        )

        # Step 2: Fetch conversation history from database
        history = await get_conversation_history(session, conversation.id)

        # Step 3: Store user message in database
        await save_message(
            session, conversation.id, user_id, "user", request.message
        )

        # Step 4: Run agent with MCP tools
        agent = get_agent()
        result = await agent.chat(
            user_id=user_id,
            message=request.message,
            session=session,
            conversation_history=history
        )

        # Step 5: Store assistant response in database
        await save_message(
            session, conversation.id, user_id, "assistant", result["response"]
        )

        # Step 6: Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        await session.commit()

        # Return response
        return ChatResponse(
            conversation_id=conversation.id,
            response=result["response"],
            tool_calls=result.get("tool_calls", [])
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(e)}"
        )


@router.get("/{user_id}/conversations")
async def get_conversations(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all conversations for a user."""
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    return [
        {
            "id": c.id,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat()
        }
        for c in conversations
    ]


@router.get("/{user_id}/conversations/{conversation_id}/messages")
async def get_messages(
    user_id: int,
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get messages for a conversation."""
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Verify conversation belongs to user
    result = await session.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    history = await get_conversation_history(session, conversation_id, limit=100)
    return {"messages": history}
