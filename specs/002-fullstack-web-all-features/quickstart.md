# Quickstart Guide - Phase II: Full-Stack Todo Application

**Feature**: Full-Stack Todo Web Application (All Features)
**Branch**: 002-fullstack-web-all-features
**Last Updated**: 2026-01-01

This guide helps developers set up the Phase II todo application locally and understand the deployment pipeline.

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.13+** (`python --version`)
- **UV** package manager ([installation](https://github.com/astral-sh/uv))
- **Node.js 20+** (`node --version`)
- **Git** (`git --version`)
- **Database**: Neon PostgreSQL connection string (provided)
- **Editor**: VS Code or any IDE with TypeScript support

---

## Project Structure

```
/phase2/
├── frontend/                 # Next.js 16 frontend
│   ├── app/
│   │   ├── (auth)/           # Authentication pages
│   │   │   ├── signin/
│   │   │   └── signup/
│   │   └── (protected)/      # Protected pages (require auth)
│   │       └── dashboard/
│   ├── components/
│   │   ├── tasks/            # Task-related components
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   ├── TaskFilters.tsx
│   │   │   └── TaskSearch.tsx
│   │   └── ui/               # Reusable UI components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Modal.tsx
│   │       ├── Badge.tsx
│   │       ├── DatePicker.tsx
│   │       └── Toast.tsx
│   ├── lib/
│   │   ├── api.ts            # API client with JWT handling
│   │   └── auth.ts           # Better Auth configuration
│   ├── types/
│   │   └── api.ts            # TypeScript types (from contracts/)
│   ├── .env.local            # Environment variables
│   ├── package.json
│   └── next.config.js
│
├── backend/                  # FastAPI backend
│   ├── main.py               # FastAPI app initialization
│   ├── models.py             # SQLModel entities (User, Task, Notification)
│   ├── routes/
│   │   ├── tasks.py          # Task CRUD endpoints
│   │   └── notifications.py  # Notification endpoints
│   ├── services/
│   │   ├── task_service.py   # Business logic (create_next_occurrence)
│   │   └── reminder_service.py # APScheduler reminder job
│   ├── auth.py               # JWT middleware (get_current_user)
│   ├── db.py                 # Database connection (Neon)
│   ├── .env                  # Environment variables
│   ├── pyproject.toml        # UV dependencies
│   └── migrations/           # Alembic migrations
│       └── versions/
│
└── specs/                    # Planning artifacts (read-only for code)
    ├── spec.md
    ├── plan.md
    ├── tasks.md
    ├── research.md
    ├── data-model.md
    └── contracts/
        ├── openapi.yaml
        └── types.ts
```

---

## Setup Instructions

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd hackathon_02
git checkout 002-fullstack-web-all-features
```

### 2. Backend Setup

#### a. Navigate to backend directory
```bash
cd phase2/backend
```

#### b. Create virtual environment with UV
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### c. Install dependencies
```bash
uv pip install fastapi sqlmodel uvicorn python-jose python-dotenv apscheduler alembic psycopg2-binary
```

#### d. Configure environment variables
Create `phase2/backend/.env`:
```env
# Database
DATABASE_URL=postgresql://neondb_owner:npg_BgPz4iroO6Lb@ep-square-rice-agd7ah2g-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-here-minimum-32-chars

# CORS
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app

# Server
PORT=8000
```

**Generate BETTER_AUTH_SECRET:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### e. Run database migrations
```bash
alembic upgrade head
```

#### f. Start backend server
```bash
uvicorn main:app --reload --port 8000
```

Server running at: http://localhost:8000
API docs: http://localhost:8000/docs (auto-generated from OpenAPI)

---

### 3. Frontend Setup

#### a. Navigate to frontend directory (new terminal)
```bash
cd phase2/frontend
```

#### b. Install dependencies
```bash
npm install
# or
pnpm install
```

#### c. Configure environment variables
Create `phase2/frontend/.env.local`:
```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
NEXT_PUBLIC_BETTER_AUTH_URL=/api/auth
BETTER_AUTH_SECRET=<same-secret-as-backend>

# Optional: Production URLs
# NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

#### d. Copy TypeScript types
```bash
cp ../specs/contracts/types.ts types/api.ts
```

#### e. Start frontend dev server
```bash
npm run dev
```

Frontend running at: http://localhost:3000

---

## Verify Installation

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### 2. Check Database Connection
```bash
# From backend directory
python -c "from db import engine; from sqlmodel import Session; session = Session(engine); print('Connected!')"
```

### 3. Test Authentication Flow
1. Navigate to http://localhost:3000/signup
2. Create account: test@example.com / password123
3. Verify redirect to /dashboard
4. Check browser DevTools → Application → Cookies for `auth-token`

### 4. Test Task Creation
1. On dashboard, click "Add Task"
2. Enter title: "Test Task"
3. Submit form
4. Verify task appears in list

---

## Development Workflow

### 1. Making Code Changes

**Frontend (Next.js):**
- Edit components in `phase2/frontend/components/`
- Hot reload active (changes apply immediately)
- Check browser console for errors

**Backend (FastAPI):**
- Edit routes/models in `phase2/backend/`
- Uvicorn auto-reloads on file save
- Check terminal output for errors

### 2. Database Migrations

When changing `models.py`:

```bash
cd phase2/backend

# Generate migration
alembic revision --autogenerate -m "Add field to Task"

# Review generated migration in migrations/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### 3. API Documentation

FastAPI auto-generates docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

Test endpoints directly in Swagger UI (with JWT authentication).

### 4. Testing Reminders

Background job runs every 60 seconds. To test:

```bash
# 1. Create task with due date 2 minutes from now
# 2. Set reminder offset to 60 minutes (but test with 1 minute)
# 3. Wait 1 minute
# 4. Poll /api/{user_id}/notifications
# 5. Verify notification appears
```

**Trigger manually (dev only):**
```bash
cd phase2/backend
python -c "from services.reminder_service import check_reminders; check_reminders()"
```

---

## Deployment

### Frontend Deployment (Vercel)

#### 1. Connect Repository
1. Go to https://vercel.com/new
2. Import Git repository
3. Select `phase2/frontend` as root directory
4. Framework preset: Next.js
5. Add environment variables (from `.env.local`)
6. Deploy

#### 2. Configure Environment
In Vercel dashboard → Settings → Environment Variables:
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
BETTER_AUTH_SECRET=<your-secret>
NEXT_PUBLIC_BETTER_AUTH_URL=/api/auth
```

#### 3. Update CORS in Backend
Add Vercel URL to `CORS_ORIGINS` in backend `.env`.

---

### Backend Deployment (Railway)

#### 1. Create New Project
1. Go to https://railway.app
2. New Project → Deploy from GitHub repo
3. Select repository
4. Set root directory: `phase2/backend`

#### 2. Configure Environment
In Railway dashboard → Variables:
```
DATABASE_URL=<neon-connection-string>
BETTER_AUTH_SECRET=<your-secret>
CORS_ORIGINS=https://your-app.vercel.app
PORT=8000
```

#### 3. Configure Build
Railway auto-detects Python. Create `phase2/backend/Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 4. Run Migrations on Deploy
Add to Railway → Settings → Deploy → Build Command:
```bash
alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 5. Test Production API
```bash
curl https://your-backend.railway.app/health
```

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'sqlmodel'"
**Solution:**
```bash
cd phase2/backend
uv pip install sqlmodel
```

### Issue: "Database connection failed"
**Solution:**
1. Verify Neon connection string in `.env`
2. Check Neon dashboard for connection status
3. Ensure `-pooler` suffix in connection string (required for serverless)

### Issue: "CORS error in browser"
**Solution:**
1. Check `CORS_ORIGINS` in backend `.env`
2. Ensure frontend URL (with port) is included
3. Restart backend server after changing CORS

### Issue: "JWT token invalid"
**Solution:**
1. Verify `BETTER_AUTH_SECRET` matches in frontend and backend
2. Clear browser cookies and re-login
3. Check token expiration (7 days)

### Issue: "Reminders not triggering"
**Solution:**
1. Verify APScheduler is running (check backend logs for "Scheduler started")
2. Test manually: `python -c "from services.reminder_service import check_reminders; check_reminders()"`
3. Check `due_date` and `reminder_offset_minutes` in database

### Issue: "Next.js build fails on Vercel"
**Solution:**
1. Ensure TypeScript types have no errors: `npm run build` locally
2. Check `next.config.js` for correct configuration
3. Verify environment variables in Vercel dashboard

---

## Useful Commands

### Backend

```bash
# Start server
uvicorn main:app --reload --port 8000

# Start with debug logging
uvicorn main:app --reload --log-level debug

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Rollback migration
alembic downgrade -1

# Open Python shell with DB session
python
>>> from db import engine
>>> from sqlmodel import Session, select
>>> from models import Task
>>> session = Session(engine)
>>> tasks = session.exec(select(Task)).all()
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run TypeScript type check
npm run type-check

# Run linter
npm run lint

# Format code
npm run format
```

### Database

```bash
# Connect to Neon via psql
psql "postgresql://neondb_owner:npg_BgPz4iroO6Lb@ep-square-rice-agd7ah2g-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Query tasks
SELECT id, title, completed FROM tasks ORDER BY created_at DESC LIMIT 10;

# Check notifications
SELECT * FROM notifications WHERE read = false;

# View recurrence data (JSONB)
SELECT title, recurrence FROM tasks WHERE recurrence IS NOT NULL;
```

---

## API Testing with cURL

### Create Task
```bash
# Get JWT token from browser cookies (auth-token)
export TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8000/api/usr_abc123xyz/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Created via cURL",
    "priority": "high",
    "tags": ["test", "api"]
  }'
```

### List Tasks
```bash
curl http://localhost:8000/api/usr_abc123xyz/tasks?status=pending \
  -H "Authorization: Bearer $TOKEN"
```

### Toggle Complete
```bash
curl -X PATCH http://localhost:8000/api/usr_abc123xyz/tasks/1/complete \
  -H "Authorization: Bearer $TOKEN"
```

### Get Notifications
```bash
curl http://localhost:8000/api/usr_abc123xyz/notifications?read=false \
  -H "Authorization: Bearer $TOKEN"
```

---

## Performance Monitoring

### Backend Metrics

**Response Times:**
```bash
# Add timing middleware in main.py
import time
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

**Database Query Logging:**
```python
# In db.py
engine = create_engine(DATABASE_URL, echo=True)  # Logs all queries
```

### Frontend Metrics

**Next.js Analytics:**
```bash
npm install @vercel/analytics
```

In `app/layout.tsx`:
```tsx
import { Analytics } from '@vercel/analytics/react'
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

---

## Next Steps

After setup is complete:

1. **Read Planning Artifacts**:
   - `specs/spec.md` - Feature requirements
   - `specs/data-model.md` - Database schema
   - `specs/contracts/openapi.yaml` - API specification

2. **Review Architecture**:
   - `specs/research.md` - Technology decisions
   - `specs/plan.md` - Implementation strategy (when generated)

3. **Start Implementation**:
   - Follow `specs/tasks.md` (when generated)
   - Use `/sp.implement` command to execute tasks

4. **Test Locally**:
   - Verify all 7 user stories work
   - Check edge cases from spec.md

5. **Deploy**:
   - Push to GitHub
   - Vercel auto-deploys frontend
   - Railway auto-deploys backend

---

## Support

**Documentation:**
- Next.js: https://nextjs.org/docs
- FastAPI: https://fastapi.tiangolo.com
- SQLModel: https://sqlmodel.tiangolo.com
- Better Auth: https://www.better-auth.com/docs

**Issues:**
- Project issues: [GitHub Issues]
- Neon database: https://neon.tech/docs
- Vercel deployment: https://vercel.com/docs
- Railway deployment: https://docs.railway.app

**Quick Links:**
- API Docs (local): http://localhost:8000/docs
- Frontend (local): http://localhost:3000
- Neon Console: https://console.neon.tech
- Vercel Dashboard: https://vercel.com/dashboard
- Railway Dashboard: https://railway.app/dashboard
