"""Service for managing conversations and messages."""

from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation
from src.models.message import Message


class ConversationService:
    """Service for conversation and message operations."""

    @classmethod
    async def create_conversation(
        cls,
        session: AsyncSession,
        user_id: str,
        title: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(user_id=user_id, title=title)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

    @classmethod
    async def get_conversation(
        cls,
        session: AsyncSession,
        conversation_id: UUID,
        user_id: str
    ) -> Optional[Conversation]:
        """Get conversation by ID and verify ownership."""
        statement = select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        result = await session.execute(statement)
        return result.scalars().first()

    @classmethod
    async def get_user_conversations(
        cls,
        session: AsyncSession,
        user_id: str,
        limit: int = 10
    ) -> list[Conversation]:
        """Get recent conversations for a user."""
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        return result.scalars().all()

    @classmethod
    async def add_message(
        cls,
        session: AsyncSession,
        conversation_id: UUID,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            msg_metadata=metadata
        )
        session.add(message)

        # Update conversation updated_at timestamp
        statement = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(statement)
        conversation = result.scalars().first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)

        await session.commit()
        await session.refresh(message)
        return message

    @classmethod
    async def get_messages(
        cls,
        session: AsyncSession,
        conversation_id: UUID
    ) -> list[Message]:
        """Get all messages in a conversation, ordered by created_at."""
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        result = await session.execute(statement)
        return result.scalars().all()

    @classmethod
    async def get_recent_messages(
        cls,
        session: AsyncSession,
        conversation_id: UUID,
        limit: int = 50
    ) -> list[Message]:
        """Get recent messages from a conversation, in chronological order."""
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order

    @classmethod
    async def delete_conversation(
        cls,
        session: AsyncSession,
        conversation_id: UUID,
        user_id: str
    ) -> bool:
        """Delete a conversation (cascades to messages)."""
        conversation = await cls.get_conversation(session, conversation_id, user_id)
        if not conversation:
            return False

        await session.delete(conversation)
        await session.commit()
        return True
