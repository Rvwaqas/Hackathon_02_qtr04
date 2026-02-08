# Skill: Neon Serverless PostgreSQL Setup

## Purpose
Configure and use Neon serverless PostgreSQL database with SQLModel ORM for scalable, cost-effective data persistence.

## Tech Stack
- **Neon**: Serverless PostgreSQL
- **SQLModel**: Python ORM (combines SQLAlchemy + Pydantic)
- **Asyncpg**: Async PostgreSQL driver
- **Alembic**: Database migrations (optional)

## What is Neon?

Neon is a serverless PostgreSQL platform that automatically scales compute resources and separates storage from compute. Key benefits:
- **Serverless**: No server management
- **Autoscaling**: Scales to zero when idle
- **Branching**: Create database branches like Git
- **Free tier**: Generous limits for development

## Account Setup

### Step 1: Create Neon Account

1. Go to: https://neon.tech
2. Sign up (free account)
3. Create a new project
4. Select region (closest to your users)
5. Copy connection string

### Step 2: Get Connection String

Neon provides connection string in format:
```
postgresql://username:password@ep-xxx.region.neon.tech/dbname?sslmode=require
```

**Important**: Copy the connection string immediately - password shown only once!

## Installation

```bash
# Using UV
uv add sqlmodel asyncpg psycopg2-binary

# Or pip
pip install sqlmodel asyncpg psycopg2-binary
```

## Environment Configuration

### 1. Store Connection String

```bash
# .env
DATABASE_URL=postgresql://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require

# For async support, use postgresql+asyncpg://
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require
```

```python
# config.py
# [Task]: T-040
# [From]: plan.md §3.2 - Database Configuration

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Database Connection Setup

### 2. Async Database Connection

```python
"""
db.py - Database connection and session management
[Task]: T-041
[From]: plan.md §3.2 - Neon Database Setup
"""

from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Log SQL queries (disable in production)
    future=True,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """
    Create all database tables.
    
    [Task]: T-042
    [Spec]: Run this once at application startup
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """
    Dependency for FastAPI route handlers.
    
    [Task]: T-043
    [Usage]: session: AsyncSession = Depends(get_session)
    """
    async with async_session() as session:
        yield session
```

## Database Models

### 3. Define SQLModel Models

```python
"""
models.py - Database models
[Task]: T-044
[From]: plan.md §3.1 - Database Schema
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """
    Task model for todo items.
    
    [Task]: T-044-A
    [Spec]: specify.md §3.2 - Task Schema
    """
    __tablename__ = "tasks"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # User reference
    user_id: str = Field(index=True)  # Indexed for fast user queries
    
    # Task fields
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)  # Indexed for filtering
    
    # Phase 5: Advanced features
    priority: Optional[str] = Field(default="medium")  # low, medium, high
    tags: Optional[str] = Field(default=None)  # JSON string of tags
    due_date: Optional[datetime] = Field(default=None)
    recurring: bool = Field(default=False)
    recurring_pattern: Optional[str] = Field(default=None)  # daily, weekly, monthly
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Conversation(SQLModel, table=True):
    """
    Conversation model for chat history.
    
    [Task]: T-044-B
    [Spec]: plan.md §5.2 - Phase III Requirements
    """
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to messages
    messages: list["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    """
    Message model for conversation history.
    
    [Task]: T-044-C
    [Spec]: plan.md §5.2 - Stateless Chat Architecture
    """
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id")
    user_id: str = Field(index=True)
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

# Phase 2: Better Auth tables (managed by Better Auth)
# These are created automatically by Better Auth, listed here for reference
"""
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: str = Field(primary_key=True)
    email: str = Field(unique=True)
    name: str
    email_verified: Optional[datetime] = None
    image: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Session(SQLModel, table=True):
    __tablename__ = "sessions"
    
    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
"""
```

## FastAPI Integration

### 4. Initialize Database on Startup

```python
"""
main.py - FastAPI application with database initialization
[Task]: T-045
[From]: plan.md §2.1 - FastAPI Setup
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import init_db
from routes import tasks, chat

app = FastAPI(title="Todo API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """
    Initialize database on application startup.
    
    [Task]: T-046
    [Spec]: Creates all tables if they don't exist
    """
    await init_db()
    print("✅ Database initialized")

# Register routes
app.include_router(tasks.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Todo API", "database": "Neon PostgreSQL"}
```

## CRUD Operations

### 5. Database Operations Example

```python
"""
Example CRUD operations with Neon + SQLModel
[Task]: T-047
[From]: plan.md §4.1 - Task CRUD Operations
"""

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Task
from datetime import datetime

# CREATE
async def create_task(
    session: AsyncSession,
    user_id: str,
    title: str,
    description: str = None
) -> Task:
    """
    Create a new task.
    
    [Task]: T-047-A
    """
    task = Task(
        user_id=user_id,
        title=title,
        description=description
    )
    
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    return task

# READ (Single)
async def get_task(
    session: AsyncSession,
    task_id: int,
    user_id: str
) -> Task | None:
    """
    Get a single task by ID.
    
    [Task]: T-047-B
    """
    result = await session.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
    )
    return result.scalar_one_or_none()

# READ (Multiple)
async def list_tasks(
    session: AsyncSession,
    user_id: str,
    status: str = "all"
) -> list[Task]:
    """
    List all tasks for a user with optional filtering.
    
    [Task]: T-047-C
    """
    # Build query
    query = select(Task).where(Task.user_id == user_id)
    
    # Apply status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)
    
    # Order by created date
    query = query.order_by(Task.created_at.desc())
    
    # Execute
    result = await session.execute(query)
    return result.scalars().all()

# UPDATE
async def update_task(
    session: AsyncSession,
    task_id: int,
    user_id: str,
    **updates
) -> Task | None:
    """
    Update a task.
    
    [Task]: T-047-D
    """
    # Fetch task
    task = await get_task(session, task_id, user_id)
    
    if not task:
        return None
    
    # Apply updates
    for key, value in updates.items():
        if hasattr(task, key):
            setattr(task, key, value)
    
    task.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(task)
    
    return task

# DELETE
async def delete_task(
    session: AsyncSession,
    task_id: int,
    user_id: str
) -> bool:
    """
    Delete a task.
    
    [Task]: T-047-E
    """
    task = await get_task(session, task_id, user_id)
    
    if not task:
        return False
    
    await session.delete(task)
    await session.commit()
    
    return True
```

## Connection Pooling

### 6. Production Connection Settings

```python
"""
Production-ready connection pool configuration
[Task]: T-048
[From]: Neon Best Practices
"""

from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    settings.database_url,
    
    # Connection pool settings
    pool_size=20,              # Max connections in pool
    max_overflow=10,           # Extra connections if pool is full
    pool_timeout=30,           # Wait time for connection (seconds)
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_pre_ping=True,        # Verify connection before use
    
    # Performance
    echo=False,                # Disable SQL logging in production
    future=True,
    
    # SSL (required by Neon)
    connect_args={
        "ssl": "require",
        "server_settings": {
            "application_name": "todo_app"
        }
    }
)
```

## Database Migrations (Optional)

### 7. Using Alembic for Migrations

```bash
# Install Alembic
uv add alembic

# Initialize
alembic init migrations

# Edit alembic.ini
sqlalchemy.url = postgresql+asyncpg://...
```

```python
# migrations/env.py
from sqlmodel import SQLModel
from models import Task, Conversation, Message

target_metadata = SQLModel.metadata
```

```bash
# Create migration
alembic revision --autogenerate -m "Add tasks table"

# Apply migration
alembic upgrade head
```

## Best Practices

### 1. Always Use Connection Pooling

```python
# ✅ Good - Reuse connections
engine = create_async_engine(url, pool_size=20)

# ❌ Bad - New connection every time
engine = create_async_engine(url, poolclass=NullPool)
```

### 2. Use Indexes for Frequently Queried Fields

```python
# ✅ Good - Indexed for fast queries
user_id: str = Field(index=True)
completed: bool = Field(default=False, index=True)

# ❌ Bad - No indexes, slow queries
user_id: str
completed: bool = False
```

### 3. Use Transactions for Multiple Operations

```python
# ✅ Good - Atomic transaction
async with session.begin():
    await session.execute(...)
    await session.execute(...)
    # Both succeed or both fail

# ❌ Bad - Partial updates possible
await session.execute(...)
await session.commit()
await session.execute(...)
await session.commit()
```

### 4. Always Filter by user_id

```python
# ✅ Good - Security check
query = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id  # Prevent access to other user's tasks
)

# ❌ Bad - Security vulnerability
query = select(Task).where(Task.id == task_id)
```

## Testing with Neon

```python
"""
Test database operations
[Task]: T-049
"""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

@pytest.fixture
async def test_session():
    """Create test database session"""
    
    # Use separate test database
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost/test_db"
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_task(test_session):
    """Test task creation"""
    
    task = await create_task(
        test_session,
        user_id="test_user",
        title="Test task"
    )
    
    assert task.id is not None
    assert task.title == "Test task"
    assert task.completed is False
```

## Common Issues & Solutions

### Issue 1: SSL Required Error

**Error**: `SSL SYSCALL error`

**Solution**:
```python
# Add SSL mode to connection string
DATABASE_URL=postgresql://...?sslmode=require
```

### Issue 2: Connection Pool Exhausted

**Error**: `TimeoutError: QueuePool limit`

**Solution**:
```python
# Increase pool size
engine = create_async_engine(url, pool_size=30, max_overflow=20)
```

### Issue 3: Tables Not Created

**Error**: Tables don't exist

**Solution**:
```python
# Ensure init_db() is called on startup
@app.on_event("startup")
async def startup():
    await init_db()
```

## Neon-Specific Features

### Database Branching

```bash
# Create branch (like Git)
neon branches create --project-id your-project --name dev

# Each branch has its own connection string
# Use for testing without affecting production
```

### Autoscaling

Neon automatically scales compute resources based on load:
- Scales to zero when idle (saves cost)
- Auto-scales up under load
- No configuration needed

## Summary

This skill provides:
- ✅ Neon PostgreSQL setup
- ✅ SQLModel ORM integration
- ✅ Async database operations
- ✅ Connection pooling
- ✅ Production-ready configuration
- ✅ Security best practices
- ✅ CRUD operations
- ✅ Migration support (optional)
- ✅ Testing patterns
- ✅ Error handling

**For Hackathon Phase II+**: Use this setup for all database operations with automatic scaling and zero downtime. 