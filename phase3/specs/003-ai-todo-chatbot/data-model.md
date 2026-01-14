# Data Model: AI-Powered Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Created**: 2026-01-14
**Status**: Complete

---

## Overview

Phase III adds two new tables to the existing database schema:
- `conversations` - Stores conversation sessions per user
- `messages` - Stores individual messages within conversations

Existing tables (`users`, `tasks`, `notifications`) remain unchanged.

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│   users     │       │  conversations   │       │  messages   │
├─────────────┤       ├──────────────────┤       ├─────────────┤
│ id (PK)     │──┐    │ id (PK, UUID)    │──┐    │ id (PK)     │
│ email       │  │    │ user_id (FK)     │◄─┘    │ conv_id(FK) │
│ name        │  └───►│ title            │       │ user_id     │
│ ...         │       │ created_at       │       │ role        │
└─────────────┘       │ updated_at       │◄──────│ content     │
       │              └──────────────────┘       │ tool_call_id│
       │                                         │ tool_name   │
       │              ┌──────────────────┐       │ created_at  │
       │              │     tasks        │       └─────────────┘
       └─────────────►│ (existing)       │
                      │ id, user_id, ... │
                      └──────────────────┘
```

---

## New Tables

### Table: `conversations`

Stores chat conversation sessions for each user. Single active thread per user.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique conversation identifier |
| `user_id` | VARCHAR(255) | NOT NULL, FOREIGN KEY → users.id | Owner of conversation |
| `title` | VARCHAR(200) | NULL | Auto-generated from first message (optional) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Conversation start time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message time |

**Indexes**:
- `idx_conversations_user_id` on `user_id` (for user's conversations lookup)
- `idx_conversations_updated` on `user_id, updated_at DESC` (for recent conversation)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    user_id: str = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### Table: `messages`

Stores individual messages within conversations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique message identifier |
| `conversation_id` | UUID | NOT NULL, FOREIGN KEY → conversations.id | Parent conversation |
| `user_id` | VARCHAR(255) | NOT NULL | Message owner (denormalized for isolation) |
| `role` | VARCHAR(20) | NOT NULL | Message type: "user", "assistant", "tool", "system" |
| `content` | TEXT | NOT NULL | Message text content |
| `tool_call_id` | VARCHAR(100) | NULL | ID for tool response correlation |
| `tool_name` | VARCHAR(100) | NULL | Name of tool called (for tool messages) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Message timestamp |

**Indexes**:
- `idx_messages_conv_user` on `conversation_id, user_id` (for conversation history)
- `idx_messages_created` on `conversation_id, created_at` (for ordering)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Index
from datetime import datetime
from typing import Optional

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True)  # Denormalized for data isolation
    role: str = Field(max_length=20)  # "user", "assistant", "tool", "system"
    content: str
    tool_call_id: Optional[str] = Field(default=None, max_length=100)
    tool_name: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("idx_messages_conv_user", "conversation_id", "user_id"),
        Index("idx_messages_created", "conversation_id", "created_at"),
    )
```

---

## Role Values

The `role` field in messages supports these values:

| Role | Description | Example |
|------|-------------|---------|
| `user` | Message from the user | "Add a task to buy milk" |
| `assistant` | Response from the AI agent | "Task 'Buy milk' added! ✅" |
| `tool` | Result from MCP tool execution | `{"success": true, "task_id": 5}` |
| `system` | System-level instructions | Agent instructions (optional) |

---

## Validation Rules

### Conversation Validation
- `user_id` MUST match authenticated user from JWT
- `title` is auto-generated from first user message (first 50 chars)
- `updated_at` MUST be updated on each new message

### Message Validation
- `conversation_id` MUST reference valid conversation owned by user
- `user_id` MUST match conversation's user_id (double check)
- `role` MUST be one of: "user", "assistant", "tool", "system"
- `content` MUST NOT be empty for user/assistant messages
- `tool_call_id` REQUIRED when role = "tool"
- `tool_name` REQUIRED when role = "tool"

---

## Query Patterns

### Get or Create Conversation for User
```python
async def get_or_create_conversation(session, user_id: str) -> Conversation:
    # Try to find existing conversation
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
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
```

### Load Message History (Limited)
```python
async def load_history(session, conversation_id: str, user_id: str, limit: int = 20) -> list[dict]:
    result = await session.execute(
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id  # Data isolation
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    # Reverse to chronological order
    return [
        {"role": m.role, "content": m.content}
        for m in reversed(messages)
    ]
```

### Save Message
```python
async def save_message(
    session,
    conversation_id: str,
    user_id: str,
    role: str,
    content: str,
    tool_call_id: str = None,
    tool_name: str = None
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
        tool_call_id=tool_call_id,
        tool_name=tool_name
    )
    session.add(message)

    # Update conversation timestamp
    await session.execute(
        update(Conversation)
        .where(Conversation.id == conversation_id)
        .values(updated_at=datetime.utcnow())
    )

    await session.commit()
    await session.refresh(message)
    return message
```

---

## Migration Script

```sql
-- Migration: Add conversations and messages tables for Phase III

-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated ON conversations(user_id, updated_at DESC);

-- Create messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_call_id VARCHAR(100),
    tool_name VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conv_user ON messages(conversation_id, user_id);
CREATE INDEX idx_messages_created ON messages(conversation_id, created_at);

-- Add CHECK constraint for role values
ALTER TABLE messages ADD CONSTRAINT chk_message_role
    CHECK (role IN ('user', 'assistant', 'tool', 'system'));
```

---

## Existing Tables (Unchanged)

The following tables from Phase II remain unchanged:

| Table | Purpose |
|-------|---------|
| `users` | User accounts (Better Auth managed) |
| `tasks` | Todo tasks with all features |
| `notifications` | Due date reminders |

MCP tools will query the `tasks` table using existing `TaskService` methods.

---

## Data Isolation Guarantees

1. **Conversation Level**: `user_id` on conversations ensures users only see their own
2. **Message Level**: `user_id` denormalized on messages for double-check
3. **Query Level**: All queries MUST filter by `user_id`
4. **API Level**: `user_id` extracted from JWT, validated against path parameter
