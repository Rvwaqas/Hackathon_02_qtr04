# Phase 0: Research & Technology Decisions

**Feature**: Full-Stack Todo Web Application (All Features)
**Branch**: 002-fullstack-web-all-features
**Date**: 2026-01-01

## Executive Summary

This document captures all technology decisions, research findings, and architectural choices for Phase II of the Evolution of Todo hackathon project. All decisions align with the project constitution and prioritize AI-native development, cloud-native design, and progressive enhancement.

---

## Decision 1: Monorepo vs Separate Repositories

**Decision**: Monorepo structure (`/phase2/frontend` + `/phase2/backend`)

**Rationale**:
- Claude Code can see entire project structure in single context window
- Easier cross-stack changes (e.g., updating API contract requires seeing both frontend and backend)
- Simplified deployment configuration (single repo to clone)
- Aligns with hackathon timeframe - reduces coordination overhead
- Follows project's file structure standards (constitution.md:109-134)

**Alternatives Considered**:
1. **Separate repos** (frontend, backend) - Better for large teams, but adds overhead for AI agent coordination
2. **Turborepo/Nx monorepo** - Overkill for 2-component structure
3. **Git submodules** - Complexity without benefit

**Trade-offs**:
- Pro: Single source of truth, atomic commits across stack
- Con: Larger repo size, but negligible for this project

---

## Decision 2: Frontend Framework - Next.js 16 (App Router)

**Decision**: Next.js 16 with App Router, TypeScript, and Tailwind CSS

**Rationale**:
- **Next.js 16**: Latest stable version (required by constitution.md:93)
- **App Router**: Server components by default, better performance
- **TypeScript**: Required by constitution (type hints mandatory, constitution.md:66)
- **Tailwind CSS**: Utility-first, fast styling without CSS files
- **Vercel deployment**: Zero-config deployment (Next.js native platform)

**Alternatives Considered**:
1. **React (Vite)** - Fast, but manual SSR/routing setup
2. **Remix** - Great DX, but smaller ecosystem than Next.js
3. **SvelteKit** - Excellent performance, but team unfamiliar
4. **Vue/Nuxt** - Good options, but Next.js better documented for Better Auth

**Research Sources**:
- Next.js 16 docs: https://nextjs.org/docs (App Router patterns)
- Better Auth Next.js integration: https://www.better-auth.com/docs/integrations/nextjs
- Tailwind CSS with Next.js: https://tailwindcss.com/docs/guides/nextjs

**Trade-offs**:
- Pro: Server components reduce bundle size, SEO-ready (future marketing pages)
- Pro: Automatic code splitting, image optimization
- Con: App Router learning curve (but AI generates all code)

---

## Decision 3: Backend Framework - FastAPI + SQLModel

**Decision**: FastAPI with SQLModel ORM, Python 3.13+

**Rationale**:
- **FastAPI**: Async-first (required by constitution.md:67), automatic OpenAPI docs
- **SQLModel**: Combines SQLAlchemy ORM + Pydantic validation (required by constitution.md:72)
- **Python 3.13**: Latest stable, improved async performance
- **UV**: Fast package manager (required by constitution.md:92)
- **Type hints**: Native Python 3.10+ feature (constitution requirement)

**Alternatives Considered**:
1. **Django + DRF** - Full-featured, but heavy for API-only backend
2. **Flask** - Lightweight, but lacks async, manual OpenAPI
3. **Node.js (Express/Fastify)** - Good option, but constitution mandates Python
4. **Go (Gin/Echo)** - Excellent performance, but no Python type hints

**Research Sources**:
- FastAPI docs: https://fastapi.tiangolo.com/
- SQLModel docs: https://sqlmodel.tiangolo.com/
- FastAPI + Neon: https://neon.tech/docs/guides/fastapi

**Trade-offs**:
- Pro: Auto-generated API docs, Pydantic validation, async performance
- Pro: SQLModel reduces boilerplate (single model for DB + API)
- Con: Smaller ecosystem than Django, but sufficient for our needs

---

## Decision 4: Authentication - Better Auth (JWT Mode)

**Decision**: Better Auth with JWT provider, httpOnly cookies

**Rationale**:
- **Better Auth**: Modern auth library, Next.js + FastAPI support (constitution.md:96)
- **JWT mode**: Stateless tokens enable horizontal scaling
- **httpOnly cookies**: Most secure storage (XSS-resistant)
- **7-day expiration**: Balance between security and UX (constitution.md:152)

**Alternatives Considered**:
1. **NextAuth.js** - Popular, but Better Auth has better FastAPI integration
2. **Clerk** - SaaS, but requires paid plan for production
3. **Auth0** - Enterprise-grade, overkill for hackathon
4. **Manual JWT** - Reinventing the wheel, error-prone

**JWT Storage Options**:
1. **httpOnly cookie (chosen)**: Secure, auto-sent with requests, XSS-resistant
2. **localStorage**: Vulnerable to XSS attacks (constitution.md:103 prohibits)
3. **sessionStorage**: Lost on tab close, poor UX

**Research Sources**:
- Better Auth docs: https://www.better-auth.com/docs
- Better Auth JWT: https://www.better-auth.com/docs/concepts/jwt
- OWASP JWT security: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html

**Trade-offs**:
- Pro: Stateless (no session store), scalable, industry-standard
- Pro: Better Auth handles password hashing, token refresh automatically
- Con: Token revocation requires additional logic (blacklist), but not needed for Phase II

---

## Decision 5: Database - Neon Serverless PostgreSQL

**Decision**: Neon Serverless PostgreSQL with connection pooling

**Rationale**:
- **Already provisioned**: Connection string provided in requirements
- **Serverless**: Auto-scales to zero, cost-effective for hackathon
- **PostgreSQL 15**: JSONB support for tags/recurrence fields (required for FR-013, FR-025)
- **Connection pooling**: Built-in via `-pooler` endpoint (critical for serverless)
- **Required by constitution**: Neon specified (constitution.md:95)

**Connection String**:
```
postgresql://neondb_owner:npg_BgPz4iroO6Lb@ep-square-rice-agd7ah2g-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**Database Features Required**:
- **JSONB columns**: For tags (string array) and recurrence (object)
- **Timestamps**: `created_at`, `updated_at` (auto-managed)
- **Foreign keys**: `user_id`, `task_id`, `parent_task_id` (enforced at DB level)
- **Indexes**: On `user_id`, `due_date`, `completed` (constitution.md:75)

**Alternatives Considered**:
1. **Supabase PostgreSQL** - Good option, but Neon already configured
2. **PlanetScale (MySQL)** - No JSONB support
3. **MongoDB** - NoSQL, but constitution requires SQLModel (SQL-based)

**Research Sources**:
- Neon docs: https://neon.tech/docs/introduction
- PostgreSQL JSONB: https://www.postgresql.org/docs/current/datatype-json.html
- SQLModel + PostgreSQL: https://sqlmodel.tiangolo.com/databases/

**Trade-offs**:
- Pro: Generous free tier (500 MB storage), automatic backups
- Pro: JSONB enables flexible schema for tags/recurrence without joins
- Con: Cold starts (<1s), but acceptable for hackathon

---

## Decision 6: Real-Time Notifications - Polling (30s Interval)

**Decision**: HTTP polling every 30 seconds for notifications

**Rationale**:
- **Simplicity**: Single FastAPI endpoint `/api/{user_id}/notifications`
- **Acceptable latency**: 30s delay for reminders is acceptable (not chat app)
- **No additional infrastructure**: WebSockets require persistent connections
- **Constitution compliance**: Async I/O (constitution.md:67)

**Alternatives Considered**:
1. **WebSocket** - True real-time, but complex setup (needs Redis for multi-instance)
2. **Server-Sent Events (SSE)** - One-way streaming, good middle ground
3. **Push notifications** - Requires service worker, browser permissions
4. **Polling (chosen)** - Simple, works everywhere, sufficient for use case

**Implementation**:
```typescript
// Frontend: polling hook
useEffect(() => {
  const interval = setInterval(async () => {
    const notifications = await fetchNotifications(userId);
    setNotifications(notifications);
  }, 30000); // 30 seconds
  return () => clearInterval(interval);
}, [userId]);
```

**Research Sources**:
- Polling vs WebSocket: https://ably.com/topic/long-polling-vs-websockets
- FastAPI WebSocket docs: https://fastapi.tiangolo.com/advanced/websockets/

**Trade-offs**:
- Pro: No additional infrastructure, simple to implement/debug
- Pro: Survives server restarts (no connection state to manage)
- Con: 30s delay (acceptable for reminders), extra HTTP requests (negligible)

---

## Decision 7: Reminder Implementation - APScheduler

**Decision**: APScheduler background job running every 60 seconds

**Rationale**:
- **APScheduler**: Built-in Python library, no external dependencies
- **60-second interval**: Sufficient for reminder accuracy (FR-033)
- **Runs in-process**: No separate worker service needed
- **Constitution compliance**: Simplest solution (avoid over-engineering)

**Alternatives Considered**:
1. **Celery + Redis** - Production-grade, but overkill for Phase II
2. **AWS EventBridge** - Cloud-native, but adds AWS dependency
3. **Database triggers** - PostgreSQL could do this, but couples logic to DB
4. **APScheduler (chosen)** - Simple, sufficient, follows YAGNI principle

**Implementation**:
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', seconds=60)
def check_reminders():
    # Query tasks with due reminders
    # Create notification records
    pass

scheduler.start()  # In main.py startup
```

**Research Sources**:
- APScheduler docs: https://apscheduler.readthedocs.io/
- FastAPI background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/

**Trade-offs**:
- Pro: Zero infrastructure, simple debugging
- Pro: Survives restarts (state in DB, not memory)
- Con: Single instance only (fine for Phase II, migrate to Celery in Phase IV)
- Con: 60s resolution (vs cron's 1-minute minimum) - acceptable

---

## Decision 8: Tag Storage - JSONB Array

**Decision**: Store tags as PostgreSQL JSONB array in `tasks.tags` column

**Rationale**:
- **JSONB**: Native PostgreSQL type, queryable, indexable
- **Array format**: `["work", "urgent", "backend"]` - simple, sufficient
- **No joins**: Faster queries, simpler code
- **Constitution compliance**: Smallest viable solution

**Alternatives Considered**:
1. **Separate `tags` table + junction table** - Normalized, but premature optimization
2. **JSONB array (chosen)** - Simple, queryable, sufficient for Phase II
3. **Comma-separated string** - Not queryable, fragile
4. **PostgreSQL array type** - JSONB more flexible (can evolve to objects)

**Query Example**:
```python
# Find tasks with "work" tag
tasks = session.exec(
    select(Task)
    .where(Task.tags.contains(["work"]))  # SQLModel JSONB query
).all()
```

**Research Sources**:
- PostgreSQL JSONB operators: https://www.postgresql.org/docs/current/functions-json.html
- SQLModel JSON fields: https://sqlmodel.tiangolo.com/tutorial/json-fields/

**Trade-offs**:
- Pro: Simple schema, fast queries, indexable with GIN index
- Pro: Can migrate to normalized tags table in Phase III without breaking API
- Con: Tag analytics harder (e.g., "most used tags") - but not required in Phase II

---

## Decision 9: Recurring Task Logic - Parent-Child Model

**Decision**: Store recurring metadata in `Task.recurrence` JSONB, link occurrences via `parent_task_id`

**Rationale**:
- **Recurrence JSONB**: Flexible schema `{type: "daily", interval: 2, days: [1,3,5]}`
- **Parent-child link**: Audit trail, enables "show all occurrences" feature (future)
- **On-complete trigger**: When marking complete, check `recurrence` → create next occurrence
- **Constitution**: Smallest viable change (constitution.md principle)

**Recurrence Schema**:
```json
{
  "type": "daily" | "weekly" | "monthly",
  "interval": 1,  // Every N days/weeks/months
  "days": [1, 3, 5]  // For weekly: 1=Monday, 7=Sunday (optional)
}
```

**Alternatives Considered**:
1. **Cron expressions** - Powerful, but overkill and confusing UX
2. **RFC 5545 (iCalendar)** - Standard, but complex to implement
3. **Simple JSONB (chosen)** - Sufficient for daily/weekly/monthly recurrence

**Month-End Edge Case Handling**:
```python
# Jan 31 → Feb 28 (not Feb 31)
if due_date.day > 28 and next_month == 2:
    next_due = due_date.replace(month=2, day=28)
elif due_date.day == 31 and next_month in [4, 6, 9, 11]:
    next_due = due_date.replace(month=next_month, day=30)
```

**Research Sources**:
- Python dateutil: https://dateutil.readthedocs.io/en/stable/
- iCalendar RRULE: https://icalendar.org/iCalendar-RFC-5545/3-8-5-3-recurrence-rule.html (rejected)

**Trade-offs**:
- Pro: Simple to implement, covers 90% of use cases
- Pro: Parent-child model enables future "view recurring series" feature
- Con: Cannot express complex rules ("last Friday of month"), but not required

---

## Decision 10: Deployment Strategy

**Decision**:
- **Frontend**: Vercel (automatic deployments from Git)
- **Backend**: Railway or Render (free tier)
- **Database**: Neon (already provisioned)

**Rationale**:
- **Vercel**: Zero-config Next.js deployment, automatic HTTPS, preview deploys
- **Railway/Render**: Free tier supports Python, auto-deploy from Git, similar to Heroku
- **Neon**: Serverless PostgreSQL, no deployment needed (already running)
- **Constitution**: Cloud-native design (constitution.md:49-54)

**Deployment Flow**:
1. Push to `002-fullstack-web-all-features` branch
2. Vercel auto-deploys frontend to `https://hackathon-02-*.vercel.app`
3. Railway/Render auto-deploys backend to `https://hackathon-02-*.railway.app`
4. Configure environment variables (DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS)

**Alternatives Considered**:
1. **AWS (EC2 + RDS)** - Too complex, manual setup
2. **Google Cloud Run** - Good, but Railway simpler
3. **Docker Compose (self-hosted)** - For Phase IV with Kubernetes
4. **Vercel + Railway (chosen)** - Simplest, fastest, free tier

**Research Sources**:
- Vercel deployment: https://vercel.com/docs/deployments/overview
- Railway Python: https://docs.railway.app/guides/python
- Render Python: https://render.com/docs/deploy-fastapi

**Trade-offs**:
- Pro: Zero-downtime deploys, automatic HTTPS, environment management
- Pro: Free tier sufficient for demo (Railway: 500 hours/month, Render: 750 hours/month)
- Con: Cold starts on free tier (<2s), but acceptable for hackathon

---

## Decision 11: API Contract - RESTful with Standard Response Format

**Decision**: RESTful API with consistent response envelope

**Response Format**:
```typescript
// Success
{ data: Task | Task[] | null, error: null }

// Error
{ data: null, error: { message: string, code: string } }
```

**HTTP Status Codes**:
- **200 OK**: GET, PUT, PATCH success
- **201 Created**: POST success
- **400 Bad Request**: Validation error
- **401 Unauthorized**: Missing/invalid JWT
- **403 Forbidden**: Valid JWT, but not authorized (e.g., accessing other user's task)
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Unexpected error

**Rationale**:
- **RESTful**: Industry standard, predictable (constitution.md:77-81)
- **Response envelope**: Consistent structure, easy error handling in frontend
- **Consistent errors**: Frontend can handle all errors with single function

**Alternatives Considered**:
1. **GraphQL** - Flexible, but overkill for simple CRUD
2. **tRPC** - Type-safe, but requires TypeScript backend
3. **REST (chosen)** - Simple, well-understood, sufficient

**Research Sources**:
- REST API best practices: https://restfulapi.net/
- FastAPI response models: https://fastapi.tiangolo.com/tutorial/response-model/

**Trade-offs**:
- Pro: Every frontend dev understands REST, OpenAPI docs auto-generated
- Pro: Response envelope simplifies error handling
- Con: More endpoints than GraphQL (but clear separation of concerns)

---

## Decision 12: Frontend State Management - React Hooks + URL State

**Decision**: Use React hooks (useState, useEffect) and URL query params for state

**Rationale**:
- **React hooks**: Sufficient for small app (no global state needed)
- **URL state**: Filters/sort in query params enables deep linking
- **Server state**: Tasks fetched fresh on mount (no stale data)
- **Constitution**: Avoid over-engineering (simplest solution wins)

**State Locations**:
- **Local state** (useState): Form inputs, modals, loading flags
- **URL state**: Filters (status, priority, tag), sort (field, order), search query
- **Server state**: Tasks, notifications (fetched on demand)

**Alternatives Considered**:
1. **Redux/Zustand** - Global store, but overkill for simple app
2. **React Query** - Caching layer, good for large apps, but not needed
3. **Jotai/Recoil** - Atomic state, but no real benefit here
4. **React hooks + URL (chosen)** - Simple, no dependencies

**URL State Example**:
```typescript
// URL: /dashboard?status=pending&priority=high&sort=due_date&order=asc
const [searchParams, setSearchParams] = useSearchParams();
const status = searchParams.get('status') || 'all';
const priority = searchParams.get('priority') || 'all';
```

**Research Sources**:
- React hooks: https://react.dev/reference/react/hooks
- Next.js search params: https://nextjs.org/docs/app/api-reference/functions/use-search-params

**Trade-offs**:
- Pro: Simple, no learning curve, shareable URLs
- Pro: URL state persists on refresh
- Con: Manual sync between URL and UI (but Next.js makes this easy)

---

## Open Questions (Resolved)

All questions from Technical Context have been resolved:

1. **Authentication method**: Better Auth with JWT (httpOnly cookies)
2. **JWT storage**: httpOnly cookie (XSS-resistant)
3. **Recurring task logic**: JSONB metadata + parent_task_id link
4. **Tag storage**: JSONB array (queryable, simple)
5. **Reminder implementation**: APScheduler (60s interval, in-process)
6. **Real-time notifications**: HTTP polling (30s interval)
7. **Deployment platforms**: Vercel (frontend), Railway/Render (backend)
8. **Month-end edge cases**: Clamp to last valid day of month

---

## Next Steps (Phase 1: Design & Contracts)

1. **data-model.md**: Define SQLModel classes (User, Task, Notification)
2. **contracts/**: Generate OpenAPI schema and TypeScript types
3. **quickstart.md**: Developer setup instructions
4. **plan.md**: Full implementation plan with decision records

**No blockers**. All technology decisions made and justified.
