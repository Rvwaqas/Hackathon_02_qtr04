# Skill: Next.js App Router Development

## Purpose
Build modern Next.js 16+ frontends using App Router, Server Components, TypeScript, and Tailwind CSS.

## Tech Stack
- **Next.js**: 16+ (App Router)
- **TypeScript**: Latest
- **Tailwind CSS**: For styling
- **Better Auth**: For authentication
- **React**: 19+

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page
│   ├── login/
│   │   └── page.tsx
│   ├── dashboard/
│   │   ├── layout.tsx          # Dashboard layout
│   │   └── page.tsx            # Dashboard page
│   └── api/
│       └── auth/
│           └── [...all]/route.ts  # Better Auth handler
├── components/
│   ├── ui/                     # Reusable UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── card.tsx
│   ├── task-list.tsx
│   ├── task-form.tsx
│   └── navbar.tsx
├── lib/
│   ├── api.ts                  # Backend API client
│   ├── auth.ts                 # Better Auth config
│   └── types.ts                # TypeScript types
├── public/
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## Core Patterns

### 1. Root Layout (Server Component)

```typescript
/**
 * app/layout.tsx - Root layout
 * [Task]: T-030
 * [From]: plan.md §6.1
 */

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Todo App - Hackathon II',
  description: 'AI-powered todo application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}
```

### 2. Server Component (Default)

```typescript
/**
 * app/dashboard/page.tsx - Dashboard page (Server Component)
 * [Task]: T-031
 * [From]: specify.md §5.1, plan.md §6.2
 */

import { redirect } from 'next/navigation'
import { auth } from '@/lib/auth'
import TaskList from '@/components/task-list'

export default async function DashboardPage() {
  /**
   * Server component - runs on server, can access backend directly
   * [Spec]: plan.md §6.2 - Use Server Components by default
   */
  
  // Check authentication (server-side)
  const session = await auth()
  
  if (!session?.user) {
    redirect('/login')
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
      
      {/* Client component for interactivity */}
      <TaskList userId={session.user.id} />
    </div>
  )
}
```

### 3. Client Component (Interactive)

```typescript
/**
 * components/task-list.tsx - Interactive task list
 * [Task]: T-032
 * [From]: specify.md §3.2, plan.md §6.3
 */

'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import type { Task } from '@/lib/types'
import TaskForm from './task-form'

interface TaskListProps {
  userId: string
}

export default function TaskList({ userId }: TaskListProps) {
  /**
   * Client component for interactivity
   * [Spec]: plan.md §6.3 - Client components only when needed
   */
  
  const [tasks, setTasks] = useState<Task[]>([])
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTasks()
  }, [filter])

  async function loadTasks() {
    setLoading(true)
    try {
      const data = await api.getTasks(userId, filter)
      setTasks(data.tasks)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleToggleComplete(taskId: number) {
    try {
      await api.toggleComplete(userId, taskId)
      await loadTasks() // Refresh list
    } catch (error) {
      console.error('Failed to toggle task:', error)
    }
  }

  async function handleDelete(taskId: number) {
    try {
      await api.deleteTask(userId, taskId)
      await loadTasks() // Refresh list
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }

  if (loading) {
    return <div>Loading tasks...</div>
  }

  return (
    <div className="space-y-4">
      {/* Filter buttons */}
      <div className="flex gap-2 mb-4">
        {(['all', 'pending', 'completed'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg ${
              filter === f
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Add task form */}
      <TaskForm userId={userId} onTaskAdded={loadTasks} />

      {/* Task list */}
      <div className="space-y-2">
        {tasks.length === 0 ? (
          <p className="text-gray-500">No tasks found</p>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className="flex items-center gap-4 p-4 bg-white rounded-lg shadow"
            >
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => handleToggleComplete(task.id)}
                className="w-5 h-5"
              />
              
              <div className="flex-1">
                <h3 className={`font-medium ${task.completed ? 'line-through text-gray-500' : ''}`}>
                  {task.title}
                </h3>
                {task.description && (
                  <p className="text-sm text-gray-600">{task.description}</p>
                )}
              </div>

              <button
                onClick={() => handleDelete(task.id)}
                className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
              >
                Delete
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
```

### 4. API Client (Type-Safe)

```typescript
/**
 * lib/api.ts - Backend API client
 * [Task]: T-033
 * [From]: plan.md §6.4
 */

import type { Task } from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Get JWT token from Better Auth session
 */
async function getAuthToken(): Promise<string> {
  // Better Auth stores token in httpOnly cookie
  // We need to fetch it from Better Auth endpoint
  const response = await fetch('/api/auth/get-session')
  const session = await response.json()
  return session.token
}

/**
 * API client with automatic JWT injection
 * [Spec]: plan.md §4.3 - JWT Authentication
 */
export const api = {
  async getTasks(userId: string, status: string = 'all'): Promise<{ tasks: Task[] }> {
    const token = await getAuthToken()
    
    const response = await fetch(
      `${API_BASE}/api/${userId}/tasks?status=${status}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error('Failed to fetch tasks')
    }

    return response.json()
  },

  async createTask(
    userId: string,
    title: string,
    description?: string
  ): Promise<Task> {
    const token = await getAuthToken()

    const response = await fetch(`${API_BASE}/api/${userId}/tasks`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, description }),
    })

    if (!response.ok) {
      throw new Error('Failed to create task')
    }

    return response.json()
  },

  async toggleComplete(userId: string, taskId: number): Promise<Task> {
    const token = await getAuthToken()

    const response = await fetch(
      `${API_BASE}/api/${userId}/tasks/${taskId}/complete`,
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error('Failed to toggle task')
    }

    return response.json()
  },

  async deleteTask(userId: string, taskId: number): Promise<void> {
    const token = await getAuthToken()

    const response = await fetch(`${API_BASE}/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to delete task')
    }
  },
}
```

### 5. TypeScript Types

```typescript
/**
 * lib/types.ts - Shared type definitions
 * [Task]: T-034
 * [From]: plan.md §3.1
 */

export interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
}

export interface User {
  id: string
  email: string
  name: string
}

export interface Session {
  user: User
  token: string
}
```

### 6. Better Auth Setup

```typescript
/**
 * lib/auth.ts - Better Auth configuration
 * [Task]: T-035
 * [From]: plan.md §4.3
 */

import { betterAuth } from 'better-auth'

export const auth = betterAuth({
  database: {
    provider: 'postgresql',
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
  },
  jwt: {
    enabled: true,
    secret: process.env.BETTER_AUTH_SECRET!,
  },
})
```

```typescript
/**
 * app/api/auth/[...all]/route.ts - Better Auth API handler
 * [Task]: T-036
 */

import { auth } from '@/lib/auth'

export const { GET, POST } = auth.handler
```

## Best Practices

### 1. Server Components by Default

```typescript
// ✅ Good - Server Component (default)
export default async function Page() {
  const data = await fetchData() // Direct server-side fetch
  return <div>{data}</div>
}

// ❌ Bad - Unnecessary Client Component
'use client'
export default function Page() {
  const [data, setData] = useState(null)
  useEffect(() => { fetchData() }, []) // Unnecessary client-side fetch
  return <div>{data}</div>
}
```

### 2. Use Client Components Only for Interactivity

```typescript
// ✅ Good - Client Component only for interactive parts
'use client'
export default function TaskForm() {
  const [title, setTitle] = useState('')
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    await api.createTask(title)
  }
  
  return <form onSubmit={handleSubmit}>...</form>
}
```

### 3. Tailwind for Styling

```tsx
// ✅ Good - Tailwind classes
<button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
  Add Task
</button>

// ❌ Bad - Inline styles
<button style={{ padding: '8px 16px', background: 'blue' }}>
  Add Task
</button>
```

### 4. Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret-key
```

## Running the Frontend

```bash
# Development
npm run dev

# Build
npm run build

# Production
npm start
```

## Summary

This skill provides:
- ✅ Modern Next.js App Router patterns
- ✅ Server Components for performance
- ✅ Client Components for interactivity
- ✅ Type-safe API client
- ✅ Better Auth integration
- ✅ Tailwind CSS styling
- ✅ Production-ready structure