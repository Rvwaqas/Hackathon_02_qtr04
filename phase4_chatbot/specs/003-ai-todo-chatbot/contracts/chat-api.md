# API Contract: Chat Endpoint

**Endpoint**: `POST /api/{user_id}/chat`

**Purpose**: Accept user messages, execute agent reasoning with Cohere LLM and MCP tools, and return assistant response

**Authentication**: Required — JWT token via Authorization header or cookie (Better Auth)

**Status**: Proposal (Phase 1 design output)

---

## Request

### URL Parameters

- `{user_id}` (path, string, required) — ID of authenticated user (from JWT payload)

### Headers

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Body

```json
{
  "message": "Add a task to buy groceries tomorrow",
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

**Field Descriptions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | ✅ yes | User's natural language input (max 10,000 characters) |
| `conversation_id` | string (UUID) | ❌ no | ID of existing conversation; if omitted, create new |

### Request Validation

- `message`: Required, non-empty, max 10,000 characters
- `conversation_id` (if provided): Must be valid UUID format and belong to authenticated `user_id`
- `user_id` (path): Must match JWT subject claim

---

## Response (Success)

**Status Code**: `200 OK`

```json
{
  "response": "Task 'Buy groceries tomorrow' added! ✅",
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message_id": "a1b2c3d4-e5f6-4789-abcd-ef1234567890"
}
```

**Field Descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | Assistant's natural language response (friendly, includes action confirmation) |
| `conversation_id` | string | ID of conversation (same as request or newly created) |
| `message_id` | string | ID of the assistant's message (for future reference) |

### Response Validation

- `response`: Non-empty string, max 5,000 characters (assistant's answer)
- `conversation_id`: Valid UUID, matches request or newly generated
- `message_id`: Valid UUID

---

## Response (Error)

### 400 Bad Request

Invalid input format

```json
{
  "error": "validation_error",
  "message": "message field is required",
  "details": {
    "field": "message",
    "reason": "empty_string"
  }
}
```

### 401 Unauthorized

Missing or invalid JWT token

```json
{
  "error": "unauthorized",
  "message": "Invalid or missing authentication token"
}
```

### 404 Not Found

Conversation does not exist or belongs to different user

```json
{
  "error": "not_found",
  "message": "Conversation f47ac10b-... not found",
  "conversation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

### 500 Internal Server Error

Unexpected server error (Cohere API failure, database error, etc.)

```json
{
  "error": "internal_error",
  "message": "I'm having trouble thinking right now. Please try again.",
  "request_id": "req-1234567890"
}
```

---

## Behavior Specifications

### Conversation Lifecycle

1. **First Message** (`conversation_id` omitted or invalid):
   - Create new conversation: `INSERT INTO conversations (user_id, created_at, updated_at)`
   - Return new `conversation_id`

2. **Subsequent Messages** (valid `conversation_id`):
   - Load conversation: `SELECT * FROM conversations WHERE id = ? AND user_id = ?`
   - If not found: return 404
   - If found: continue with agent execution

### Agent Execution Flow

1. **Load Conversation History**:
   - `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC`
   - Format as: `[{role: "user", content: "..."}, {role: "assistant", content: "..."}]`

2. **Save User Message**:
   - `INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, "user", ?, NOW())`

3. **Execute Agent**:
   - Initialize Cohere client: `AsyncOpenAI(api_key=COHERE_API_KEY, base_url="https://api.cohere.com/v1")`
   - Model: `"command-r-plus"` (or latest available)
   - Messages: include conversation history + new user message
   - Tools: MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)
   - Instructions: "You are a friendly todo assistant. Always confirm actions. Use tools when needed."
   - Wait for agent completion (timeout: 30 seconds)

4. **Save Assistant Response**:
   - `INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, "assistant", ?, NOW())`
   - `UPDATE conversations SET updated_at = NOW() WHERE id = ?`

5. **Return Response**:
   - Extract response text from agent output
   - Include `conversation_id` and new message `message_id`

### Error Handling

| Error Scenario | Behavior |
|----------------|----------|
| User not found | Return 401 Unauthorized |
| Conversation not found | Return 404 Not Found |
| Message validation fails | Return 400 Bad Request |
| Agent timeout (>30s) | Return 500 with message: "Agent took too long. Please try again." |
| Cohere API error | Return 500 with message: "I'm having trouble thinking right now. Please try again." |
| Database error | Return 500 with message: "I'm having trouble accessing your tasks. Please try again." |
| Invalid tool call | Agent catches error; responds naturally: "I couldn't find that task..." |

### Rate Limiting (Optional)

Recommended but not required for MVP:
- Per user: 10 messages/minute
- Per IP: 100 messages/minute
- Return 429 Too Many Requests if exceeded

---

## Example Workflows

### Workflow 1: Add Task

```
REQUEST:
POST /api/user-123/chat
{
  "message": "Add a task to call mom tonight"
}

AGENT EXECUTION:
1. Load conversation history: empty (first message)
2. Save user message to DB
3. Execute agent with Cohere
   - Agent understands intent: "create task"
   - Calls MCP tool: add_task(user_id="user-123", title="Call mom tonight")
   - Task created with ID 42
4. Save assistant response: "Task 'Call mom tonight' added! ✅"
5. Return response

RESPONSE:
{
  "response": "Task 'Call mom tonight' added! ✅",
  "conversation_id": "abc-123",
  "message_id": "msg-001"
}
```

### Workflow 2: List Pending Tasks

```
REQUEST:
POST /api/user-123/chat
{
  "message": "Show me my pending tasks",
  "conversation_id": "abc-123"
}

AGENT EXECUTION:
1. Load conversation history: [user msg 1, assistant msg 1, ...]
2. Save user message to DB
3. Execute agent with Cohere
   - Agent understands intent: "list pending tasks"
   - Calls MCP tool: list_tasks(user_id="user-123", status="pending")
   - Retrieves 3 pending tasks
4. Save assistant response with formatted task list:
   "Here are your pending tasks:
   1. Call mom tonight
   2. Buy groceries
   3. Review PR"
5. Return response

RESPONSE:
{
  "response": "Here are your pending tasks:\n1. Call mom tonight\n2. Buy groceries\n3. Review PR",
  "conversation_id": "abc-123",
  "message_id": "msg-002"
}
```

### Workflow 3: Error - Task Not Found

```
REQUEST:
POST /api/user-123/chat
{
  "message": "Mark task 999 as complete",
  "conversation_id": "abc-123"
}

AGENT EXECUTION:
1. Load conversation history
2. Save user message
3. Execute agent with Cohere
   - Agent tries: complete_task(user_id="user-123", task_id="999")
   - Tool returns error: "Task not found"
   - Agent handles gracefully
4. Save assistant response: "I couldn't find task 999 in your pending tasks. Would you like me to list your tasks?"
5. Return response

RESPONSE:
{
  "response": "I couldn't find task 999 in your pending tasks. Would you like me to list your tasks?",
  "conversation_id": "abc-123",
  "message_id": "msg-003"
}
```

---

## Implementation Notes

### Idempotency

The endpoint is **not idempotent** by design:
- Each message is saved as a new message record
- Duplicate requests create duplicate messages
- Consider adding `idempotency_key` header support in future (out of scope for MVP)

### Timeouts

- **Request timeout**: 30 seconds (agent execution may take 5-10s due to Cohere API latency)
- **Database timeout**: 5 seconds
- **Cohere API timeout**: 20 seconds (handled by AsyncOpenAI client)

### Concurrency

- Multiple requests from same user are processed independently
- Database serialization ensures message order
- No locks or synchronization needed (stateless design)

### Logging

Every request should log:
- `timestamp`, `user_id`, `conversation_id`, `message` (first 100 chars)
- `response` (first 100 chars), `agent_tokens_used`, `latency_ms`
- Any errors or MCP tool calls

---

## Future Enhancements (Out of Scope)

- Streaming response (use Server-Sent Events)
- Message editing/deletion
- Conversation search
- Batch requests
- WebSocket support for real-time chat
- Audio input/output (voice chat)

