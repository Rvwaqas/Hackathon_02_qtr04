# Implementation Plan: Full-Stack Multi-User Todo Web Application

**Feature Branch**: `001-web-app-auth`
**Created**: 2025-12-31
**Status**: Draft
**Input**: Spec 001-web-app-auth

## Technical Context

### Technology Stack

**Frontend**:
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth client with JWT
- **HTTP Client**: Fetch API with centralized wrapper
- **State**: React hooks (useState, useEffect) for local state
- **Forms**: React controlled components

**Backend**:
- **Framework**: FastAPI (async)
- **Language**: Python 3.13+
- **ORM**: SQLModel (async)
- **Database**: Neon PostgreSQL (serverless)
- **Authentication**: JWT verification middleware
- **Package Manager**: UV

**Authentication & Security**:
- **Auth Library**: Better Auth with JWT plugin
- **Token Type**: JWT (JSON Web Tokens)
- **Token Expiration**: 7 days (per constitution)
- **Shared Secret**: BETTER_AUTH_SECRET (same in frontend and backend)
- **Password Hashing**: Handled by Better Auth (bcrypt/argon2)

**Development Tools**:
- **Documentation**: Context7 MCP server for Next.js, FastAPI, SQLModel, Better Auth docs
- **Code Generation**: Claude Code (100% AI-generated, per constitution)
- **Workflow**: Spec → Plan → Tasks → Implement

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Next.js Frontend (Port 3000)                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ app/                                                       │ │
│  │ ├── (auth)/                                                │ │
│  │ │   ├── login/page.tsx       # Sign in page               │ │
│  │ │   └── signup/page.tsx      # Registration page          │ │
│  │ ├── dashboard/                                             │ │
│  │ │   └── page.tsx             # Main task list (protected) │ │
│  │ ├── components/                                            │ │
│  │ │   ├── TaskList.tsx         # Task display component     │ │
│  │ │   ├── TaskForm.tsx         # Create/Edit task form      │ │
│  │ │   └── TaskItem.tsx         # Individual task component  │ │
│  │ ├── lib/                                                   │ │
│  │   ├── api-client.ts          # Centralized API wrapper    │ │
│  │   ├── auth.ts                # Better Auth client config  │ │
│  │   └── session.ts             # Session helpers            │ │
│  │ ├── middleware.ts            # JWT validation, redirects  │ │
│  │ └── layout.tsx               # Root layout                │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP (JSON)
                  │ Authorization: Bearer <JWT>
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ app/                                                       │ │
│  │ ├── main.py                  # FastAPI app, CORS, startup │ │
│  │ ├── models.py                # SQLModel User, Task models │ │
│  │ ├── database.py              # Async engine, session      │ │
│  │ ├── middleware/                                            │ │
│  │ │   └── auth.py              # JWT verification decorator │ │
│  │ ├── routers/                                               │ │
│  │ │   ├── auth.py              # POST /auth/signup, /signin │ │
│  │ │   └── tasks.py             # CRUD /users/{id}/tasks/*   │ │
│  │ ├── schemas.py               # Pydantic request/response  │ │
│  │ └── config.py                # Settings from env vars     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────────┘
                  │ SQLModel (async)
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              Neon PostgreSQL (Serverless)                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Tables:                                                    │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ users                                               │  │ │
│  │  │ - id (UUID, PK)                                     │  │ │
│  │  │ - email (VARCHAR, UNIQUE)                           │  │ │
│  │  │ - password_hash (VARCHAR)                           │  │ │
│  │  │ - created_at (TIMESTAMP)                            │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ tasks                                               │  │ │
│  │  │ - id (SERIAL, PK)                                   │  │ │
│  │  │ - user_id (UUID, FK → users.id)                     │  │ │
│  │  │ - title (VARCHAR(200))                              │  │ │
│  │  │ - description (TEXT, nullable)                      │  │ │
│  │  │ - completed (BOOLEAN, default=false)                │  │ │
│  │  │ - created_at (TIMESTAMP, default=now())             │  │ │
│  │  │ - updated_at (TIMESTAMP, default=now())             │  │ │
│  │  │ INDEX on user_id                                    │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Constitution Check

### Compliance Review

**✅ Spec-First Development**
- Implementation plan follows approved spec 001-web-app-auth
- All requirements documented before code
- User stories prioritized (P0-P3)

**✅ AI-Native Architecture**
- All code generation by Claude Code
- Context7 MCP server for documentation
- No manual coding

**✅ Cloud-Native Design**
- Stateless backend (JWT authentication)
- Serverless database (Neon PostgreSQL)
- Horizontally scalable (stateless FastAPI)
- Containerization deferred to Phase IV (per constitution)

**✅ Progressive Enhancement**
- Extends Phase 1 features (Basic Level CRUD)
- Adds authentication and persistence
- Phase 1 code remains untouched in ../phase1/

**✅ Code Quality Standards**
- Type hints required (TypeScript + Python)
- Async/await for all I/O (database, API calls)
- Error handling on every external call
- Zero hardcoded credentials (env vars: DATABASE_URL, BETTER_AUTH_SECRET)

**✅ Database Standards**
- SQLModel for all ORM operations
- Migrations tracked (Alembic integration)
- Foreign keys enforced (tasks.user_id → users.id)
- Indexes on user_id and email

**✅ API Design Standards**
- RESTful conventions (GET/POST/PUT/DELETE)
- JWT authentication on all endpoints
- JSON responses with consistent error structure: `{"error": {"code": str, "message": str}}`
- User isolation enforced at query level (WHERE user_id = ?)

### Deviations
None. Phase 2 fully complies with constitution.

## Project Structure

```
phase2/
├── frontend/                    # Next.js 16+ App Router
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskItem.tsx
│   │   ├── lib/
│   │   │   ├── api-client.ts
│   │   │   ├── auth.ts
│   │   │   └── types.ts
│   │   ├── middleware.ts
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── public/
│   ├── .env.local
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   └── CLAUDE.md
│
├── backend/                     # FastAPI + SQLModel
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   ├── middleware/
│   │   │   └── auth.py
│   │   └── routers/
│   │       ├── auth.py
│   │       └── tasks.py
│   ├── migrations/              # Alembic migrations
│   ├── .env
│   ├── pyproject.toml
│   └── CLAUDE.md
│
└── specs/
    └── 001-web-app-auth/
        ├── spec.md              # ✅ Created
        ├── plan.md              # 📝 This file
        ├── tasks.md             # ⏳ Next step
        └── checklists/
```

## Design Decisions

### Decision 1: Authentication Architecture

**Options Considered**:
1. **Better Auth with JWT** (chosen)
2. NextAuth.js with session tokens
3. Custom JWT implementation
4. Session-based with Redis

**Trade-offs**:
- **Better Auth JWT**: Framework-agnostic, works with both Next.js and FastAPI, stateless, constitution-mandated
- **NextAuth**: Next.js-specific, doesn't work with FastAPI backend
- **Custom JWT**: Full control, but error-prone and not constitution-compliant
- **Session-based**: Requires shared state (Redis), not stateless

**Decision**: Use **Better Auth with JWT plugin**

**Rationale**:
- Constitution mandates Better Auth (specified in required stack)
- JWT is stateless (cloud-native requirement)
- Works across frontend (Next.js) and backend (FastAPI)
- Better Auth handles password hashing, token generation, validation
- Plugin ecosystem supports future enhancements (2FA, social auth)

**Implementation**:
- Frontend: Better Auth client issues JWT on login, stores in httpOnly cookie
- Backend: FastAPI middleware verifies JWT signature and extracts user_id
- Shared secret: BETTER_AUTH_SECRET environment variable (same value both sides)

---

### Decision 2: Database ORM Strategy

**Options Considered**:
1. **SQLModel with async** (chosen)
2. SQLAlchemy 2.0 with async
3. Raw SQL with asyncpg
4. Prisma ORM

**Trade-offs**:
- **SQLModel**: Combines SQLAlchemy + Pydantic, FastAPI-native, type-safe, async support
- **SQLAlchemy**: More mature, but verbose, lacks Pydantic integration
- **Raw SQL**: Maximum control, but no type safety, manual mapping
- **Prisma**: TypeScript-first, doesn't work with Python backend

**Decision**: Use **SQLModel with async operations**

**Rationale**:
- Constitution mandates SQLModel
- Pydantic integration: Models serve as both ORM and API schemas
- Type safety: Full type hints for database operations
- Async support: Non-blocking I/O (constitution requirement)
- FastAPI native: Designed by same author (Sebastián Ramírez)

**Implementation**:
```python
from sqlmodel import SQLModel, Field, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### Decision 3: API Endpoint Structure

**Options Considered**:
1. **Nested user resource**: `/api/users/{user_id}/tasks` (chosen)
2. Flat structure: `/api/tasks` (filter by user_id in query)
3. JWT-only: `/api/tasks` (user_id from JWT only)

**Trade-offs**:
- **Nested**: Explicit ownership in URL, clear resource hierarchy, easy to validate path vs JWT
- **Flat with query**: Simpler URLs, but ownership less explicit
- **JWT-only**: Most flexible, but harder to validate user_id mismatch

**Decision**: Use **nested user resource structure**

**Rationale**:
- Explicit ownership: `/api/users/{user_id}/tasks` clearly shows resource belongs to user
- Security: Can validate path user_id matches JWT user_id (prevents user A accessing user B's tasks via URL manipulation)
- RESTful: Follows REST sub-resource pattern
- Per user request: "API routes must include {user_id} in path"

**Implementation**:
```python
@router.get("/users/{user_id}/tasks")
async def get_tasks(user_id: str, current_user: User = Depends(get_current_user)):
    # Validate path user_id matches JWT user_id
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Query tasks filtered by user_id
    tasks = await session.exec(select(Task).where(Task.user_id == user_id))
    return tasks.all()
```

---

### Decision 4: Frontend State Management

**Options Considered**:
1. **React hooks + Context API** (chosen)
2. Redux Toolkit
3. Zustand
4. TanStack Query (React Query)

**Trade-offs**:
- **React hooks**: Built-in, simple, no dependencies, good for small-medium apps
- **Redux**: Powerful, but overkill for Phase 2 scope
- **Zustand**: Lightweight, but adds dependency
- **TanStack Query**: Best for server state, but adds complexity

**Decision**: Use **React hooks (useState, useEffect) + Context API**

**Rationale**:
- Simplicity: Phase 2 has limited state (task list, current user)
- No external dependencies: Aligns with "keep it simple" principle
- Built-in: No additional libraries to learn
- Sufficient: Can manage task CRUD and auth state easily
- Upgrade path: Can add TanStack Query in Phase 3 if needed

**Implementation**:
```typescript
// app/lib/AuthContext.tsx
const AuthContext = createContext<{user: User | null, signOut: () => void}>(...)

// app/dashboard/page.tsx
const [tasks, setTasks] = useState<Task[]>([])

useEffect(() => {
  fetchTasks().then(setTasks)
}, [])
```

---

### Decision 5: Database Migration Strategy

**Options Considered**:
1. **Alembic migrations** (chosen)
2. SQLModel.metadata.create_all() (no migrations)
3. Custom migration scripts

**Trade-offs**:
- **Alembic**: Industry standard, tracks schema changes, supports rollback
- **create_all()**: Simple for dev, but no migration history, unsafe for production
- **Custom**: Full control, but reinventing wheel

**Decision**: Use **Alembic for database migrations**

**Rationale**:
- Constitution requirement: "Migrations tracked in /migrations"
- Schema evolution: Phase 3+ will add more fields (priorities, tags, due_dates)
- Rollback support: Can revert schema changes if needed
- Production-ready: Safe for Neon PostgreSQL in production
- SQLModel integration: Alembic works well with SQLModel

**Implementation**:
```bash
# Initialize Alembic
alembic init migrations

# Generate migration
alembic revision --autogenerate -m "Create users and tasks tables"

# Apply migration
alembic upgrade head
```

## Implementation Phases

### Phase 0: Project Setup & Configuration
**Goal**: Initialize frontend and backend projects with all dependencies

**Frontend Setup**:
- Initialize Next.js 16+ with App Router using `npx create-next-app@latest`
- Install dependencies: `better-auth`, `tailwindcss`
- Configure TypeScript, Tailwind CSS
- Create .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000, BETTER_AUTH_SECRET
- Create CLAUDE.md in frontend/

**Backend Setup**:
- Initialize FastAPI project with UV: `uv init backend`
- Add dependencies to pyproject.toml: fastapi, sqlmodel, asyncpg, python-jose, passlib, alembic
- Configure .env with DATABASE_URL, BETTER_AUTH_SECRET
- Create CLAUDE.md in backend/

**Validation**: Both projects initialize, dependencies install, env files configured

---

### Phase 1: Database Models & Migrations (P0 - Foundation)
**Goal**: Define User and Task models, create database schema

**Backend Changes**:
- **app/models.py**:
  - Define User model (id UUID, email unique, password_hash, created_at)
  - Define Task model (id serial, user_id FK, title, description, completed, created_at, updated_at)
  - Add relationship: User.tasks (back-populate)

- **app/database.py**:
  - Create async engine: `create_async_engine(DATABASE_URL)`
  - Create async session maker
  - Define get_session() dependency

- **migrations/**:
  - Initialize Alembic: `alembic init migrations`
  - Configure env.py to use SQLModel.metadata
  - Generate initial migration: "Create users and tasks tables"
  - Apply migration: `alembic upgrade head`

**Validation**: Run migrations, verify tables exist in Neon database, check indexes created

---

### Phase 2: Backend Authentication (P0 - Foundation)
**Goal**: Implement user registration and sign-in with JWT

**Backend Changes**:
- **app/config.py**:
  - Load BETTER_AUTH_SECRET from env
  - Configure JWT settings (algorithm HS256, expiration 7 days)

- **app/schemas.py**:
  - UserCreate schema (email, password)
  - UserResponse schema (id, email, created_at)
  - TokenResponse schema (access_token, token_type)

- **app/routers/auth.py**:
  - POST /auth/signup: Create user, hash password, return user
  - POST /auth/signin: Validate credentials, issue JWT with user_id claim
  - Use Better Auth or python-jose for JWT generation

- **app/middleware/auth.py**:
  - create_access_token(user_id) function
  - verify_token(token) function
  - get_current_user() dependency (extracts user_id from JWT)

**Validation**: Call /auth/signup, verify user created; call /auth/signin, verify JWT returned

---

### Phase 3: Backend Task CRUD (P1-P3)
**Goal**: Implement all task operations with user ownership enforcement

**Backend Changes**:
- **app/routers/tasks.py**:
  - GET /users/{user_id}/tasks: List user's tasks (filtered by user_id, ordered by created_at desc)
  - POST /users/{user_id}/tasks: Create task (associate with user_id)
  - PUT /users/{user_id}/tasks/{task_id}: Update task (ownership check)
  - DELETE /users/{user_id}/tasks/{task_id}: Delete task (ownership check)
  - PATCH /users/{user_id}/tasks/{task_id}/complete: Toggle completion (ownership check)

- **app/schemas.py**:
  - TaskCreate schema (title, description optional)
  - TaskUpdate schema (title optional, description optional)
  - TaskResponse schema (all fields)

- **Ownership Validation**:
  - Every endpoint validates: path user_id == JWT user_id
  - Every query includes: WHERE task.user_id = current_user.id
  - Returns 403 if mismatch, 404 if task not found

**Validation**: Create task via API, verify persisted; attempt to access other user's task, verify 403

---

### Phase 4: Frontend Authentication UI (P0)
**Goal**: Sign up, sign in, sign out pages with Better Auth

**Frontend Changes**:
- **app/lib/auth.ts**:
  - Configure Better Auth client
  - Export authClient with signup, signin, signout methods

- **app/(auth)/signup/page.tsx**:
  - Form: email, password inputs
  - Client-side validation (email format, password min 8 chars)
  - Call authClient.signup() on submit
  - Redirect to /dashboard on success
  - Display errors from API

- **app/(auth)/login/page.tsx**:
  - Form: email, password inputs
  - Call authClient.signin() on submit
  - Store JWT in httpOnly cookie (handled by Better Auth)
  - Redirect to /dashboard on success

- **app/middleware.ts**:
  - Protected routes: ['/dashboard']
  - Public routes: ['/login', '/signup', '/']
  - Decrypt session from cookie
  - Redirect to /login if accessing protected route without session
  - Redirect to /dashboard if accessing public route with session

**Validation**: Sign up new user, verify redirected to dashboard; sign out, verify redirected to landing; try to access /dashboard without auth, verify redirected to /login

---

### Phase 5: Frontend Task UI (P1-P3)
**Goal**: Task list, create, edit, delete, complete toggle

**Frontend Changes**:
- **app/lib/api-client.ts**:
  - Centralized fetch wrapper
  - Automatically includes JWT in Authorization header
  - Handles 401 (redirect to login), 403 (show error), 500 (show error)
  - Methods: getTasks(), createTask(), updateTask(), deleteTask(), toggleComplete()

- **app/dashboard/page.tsx**:
  - Fetch tasks on mount using api-client
  - Display TaskList component
  - Display TaskForm component (for creating)
  - Handle loading and error states

- **app/components/TaskList.tsx**:
  - Map over tasks array
  - Render TaskItem for each task
  - Empty state: "No tasks yet. Create your first task!"

- **app/components/TaskForm.tsx**:
  - Controlled form with title, description inputs
  - Validation: title required (1-200 chars), description max 1000 chars
  - onSubmit: call api-client.createTask()
  - Clear form on success

- **app/components/TaskItem.tsx**:
  - Display task with checkbox, title, description preview
  - Edit button → show inline edit form or modal
  - Delete button → confirm, call api-client.deleteTask()
  - Checkbox → call api-client.toggleComplete()

**Validation**: Create task, verify appears in list; edit task, verify updated; delete task, verify removed; toggle complete, verify checkbox state

---

### Phase 6: Integration & Polish
**Goal**: End-to-end functionality, CORS, error handling, README

**Backend Changes**:
- **app/main.py**:
  - Add CORS middleware: allow origin localhost:3000
  - Add exception handlers for 404, 500
  - Add startup event: verify database connection

**Frontend Changes**:
- **Styling**: Tailwind CSS for clean, responsive UI
- **Error boundaries**: React error boundary for graceful degradation
- **Loading states**: Skeletons or spinners during API calls

**Documentation**:
- **phase2/README.md**:
  - Setup instructions (install dependencies, env vars, run migrations, start both servers)
  - Architecture diagram
  - API documentation
  - Development workflow

**Validation**: Full workflow test (signup → signin → create task → view → update → delete → signout)

## Testing Strategy

### Manual Validation (Phase 2 approach)

**Authentication Tests**:
1. Sign up with valid email/password → verify account created
2. Sign up with duplicate email → verify error "Email already registered"
3. Sign in with correct credentials → verify JWT received, redirected to dashboard
4. Sign in with wrong password → verify error "Invalid credentials"
5. Access /dashboard without auth → verify redirected to /login
6. Sign out → verify JWT cleared, redirected to landing page

**Task CRUD Tests**:
1. Create task "Buy groceries" → verify appears in list
2. Create task with description → verify description preview (50 chars) shown
3. View task list → verify ordered by created_at descending
4. Edit task title → verify updated in list
5. Delete task → verify removed from list
6. Toggle task complete → verify checkbox checked
7. Toggle task incomplete → verify checkbox unchecked

**User Isolation Tests**:
1. User A creates 5 tasks, User B creates 3 tasks
2. User A views dashboard → verify sees only 5 tasks (not User B's)
3. User A attempts to access User B's task via direct API call → verify 403 Forbidden

**Error Handling Tests**:
1. Submit empty title → verify validation error
2. Submit 201-character title → verify validation error
3. Disconnect database → verify 500 error with friendly message
4. Use expired JWT → verify 401, redirected to login

## Dependencies

### Requires
- **Phase 1 Complete**: Console app fully implemented (baseline for features)
- **Neon Database**: PostgreSQL instance provisioned with connection string
- **Node.js 18+**: For Next.js frontend
- **Python 3.13+**: For FastAPI backend
- **UV**: Python package manager

### Blocks
- **Phase 3**: AI Chatbot cannot start until web app foundation exists

### Related
- **Phase 1**: Feature baseline (5 Basic Level CRUD operations)
- **Future Phases**: Will build on this authentication and persistence foundation

## Risks and Mitigations

### Risk 1: JWT Secret Mismatch Between Frontend and Backend
**Probability**: Medium
**Impact**: High (authentication breaks entirely)
**Mitigation**:
- Use same BETTER_AUTH_SECRET value in both .env files
- Document clearly in README
- Add startup validation: backend logs "JWT secret configured: [first 4 chars]..."
- Frontend/backend integration test to verify token validation works

### Risk 2: CORS Configuration Errors
**Probability**: Medium
**Impact**: High (frontend cannot call backend API)
**Mitigation**:
- Configure CORS in FastAPI main.py with explicit origin: localhost:3000
- Allow credentials: True (for cookies)
- Test with browser DevTools Network tab
- Document CORS setup in README

### Risk 3: Database Connection Issues (Neon)
**Probability**: Low
**Impact**: High (app unusable without database)
**Mitigation**:
- Verify DATABASE_URL format: postgresql+asyncpg://...
- Add connection test on backend startup
- Provide clear error messages: "Database connection failed: check DATABASE_URL"
- Document Neon setup steps in README

### Risk 4: Async/Await Confusion (SQLModel)
**Probability**: Medium
**Impact**: Medium (runtime errors, blocking I/O)
**Mitigation**:
- Use async def for all database operations
- Use AsyncSession, not Session
- Always await database calls
- Context7 documentation for async patterns

### Risk 5: User Isolation Bugs (Security)
**Probability**: Medium
**Impact**: Critical (users see each other's data)
**Mitigation**:
- Double-check every query has WHERE user_id = current_user.id
- Validate path user_id matches JWT user_id in every endpoint
- Manual testing with 2 different user accounts
- Add integration test: User A cannot access User B's tasks

## Success Criteria

### Implementation Complete When
- [ ] All 4 user stories (US1-US4) implemented and tested
- [ ] All 40 functional requirements (FR-001 to FR-040) met
- [ ] All 15 success criteria (SC-001 to SC-015) verified
- [ ] All edge cases handled correctly
- [ ] Database schema matches spec
- [ ] Full workflow demo completes in <90 seconds
- [ ] Context7 documentation consulted for all major patterns

### Code Quality Checklist
- [ ] TypeScript types on all frontend code
- [ ] Python type hints on all backend code
- [ ] Async/await for all database operations
- [ ] Error handling on all API calls
- [ ] JWT validation on all protected endpoints
- [ ] User ownership checks on all task operations
- [ ] Environment variables for all secrets
- [ ] README with setup instructions

## Next Steps

1. **Create tasks.md**: Break down plan into specific implementation tasks (~120 tasks)
2. **Run `/sp.implement`**: Execute all tasks using Claude Code + Context7
3. **Manual validation**: Test all acceptance scenarios with 2 user accounts
4. **Create demo**: Show full workflow in <90 seconds
5. **Deploy** (optional): Vercel (frontend) + Neon (database, already hosted)
6. **Commit**: `feat: implement Phase 2 full-stack web app with auth and persistence`

---

**Plan Version**: 1.0
**Estimated Complexity**: High (full-stack, authentication, database, frontend + backend)
**Estimated Tasks**: ~120 tasks across 6 phases
**Estimated Time**: ~15 hours (single developer, sequential)
**Context7 Resources**: Next.js App Router, Better Auth JWT, FastAPI, SQLModel
