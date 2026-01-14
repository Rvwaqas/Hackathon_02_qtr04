# Quickstart Guide: AI-Powered Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Created**: 2026-01-14

---

## Prerequisites

Before starting Phase III implementation:

1. **Phase II Complete**: Full-stack todo app with auth must be working
2. **Cohere API Key**: Get from [cohere.com](https://cohere.com)
3. **Neon Database**: Same database from Phase II
4. **Node.js 18+**: For frontend
5. **Python 3.11+**: For backend

---

## Environment Setup

### Backend (.env)

Add to `backend/.env`:

```bash
# Existing from Phase II
DATABASE_URL=postgresql://...
JWT_SECRET=your-jwt-secret

# New for Phase III
COHERE_API_KEY=Ik1ziqg6vN9wui3DwFsKVtPyHMOR1YNjMXpcTe0o
```

### Frontend (.env.local)

Add to `frontend/.env.local`:

```bash
# Existing
NEXT_PUBLIC_API_URL=http://localhost:8000

# New for Phase III (production only)
NEXT_PUBLIC_CHATKIT_DOMAIN=your-domain.com
```

---

## Quick Start (Development)

### 1. Install Backend Dependencies

```bash
cd backend
pip install openai mcp cohere
# or with uv:
uv pip install openai mcp cohere
```

### 2. Run Database Migration

```bash
cd backend
# Run migration for conversations and messages tables
python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 3. Start Backend

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install @openai/chatkit
```

### 5. Start Frontend

```bash
cd frontend
npm run dev
```

### 6. Test the Chatbot

1. Open http://localhost:3000
2. Sign in to your account
3. Click the chat icon (bottom-right)
4. Try these commands:
   - "Add a task to buy groceries"
   - "Show my tasks"
   - "Mark task 1 as complete"
   - "Delete task 2"

---

## Project Structure (Phase III Additions)

```
phase3/
├── backend/
│   └── src/
│       ├── models/
│       │   ├── conversation.py  # NEW
│       │   └── message.py       # NEW
│       ├── mcp/                  # NEW DIRECTORY
│       │   ├── __init__.py
│       │   └── tools.py         # 5 MCP tools
│       ├── services/
│       │   ├── agent.py         # NEW - Cohere agent
│       │   └── conversation.py  # NEW - Conversation CRUD
│       └── api/
│           └── chat.py          # NEW - Chat endpoint
│
├── frontend/
│   ├── app/
│   │   └── dashboard/
│   │       └── page.tsx         # MODIFIED - Add ChatIcon
│   ├── components/
│   │   ├── ChatIcon.tsx         # NEW
│   │   ├── ChatPanel.tsx        # NEW
│   │   └── ChatMessages.tsx     # NEW
│   └── lib/
│       └── chat-api.ts          # NEW
│
└── specs/
    └── 003-ai-todo-chatbot/
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        └── contracts/
            ├── chat-api.yaml
            └── mcp-tools.md
```

---

## Key Files to Create

### 1. Conversation Model

`backend/src/models/conversation.py`:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    title: str = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Message Model

`backend/src/models/message.py`:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(index=True)
    user_id: str
    role: str  # "user", "assistant", "tool"
    content: str
    tool_call_id: Optional[str] = None
    tool_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3. Cohere Client Setup

`backend/src/services/agent.py`:
```python
from openai import AsyncOpenAI
import os

cohere_client = AsyncOpenAI(
    api_key=os.getenv("COHERE_API_KEY"),
    base_url="https://api.cohere.com/v1"
)
```

### 4. Chat Endpoint

`backend/src/api/chat.py`:
```python
from fastapi import APIRouter, Depends
from src.middleware.jwt_auth import get_current_user

router = APIRouter()

@router.post("/api/users/{user_id}/chat")
async def chat(user_id: str, request: ChatRequest, current_user = Depends(get_current_user)):
    # Validate user_id matches JWT
    # Load conversation history
    # Run agent with tools
    # Save messages
    # Return response
    pass
```

### 5. Chat Icon Component

`frontend/components/ChatIcon.tsx`:
```tsx
'use client';
import { useState } from 'react';
import { ChatPanel } from './ChatPanel';

export function ChatIcon() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 w-14 h-14 bg-blue-500 rounded-full shadow-lg flex items-center justify-center text-white hover:bg-blue-600"
      >
        💬
      </button>
      {isOpen && <ChatPanel onClose={() => setIsOpen(false)} />}
    </>
  );
}
```

---

## Testing Checklist

After implementation, verify:

- [ ] Chat icon visible on dashboard
- [ ] Panel opens/closes smoothly
- [ ] "Add task" command works
- [ ] "List tasks" command works
- [ ] "Complete task" command works
- [ ] "Update task" command works
- [ ] "Delete task" command works
- [ ] History persists after refresh
- [ ] History persists after server restart
- [ ] User isolation works (user A can't see user B's data)
- [ ] Existing dashboard still works
- [ ] Existing REST API still works

---

## Common Issues

### Cohere API Error
- Check `COHERE_API_KEY` is set correctly
- Verify API key has sufficient quota
- Check network connectivity

### Tool Not Found
- Ensure MCP tools are registered with agent
- Check tool names match exactly

### Conversation Not Loading
- Verify database migration ran
- Check composite index exists
- Verify user_id filtering in queries

### JWT Validation Failed
- Ensure existing auth middleware is applied
- Check token expiration
- Verify user_id in path matches JWT

---

## Next Steps

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Follow tasks in order (database → backend → frontend)
3. Test each component before moving to next
4. Run full end-to-end test at the end
