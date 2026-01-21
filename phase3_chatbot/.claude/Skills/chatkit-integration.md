# Skill: OpenAI ChatKit Integration

## Purpose
Implement OpenAI ChatKit UI component for conversational interfaces in Next.js applications with proper domain configuration and backend integration.

## Tech Stack
- **OpenAI ChatKit**: Chat UI component
- **Next.js**: 16+ (App Router)
- **TypeScript**: Type safety
- **React**: 19+

## What is ChatKit?

ChatKit is OpenAI's embeddable chat interface that provides:
- Beautiful, pre-built chat UI
- Message streaming support
- File upload handling
- Mobile responsive design
- Markdown rendering
- Code syntax highlighting

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Next.js Frontend (ChatKit)                  │
│  ┌────────────────────────────────────────────────┐     │
│  │  ChatKit Component                             │     │
│  │  - Renders messages                            │     │
│  │  - Handles user input                          │     │
│  │  - Streams responses                           │     │
│  └───────────────┬────────────────────────────────┘     │
│                  │ HTTP POST                            │
└──────────────────┼──────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────┐
│           FastAPI Backend (Chat API)                      │
│  POST /api/{user_id}/chat                                │
│  - Runs OpenAI Agent with MCP tools                      │
│  - Returns response                                      │
└──────────────────────────────────────────────────────────┘
```

## Installation

```bash
# In your Next.js frontend
npm install @openai/chat-kit
# or
pnpm add @openai/chat-kit
```

## CRITICAL: Domain Allowlist Setup

Before deploying, you **MUST** configure OpenAI's domain allowlist:

### Step 1: Deploy Your Frontend First

```bash
# Deploy to Vercel
vercel deploy

# You'll get a URL like:
# https://your-app.vercel.app
```

### Step 2: Add Domain to OpenAI Allowlist

1. Go to: https://platform.openai.com/settings/organization/security/domain-allowlist
2. Click "Add domain"
3. Enter your frontend URL: `https://your-app.vercel.app`
4. Save changes
5. Copy the **domain key** provided

### Step 3: Add Domain Key to Environment

```bash
# .env.local
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
NEXT_PUBLIC_API_URL=http://localhost:8000  # or your backend URL
```

**Note**: `localhost` typically works without domain allowlist configuration during development.

## Basic ChatKit Implementation

### 1. ChatKit Component (Client Component)

```typescript
/**
 * components/chatkit-interface.tsx
 * [Task]: T-080
 * [From]: plan.md §7.4 - ChatKit UI Implementation
 */

'use client'

import { ChatKit } from '@openai/chat-kit'
import { useState } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface ChatKitInterfaceProps {
  userId: string
  conversationId?: number
}

export default function ChatKitInterface({ 
  userId, 
  conversationId: initialConversationId 
}: ChatKitInterfaceProps) {
  /**
   * ChatKit interface for todo chatbot.
   * 
   * [Spec]: plan.md §7.4 - Conversational Interface
   */
  
  const [conversationId, setConversationId] = useState<number | undefined>(
    initialConversationId
  )
  const [messages, setMessages] = useState<Message[]>([])

  async function handleSendMessage(message: string) {
    /**
     * Send message to backend and update UI.
     * 
     * [Task]: T-081
     */
    
    // Add user message to UI immediately
    const userMessage: Message = { role: 'user', content: message }
    setMessages(prev => [...prev, userMessage])

    try {
      // Call backend API
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${await getAuthToken()}`
          },
          body: JSON.stringify({
            message,
            conversation_id: conversationId
          })
        }
      )

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()

      // Update conversation ID if it's a new conversation
      if (!conversationId) {
        setConversationId(data.conversation_id)
      }

      // Add assistant response to UI
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response
      }
      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error('Error sending message:', error)
      
      // Add error message to UI
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }])
    }
  }

  return (
    <div className="h-screen flex flex-col">
      <ChatKit
        messages={messages}
        onSendMessage={handleSendMessage}
        placeholder="Type a message... (e.g., 'Add a task to buy groceries')"
        className="flex-1"
      />
    </div>
  )
}

/**
 * Get authentication token from Better Auth session
 */
async function getAuthToken(): Promise<string> {
  const response = await fetch('/api/auth/get-session')
  const session = await response.json()
  return session.token
}
```

### 2. Chat Page

```typescript
/**
 * app/chat/page.tsx
 * [Task]: T-082
 * [From]: plan.md §7.4 - Chat Page
 */

import { redirect } from 'next/navigation'
import { auth } from '@/lib/auth'
import ChatKitInterface from '@/components/chatkit-interface'

export default async function ChatPage() {
  /**
   * Chat page with authentication check.
   * 
   * [Spec]: Server Component for auth check
   */
  
  // Check authentication (server-side)
  const session = await auth()
  
  if (!session?.user) {
    redirect('/login')
  }

  return (
    <div className="container mx-auto h-screen p-4">
      <div className="max-w-4xl mx-auto h-full">
        <h1 className="text-2xl font-bold mb-4">Todo Chat Assistant</h1>
        
        <div className="bg-white rounded-lg shadow-lg h-[calc(100%-4rem)]">
          <ChatKitInterface userId={session.user.id} />
        </div>
      </div>
    </div>
  )
}
```

## Advanced: Streaming Support

### 3. Streaming Messages

```typescript
/**
 * components/streaming-chatkit.tsx
 * [Task]: T-083
 * [From]: OpenAI ChatKit - Streaming Documentation
 */

'use client'

import { ChatKit } from '@openai/chat-kit'
import { useState } from 'react'

export default function StreamingChatKit({ userId }: { userId: string }) {
  /**
   * ChatKit with streaming support for real-time responses.
   * 
   * [Spec]: Enhanced user experience with streaming
   */
  
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)

  async function handleSendMessage(message: string) {
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: message }])
    
    // Start streaming
    setIsStreaming(true)
    
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/${userId}/chat/stream`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${await getAuthToken()}`
          },
          body: JSON.stringify({ message })
        }
      )

      if (!response.ok) throw new Error('Streaming failed')

      // Read stream
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let accumulatedResponse = ''

      // Add placeholder message for streaming
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: ''
      }])

      while (true) {
        const { done, value } = await reader!.read()
        if (done) break

        const chunk = decoder.decode(value)
        accumulatedResponse += chunk

        // Update the last message with accumulated content
        setMessages(prev => {
          const newMessages = [...prev]
          newMessages[newMessages.length - 1].content = accumulatedResponse
          return newMessages
        })
      }

    } catch (error) {
      console.error('Streaming error:', error)
    } finally {
      setIsStreaming(false)
    }
  }

  return (
    <ChatKit
      messages={messages}
      onSendMessage={handleSendMessage}
      isLoading={isStreaming}
      placeholder="Ask me anything about your tasks..."
    />
  )
}
```

## Custom Styling

### 4. Styled ChatKit

```typescript
/**
 * Custom ChatKit styling
 * [Task]: T-084
 */

import { ChatKit } from '@openai/chat-kit'
import '@/styles/chatkit-custom.css'

export default function StyledChatKit() {
  return (
    <ChatKit
      messages={messages}
      onSendMessage={handleSendMessage}
      className="custom-chatkit"
      theme={{
        primary: '#3b82f6',      // Blue
        secondary: '#f3f4f6',    // Gray
        text: '#1f2937',         // Dark gray
        background: '#ffffff'    // White
      }}
    />
  )
}
```

**Custom CSS:**

```css
/* styles/chatkit-custom.css */

.custom-chatkit {
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.custom-chatkit .message-user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 18px;
  padding: 12px 16px;
}

.custom-chatkit .message-assistant {
  background: #f3f4f6;
  border-radius: 18px;
  padding: 12px 16px;
}

.custom-chatkit .input-area {
  border-top: 2px solid #e5e7eb;
  padding: 16px;
}
```

## File Upload Support

### 5. ChatKit with File Upload

```typescript
/**
 * ChatKit with file upload capability
 * [Task]: T-085
 * [From]: ChatKit Documentation - File Upload
 */

'use client'

import { ChatKit } from '@openai/chat-kit'
import { useState } from 'react'

export default function FileUploadChatKit({ userId }: { userId: string }) {
  const [messages, setMessages] = useState<Message[]>([])

  async function handleSendMessage(
    message: string, 
    files?: File[]
  ) {
    /**
     * Handle text message with optional file uploads.
     * 
     * [Spec]: Support document upload for context
     */
    
    const formData = new FormData()
    formData.append('message', message)
    formData.append('user_id', userId)

    // Add files if present
    if (files && files.length > 0) {
      files.forEach((file, index) => {
        formData.append(`file_${index}`, file)
      })
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/chat/upload`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${await getAuthToken()}`
          },
          body: formData
        }
      )

      const data = await response.json()

      setMessages(prev => [
        ...prev,
        { role: 'user', content: message },
        { role: 'assistant', content: data.response }
      ])

    } catch (error) {
      console.error('Upload error:', error)
    }
  }

  return (
    <ChatKit
      messages={messages}
      onSendMessage={handleSendMessage}
      enableFileUpload={true}
      acceptedFileTypes={['.txt', '.pdf', '.doc', '.docx']}
      maxFileSize={5 * 1024 * 1024}  // 5MB
    />
  )
}
```

## Best Practices

### 1. Always Check Authentication

```typescript
// ✅ Good - Server Component checks auth
export default async function ChatPage() {
  const session = await auth()
  if (!session) redirect('/login')
  
  return <ChatKitInterface userId={session.user.id} />
}

// ❌ Bad - No auth check
export default function ChatPage() {
  return <ChatKitInterface userId="guest" />
}
```

### 2. Handle Errors Gracefully

```typescript
// ✅ Good - Show user-friendly error
catch (error) {
  setMessages(prev => [...prev, {
    role: 'assistant',
    content: 'Sorry, something went wrong. Please try again.'
  }])
}

// ❌ Bad - Silent failure
catch (error) {
  console.error(error)
}
```

### 3. Optimistic UI Updates

```typescript
// ✅ Good - Immediate feedback
setMessages(prev => [...prev, userMessage])  // Show immediately
await sendToBackend()  // Then send

// ❌ Bad - Wait for server
await sendToBackend()  // User sees nothing
setMessages(prev => [...prev, userMessage])  // Then show
```

### 4. Use Environment Variables

```typescript
// ✅ Good
const API_URL = process.env.NEXT_PUBLIC_API_URL

// ❌ Bad - Hardcoded
const API_URL = 'http://localhost:8000'
```

## Testing ChatKit

```typescript
/**
 * __tests__/chatkit.test.tsx
 * [Task]: T-086
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ChatKitInterface from '@/components/chatkit-interface'

describe('ChatKitInterface', () => {
  it('sends message and displays response', async () => {
    // Mock fetch
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          conversation_id: 1,
          response: "I've added the task!"
        })
      })
    ) as jest.Mock

    render(<ChatKitInterface userId="test_user" />)

    // Type message
    const input = screen.getByPlaceholderText(/Type a message/i)
    fireEvent.change(input, { target: { value: 'Add a task' } })

    // Send message
    const sendButton = screen.getByRole('button', { name: /send/i })
    fireEvent.click(sendButton)

    // Wait for response
    await waitFor(() => {
      expect(screen.getByText("I've added the task!")).toBeInTheDocument()
    })
  })
})
```

## Common Issues & Solutions

### Issue 1: Domain Not Allowed Error

**Error**: `Domain not allowed in allowlist`

**Solution**:
1. Add your domain to OpenAI allowlist
2. Ensure you're using the correct domain key
3. Check `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is set

### Issue 2: CORS Error

**Error**: `CORS policy blocked`

**Solution**:
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: Messages Not Persisting

**Solution**: Ensure conversation_id is passed and stored:
```typescript
const [conversationId, setConversationId] = useState<number>()

// Update when backend returns conversation_id
if (!conversationId && data.conversation_id) {
  setConversationId(data.conversation_id)
}
```

## Summary

This skill provides:
- ✅ ChatKit component integration
- ✅ Domain allowlist configuration
- ✅ Backend API connection
- ✅ Message streaming support
- ✅ File upload handling
- ✅ Custom styling
- ✅ Error handling
- ✅ Authentication integration
- ✅ Mobile responsive UI
- ✅ Production-ready patterns

**For Hackathon Phase III**: Use the basic ChatKit implementation with your stateless chat API endpoint.