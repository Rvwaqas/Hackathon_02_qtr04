# Data Model: AI-Powered Todo Chatbot

**Purpose**: Define new database entities and relationships introduced for Phase III chatbot feature

**Status**: Proposal (Phase 1 design output)

## New Entities

### Conversation

Represents a chat session for an authenticated user.

**Storage**: PostgreSQL table `conversations`

**Fields**:
- `id` (UUID, Primary Key) — Unique conversation identifier
- `user_id` (String, Foreign Key to users.id) — Owner of conversation; used for isolation
- `created_at` (DateTime) — Timestamp when conversation started
- `updated_at` (DateTime) — Timestamp of last message
- `title` (String, Optional) — Auto-generated or user-set conversation title (e.g., "Grocery List" or "Friday Tasks")

**Indexes**:
- Primary: `id`
- Foreign Key: `user_id` (enable fast lookup of user's conversations)
- Compound: `(user_id, updated_at DESC)` (latest conversation for user)

**Validation**:
- `user_id`: required, non-empty string
- `created_at`, `updated_at`: required, valid timestamp
- `title`: optional, max 255 characters

**Relationships**:
- Belongs to: `User` (1:M from User perspective)
- Has many: `Message` (1:M)

---

### Message

Represents a single message (user input or assistant response) within a conversation.

**Storage**: PostgreSQL table `messages`

**Fields**:
- `id` (UUID, Primary Key) — Unique message identifier
- `conversation_id` (UUID, Foreign Key to conversations.id) — Parent conversation
- `role` (Enum: "user" | "assistant") — Who sent the message
- `content` (Text) — Message content (user question or assistant response)
- `created_at` (DateTime) — Timestamp when message was created
- `metadata` (JSON, Optional) — For future extensibility (tools used, tokens, etc.)

**Indexes**:
- Primary: `id`
- Foreign Key: `conversation_id`
- Compound: `(conversation_id, created_at ASC)` (load conversation history in order)

**Validation**:
- `conversation_id`: required, valid UUID, must exist in conversations
- `role`: required, enum only ("user" or "assistant")
- `content`: required, non-empty, max 10,000 characters
- `created_at`: required, valid timestamp
- `metadata`: optional, valid JSON

**Relationships**:
- Belongs to: `Conversation` (M:1)

---

## Entity Relationships

```
User (1) ──── (M) Conversation
              |
              └──── (M) Message
                    |
                    └── Each message has role (user/assistant)
                        and content from chat turn

Task (existing) ──── (M) User (existing)
                |
                └──── Referenced by agent via MCP tools
                      when user types task commands
```

**Key Relationship Pattern**:
- `Conversation.user_id` enforces data isolation
- `Message.conversation_id` ties messages to conversation
- Agent reads conversation history via conversation_id
- Agent calls MCP tools with user_id to ensure task access control

---

## Schema Migrations

### Migration 1: Create Conversations Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    title VARCHAR(255),
    UNIQUE(id)
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
```

### Migration 2: Create Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB,
    UNIQUE(id)
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at ASC);
```

---

## Data Flow

### User Sends Chat Message

1. **Request**: POST `/api/{user_id}/chat` with `{message, conversation_id?}`
2. **Load Conversation**:
   - If `conversation_id` provided: Load from `conversations` where `id = conversation_id AND user_id = {user_id}`
   - If not provided or not found: Create new conversation
3. **Load History**:
   - Query `messages` where `conversation_id = {conversation_id}` ordered by `created_at ASC`
   - Return ordered list to agent
4. **Save User Message**:
   - Insert into `messages`: `{conversation_id, role: "user", content: user_message, created_at: NOW()}`
5. **Run Agent**:
   - Pass conversation history to agent
   - Agent uses Cohere + MCP tools to generate response
6. **Save Assistant Response**:
   - Insert into `messages`: `{conversation_id, role: "assistant", content: assistant_response, created_at: NOW()}`
   - Update `conversations.updated_at = NOW()`
7. **Return Response**:
   - Return `{response, conversation_id}` to frontend

---

## State Transitions

### Conversation Lifecycle

```
[NEW] ──── User sends first message ──→ [ACTIVE]
 |
 └─────────────────────────────────────────┘
                                           │
                                           │ User closes chat
                                           │ (no state change; just UI closed)
                                           │
                                        [ACTIVE] ──┬→ User reopens chat
                                                   │   (reload from DB)
                                                   │
                                                   └→ Server restarts
                                                       (all conversations persist)
```

**Note**: Conversations persist indefinitely. No archival or deletion mechanism implemented (out of scope).

### Message State

Messages are **immutable** once created — no editing or deletion of past messages. This ensures conversation history accuracy.

---

## Indexes & Performance Considerations

**Read Queries** (frequent):
- `SELECT * FROM conversations WHERE user_id = ? AND id = ?` — Single conversation lookup → use index on (user_id, id)
- `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at` — Load conversation history → use index on (conversation_id, created_at)
- `SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1` — Latest conversation → use index on (user_id, updated_at DESC)

**Write Queries**:
- `INSERT INTO conversations (...)` — New conversation creation
- `INSERT INTO messages (...)` — New message logging

**Performance Targets**:
- Conversation lookup: <10ms
- History load (50 messages): <50ms
- Message insert: <5ms
- Conversation count per user expected: 1-10 (single thread model)

---

## Assumptions & Constraints

**Assumptions**:
- User_id from JWT is valid and references existing user
- Messages are write-once, never edited or deleted
- Single conversation thread per user (no multiple threads)
- Conversation history is fully loaded before agent execution (no streaming)

**Constraints**:
- Maximum message content size: 10,000 characters (allow long task descriptions + context)
- Maximum conversation history loaded: all messages (assume <1000 messages per user)
- No encryption of message content (trust PostgreSQL + TLS for transport)
- No soft deletes — CASCADE delete when user deleted

---

## Extension Points (Future)

The data model supports future enhancements:

1. **Conversation Tagging**: Add `tags` (JSONB) field to group conversations (e.g., "urgent", "personal")
2. **Message Metadata**: Expand `metadata` field to log tool usage, tokens consumed, latency
3. **Multi-thread Support**: Add `is_archived` flag to support multiple concurrent conversations
4. **Fine-grained Permissions**: Add `shared_with` field for conversation sharing (future user collaboration)
5. **Search/Analytics**: Add full-text index on `content` field for message search

---

