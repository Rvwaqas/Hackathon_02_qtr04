# Data Model: Todo AI Chatbot Integration

**Feature**: `003-ai-chatbot-mcp`
**Date**: 2026-01-13

## Entity Relationship Diagram

```
┌─────────────┐       ┌───────────────────┐       ┌─────────────────┐
│    users    │       │   conversations   │       │    messages     │
├─────────────┤       ├───────────────────┤       ├─────────────────┤
│ id (PK)     │──┐    │ id (PK)           │──┐    │ id (PK)         │
│ email       │  │    │ user_id (FK)      │◄─┘    │ conversation_id │
│ name        │  │    │ created_at        │       │    (FK)         │
│ password_   │  └───►│ updated_at        │       │ user_id (FK)    │
│   hash      │       └───────────────────┘       │ role            │
│ created_at  │                                   │ content         │
│ updated_at  │                                   │ created_at      │
└─────────────┘                                   └─────────────────┘
       │
       │        ┌─────────────────┐
       └───────►│     tasks       │  (existing Phase 2)
                ├─────────────────┤
                │ id (PK)         │
                │ user_id (FK)    │
                │ title           │
                │ description     │
                │ completed       │
                │ priority        │
                │ tags            │
                │ ...             │
                └─────────────────┘
```

## New Tables (Phase 3)

### conversations

Represents a chat session between a user and the AI assistant.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique conversation identifier |
| user_id | INTEGER | NOT NULL, FK → users.id | Owner of the conversation |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When conversation started |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp |

**Indexes**:
- `ix_conversations_user_id` on `user_id` (frequent lookup by user)
- `ix_conversations_updated_at` on `updated_at` (sort by recent)

**SQLModel Definition**:
```python
class Conversation(SQLModel, table=True):
    """Chat conversation session."""

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

---

### messages

Stores individual messages within a conversation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique message identifier |
| conversation_id | INTEGER | NOT NULL, FK → conversations.id | Parent conversation |
| user_id | INTEGER | NOT NULL, FK → users.id | Owner (denormalized for access control) |
| role | VARCHAR(20) | NOT NULL, CHECK IN ('user', 'assistant') | Message sender type |
| content | TEXT | NOT NULL | Message text content |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When message was sent |

**Indexes**:
- `ix_messages_conversation_id` on `conversation_id` (load conversation history)
- `ix_messages_user_id` on `user_id` (ownership validation)
- `ix_messages_created_at` on `created_at` (chronological ordering)

**SQLModel Definition**:
```python
class Message(SQLModel, table=True):
    """Individual chat message."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

---

## Existing Tables (Phase 2 - No Changes)

### users

| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PRIMARY KEY |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| name | VARCHAR(255) | NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

### tasks

| Column | Type | Constraints |
|--------|------|-------------|
| id | SERIAL | PRIMARY KEY |
| user_id | INTEGER | FK → users.id |
| title | VARCHAR(200) | NOT NULL |
| description | VARCHAR(2000) | |
| completed | BOOLEAN | DEFAULT FALSE |
| priority | VARCHAR(20) | DEFAULT 'none' |
| tags | JSON | DEFAULT [] |
| recurrence | JSON | |
| due_date | TIMESTAMP | |
| reminder_offset_minutes | INTEGER | |
| parent_task_id | INTEGER | FK → tasks.id |
| created_at | TIMESTAMP | DEFAULT NOW() |
| updated_at | TIMESTAMP | DEFAULT NOW() |

---

## Validation Rules

### Conversation

| Field | Rule |
|-------|------|
| user_id | Must exist in users table |
| created_at | Auto-set on creation, immutable |
| updated_at | Auto-updated on new message |

### Message

| Field | Rule |
|-------|------|
| conversation_id | Must exist and belong to user |
| user_id | Must match conversation owner |
| role | Must be 'user' or 'assistant' |
| content | Max 10000 characters (accommodates AI responses) |
| created_at | Auto-set, immutable |

---

## Query Patterns

### Load Conversation History (20 messages)

```sql
SELECT id, role, content, created_at
FROM messages
WHERE conversation_id = :conversation_id
  AND user_id = :user_id
ORDER BY created_at DESC
LIMIT 20;
```

### Get User's Most Recent Conversation

```sql
SELECT id, created_at, updated_at
FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 1;
```

### Create New Conversation

```sql
INSERT INTO conversations (user_id, created_at, updated_at)
VALUES (:user_id, NOW(), NOW())
RETURNING id;
```

### Save Message

```sql
INSERT INTO messages (conversation_id, user_id, role, content, created_at)
VALUES (:conversation_id, :user_id, :role, :content, NOW());

UPDATE conversations
SET updated_at = NOW()
WHERE id = :conversation_id;
```

---

## Migration Script

```sql
-- Phase 3: AI Chatbot Tables

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS ix_conversations_updated_at ON conversations(updated_at);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS ix_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS ix_messages_created_at ON messages(created_at);
```

---

## Data Retention

- **Conversations**: Retained indefinitely (user data)
- **Messages**: Retained indefinitely (audit trail)
- **Context window**: Last 20 messages loaded per request (performance)
- **Cleanup**: No automatic deletion (user can delete via future feature)
