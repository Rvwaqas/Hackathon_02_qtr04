# AI-Powered Todo Chatbot - API Documentation

Complete API reference for the TaskFlow Todo Chatbot backend with OpenAI Agents SDK integration.

## Overview

This API provides a natural language interface to manage todo tasks through an AI chatbot powered by Cohere LLM and OpenAI Agents SDK.

**Base URL**: `http://localhost:8000/api`

**Authentication**: JWT Bearer token in `Authorization` header

```
Authorization: Bearer <your_jwt_token>
```

---

## Core Concepts

### Conversations
- A conversation is a persistent chat session containing multiple messages
- Each conversation belongs to a user and maintains full message history
- Conversations are created automatically on first message or explicitly via API

### Messages
- Messages represent individual exchanges in a conversation
- Each message has a role (`user` or `assistant`), content, and timestamp
- Messages are automatically saved when sent through the chat endpoint

### MCP Tools
The chatbot has access to 5 MCP (Model Context Protocol) tools for task management:
- `add_task` - Create new tasks
- `list_tasks` - Retrieve tasks with filtering
- `complete_task` - Mark tasks as done
- `update_task` - Modify task properties
- `delete_task` - Remove tasks

---

## API Endpoints

### 1. Send Chat Message

**Endpoint**: `POST /{user_id}/chat`

Send a message to the chatbot and receive an AI-powered response. The agent automatically interprets natural language, executes appropriate tools, and responds.

**Request**:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": null
}
```

**Parameters**:
- `message` (string, required): User's message
- `conversation_id` (string, optional): UUID of existing conversation. Omit to create new conversation.

**Response** (200 OK):
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Task 'buy groceries' added! ✅",
  "role": "assistant"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid conversation ID format
- `403 Forbidden`: Accessing other user's conversation
- `404 Not Found`: Conversation doesn't exist
- `500 Internal Server Error`: Agent execution failed

**Example (curl)**:
```bash
curl -X POST http://localhost:8000/api/1/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": null
  }'
```

**Natural Language Examples**:
- "Add a task to buy groceries" → Creates task via `add_task` tool
- "Show my tasks" → Lists tasks via `list_tasks` tool
- "Mark task 1 as complete" → Completes task via `complete_task` tool
- "Change task 5 priority to high" → Updates task via `update_task` tool
- "Delete task 3" → Removes task via `delete_task` tool

---

### 2. List User Conversations

**Endpoint**: `GET /{user_id}/conversations`

Retrieve paginated list of conversations for the authenticated user, ordered by most recent.

**Response** (200 OK):
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": null,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "title": "Shopping tasks",
    "created_at": "2024-01-14T15:20:00Z",
    "updated_at": "2024-01-14T16:45:00Z"
  }
]
```

**Query Parameters**:
- None (returns up to 50 most recent conversations)

**Error Responses**:
- `403 Forbidden`: Accessing other user's conversations
- `500 Internal Server Error`: Database retrieval failed

**Example (curl)**:
```bash
curl -X GET http://localhost:8000/api/1/conversations \
  -H "Authorization: Bearer <token>"
```

---

### 3. Get Conversation Details

**Endpoint**: `GET /{user_id}/conversations/{conversation_id}`

Retrieve full conversation with complete message history in chronological order.

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": null,
  "messages": [
    {
      "role": "user",
      "content": "Add a task to buy groceries",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Task 'buy groceries' added! ✅",
      "created_at": "2024-01-15T10:30:01Z"
    },
    {
      "role": "user",
      "content": "Show my tasks",
      "created_at": "2024-01-15T10:31:00Z"
    },
    {
      "role": "assistant",
      "content": "Found 1 task:\n1. Buy groceries (pending, low priority)",
      "created_at": "2024-01-15T10:31:01Z"
    }
  ],
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:31:01Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid UUID format
- `403 Forbidden`: Accessing other user's conversation
- `404 Not Found`: Conversation doesn't exist
- `500 Internal Server Error`: Database retrieval failed

**Example (curl)**:
```bash
curl -X GET "http://localhost:8000/api/1/conversations/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer <token>"
```

---

### 4. Delete Conversation

**Endpoint**: `DELETE /{user_id}/conversations/{conversation_id}`

Permanently delete a conversation and all its messages (cascading delete).

**Response**: 204 No Content (on success)

**Error Responses**:
- `400 Bad Request`: Invalid UUID format
- `403 Forbidden`: Accessing other user's conversation
- `404 Not Found`: Conversation doesn't exist
- `500 Internal Server Error`: Deletion failed

**Example (curl)**:
```bash
curl -X DELETE "http://localhost:8000/api/1/conversations/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer <token>"
```

---

## Natural Language Examples

### Adding Tasks
```
Input:  "Add a task to buy groceries"
Output: "Task 'buy groceries' added! ✅"

Input:  "Create a high-priority task to finish the report by tomorrow"
Output: "Task 'finish the report' added with high priority! ✅"

Input:  "Add 3 tasks: wash dishes, do laundry, call mom"
Output: "Task 'wash dishes' added! ✅\nTask 'do laundry' added! ✅\nTask 'call mom' added! ✅"
```

### Listing Tasks
```
Input:  "Show my tasks"
Output: "Found 3 task(s)
         1. Buy groceries (pending, low priority)
         2. Finish report (pending, high priority)
         3. Call mom (pending, medium priority)"

Input:  "What's my high-priority tasks?"
Output: "Found 1 task(s)
         1. Finish report (pending, high priority)"

Input:  "Show completed tasks"
Output: "Found 0 task(s). You don't have any completed tasks yet."
```

### Completing Tasks
```
Input:  "Mark task 1 as done"
Output: "Task 1 marked as complete! 🎉"

Input:  "Complete task 2"
Output: "Task 2 marked as complete! 🎉"
```

### Updating Tasks
```
Input:  "Change task 3 priority to high"
Output: "Task 3 updated! ✏️"

Input:  "Update task 2 to 'Finish report - urgent'"
Output: "Task 2 updated! ✏️"

Input:  "Mark task 1 as pending"
Output: "Task 1 updated! ✏️"
```

### Deleting Tasks
```
Input:  "Delete task 3"
Output: "Task 3 deleted. ✂️"

Input:  "Remove task 1"
Output: "Task 1 deleted. ✂️"
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### Common Errors

| Status | Error | Cause | Solution |
|--------|-------|-------|----------|
| 400 | Invalid conversation ID format | Malformed UUID | Use valid UUID format or omit for new conversation |
| 403 | Cannot access other users' conversations | User ID mismatch | Ensure user_id in path matches authenticated user |
| 404 | Conversation not found | Conversation deleted or doesn't exist | Create new conversation |
| 422 | Validation error | Missing required fields | Include all required fields in request |
| 500 | Chat execution failed | Agent or database error | Check logs and retry |

---

## Rate Limiting & Quotas

- **Chat messages**: Up to 100 messages per conversation
- **Concurrent conversations**: Unlimited
- **Message history context**: Last 20 messages loaded per request
- **Rate limit**: No explicit limit (implement at deployment level)

---

## Authentication

### Getting a JWT Token

Use the authentication endpoint:

```bash
POST /api/auth/signin
```

Request:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include in all requests:
```
Authorization: Bearer <access_token>
```

---

## Environment Setup

### Required Environment Variables

```env
# Cohere API
COHERE_API_KEY=your_api_key_here
COHERE_MODEL=command-r-plus

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db

# JWT
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Database
```bash
# Run migrations
alembic upgrade head
```

### 3. Start Server
```bash
python -m uvicorn src.main:app --reload
```

### 4. First Chat Request
```bash
# 1. Get auth token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}' | jq -r '.access_token')

# 2. Send chat message
curl -X POST http://localhost:8000/api/1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add a task to learn FastAPI"}'
```

---

## Integration Examples

### JavaScript/TypeScript

```typescript
const API_BASE = "http://localhost:8000/api";

async function sendMessage(userId: number, message: string, conversationId?: string) {
  const response = await fetch(`${API_BASE}/${userId}/chat`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId || null,
    }),
  });
  return response.json();
}

async function getConversations(userId: number) {
  const response = await fetch(`${API_BASE}/${userId}/conversations`, {
    headers: { "Authorization": `Bearer ${token}` },
  });
  return response.json();
}
```

### Python

```python
import requests
import os

API_BASE = "http://localhost:8000/api"
token = os.getenv("JWT_TOKEN")

def send_message(user_id: int, message: str, conversation_id: str = None):
    response = requests.post(
        f"{API_BASE}/{user_id}/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": message, "conversation_id": conversation_id}
    )
    return response.json()

def get_conversations(user_id: int):
    response = requests.get(
        f"{API_BASE}/{user_id}/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

---

## Troubleshooting

### Agent Not Responding
- Check `COHERE_API_KEY` is set correctly
- Verify Cohere API is accessible
- Check logs for rate limiting errors

### Messages Not Saving
- Verify database connection
- Check `DATABASE_URL` is correct
- Ensure migrations have run

### Authentication Failing
- Verify JWT token is not expired
- Check `JWT_SECRET` matches between auth and API
- Ensure user exists in database

---

## Performance Metrics

- **Chat response time**: < 2 seconds (p95)
- **Conversation retrieval**: < 100ms for < 100 messages
- **Message save**: < 50ms
- **Database indexes**: On user_id, conversation_id, created_at

---

## Support

For issues or questions:
1. Check existing conversations for context
2. Review the MCP tools error messages
3. Consult the test files for usage examples
4. Review logs for detailed error traces

---

## API Versioning

Current Version: **1.0.0**

This API follows semantic versioning. Breaking changes will increment the major version.

---

*Last Updated: 2024-01-15*
*API Documentation for Phase III Chatbot Implementation*
