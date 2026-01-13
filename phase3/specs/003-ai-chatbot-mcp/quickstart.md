# Quickstart: Todo AI Chatbot

**Feature**: `003-ai-chatbot-mcp`
**Date**: 2026-01-13

## Prerequisites

- Phase 2 backend running (`phase3/backend`)
- Phase 2 frontend running (`phase3/frontend`)
- Neon PostgreSQL database configured
- Python 3.11+
- Node.js 18+

## Environment Setup

### 1. Backend Environment Variables

Add to `phase3/backend/.env`:

```env
# Existing Phase 2 variables
DATABASE_URL=postgresql://...your-neon-url...
JWT_SECRET=your-jwt-secret-minimum-32-chars
CORS_ORIGINS=http://localhost:3000

# New Phase 3 variable
COHERE_API_KEY=your-cohere-api-key-here
```

### 2. Install AI Agent Dependencies

```bash
cd phase3/backend
pip install openai-agents
```

### 3. Run Database Migration

```bash
cd phase3/backend
python -c "
from src.database import engine
from sqlmodel import SQLModel
from src.models.conversation import Conversation
from src.models.message import Message

import asyncio

async def migrate():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print('Migration complete!')

asyncio.run(migrate())
"
```

## Quick Test

### 1. Start Backend

```bash
cd phase3/backend
uvicorn src.main:app --reload --port 8000
```

### 2. Test Chat Endpoint

```bash
# Get JWT token first (sign in via Phase 2)
TOKEN="your-jwt-token"

# Send chat message
curl -X POST "http://localhost:8000/api/1/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "Add buy groceries"}'
```

Expected response:
```json
{
  "conversation_id": 1,
  "response": "✅ Added: 'buy groceries' (Task #1)",
  "tool_calls": ["add_task"]
}
```

### 3. Test via Frontend

1. Start frontend: `cd phase3/frontend && npm run dev`
2. Sign in at http://localhost:3000/signin
3. Navigate to dashboard
4. Click chat button (bottom-right)
5. Type "Show my tasks"

## Natural Language Commands

| Intent | Example Commands |
|--------|-----------------|
| Create task | "Add buy groceries", "Remind me to call mom", "I need to pay bills" |
| List tasks | "Show my tasks", "What's pending?", "List completed" |
| Complete task | "Mark task 5 done", "I finished the meeting", "Complete buy milk" |
| Update task | "Change task 3 to 'Call mom tonight'", "Rename groceries task" |
| Delete task | "Delete task 7", "Remove the meeting", "Cancel buy milk" |
| Compound | "Add eggs and show my tasks", "Complete task 3 and show pending" |

## Architecture Overview

```
User Input → FastAPI Endpoint → Main Orchestrator Agent
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             ContextManager    IntentParser      MCPValidator
                    │                 │                 │
                    ▼                 ▼                 ▼
            Load/Save History   Parse Intent    Validate Params
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                              TaskManager Agent
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
               add_task        list_tasks       complete_task
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                           ResponseFormatter Agent
                                      │
                                      ▼
                              Formatted Response
```

## File Structure

```
phase3/backend/
├── src/
│   ├── api/
│   │   └── chat.py              # Chat endpoint
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Main orchestrator
│   │   ├── intent_parser.py     # Intent parsing
│   │   ├── task_manager.py      # MCP tool execution
│   │   ├── context_manager.py   # Conversation persistence
│   │   ├── response_formatter.py # Response formatting
│   │   └── mcp_validator.py     # Input validation
│   ├── tools/
│   │   └── mcp_tools.py         # MCP tool definitions
│   ├── models/
│   │   ├── conversation.py      # NEW
│   │   └── message.py           # NEW
│   └── schemas/
│       └── chat.py              # Request/Response schemas
└── tests/
    └── test_chat.py             # Chat endpoint tests

phase3/frontend/
├── components/
│   └── chat/
│       ├── ChatWidget.tsx       # Main chat component
│       ├── ChatMessage.tsx      # Individual message
│       ├── ChatInput.tsx        # Input field
│       └── ChatToggle.tsx       # Floating button
└── app/
    └── dashboard/
        └── page.tsx             # Dashboard with chat integration
```

## Troubleshooting

### "Chat service unavailable"
- Check `COHERE_API_KEY` is set correctly
- Verify Cohere API is accessible: `curl https://api.cohere.ai/v1/models`

### "Session expired"
- JWT token has expired, sign in again
- Check `JWT_EXPIRATION_DAYS` in config

### "Task not found"
- User may be referencing wrong task ID
- Run "show my tasks" to see available tasks

### Slow responses (>2s)
- Check database connection latency
- Verify indexes exist on `messages.conversation_id`
- Check Cohere API response time
