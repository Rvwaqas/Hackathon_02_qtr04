"""Conversation service for managing chat history."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from src.models.conversation import Conversation
from src.models.message import Message
from typing import List, Optional, Dict, Any
from datetime import datetime


class ConversationService:
    """Service for managing conversations and messages."""

    @staticmethod
    async def create_conversation(
        session: AsyncSession,
        user_id: int,
        title: str = "New Conversation"
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            session: Database session
            user_id: User ID
            title: Conversation title

        Returns:
            Created conversation
        """
        conversation = Conversation(
            user_id=user_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

    @staticmethod
    async def get_conversation(
        session: AsyncSession,
        conversation_id: int,
        user_id: int
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID, ensuring user ownership.

        Args:
            session: Database session
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            Conversation if found and owned by user, None otherwise
        """
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_messages(
        session: AsyncSession,
        conversation_id: int,
        limit: int = 20
    ) -> List[Message]:
        """
        Get messages from a conversation.

        Args:
            session: Database session
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages (most recent first, then reversed for chronological order)
        """
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        messages = list(result.scalars().all())
        # Reverse to get chronological order (oldest first)
        return list(reversed(messages))

    @staticmethod
    async def add_message(
        session: AsyncSession,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            session: Database session
            conversation_id: Conversation ID
            role: Message role ("user" or "assistant")
            content: Message content
            tool_calls: List of tool names that were called
            metadata: Additional metadata

        Returns:
            Created message
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            metadata=metadata,
            created_at=datetime.utcnow()
        )
        session.add(message)

        # Update conversation's updated_at timestamp
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(stmt)
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)

        await session.commit()
        await session.refresh(message)
        return message

    @staticmethod
    async def update_conversation_title(
        session: AsyncSession,
        conversation_id: int,
        user_id: int,
        title: str
    ) -> Optional[Conversation]:
        """
        Update conversation title.

        Args:
            session: Database session
            conversation_id: Conversation ID
            user_id: User ID (for ownership validation)
            title: New title

        Returns:
            Updated conversation or None if not found
        """
        conversation = await ConversationService.get_conversation(
            session, conversation_id, user_id
        )
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
        return conversation

    @staticmethod
    async def list_user_conversations(
        session: AsyncSession,
        user_id: int,
        limit: int = 50
    ) -> List[Conversation]:
        """
        List all conversations for a user.

        Args:
            session: Database session
            user_id: User ID
            limit: Maximum number of conversations to retrieve

        Returns:
            List of conversations (most recent first)
        """
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
