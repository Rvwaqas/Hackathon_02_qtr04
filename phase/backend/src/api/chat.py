"""Chat API endpoints for AI-powered todo chatbot."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

from src.database import get_session
from src.middleware import get_current_user_id
from src.schemas import ChatRequest, ChatResponse
from src.services import ConversationService
from src.agents import TodoAgent

router = APIRouter(prefix="/api", tags=["Chat"])


class MessageResponse(BaseModel):
    """Single message in conversation."""
    role: str
    content: str
    created_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class ConversationListResponse(BaseModel):
    """Conversation in user's conversation list."""
    id: str
    title: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Grocery shopping tasks",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class ConversationDetailResponse(BaseModel):
    """Full conversation with message history."""
    id: str
    title: Optional[str]
    messages: List[MessageResponse]
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": None,
                "messages": [
                    {"role": "user", "content": "Add groceries", "created_at": "2024-01-15T10:30:00Z"},
                    {"role": "assistant", "content": "Done! [COMPLETED]", "created_at": "2024-01-15T10:30:01Z"}
                ],
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:30:01Z"
            }
        }


@router.post("/{user_id}/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    user_id: int,
    data: ChatRequest,
    session: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Send a message to the AI todo chatbot.

    - **user_id**: User ID from path (must match authenticated user)
    - **data**: ChatRequest with message and optional conversation_id
    - **Returns**: ChatResponse with agent response and conversation ID
    """
    # Verify user is accessing their own conversations
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' conversations"
        )

    try:
        if data.conversation_id:
            # Load existing conversation
            try:
                conv_uuid = UUID(data.conversation_id)
                conversation = await ConversationService.get_conversation(
                    session, conv_uuid, str(user_id)
                )
                if not conversation:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Conversation not found"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation ID format"
                )
        else:
            # Create new conversation
            conversation = await ConversationService.create_conversation(
                session, str(user_id), title=None
            )

        # Load message history (last 20 messages in chronological order)
        messages_list = await ConversationService.get_recent_messages(
            session, conversation.id, limit=20
        )

        # Convert messages to chat format for agent context
        chat_history = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages_list
        ]

        # Execute agent with conversation history
        agent = TodoAgent(session, str(user_id))
        agent_response = await agent.execute(
            user_message=data.message,
            conversation_history=chat_history
        )

        # Save user message to conversation
        await ConversationService.add_message(
            session,
            conversation.id,
            role="user",
            content=data.message,
            metadata={"source": "api"}
        )

        # Save agent response to conversation
        await ConversationService.add_message(
            session,
            conversation.id,
            role="assistant",
            content=agent_response,
            metadata={"source": "agent"}
        )

        return ChatResponse(
            conversation_id=str(conversation.id),
            message=agent_response,
            role="assistant"
        )

    except HTTPException:
        raise
    except Exception as e:
        # Safely encode error message to handle non-ASCII characters
        error_message = str(e).encode('utf-8', errors='replace').decode('utf-8')
        print(f"Chat execution failed: {error_message}".encode('utf-8', errors='replace').decode('utf-8'))  # Safe print
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat execution failed: {error_message}"
        )


@router.get("/{user_id}/conversations", response_model=List[ConversationListResponse])
async def get_conversations(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get list of conversations for the authenticated user.

    - **user_id**: User ID from path (must match authenticated user)
    - **Returns**: List of conversations with metadata (no messages)
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' conversations"
        )

    try:
        conversations = await ConversationService.get_user_conversations(
            session, str(user_id), limit=50
        )

        return [
            ConversationListResponse(
                id=str(conv.id),
                title=conv.title,
                created_at=conv.created_at.isoformat() if conv.created_at else "",
                updated_at=conv.updated_at.isoformat() if conv.updated_at else ""
            )
            for conv in conversations
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversations: {str(e)}"
        )


@router.get("/{user_id}/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    user_id: int,
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Get full conversation with message history.

    - **user_id**: User ID from path (must match authenticated user)
    - **conversation_id**: ID of conversation to retrieve
    - **Returns**: Conversation with all messages in chronological order
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' conversations"
        )

    try:
        conv_uuid = UUID(conversation_id)
        conversation = await ConversationService.get_conversation(
            session, conv_uuid, str(user_id)
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get all messages in chronological order
        messages = await ConversationService.get_messages(session, conv_uuid)

        return ConversationDetailResponse(
            id=str(conversation.id),
            title=conversation.title,
            messages=[
                MessageResponse(
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at.isoformat() if msg.created_at else ""
                )
                for msg in messages
            ],
            created_at=conversation.created_at.isoformat() if conversation.created_at else "",
            updated_at=conversation.updated_at.isoformat() if conversation.updated_at else ""
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation: {str(e)}"
        )


@router.delete("/{user_id}/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    user_id: int,
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Delete a conversation and all its messages.

    - **user_id**: User ID from path (must match authenticated user)
    - **conversation_id**: ID of conversation to delete
    - **Returns**: 204 No Content on success
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other users' conversations"
        )

    try:
        conv_uuid = UUID(conversation_id)
        result = await ConversationService.delete_conversation(
            session, conv_uuid, str(user_id)
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        )
