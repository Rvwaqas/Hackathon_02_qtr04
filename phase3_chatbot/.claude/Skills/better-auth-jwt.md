# Skill: Better Auth with JWT Integration

## Purpose
Implement secure user authentication using Better Auth in Next.js frontend with JWT token verification in FastAPI backend.

## Tech Stack
- **Better Auth**: Modern authentication library
- **Next.js**: 16+ (Frontend)
- **FastAPI**: Python backend
- **JWT**: Token-based authentication
- **PostgreSQL**: Session storage (Neon)

## What is Better Auth?

Better Auth is a TypeScript/JavaScript authentication library that provides:
- Email/password authentication
- OAuth providers (Google, GitHub, etc.)
- JWT token support
- Session management
- Built-in security features

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Better Auth                                              │  │
│  │ - User signup/signin                                     │  │
│  │ - Issues JWT tokens                                      │  │
│  │ - Manages sessions in DB                                 │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │ JWT Token in Header                         │
└───────────────────┼─────────────────────────────────────────────┘
                    │ Authorization: Bearer <jwt>
                    ▼
┌────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ JWT Middleware                                           │  │
│  │ - Verifies JWT signature                                 │  │
│  │ - Extracts user_id                                       │  │
│  │ - Injects into route handlers                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

## Installation

### Frontend (Next.js)
```bash
npm install better-auth
# or
pnpm add better-auth
```

### Backend (FastAPI)
```bash
uv add pyjwt python-jose[cryptography]
# or
pip install pyjwt python-jose[cryptography]
```

## Shared Secret

**CRITICAL**: Frontend and backend must use the **same secret key** for JWT signing/verification.

```bash
# Generate a secure secret (run once)
openssl rand -base64 32

# Save to .env in BOTH frontend and backend
# .env (frontend and backend)
BETTER_AUTH_SECRET=your-generated-secret-here
DATABASE_URL=postgresql://...
```

## Frontend Setup (Better Auth)

### 1. Better Auth Configuration

```typescript
/**
 * lib/auth.ts - Better Auth configuration
 * [Task]: T-100
 * [From]: plan.md §4.3 - Better Auth Setup
 */

import { betterAuth } from "better-auth"

export const auth = betterAuth({
  /**
   * Database configuration
   * Better Auth creates and manages user/session tables
   */
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL!,
  },
  
  /**
   * Enable email/password authentication
   */
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set true in production
  },
  
  /**
   * Enable JWT tokens (CRITICAL for backend verification)
   */
  jwt: {
    enabled: true,
    secret: process.env.BETTER_AUTH_SECRET!,
    expiresIn: "7d", // Token expires in 7 days
  },
  
  /**
   * Session configuration
   */
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days in seconds
    updateAge: 60 * 60 * 24, // Update session every day
  },
})
```

### 2. Better Auth API Route

```typescript
/**
 * app/api/auth/[...all]/route.ts - Better Auth API handler
 * [Task]: T-101
 * [From]: Better Auth Documentation
 */

import { auth } from "@/lib/auth"

/**
 * Export GET and POST handlers for Better Auth.
 * Handles all auth endpoints:
 * - POST /api/auth/signup
 * - POST /api/auth/signin
 * - POST /api/auth/signout
 * - GET /api/auth/session
 */
export const { GET, POST } = auth.handler
```

### 3. Auth Client Hook

```typescript
/**
 * lib/auth-client.ts - Client-side auth utilities
 * [Task]: T-102
 */

import { createAuthClient } from "better-auth/client"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
})

/**
 * Get current JWT token from session
 */
export async function getAuthToken(): Promise<string | null> {
  const { data: session } = await authClient.getSession()
  
  if (!session?.token) {
    return null
  }
  
  return session.token
}
```

### 4. Login Page

```typescript
/**
 * app/login/page.tsx - Login page
 * [Task]: T-103
 * [From]: specify.md §4.1 - User Authentication
 */

"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { authClient } from "@/lib/auth-client"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const router = useRouter()

  async function handleSignIn(e: React.FormEvent) {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      const { data, error } = await authClient.signIn.email({
        email,
        password,
      })

      if (error) {
        setError(error.message)
        return
      }

      // Success - redirect to dashboard
      router.push("/dashboard")
    } catch (err) {
      setError("An error occurred. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Sign in to Todo App</h2>

        <form onSubmit={handleSignIn} className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
          >
            {isLoading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-600">
          Don't have an account?{" "}
          <a href="/signup" className="text-blue-600 hover:text-blue-500">
            Sign up
          </a>
        </p>
      </div>
    </div>
  )
}
```

### 5. Signup Page

```typescript
/**
 * app/signup/page.tsx - Signup page
 * [Task]: T-104
 */

"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { authClient } from "@/lib/auth-client"

export default function SignupPage() {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const router = useRouter()

  async function handleSignUp(e: React.FormEvent) {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      const { data, error } = await authClient.signUp.email({
        email,
        password,
        name,
      })

      if (error) {
        setError(error.message)
        return
      }

      // Success - redirect to dashboard
      router.push("/dashboard")
    } catch (err) {
      setError("An error occurred. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Create your account</h2>

        <form onSubmit={handleSignUp} className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
          >
            {isLoading ? "Creating account..." : "Sign up"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-600">
          Already have an account?{" "}
          <a href="/login" className="text-blue-600 hover:text-blue-500">
            Sign in
          </a>
        </p>
      </div>
    </div>
  )
}
```

### 6. Protected Route Example

```typescript
/**
 * app/dashboard/page.tsx - Protected dashboard
 * [Task]: T-105
 */

import { redirect } from "next/navigation"
import { auth } from "@/lib/auth"

export default async function DashboardPage() {
  /**
   * Server Component - Check auth server-side
   * 
   * [Spec]: Redirect unauthenticated users to login
   */
  
  const session = await auth()
  
  if (!session?.user) {
    redirect("/login")
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold">Welcome, {session.user.name}!</h1>
      <p className="text-gray-600">Email: {session.user.email}</p>
    </div>
  )
}
```

## Backend Setup (FastAPI JWT Verification)

### 7. JWT Verification Middleware

```python
"""
middleware.py - JWT verification for FastAPI
[Task]: T-106
[From]: plan.md §4.3 - Securing REST API
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
import os
from datetime import datetime

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> str:
    """
    Extract and verify JWT token from Authorization header.
    
    [Task]: T-106
    [Spec]: plan.md §4.3 - JWT Verification
    
    Returns:
        user_id: The authenticated user's ID
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        # Decode JWT using the SAME secret as Better Auth
        payload = jwt.decode(
            token,
            os.getenv("BETTER_AUTH_SECRET"),
            algorithms=["HS256"]
        )
        
        # Extract user ID from "sub" (subject) claim
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # Check expiration (JWT library already does this, but double-check)
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### 8. Protected API Endpoints

```python
"""
routes/tasks.py - Protected task endpoints
[Task]: T-107
[From]: plan.md §4.1 - Secured API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session
from middleware import get_current_user
from models import Task

router = APIRouter()

@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    status: str = "all",
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)  # JWT verification
):
    """
    List tasks for authenticated user.
    
    [Task]: T-107-A
    [Spec]: Security - Verify user can only access their own tasks
    """
    
    # CRITICAL: Verify the user_id in URL matches the authenticated user
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own tasks"
        )
    
    # Fetch tasks (user_id is verified)
    from sqlmodel import select
    query = select(Task).where(Task.user_id == user_id)
    
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)
    
    result = await session.execute(query)
    tasks = result.scalars().all()
    
    return {"tasks": tasks}

@router.post("/api/{user_id}/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    title: str,
    description: str = None,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Create a new task for authenticated user.
    
    [Task]: T-107-B
    """
    
    # Security check
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create tasks for yourself"
        )
    
    # Create task
    task = Task(
        user_id=user_id,
        title=title,
        description=description
    )
    
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    return task
```

## API Client (Frontend)

### 9. Authenticated API Calls

```typescript
/**
 * lib/api.ts - API client with automatic JWT injection
 * [Task]: T-108
 * [From]: plan.md §6.4 - API Client
 */

import { getAuthToken } from "./auth-client"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

/**
 * Make authenticated API request
 */
async function authenticatedFetch(url: string, options: RequestInit = {}) {
  const token = await getAuthToken()
  
  if (!token) {
    throw new Error("Not authenticated")
  }
  
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  })
}

export const api = {
  async getTasks(userId: string, status: string = "all") {
    const response = await authenticatedFetch(
      `${API_BASE}/api/${userId}/tasks?status=${status}`
    )
    
    if (!response.ok) {
      throw new Error("Failed to fetch tasks")
    }
    
    return response.json()
  },
  
  async createTask(userId: string, title: string, description?: string) {
    const response = await authenticatedFetch(
      `${API_BASE}/api/${userId}/tasks`,
      {
        method: "POST",
        body: JSON.stringify({ title, description }),
      }
    )
    
    if (!response.ok) {
      throw new Error("Failed to create task")
    }
    
    return response.json()
  },
}
```

## Security Best Practices

### 1. Always Verify User ID Matches Token

```python
# ✅ Good - Prevent unauthorized access
if user_id != current_user:
    raise HTTPException(status_code=403, detail="Access denied")

# ❌ Bad - Security vulnerability
# Accept any user_id without checking
```

### 2. Use HTTPS in Production

```typescript
// ✅ Good
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

// ❌ Bad (production)
NEXT_PUBLIC_API_URL=http://api.yourdomain.com
```

### 3. Secure Secret Storage

```bash
# ✅ Good - Use environment variables
BETTER_AUTH_SECRET=<random-generated-secret>

# ❌ Bad - Hardcoded secrets
const SECRET = "mysecret123"
```

### 4. Set Appropriate Token Expiration

```typescript
// ✅ Good - Balance security and UX
jwt: {
  expiresIn: "7d"  // 7 days
}

// ❌ Bad - Never expires
jwt: {
  expiresIn: "100y"
}
```

## Testing Authentication

```typescript
/**
 * __tests__/auth.test.ts
 * [Task]: T-109
 */

import { authClient } from "@/lib/auth-client"

describe("Authentication", () => {
  it("signs up new user", async () => {
    const { data, error } = await authClient.signUp.email({
      email: "test@example.com",
      password: "password123",
      name: "Test User",
    })
    
    expect(error).toBeNull()
    expect(data?.user).toBeDefined()
  })
  
  it("signs in existing user", async () => {
    const { data, error } = await authClient.signIn.email({
      email: "test@example.com",
      password: "password123",
    })
    
    expect(error).toBeNull()
    expect(data?.token).toBeDefined()
  })
})
```

## Common Issues & Solutions

### Issue 1: Token Verification Fails

**Error**: `Invalid token signature`

**Solution**: Ensure `BETTER_AUTH_SECRET` is identical in frontend and backend.

### Issue 2: 401 Unauthorized

**Error**: Every request returns 401

**Solution**: Check token is being sent in header:
```typescript
headers: {
  "Authorization": `Bearer ${token}`
}
```

### Issue 3: User Can Access Other Users' Data

**Solution**: Always verify `user_id` matches `current_user`:
```python
if user_id != current_user:
    raise HTTPException(status_code=403)
```

## Summary

This skill provides:
- ✅ Better Auth setup in Next.js
- ✅ JWT token generation
- ✅ Backend JWT verification
- ✅ Protected API endpoints
- ✅ User signup/signin flows
- ✅ Authenticated API client
- ✅ Security best practices
- ✅ Production-ready configuration
- ✅ CORS handling
- ✅ Error handling

**For Hackathon Phase II+**: Use this complete authentication system for secure user management and API access control.