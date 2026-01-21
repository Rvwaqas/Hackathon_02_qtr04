# Quickstart: AI-Powered Todo Chatbot

**Purpose**: Minimal runnable example demonstrating all Phase III features

**Status**: Development Guide (Phase 1 design output)

---

## Prerequisites

Before running this guide, ensure you have:

1. **Backend (Phase II complete)**:
   - Python 3.11+, FastAPI running on localhost:8000
   - PostgreSQL database with existing task schema
   - Better Auth configured for JWT
   - Existing task REST API working (`POST /tasks`, `GET /tasks/{id}`, etc.)

2. **Frontend (Phase II complete)**:
   - Next.js 16+ running on localhost:3000
   - Dashboard page accessible at `/dashboard`
   - Authentication flow complete

3. **API Keys**:
   - `COHERE_API_KEY`: Your Cohere API key (get from https://cohere.com)
   - For ChatKit domain allowlist (if using hosted ChatKit)

4. **Dependencies Installed**:
   ```bash
   # Backend: add to requirements.txt
   openai>=1.3.0
   mcp==0.1.0  # Official MCP SDK

   # Frontend: add to package.json
   @openai/chat-ui-kit  # ChatKit component
   ```

---

## Setup (Phase 1: Foundation)

### Backend: Database Setup

1. **Create migration file** (`backend/migrations/add_chat_tables.sql`):

```sql
-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    title VARCHAR(255)
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at ASC);
```

2. **Run migration**:
```bash
psql -U postgres -d todo_db -f migrations/add_chat_tables.sql
```

3. **Verify tables**:
```bash
psql -U postgres -d todo_db -c "\dt conversations,messages"
```

---

### Backend: Environment Configuration

1. **Update `.env`**:

```env
# Existing (Phase II)
DATABASE_URL=postgresql://user:password@localhost/todo_db
JWT_SECRET=your_secret_key

# NEW: Cohere & Chatbot
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=command-r-plus
```

2. **Update `src/config.py`**:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing...
    database_url: str
    jwt_secret: str

    # NEW: Cohere configuration
    cohere_api_key: str
    cohere_model: str = "command-r-plus"

    class Config:
        env_file = ".env"

settings = Settings()
```

---

### Backend: Cohere Client Setup

1. **Create `src/agents/cohere_client.py`**:

```python
from openai import AsyncOpenAI
import os

class CohereClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("COHERE_API_KEY"),
            base_url="https://api.cohere.com/v1"
        )
        self.model = os.getenv("COHERE_MODEL", "command-r-plus")

    async def create_message(self, messages, tools=None, tool_choice="auto"):
        """Send message to Cohere and get response"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools if tools else [],
            tool_choice=tool_choice
        )
        return response

cohere_client = CohereClient()
```

---

### Frontend: Environment Configuration

1. **Update `.env.local`**:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_here  # if using hosted ChatKit
```

---

## Minimal Implementation (Phase 2-3: Core Features)

### Backend: Chat Endpoint

1. **Create `src/api/routes/chat.py`**:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.models import User
from src.services import ConversationService, TaskService
from src.agents import TodoAgent
from src.middleware.jwt_auth import get_current_user

router = APIRouter(prefix="/api", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Handle chat messages with AI agent"""

    # Verify user_id matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Load or create conversation
    conv_service = ConversationService()
    if request.conversation_id:
        conversation = conv_service.get_conversation(request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = conv_service.create_conversation(user_id)

    # Load conversation history
    messages = conv_service.get_messages(conversation.id)

    # Save user message
    conv_service.add_message(conversation.id, "user", request.message)

    # Run agent
    agent = TodoAgent(user_id=user_id)
    response = await agent.execute(request.message, messages)

    # Save agent response
    conv_service.add_message(conversation.id, "assistant", response)

    return ChatResponse(response=response, conversation_id=conversation.id)
```

2. **Register route in `src/main.py`**:

```python
from src.api.routes import chat

app.include_router(chat.router)
```

---

### Backend: MCP Tools

1. **Create `src/mcp/tools.py`**:

```python
from src.services import TaskService
from typing import Optional

class TodoTools:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.task_service = TaskService()

    async def add_task(self, title: str, description: str = None, priority: str = "medium"):
        """Create a new task"""
        task = self.task_service.create_task(
            user_id=self.user_id,
            title=title,
            description=description,
            priority=priority
        )
        return {"success": True, "task_id": task.id, "message": f"Task '{title}' created"}

    async def list_tasks(self, status: str = "all"):
        """List tasks for user"""
        tasks = self.task_service.get_tasks(user_id=self.user_id, status=status)
        return {
            "success": True,
            "tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in tasks],
            "count": len(tasks)
        }

    async def complete_task(self, task_id: str):
        """Mark task as complete"""
        task = self.task_service.get_task(user_id=self.user_id, task_id=task_id)
        if not task:
            return {"success": False, "error": "Task not found"}

        self.task_service.update_task(user_id=self.user_id, task_id=task_id, status="completed")
        return {"success": True, "task_id": task_id, "message": f"Task {task_id} marked complete"}

    async def update_task(self, task_id: str, title: str = None, priority: str = None):
        """Update task properties"""
        task = self.task_service.get_task(user_id=self.user_id, task_id=task_id)
        if not task:
            return {"success": False, "error": "Task not found"}

        updates = {}
        if title:
            updates["title"] = title
        if priority:
            updates["priority"] = priority

        self.task_service.update_task(user_id=self.user_id, task_id=task_id, **updates)
        return {"success": True, "task_id": task_id, "message": f"Task {task_id} updated"}

    async def delete_task(self, task_id: str):
        """Delete a task"""
        task = self.task_service.get_task(user_id=self.user_id, task_id=task_id)
        if not task:
            return {"success": False, "error": "Task not found"}

        self.task_service.delete_task(user_id=self.user_id, task_id=task_id)
        return {"success": True, "task_id": task_id, "message": f"Task {task_id} deleted"}
```

---

### Backend: Agent

1. **Create `src/agents/todo_agent.py`**:

```python
from src.agents.cohere_client import cohere_client
from src.mcp.tools import TodoTools
import json

class TodoAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.tools = TodoTools(user_id)
        self.system_prompt = "You are a friendly todo assistant. Always confirm actions with emojis. Be concise."

    async def execute(self, user_message: str, conversation_history: list):
        """Execute agent with user message and history"""

        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            *conversation_history,
            {"role": "user", "content": user_message}
        ]

        # Define tools for agent
        tools = [
            {
                "name": "add_task",
                "description": "Create a new task",
                "parameters": {"type": "object", "properties": {...}}
            },
            # ... other tools
        ]

        # Call Cohere
        response = await cohere_client.create_message(
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        # Handle tool calls if any
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Execute tool
                result = await getattr(self.tools, tool_name)(**tool_args)

                # For MVP: return result as text
                # For full implementation: feed back to agent for next turn

        # Return final response
        return response.choices[0].message.content
```

---

### Frontend: Chat Component

1. **Create `src/components/chat/ChatButton.tsx`**:

```typescript
import { useState } from 'react';
import ChatPanel from './ChatPanel';

export default function ChatButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 w-12 h-12 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 z-40"
      >
        💬
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <ChatPanel onClose={() => setIsOpen(false)} />
      )}
    </>
  );
}
```

2. **Create `src/components/chat/ChatPanel.tsx`**:

```typescript
import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/lib/useChat';

export default function ChatPanel({ onClose }: { onClose: () => void }) {
  const { messages, sendMessage, conversationId, isLoading } = useChat();
  const [input, setInput] = useState('');
  const messagesEnd = useRef(null);

  const handleSend = async () => {
    if (!input.trim()) return;

    await sendMessage(input);
    setInput('');
  };

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="fixed bottom-20 right-4 w-80 h-96 bg-white rounded-lg shadow-2xl flex flex-col z-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
        <h2>Todo Assistant</h2>
        <button onClick={onClose}>✕</button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs px-3 py-2 rounded ${
              msg.role === 'user' ? 'bg-blue-100 text-blue-900' : 'bg-gray-100 text-gray-900'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && <div className="text-gray-500 text-sm">Thinking...</div>}
        <div ref={messagesEnd} />
      </div>

      {/* Input */}
      <div className="border-t p-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Say something..."
          className="flex-1 border rounded px-3 py-2 text-sm"
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700 disabled:bg-gray-300"
        >
          Send
        </button>
      </div>
    </div>
  );
}
```

3. **Create `src/lib/useChat.ts`**:

```typescript
import { useState, useCallback } from 'react';
import { chatApi } from './chatApi';

export function useChat() {
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (message: string) => {
    setIsLoading(true);

    try {
      const response = await chatApi.send(message, conversationId);

      // Add user message
      setMessages(prev => [...prev, { role: 'user', content: message }]);

      // Add assistant response
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);

      // Update conversation ID
      setConversationId(response.conversation_id);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  return { messages, sendMessage, conversationId, isLoading };
}
```

4. **Create `src/lib/chatApi.ts`**:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const chatApi = {
  async send(message: string, conversationId: string | null) {
    const userId = (await fetch('/api/auth/me').then(r => r.json())).id;

    const response = await fetch(`${API_URL}/api/${userId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, conversation_id: conversationId }),
      credentials: 'include'
    });

    if (!response.ok) throw new Error('Chat failed');
    return response.json();
  }
};
```

---

## Testing the Implementation

### Test 1: Add Task

```bash
curl -X POST http://localhost:8000/api/user-123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

Expected response:
```json
{
  "response": "Task 'Buy groceries' added! ✅",
  "conversation_id": "abc-123"
}
```

### Test 2: List Tasks

```bash
curl -X POST http://localhost:8000/api/user-123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my pending tasks",
    "conversation_id": "abc-123"
  }'
```

### Test 3: Browser Integration

1. Navigate to http://localhost:3000/dashboard
2. Click the floating chat icon (💬) in bottom-right
3. Type: "Add a task to call mom tonight"
4. Verify task appears in dashboard
5. Type: "Mark it complete"
6. Verify status changes in dashboard

---

## Common Issues & Debugging

| Issue | Solution |
|-------|----------|
| "COHERE_API_KEY not found" | Check `.env` and restart backend |
| 401 Unauthorized | Verify JWT token is valid and user_id matches |
| Agent takes >10s | Check Cohere API status; reduce message history |
| Tasks not appearing | Verify database migrations ran; check task_service logs |
| Chat messages don't persist | Check conversations and messages tables exist; verify FK constraints |

---

## Next Steps

1. Complete all unit tests (tools, agent, endpoint)
2. Complete integration tests (multi-turn conversations, user isolation)
3. Performance testing (load test with 100+ concurrent users)
4. Manual scenario testing (all examples from spec)
5. Deploy to staging environment
6. Production rollout with monitoring

