# Tasks: Full-Stack Multi-User Todo Web Application (All Features)

**Input**: Design documents from `phase2/specs/002-fullstack-web-all-features/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/openapi.yaml ✓

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are excluded. Focus is on implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Web application structure:
- Backend: `phase2/backend/`
- Frontend: `phase2/frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create phase2 directory structure with backend/ and frontend/ subdirectories
- [ ] T002 [P] Initialize backend Python project with UV in phase2/backend/ (pyproject.toml with fastapi, sqlmodel, uvicorn, asyncpg, python-jose, python-multipart, apscheduler, alembic)
- [ ] T003 [P] Initialize frontend Next.js 16 project in phase2/frontend/ with TypeScript, Tailwind CSS, and Better Auth (npx create-next-app@latest --typescript --tailwind --app)
- [ ] T004 [P] Create backend .env.example file in phase2/backend/ with DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS placeholders
- [ ] T005 [P] Create frontend .env.local.example file in phase2/frontend/ with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET placeholders
- [ ] T006 [P] Configure Tailwind CSS with custom colors for priority badges in phase2/frontend/tailwind.config.js
- [ ] T007 [P] Create backend README.md in phase2/backend/ with setup instructions
- [ ] T008 [P] Create frontend README.md in phase2/frontend/ with setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Models

- [ ] T009 Create database configuration module in phase2/backend/src/database.py with async SQLModel engine and session manager using Neon connection string
- [ ] T010 Create User SQLModel in phase2/backend/src/models/user.py (read-only, managed by Better Auth)
- [ ] T011 Create Task SQLModel in phase2/backend/src/models/task.py with all fields (id, user_id, title, description, completed, priority, tags, recurrence, due_date, reminder_offset_minutes, parent_task_id, created_at, updated_at)
- [ ] T012 Create Notification SQLModel in phase2/backend/src/models/notification.py with fields (id, user_id, task_id, message, read, created_at)
- [ ] T013 Create Alembic migration 001_initial_schema.py in phase2/backend/migrations/versions/ to create tasks and notifications tables with indexes and foreign keys

### API Infrastructure

- [ ] T014 Create FastAPI app initialization in phase2/backend/src/main.py with CORS middleware, startup/shutdown events, and health check endpoint
- [ ] T015 Create JWT authentication middleware in phase2/backend/src/middleware/jwt_auth.py with get_current_user dependency that extracts and validates JWT token
- [ ] T016 Create Pydantic schemas for Task in phase2/backend/src/schemas/task.py (TaskCreate, TaskUpdate, TaskResponse with validation)
- [ ] T017 Create Pydantic schemas for Notification in phase2/backend/src/schemas/notification.py (NotificationResponse)
- [ ] T018 Create error response schemas in phase2/backend/src/schemas/common.py (ErrorResponse with data and error fields)

### Frontend Infrastructure

- [ ] T019 Create Better Auth configuration in phase2/frontend/src/lib/auth.ts with JWT provider setup
- [ ] T020 Create Better Auth API route handler in phase2/frontend/src/app/api/auth/[...betterauth]/route.ts
- [ ] T021 Create API client with JWT handling in phase2/frontend/src/lib/api.ts (fetch wrapper with Authorization header)
- [ ] T022 Create TypeScript types from OpenAPI in phase2/frontend/src/types/api.ts (Task, Notification, Priority, RecurrenceType interfaces)
- [ ] T023 Create root layout with Better Auth provider in phase2/frontend/src/app/layout.tsx
- [ ] T024 Create global Tailwind styles in phase2/frontend/src/styles/globals.css
- [ ] T025 Create reusable Button component in phase2/frontend/src/components/ui/Button.tsx
- [ ] T026 Create reusable Input component in phase2/frontend/src/components/ui/Input.tsx
- [ ] T027 Create reusable Modal component in phase2/frontend/src/components/ui/Modal.tsx
- [ ] T028 Create reusable Badge component in phase2/frontend/src/components/ui/Badge.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration & Authentication (Priority: P0) 🎯 MVP Foundation

**Goal**: Enable users to sign up, sign in, and sign out securely with JWT authentication

**Independent Test**: Navigate to app, click Sign Up, create account with name/email/password, verify redirected to dashboard, sign out, sign back in with same credentials, verify access to same account and data isolation

### Backend Implementation

- [ ] T029 [P] [US1] Create auth service module in phase2/backend/src/services/auth.py with Better Auth integration for user registration and JWT generation
- [ ] T030 [P] [US1] Create auth routes in phase2/backend/src/api/auth.py with POST /api/auth/signup endpoint (validate email, hash password, create user via Better Auth, return JWT)
- [ ] T031 [P] [US1] Add POST /api/auth/signin endpoint to phase2/backend/src/api/auth.py (validate credentials, verify password, return JWT token)
- [ ] T032 [P] [US1] Add POST /api/auth/signout endpoint to phase2/backend/src/api/auth.py (invalidate token if needed, return success)

### Frontend Implementation

- [ ] T033 [US1] Create landing page in phase2/frontend/src/app/page.tsx with hero section and Sign Up CTA
- [ ] T034 [P] [US1] Create signup page in phase2/frontend/src/app/signup/page.tsx with form (name, email, password fields with validation)
- [ ] T035 [P] [US1] Create signin page in phase2/frontend/src/app/signin/page.tsx with form (email, password fields with error handling)
- [ ] T036 [US1] Create auth hook useAuth in phase2/frontend/src/hooks/useAuth.ts for authentication state management
- [ ] T037 [US1] Create auth guard middleware in phase2/frontend/src/app/dashboard/layout.tsx that redirects unauthenticated users to /signin
- [ ] T038 [US1] Add logout functionality to landing page header in phase2/frontend/src/app/page.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can signup, signin, and access protected routes

---

## Phase 4: User Story 2 - Create & View Tasks (Priority: P1) 🎯 MVP Core

**Goal**: Enable authenticated users to create new tasks and view their task list

**Independent Test**: Sign in, create 3 tasks with different titles and descriptions, verify all appear in task list ordered by creation time (newest first), verify each has unique ID and pending status, verify complete data isolation

### Backend Implementation

- [ ] T039 [US2] Create task service module in phase2/backend/src/services/task_service.py with create_task function (validates input, enforces user_id isolation)
- [ ] T040 [P] [US2] Create task routes in phase2/backend/src/api/tasks.py with POST /api/{user_id}/tasks endpoint (create task with JWT auth, return TaskResponse)
- [ ] T041 [P] [US2] Add GET /api/{user_id}/tasks endpoint to phase2/backend/src/api/tasks.py (list tasks filtered by user_id, ordered by created_at desc)
- [ ] T042 [P] [US2] Add GET /api/{user_id}/tasks/{task_id} endpoint to phase2/backend/src/api/tasks.py (get single task with ownership validation)

### Frontend Implementation

- [ ] T043 [US2] Create dashboard page in phase2/frontend/src/app/dashboard/page.tsx with task list container and create task button
- [ ] T044 [P] [US2] Create TaskList component in phase2/frontend/src/components/tasks/TaskList.tsx (displays array of tasks, handles empty state)
- [ ] T045 [P] [US2] Create TaskCard component in phase2/frontend/src/components/tasks/TaskCard.tsx (displays single task with title, description preview, status, created date)
- [ ] T046 [US2] Create TaskForm component in phase2/frontend/src/components/tasks/TaskForm.tsx in create mode (title and description inputs with validation)
- [ ] T047 [US2] Create useTasks hook in phase2/frontend/src/hooks/useTasks.ts for task CRUD operations (fetchTasks, createTask)
- [ ] T048 [US2] Add modal trigger and TaskForm integration to dashboard page in phase2/frontend/src/app/dashboard/page.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 work - users can create and view their tasks independently

---

## Phase 5: User Story 3 - Update & Delete Tasks (Priority: P2)

**Goal**: Enable users to edit task details and remove tasks they no longer need

**Independent Test**: Create task "Draft report", click Edit, change title to "Finalize report", update description, save, verify changes in list; click Delete on another task, confirm dialog, verify task removed from list

### Backend Implementation

- [ ] T049 [P] [US3] Add update_task function to phase2/backend/src/services/task_service.py (validates ownership, updates fields, returns updated task)
- [ ] T050 [P] [US3] Add PUT /api/{user_id}/tasks/{task_id} endpoint to phase2/backend/src/api/tasks.py (update task with ownership check, return TaskResponse)
- [ ] T051 [P] [US3] Add DELETE /api/{user_id}/tasks/{task_id} endpoint to phase2/backend/src/api/tasks.py (delete task and cascade notifications, ownership check, return success)

### Frontend Implementation

- [ ] T052 [US3] Update TaskCard component in phase2/frontend/src/components/tasks/TaskCard.tsx to add Edit and Delete icon buttons
- [ ] T053 [US3] Update TaskForm component in phase2/frontend/src/components/tasks/TaskForm.tsx to support edit mode (populate existing values)
- [ ] T054 [US3] Add updateTask and deleteTask functions to useTasks hook in phase2/frontend/src/hooks/useTasks.ts
- [ ] T055 [US3] Create delete confirmation modal in TaskCard component in phase2/frontend/src/components/tasks/TaskCard.tsx
- [ ] T056 [US3] Add optimistic UI updates to useTasks hook in phase2/frontend/src/hooks/useTasks.ts (update/remove from local state immediately)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 work - full CRUD operations on tasks

---

## Phase 6: User Story 4 - Mark Complete/Incomplete (Priority: P3)

**Goal**: Enable users to toggle task completion status with one click

**Independent Test**: Create task, verify checkbox is unchecked and status is "Pending", click checkbox, verify task marked complete with visual styling (strikethrough, green checkmark), click again, verify unmarked

### Backend Implementation

- [ ] T057 [US4] Add toggle_complete function to phase2/backend/src/services/task_service.py (toggles completed field, updates updated_at)
- [ ] T058 [US4] Add PATCH /api/{user_id}/tasks/{task_id}/complete endpoint to phase2/backend/src/api/tasks.py (toggle completion status, return current_task in response)

### Frontend Implementation

- [ ] T059 [US4] Update TaskCard component in phase2/frontend/src/components/tasks/TaskCard.tsx to add checkbox with click handler
- [ ] T060 [US4] Add visual styling for completed tasks in phase2/frontend/src/components/tasks/TaskCard.tsx (strikethrough text, green checkmark, faded appearance)
- [ ] T061 [US4] Add toggleComplete function to useTasks hook in phase2/frontend/src/hooks/useTasks.ts
- [ ] T062 [US4] Add optimistic checkbox toggle to TaskCard in phase2/frontend/src/components/tasks/TaskCard.tsx

**Checkpoint**: Task completion tracking now works - users can mark tasks as done

---

## Phase 7: User Story 5 - Assign Priorities (Priority: P4 - Intermediate)

**Goal**: Enable users to assign priority levels to tasks for better organization

**Independent Test**: Create task, set priority to High, verify red badge "🔴 High" appears on task card; change to Medium, verify yellow badge "🟡 Medium"; filter by priority High, verify only high-priority tasks shown

### Backend Implementation

- [ ] T063 [P] [US5] Update create_task and update_task functions in phase2/backend/src/services/task_service.py to handle priority field validation
- [ ] T064 [P] [US5] Add priority filter support to GET /api/{user_id}/tasks endpoint in phase2/backend/src/api/tasks.py (query parameter ?priority=high/medium/low/none)
- [ ] T065 [P] [US5] Add priority sort support to GET /api/{user_id}/tasks endpoint in phase2/backend/src/api/tasks.py (query parameter ?sort=priority)

### Frontend Implementation

- [ ] T066 [US5] Update TaskForm component in phase2/frontend/src/components/tasks/TaskForm.tsx to add priority dropdown selector (High, Medium, Low, None)
- [ ] T067 [US5] Update TaskCard component in phase2/frontend/src/components/tasks/TaskCard.tsx to display priority badge with emoji and color (🔴 High=red, 🟡 Medium=yellow, 🔵 Low=blue)
- [ ] T068 [US5] Create FilterPanel component in phase2/frontend/src/components/tasks/FilterPanel.tsx with priority filter dropdown
- [ ] T069 [US5] Create useFilters hook in phase2/frontend/src/hooks/useFilters.ts for filter state management
- [ ] T070 [US5] Integrate FilterPanel into dashboard page in phase2/frontend/src/app/dashboard/page.tsx

**Checkpoint**: Priority system now works - users can categorize tasks by urgency

---

## Phase 8: User Story 6 - Tag Tasks (Priority: P5 - Intermediate)

**Goal**: Enable users to add tags to tasks for flexible categorization

**Independent Test**: Create task, add tags "work, urgent, Q1", verify tags display as badges "#work #urgent #Q1"; filter by tag "work", verify only tasks with "work" tag shown; add 11th tag to task with 10 existing tags, verify error "Maximum 10 tags per task"

### Backend Implementation

- [ ] T071 [P] [US6] Update create_task and update_task functions in phase2/backend/src/services/task_service.py to handle tags field (JSONB array validation, max 10 tags, alphanumeric check, lowercase normalization)
- [ ] T072 [P] [US6] Add tag filter support to GET /api/{user_id}/tasks endpoint in phase2/backend/src/api/tasks.py (query parameter ?tag=work using PostgreSQL JSONB contains operator)

### Frontend Implementation

- [ ] T073 [US6] Update TaskForm component in phase2/frontend/src/components/tasks/TaskForm.tsx to add tag input field (comma-separated, max 10, alphanumeric validation)
- [ ] T074 [US6] Update TaskCard component in phase2/frontend/src/components/tasks/TaskCard.tsx to display tag badges with # prefix
- [ ] T075 [US6] Update FilterPanel component in phase2/frontend/src/components/tasks/FilterPanel.tsx to add tag filter dropdown (populated from existing tags)
- [ ] T076 [US6] Add tag normalization utility function to phase2/frontend/src/lib/utils.ts (lowercase, trim, alphanumeric validation)

**Checkpoint**: Tag system now works - users can organize tasks by topics

---

## Phase 9: User Story 7 - Search & Filter Tasks (Priority: P6 - Intermediate)

**Goal**: Enable users to search for tasks by keyword and filter by status, priority, or tag

**Independent Test**: Create 10 tasks with varied keywords, priorities, and tags; search "meeting", verify only matching tasks shown; filter by "High" priority + "work" tag, verify AND logic; clear filters, verify all tasks return

### Backend Implementation

- [ ] T077 [P] [US7] Add search parameter support to GET /api/{user_id}/tasks endpoint in phase2/backend/src/api/tasks.py (query parameter ?search=keyword with case-insensitive ILIKE on title and description)
- [ ] T078 [P] [US7] Add status filter support to GET /api/{user_id}/tasks endpoint in phase2/backend/src/api/tasks.py (query parameter ?status=pending/completed/all)
- [ ] T079 [P] [US7] Implement AND logic for multiple filters in phase2/backend/src/api/tasks.py (combine search, status, priority, tag filters)

### Frontend Implementation

- [ ] T080 [US7] Create SearchBar component in phase2/frontend/src/components/tasks/SearchBar.tsx with debounced input (300ms delay)
- [ ] T081 [US7] Update FilterPanel component in phase2/frontend/src/components/tasks/FilterPanel.tsx to add status filter dropdown (All, Pending, Completed)
- [ ] T082 [US7] Add "Clear filters" button to FilterPanel in phase2/frontend/src/components/tasks/FilterPanel.tsx
- [ ] T083 [US7] Update useFilters hook in phase2/frontend/src/hooks/useFilters.ts to sync filters with URL query parameters
- [ ] T084 [US7] Integrate SearchBar into dashboard page in phase2/frontend/src/app/dashboard/page.tsx
- [ ] T085 [US7] Add "X tasks found" count display to dashboard in phase2/frontend/src/app/dashboard/page.tsx

**Checkpoint**: Search and filter now work - users can quickly find specific tasks

---

## Phase 10: User Story 8 - Sort Tasks (Priority: P7 - Intermediate)

**Goal**: Enable users to sort tasks by different criteria

**Independent Test**: Create 5 tasks with different creation dates, titles, priorities, and due dates; sort by "Priority (High → Low)", verify high-priority tasks at top; sort by "Title (A-Z)", verify alphabetical order; sort by "Due Date (Earliest)", verify overdue/upcoming tasks first

### Backend Implementation

- [ ] T086 [P] [US8] Add sort and order parameters to GET /api/{user_id}/tasks endpoint in phase2/backend/src/api/tasks.py (query parameters ?sort=created_at/title/priority/due_date&order=asc/desc)
- [ ] T087 [P] [US8] Implement priority sorting logic in phase2/backend/src/api/tasks.py (custom order: high > medium > low > none)

### Frontend Implementation

- [ ] T088 [US8] Create SortDropdown component in phase2/frontend/src/components/tasks/SortDropdown.tsx (options: Created Date, Title A-Z/Z-A, Priority High-Low/Low-High, Due Date Earliest/Latest)
- [ ] T089 [US8] Update useFilters hook in phase2/frontend/src/hooks/useFilters.ts to handle sort state
- [ ] T090 [US8] Integrate SortDropdown into dashboard page in phase2/frontend/src/app/dashboard/page.tsx
- [ ] T091 [US8] Add "Sorted by: [Criteria]" display label below SortDropdown in phase2/frontend/src/app/dashboard/page.tsx

**Checkpoint**: Sorting now works - users can view tasks in their preferred order

---

## Phase 11: User Story 9 - Recurring Tasks (Priority: P8 - Advanced)

**Goal**: Enable users to create tasks that repeat automatically on a schedule

**Independent Test**: Create task "Daily standup" with Daily recurrence, mark it complete, verify new task auto-created for next day with same title/priority/tags but new ID and reset completion status; create "Monthly report" with Monthly recurrence, complete on Jan 31, verify next occurrence created for Feb 28 (month-end handling)

### Backend Implementation

- [ ] T092 [US9] Add create_next_occurrence function to phase2/backend/src/services/task_service.py (calculates next due date based on recurrence type, handles month-end edge cases, copies title/description/priority/tags, sets parent_task_id)
- [ ] T093 [US9] Update toggle_complete function in phase2/backend/src/services/task_service.py to check for recurrence and call create_next_occurrence when marking complete
- [ ] T094 [US9] Update PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in phase2/backend/src/api/tasks.py to return both current_task and next_task in response
- [ ] T095 [US9] Add month-end date calculation utility in phase2/backend/src/services/task_service.py (Jan 31 → Feb 28/29, handles leap years)

### Frontend Implementation

- [ ] T096 [US9] Create RecurrenceSelector component in phase2/frontend/src/components/tasks/RecurrenceSelector.tsx (dropdown for Daily/Weekly/Monthly, checkbox for weekly days)
- [ ] T097 [US9] Update TaskForm component in phase2/frontend/src/components/tasks/TaskForm.tsx to integrate RecurrenceSelector
- [ ] T098 [US9] Update TaskCard component in phase2/frontend/src/components/tasks/TaskCard.tsx to display recurrence badge (🔄 Daily, 🔄 Weekly Mon/Wed, 🔄 Monthly)
- [ ] T099 [US9] Add toast notification in phase2/frontend/src/components/ui/Toast.tsx for "✓ Task completed. Next occurrence created for [date]"
- [ ] T100 [US9] Update toggleComplete handler in useTasks hook in phase2/frontend/src/hooks/useTasks.ts to handle next_task in response and add to task list

**Checkpoint**: Recurring tasks now work - users can automate routine tasks

---

## Phase 12: User Story 10 - Due Dates & Reminders (Priority: P9 - Advanced)

**Goal**: Enable users to set due dates and receive notifications before tasks are due

**Independent Test**: Create task "Submit report" with due date Jan 3, 2026 9:00 AM and reminder "1 hour before"; verify task shows "Due: Jan 3, 2026 9:00 AM" with countdown "in 2 days"; wait until Jan 3, 2026 8:00 AM, verify notification appears in notification bell

### Backend Implementation

- [ ] T101 [P] [US10] Add due_date and reminder_offset_minutes validation to create_task and update_task in phase2/backend/src/services/task_service.py (due_date must be future, reminder requires due_date)
- [ ] T102 [P] [US10] Create reminder service module in phase2/backend/src/services/reminder_service.py with check_reminders function (queries tasks where due_date - now <= reminder_offset_minutes)
- [ ] T103 [US10] Add APScheduler job in phase2/backend/src/main.py that runs check_reminders every 60 seconds
- [ ] T104 [P] [US10] Add create_notification function to phase2/backend/src/services/reminder_service.py (creates notification record with task_id and formatted message)
- [ ] T105 [P] [US10] Create notification routes in phase2/backend/src/api/notifications.py with GET /api/{user_id}/notifications endpoint (list notifications filtered by user_id, ordered by created_at desc)
- [ ] T106 [P] [US10] Add PATCH /api/{user_id}/notifications/{notification_id} endpoint to phase2/backend/src/api/notifications.py (mark notification as read)

### Frontend Implementation

- [ ] T107 [US10] Create DatePicker component in phase2/frontend/src/components/ui/DatePicker.tsx for due date and time selection
- [ ] T108 [US10] Update TaskForm component in phase2/frontend/src/components/tasks/TaskForm.tsx to add due date picker and reminder offset dropdown (5/15/30/60 minutes)
- [ ] T109 [US10] Update TaskCard component in phase2/frontend/src/components/tasks/TaskCard.tsx to display due date with countdown and overdue indicator (⚠️ red background)
- [ ] T110 [US10] Add calculateCountdown utility function to phase2/frontend/src/lib/utils.ts (returns "in 2 days", "in 3 hours", "overdue by 1 day")
- [ ] T111 [US10] Create NotificationBell component in phase2/frontend/src/components/NotificationBell.tsx with unread count badge
- [ ] T112 [US10] Create useNotifications hook in phase2/frontend/src/hooks/useNotifications.ts with polling every 30 seconds
- [ ] T113 [US10] Integrate NotificationBell into dashboard header in phase2/frontend/src/app/dashboard/page.tsx
- [ ] T114 [US10] Add notification list dropdown to NotificationBell component in phase2/frontend/src/components/NotificationBell.tsx

**Checkpoint**: Due dates and reminders now work - users receive timely notifications

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T115 [P] Add formatDate utility function to phase2/frontend/src/lib/utils.ts (consistent date formatting across app)
- [ ] T116 [P] Add error handling wrapper to API client in phase2/frontend/src/lib/api.ts (consistent error display with toast notifications)
- [ ] T117 [P] Add loading states to all async operations in phase2/frontend/src/hooks/useTasks.ts
- [ ] T118 [P] Add responsive design breakpoints to dashboard layout in phase2/frontend/src/app/dashboard/page.tsx (mobile <640px, tablet 640-1024px, desktop >1024px)
- [ ] T119 [P] Add database indexes verification in migration 001_initial_schema.py in phase2/backend/migrations/versions/
- [ ] T120 [P] Add API request logging middleware to phase2/backend/src/main.py (log all requests with user_id, endpoint, status code)
- [ ] T121 [P] Add input sanitization to prevent XSS in phase2/frontend/src/components/tasks/TaskForm.tsx
- [ ] T122 [P] Update backend README with deployment instructions in phase2/backend/README.md
- [ ] T123 [P] Update frontend README with deployment instructions in phase2/frontend/README.md
- [ ] T124 Run Alembic migrations and verify all tables created successfully
- [ ] T125 Perform end-to-end test of all 10 user stories following quickstart.md validation steps
- [ ] T126 Verify all 25 success criteria (SC-001 to SC-025) from spec.md are met
- [ ] T127 Create demo video (<90 seconds) showing all features working

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-12)**: All depend on Foundational phase completion
  - US1 (Authentication) must complete first - blocks all other user stories
  - US2 (Create/View Tasks) can start after US1
  - US3 (Update/Delete) depends on US2
  - US4 (Toggle Complete) depends on US2
  - US5-US8 (Priorities, Tags, Search, Sort) can proceed in parallel after US2-US4
  - US9 (Recurring) depends on US4 (completion toggle)
  - US10 (Due Dates/Reminders) can proceed after US2
- **Polish (Phase 13)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Authentication)**: Can start after Foundational - BLOCKS all other user stories (no auth = no user isolation)
- **US2 (Create/View)**: Depends on US1 - Enables basic task functionality
- **US3 (Update/Delete)**: Depends on US2 - Needs tasks to exist
- **US4 (Complete)**: Depends on US2 - Needs tasks to exist
- **US5 (Priorities)**: Depends on US2 - Enhances task creation
- **US6 (Tags)**: Depends on US2 - Enhances task creation
- **US7 (Search/Filter)**: Depends on US2, US5, US6 - Needs tasks with priority/tags
- **US8 (Sort)**: Depends on US2, US5 - Needs tasks with priority
- **US9 (Recurring)**: Depends on US4 - Needs completion toggle to trigger recurrence
- **US10 (Due Dates/Reminders)**: Depends on US2 - Independent of other features

### Within Each User Story

- Backend implementation before frontend (API must exist for frontend to call)
- Models and schemas before routes
- Services before routes (business logic before API layer)
- Core implementation before UI polish
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T002-T008) can run in parallel
- Database models (T010-T012) can run in parallel after T009
- Backend schemas (T016-T018) can run in parallel
- Frontend UI components (T025-T028) can run in parallel
- Within each user story, [P] marked tasks can run in parallel
- Different user stories can be worked on in parallel by different team members AFTER US1 completes

---

## Parallel Example: User Story 2 (Create & View Tasks)

```bash
# Launch all backend routes in parallel:
Task: "Create task routes POST /api/{user_id}/tasks in phase2/backend/src/api/tasks.py"
Task: "Add GET /api/{user_id}/tasks endpoint to phase2/backend/src/api/tasks.py"
Task: "Add GET /api/{user_id}/tasks/{task_id} endpoint to phase2/backend/src/api/tasks.py"

# Launch all frontend components in parallel:
Task: "Create TaskList component in phase2/frontend/src/components/tasks/TaskList.tsx"
Task: "Create TaskCard component in phase2/frontend/src/components/tasks/TaskCard.tsx"
```

---

## Parallel Example: User Story 5 (Priorities)

```bash
# Launch all backend API updates in parallel:
Task: "Update create_task in phase2/backend/src/services/task_service.py for priority"
Task: "Add priority filter to GET /api/{user_id}/tasks in phase2/backend/src/api/tasks.py"
Task: "Add priority sort to GET /api/{user_id}/tasks in phase2/backend/src/api/tasks.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (Create/View Tasks)
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy/demo if ready

**MVP delivers**: Users can sign up, sign in, create tasks, view tasks - core value!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Auth) → Test independently → Deploy/Demo (can't do much without auth)
3. Add US2 (Create/View) → Test independently → Deploy/Demo (MVP! 🎉)
4. Add US3 (Update/Delete) → Test independently → Deploy/Demo
5. Add US4 (Complete) → Test independently → Deploy/Demo
6. Add US5-US8 (Intermediate features) → Test independently → Deploy/Demo
7. Add US9-US10 (Advanced features) → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. One developer completes US1 (Authentication) - blocks others
3. Once US1 done:
   - Developer A: US2 (Create/View) + US3 (Update/Delete) + US4 (Complete)
   - Developer B: US5 (Priorities) + US6 (Tags) + US7 (Search) + US8 (Sort)
   - Developer C: US9 (Recurring) + US10 (Due Dates/Reminders)
4. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 127

**Tasks by Phase**:
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 20 tasks (CRITICAL - blocks all user stories)
- Phase 3 (US1 - Auth): 10 tasks
- Phase 4 (US2 - Create/View): 10 tasks
- Phase 5 (US3 - Update/Delete): 8 tasks
- Phase 6 (US4 - Complete): 6 tasks
- Phase 7 (US5 - Priorities): 8 tasks
- Phase 8 (US6 - Tags): 6 tasks
- Phase 9 (US7 - Search/Filter): 9 tasks
- Phase 10 (US8 - Sort): 6 tasks
- Phase 11 (US9 - Recurring): 9 tasks
- Phase 12 (US10 - Due Dates/Reminders): 14 tasks
- Phase 13 (Polish): 13 tasks

**Parallel Opportunities**: 63 tasks marked [P] can run in parallel within their phase

**MVP Scope** (Recommended first delivery):
- Phase 1: Setup (8 tasks)
- Phase 2: Foundational (20 tasks)
- Phase 3: US1 - Authentication (10 tasks)
- Phase 4: US2 - Create & View Tasks (10 tasks)
- **Total MVP**: 48 tasks → delivers core value (signup, signin, create/view tasks)

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All paths are absolute from repository root (phase2/backend/, phase2/frontend/)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included as they were not explicitly requested in the specification
- Focus is on delivering working features incrementally
