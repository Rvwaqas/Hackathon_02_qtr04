# Feature Specification: Full-Stack Multi-User Todo Web Application

**Feature Branch**: `001-web-app-auth`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: "Full-Stack Multi-User Todo Web Application with Authentication and Persistent Storage - Transform Phase I console app into modern web application with Better Auth JWT, Neon PostgreSQL, Next.js frontend, and FastAPI backend"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration & Authentication (Priority: P0 - Foundation) 🎯

As a new user, I can sign up for an account and sign in securely so that I have my own private task workspace.

**Why this priority**: Authentication is the foundation - without it, there's no user isolation or data security. Must be implemented first before any task features.

**Independent Test**: Navigate to app, click Sign Up, create account with email/password, verify redirected to dashboard, sign out, sign back in with same credentials, verify access to same account.

**Acceptance Scenarios**:

1. **Given** I'm a new user on the landing page, **When** I click "Sign Up" and enter valid email/password, **Then** account is created and I'm redirected to my task dashboard
2. **Given** I try to sign up with an already-registered email, **When** I submit, **Then** I see error "Email already registered"
3. **Given** I have an account, **When** I enter correct email/password on sign-in page, **Then** I'm authenticated and see my task list
4. **Given** I enter incorrect password, **When** I submit sign-in form, **Then** I see error "Invalid credentials"
5. **Given** I'm signed in, **When** I click "Sign Out", **Then** I'm logged out and redirected to landing page
6. **Given** I'm not signed in, **When** I try to access /dashboard directly, **Then** I'm redirected to sign-in page

---

### User Story 2 - Create & View Tasks (Priority: P1 - MVP Core)

As an authenticated user, I can create new tasks and view my task list so that I can track my to-do items.

**Why this priority**: Core value proposition - users need to create and view tasks. This is the MVP that delivers immediate value after authentication.

**Independent Test**: Sign in, create 3 tasks with different titles, verify all appear in task list ordered by creation time (newest first), verify each has unique ID and pending status.

**Acceptance Scenarios**:

1. **Given** I'm signed in and on the dashboard, **When** I enter task title "Buy groceries" and click Add, **Then** task appears in my list with pending status
2. **Given** I create a task with title and description, **When** viewing the list, **Then** task shows title, description preview (50 chars), status, and created date
3. **Given** I have no tasks, **When** I view my dashboard, **Then** I see message "No tasks yet. Create your first task!"
4. **Given** I create 5 tasks, **When** viewing the list, **Then** tasks are ordered newest first (by created_at)
5. **Given** another user has 10 tasks, **When** I view my dashboard, **Then** I see only my own tasks (complete data isolation)

---

### User Story 3 - Update & Delete Tasks (Priority: P2)

As an authenticated user, I can edit task details and remove tasks I no longer need so that my task list stays current and relevant.

**Why this priority**: After creating tasks, users need to modify and remove them. Essential for maintaining an accurate task list.

**Independent Test**: Create task, click Edit, change title from "Old title" to "New title", save, verify updated in list; click Delete, confirm, verify task removed from list.

**Acceptance Scenarios**:

1. **Given** I have a task "Buy groceries", **When** I click Edit and change title to "Buy groceries and fruits", **Then** task updates and shows new title in list
2. **Given** I'm editing a task, **When** I update description, **Then** new description is saved and visible
3. **Given** I'm editing a task, **When** I click Cancel, **Then** changes are discarded and original values remain
4. **Given** I click Delete on a task, **When** I confirm deletion, **Then** task is permanently removed from my list
5. **Given** I try to edit another user's task via API, **When** request is processed, **Then** I receive 403 Forbidden error

---

### User Story 4 - Mark Complete/Incomplete (Priority: P3)

As an authenticated user, I can toggle task completion status so that I can track what's done and what's pending.

**Why this priority**: Completion tracking is essential for a todo app, but can be validated after create/edit/delete features are working.

**Independent Test**: Create task, verify checkbox is unchecked, click checkbox, verify task marked complete with visual indicator, click again, verify unmarked.

**Acceptance Scenarios**:

1. **Given** I have a pending task, **When** I click the checkbox, **Then** task is marked complete with checkmark visual indicator
2. **Given** I have a completed task, **When** I click the checkbox again, **Then** task is marked incomplete (pending)
3. **Given** I filter to show only pending tasks, **When** I mark a task complete, **Then** it disappears from the pending filter view
4. **Given** I filter to show only completed tasks, **When** viewing the list, **Then** I see only tasks where completed=true

---

### Edge Cases

- What happens when user tries to create task with empty title? → Frontend shows validation error "Title is required (1-200 characters)"
- What happens when user enters 201-character title? → Frontend shows error "Title max 200 characters"
- What happens when user enters 1001-character description? → Frontend shows error "Description max 1000 characters"
- What happens when unauthenticated user calls API directly (e.g., via curl)? → API returns 401 Unauthorized
- What happens when user A tries to delete user B's task via API manipulation? → API returns 403 Forbidden (ownership check fails)
- What happens when JWT token expires? → Frontend detects 401 response, redirects to sign-in page
- What happens when database connection fails? → Backend returns 500 error, frontend shows "Service unavailable, please try again"
- What happens when user signs out while on task detail page? → Redirect to landing page, clear JWT from storage
- What happens when two users have same email during signup race condition? → Database unique constraint prevents, API returns "Email already registered"

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Authorization (P0)

- **FR-001**: System MUST provide user registration with email and password
- **FR-002**: System MUST validate email format during registration (standard email regex)
- **FR-003**: System MUST require password minimum 8 characters during registration
- **FR-004**: System MUST hash passwords before storing (handled by Better Auth)
- **FR-005**: System MUST prevent duplicate email registrations (unique constraint)
- **FR-006**: System MUST provide sign-in with email/password authentication
- **FR-007**: System MUST issue JWT token on successful authentication
- **FR-008**: System MUST include user_id claim in JWT payload
- **FR-009**: System MUST validate JWT on every protected API request
- **FR-010**: System MUST provide sign-out functionality (clear JWT from frontend)
- **FR-011**: System MUST redirect unauthenticated users to sign-in page when accessing protected routes
- **FR-012**: System MUST expire JWT tokens after 7 days (per constitution)

#### Task CRUD Operations (P1-P3)

- **FR-013**: System MUST allow authenticated users to create tasks with title (required, 1-200 chars) and description (optional, max 1000 chars)
- **FR-014**: System MUST assign unique auto-incrementing ID to each task
- **FR-015**: System MUST associate every task with creator's user_id (foreign key)
- **FR-016**: System MUST set completed=False and created_at=now() for new tasks
- **FR-017**: System MUST allow users to view list of their own tasks only (filtered by user_id)
- **FR-018**: System MUST order tasks by created_at descending (newest first)
- **FR-019**: System MUST display task: ID, title, description preview (50 chars), status, created date
- **FR-020**: System MUST allow users to update title and description of their own tasks only
- **FR-021**: System MUST allow users to delete their own tasks only (ownership check)
- **FR-022**: System MUST allow users to toggle completion status of their own tasks only
- **FR-023**: System MUST return 403 Forbidden when user attempts to access another user's task
- **FR-024**: System MUST return 404 Not Found when task ID doesn't exist
- **FR-025**: System MUST validate title length (1-200 chars) on create and update
- **FR-026**: System MUST validate description length (max 1000 chars) on create and update

#### Data Persistence (P0)

- **FR-027**: System MUST persist all user data to Neon PostgreSQL database
- **FR-028**: System MUST persist all task data to Neon PostgreSQL database
- **FR-029**: System MUST use SQLModel for all database operations
- **FR-030**: System MUST use async database operations (no synchronous calls)
- **FR-031**: System MUST enforce foreign key constraint: tasks.user_id → users.id
- **FR-032**: System MUST create index on tasks.user_id for query performance
- **FR-033**: System MUST create index on users.email for login performance

#### API Design (P0-P3)

- **FR-034**: System MUST provide RESTful API endpoints for all operations
- **FR-035**: System MUST return JSON responses with consistent error structure
- **FR-036**: System MUST include user_id in API endpoint paths: `/api/users/{user_id}/tasks`
- **FR-037**: System MUST extract user_id from JWT and validate against path parameter
- **FR-038**: System MUST implement JWT verification middleware on all protected endpoints
- **FR-039**: System MUST return 401 Unauthorized for missing or invalid JWT
- **FR-040**: System MUST return 403 Forbidden for user_id mismatch (JWT vs path)

### Key Entities

- **User**:
  - `id` (UUID or integer): Unique user identifier
  - `email` (string, unique): User's email address for authentication
  - `password_hash` (string): Hashed password (managed by Better Auth)
  - `created_at` (datetime): Account creation timestamp

- **Task**:
  - `id` (integer): Unique auto-incrementing task identifier
  - `user_id` (UUID or integer, foreign key): Owner of the task
  - `title` (string, required): Task name (1-200 chars)
  - `description` (string, optional): Extended details (max 1000 chars)
  - `completed` (boolean): Status indicator (default False)
  - `created_at` (datetime): Task creation timestamp
  - `updated_at` (datetime): Last modification timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can sign up for a new account in under 30 seconds
- **SC-002**: Users can sign in to existing account in under 10 seconds
- **SC-003**: Users can create a new task in under 10 seconds
- **SC-004**: Users can view their task list in under 3 seconds
- **SC-005**: Users can update a task in under 15 seconds
- **SC-006**: Users can delete a task in under 10 seconds
- **SC-007**: Users can mark task complete/incomplete in under 5 seconds
- **SC-008**: System maintains complete data isolation (users never see other users' tasks)
- **SC-009**: Application handles 100 concurrent users without performance degradation
- **SC-010**: Task list loads and displays within 2 seconds for users with 100+ tasks
- **SC-011**: All API requests receive response within 500ms (p95)
- **SC-012**: Database queries complete within 100ms (p95)
- **SC-013**: Full demo workflow (signup → create task → view → update → delete → signout) completes in under 90 seconds
- **SC-014**: Zero data loss during normal operations (all data persisted)
- **SC-015**: Application works on Chrome, Firefox, Safari (desktop and mobile)

## Assumptions

1. **Phase 1 Complete**: All Phase 1 features (console app) are fully implemented and validated
2. **Environment Setup**: Developers have Node.js 18+, Python 3.13+, UV, and access to Neon database
3. **Database Access**: Neon PostgreSQL instance is provisioned with DATABASE_URL available
4. **Local Development**: Frontend runs on localhost:3000, backend on localhost:8000
5. **CORS Configuration**: Backend allows requests from frontend origin (localhost:3000)
6. **Email Uniqueness**: Email addresses are unique identifiers (no multiple accounts per email)
7. **Password Storage**: Better Auth handles password hashing (bcrypt or argon2)
8. **JWT Expiration**: Tokens valid for 7 days (per constitution requirement)
9. **No Email Verification**: Users can sign in immediately after registration (no email confirmation flow in Phase 2)
10. **No Password Reset**: Forgot password functionality deferred to future phase
11. **Single Session**: Users can be signed in on multiple devices (JWT is stateless)
12. **No Rate Limiting**: Authentication endpoints not rate-limited in Phase 2 (can add later)
13. **UTC Timestamps**: All datetime fields stored in UTC, displayed in user's local timezone
14. **Soft Deletes**: Tasks are permanently deleted (no soft delete/archive in Phase 2)
15. **Basic UI**: Clean and functional UI, advanced styling/animations deferred

## Out of Scope

The following are explicitly NOT included in Phase 2:

### Deferred to Phase III (AI Chatbot)
- AI chatbot interface for task management
- Natural language task input
- MCP server integration
- Voice commands

### Deferred to Phase IV-V (Infrastructure)
- Kubernetes deployment
- Docker containerization
- Horizontal scaling configuration
- Kafka event streaming
- Dapr integration
- Production deployment to cloud platform

### Deferred to Future Enhancements
- Advanced features from Phase 1 (priorities, tags, due dates, recurring tasks, reminders)
- Email verification for new accounts
- Password reset/forgot password flow
- Social authentication (Google, GitHub OAuth)
- Two-factor authentication (2FA)
- User profile management (name, avatar, preferences)
- Task sharing or collaboration (multi-user tasks)
- Real-time sync between multiple browser tabs/devices
- Advanced filtering and search
- Task sorting beyond creation date
- Export/import tasks (CSV, JSON)
- Dark mode or theme customization
- Internationalization (i18n) / multi-language support
- Accessibility (WCAG 2.1 Level AA compliance)
- Progressive Web App (PWA) features
- Offline support with service workers

## Implementation Notes

This specification defines Phase 2 of the "Evolution of Todo" hackathon project. Key characteristics:

1. **Migration from Phase 1**: Brings all 5 Basic Level features (CRUD operations) from console to web interface
2. **Multi-User Architecture**: Adds authentication and user isolation (not present in Phase 1)
3. **Persistent Storage**: Replaces in-memory storage with PostgreSQL database
4. **Modern Stack**: Uses Next.js 16+ App Router, FastAPI, Better Auth JWT, SQLModel, Neon PostgreSQL
5. **Monorepo Structure**: Frontend and backend in separate subdirectories under phase2/
6. **Spec-Driven**: All implementation follows spec → plan → tasks → implement workflow with Claude Code
7. **Context7 Integration**: Use MCP server to fetch up-to-date documentation for Next.js, FastAPI, SQLModel, Better Auth
8. **Constitution Compliance**: Follows all principles from `.specify/memory/constitution.md`

## Dependencies

- **Requires**: Phase 1 (console app) complete and validated - provides feature baseline
- **Blocks**: Phase 3 (AI Chatbot) - cannot start until web app foundation exists
- **Related**: Phase 1 features will NOT be ported yet (only Basic Level CRUD in Phase 2)
