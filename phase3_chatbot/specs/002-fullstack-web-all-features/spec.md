# Feature Specification: Full-Stack Multi-User Todo Web Application (All Features)

**Feature Branch**: `002-fullstack-web-all-features`
**Created**: 2026-01-01
**Status**: Draft
**Input**: User description: "Phase II: Full-Stack Todo Web Application with ALL Features (Basic + Intermediate + Advanced) - Multi-user web app with authentication, persistent storage, priorities, tags, search, filter, sort, recurring tasks, due dates, and reminders"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration & Authentication (Priority: P0 - Foundation) 🎯

As a new user, I can sign up for an account and sign in securely so that I have my own private task workspace.

**Why this priority**: Authentication is the absolute foundation - without it, there's no user isolation, no data security, and no multi-user capability. Must be implemented first before any task features.

**Independent Test**: Navigate to app, click Sign Up, create account with name/email/password, verify redirected to dashboard, sign out, sign back in with same credentials, verify access to same account and data isolation.

**Acceptance Scenarios**:

1. **Given** I'm a new user on the landing page, **When** I submit the signup form with valid name, email, and password (8+ chars with letter+number), **Then** account is created, I'm auto-logged in, and redirected to my empty task dashboard
2. **Given** I try to sign up with an already-registered email, **When** I submit, **Then** I see inline error "Email already registered"
3. **Given** I have an account, **When** I enter correct email/password on sign-in page, **Then** I'm authenticated via JWT and see my task list
4. **Given** I enter incorrect password, **When** I submit sign-in form, **Then** I see error "Invalid email or password"
5. **Given** I'm signed in, **When** I click "Logout" button, **Then** JWT is cleared and I'm redirected to landing page
6. **Given** I'm not signed in, **When** I try to access /dashboard directly, **Then** I'm redirected to /signin page

---

### User Story 2 - Create & View Tasks (Priority: P1 - MVP Core)

As an authenticated user, I can create new tasks with title and description, and view my task list so that I can track my to-do items.

**Why this priority**: Core value proposition - users need to create and view tasks. This is the MVP that delivers immediate value after authentication.

**Independent Test**: Sign in, create 3 tasks with different titles and descriptions, verify all appear in task list ordered by creation time (newest first), verify each has unique ID and pending status, verify complete data isolation (other users don't see my tasks).

**Acceptance Scenarios**:

1. **Given** I'm signed in and on the dashboard, **When** I enter task title "Buy groceries" in the form and click Add Task, **Then** task appears in my list immediately with pending status
2. **Given** I create a task with title "Team meeting" and description "Discuss Q1 roadmap", **When** viewing the list, **Then** task shows full title, description preview (first 50 chars), pending status, and created date
3. **Given** I have no tasks, **When** I view my dashboard, **Then** I see message "No tasks yet. Create your first task!" with prominent Add Task button
4. **Given** I create 5 tasks over time, **When** viewing the list, **Then** tasks are ordered newest first (by created_at timestamp)
5. **Given** another user has 10 tasks in their account, **When** I view my dashboard, **Then** I see only my own tasks (complete data isolation enforced by user_id filtering)

---

### User Story 3 - Update & Delete Tasks (Priority: P2)

As an authenticated user, I can edit task details and remove tasks I no longer need so that my task list stays current and relevant.

**Why this priority**: After creating tasks, users need to modify and remove them. Essential for maintaining an accurate task list.

**Independent Test**: Create task "Draft report", click Edit, change title to "Finalize report", update description, save, verify changes in list; click Delete on another task, confirm dialog, verify task removed from list.

**Acceptance Scenarios**:

1. **Given** I have a task "Buy groceries", **When** I click Edit icon and change title to "Buy groceries and fruits", **Then** task updates and shows new title in list immediately
2. **Given** I'm editing a task, **When** I update description from empty to "Get apples, bananas, milk", **Then** new description is saved and visible in task preview
3. **Given** I'm editing a task, **When** I click Cancel button, **Then** changes are discarded and original values remain unchanged
4. **Given** I click Delete icon on a task, **When** I confirm in dialog "Delete 'Buy groceries'?", **Then** task is permanently removed from my list and database
5. **Given** I try to edit another user's task via API manipulation, **When** request is processed, **Then** I receive 403 Forbidden error (ownership validation)

---

### User Story 4 - Mark Complete/Incomplete (Priority: P3)

As an authenticated user, I can toggle task completion status with one click so that I can track what's done and what's pending.

**Why this priority**: Completion tracking is essential for a todo app, but can be validated after create/edit/delete features are working.

**Independent Test**: Create task, verify checkbox is unchecked and status is "Pending", click checkbox, verify task marked complete with visual styling (strikethrough, green checkmark), click again, verify unmarked.

**Acceptance Scenarios**:

1. **Given** I have a pending task, **When** I click the checkbox next to it, **Then** task is marked complete with visual indicators (strikethrough text, green checkmark icon, faded appearance)
2. **Given** I have a completed task, **When** I click the checkbox again, **Then** task is marked incomplete (pending) and visual styling reverts
3. **Given** I filter to show only pending tasks, **When** I mark a task complete, **Then** it disappears from the pending filter view immediately (optimistic UI update)
4. **Given** I filter to show only completed tasks, **When** viewing the list, **Then** I see only tasks where completed=true with completion timestamp

---

### User Story 5 - Assign Priorities (Priority: P4 - Intermediate)

As a user, I can assign priority levels to tasks so that I can focus on what's most important.

**Why this priority**: Priorities help users organize tasks by urgency, but basic CRUD must work first.

**Independent Test**: Create task, set priority to High, verify red badge "🔴 High" appears on task card; change to Medium, verify yellow badge "🟡 Medium"; filter by priority High, verify only high-priority tasks shown.

**Acceptance Scenarios**:

1. **Given** I'm creating a new task, **When** I select "High" from priority dropdown and save, **Then** task displays with red badge "🔴 High"
2. **Given** I have a task with no priority (default: None), **When** I edit it and set priority to "Medium", **Then** task shows yellow badge "🟡 Medium"
3. **Given** I have tasks with mixed priorities, **When** I sort by "Priority (High → Low)", **Then** tasks reorder: High first, then Medium, then Low, then None
4. **Given** I set a task priority to "Low", **When** viewing the task card, **Then** I see blue badge "🔵 Low"

---

### User Story 6 - Tag Tasks (Priority: P5 - Intermediate)

As a user, I can add tags to tasks so that I can categorize and organize them by topic or project.

**Why this priority**: Tags enable flexible organization beyond priorities, useful once users have multiple tasks.

**Independent Test**: Create task, add tags "work, urgent, Q1", verify tags display as badges "#work #urgent #Q1"; filter by tag "work", verify only tasks with "work" tag shown; add 6th tag to task with 5 existing tags, verify error "Maximum 5 tags per task".

**Acceptance Scenarios**:

1. **Given** I'm creating a task, **When** I type "work, meeting" in tag input and press Enter, **Then** task displays with badges "#work #meeting"
2. **Given** I have a task with tags "#personal #urgent", **When** I edit it and add tag "health", **Then** task shows all three tags "#personal #urgent #health"
3. **Given** I try to add a 6th tag to a task with 5 existing tags, **When** I submit, **Then** I see error "Maximum 5 tags per task"
4. **Given** I have multiple tasks tagged "#work", **When** I click the work filter/tag badge, **Then** list filters to show only tasks with "#work" tag
5. **Given** I enter tag with special characters "my-tag!", **When** I try to save, **Then** I see error "Tags must be alphanumeric only"

---

### User Story 7 - Search & Filter Tasks (Priority: P6 - Intermediate)

As a user, I can search for tasks by keyword and filter by status, priority, or tag so that I can quickly find specific tasks.

**Why this priority**: Search and filtering become valuable as task count grows, building on priorities and tags.

**Independent Test**: Create 10 tasks with varied keywords, priorities, and tags; search "meeting", verify only matching tasks shown; filter by "High" priority + "work" tag, verify AND logic; clear filters, verify all tasks return.

**Acceptance Scenarios**:

1. **Given** I have tasks with titles "Team meeting", "Buy groceries", "Meeting notes", **When** I type "meeting" in search bar, **Then** list shows "Team meeting" and "Meeting notes" (case-insensitive match in title/description)
2. **Given** I have tasks with mixed statuses, **When** I select "Completed" filter, **Then** list shows only tasks where completed=true
3. **Given** I have tasks with different priorities, **When** I select "High" priority filter, **Then** list shows only high-priority tasks
4. **Given** I apply both "Pending" status AND "work" tag filters, **When** viewing results, **Then** I see only tasks that match BOTH criteria (AND logic)
5. **Given** search shows "X tasks found", **When** I click "Clear" button, **Then** all filters reset and full task list returns

---

### User Story 8 - Sort Tasks (Priority: P7 - Intermediate)

As a user, I can sort tasks by different criteria so that I can view them in the order most useful to me.

**Why this priority**: Sorting helps users organize views after they have multiple tasks with varied attributes.

**Independent Test**: Create 5 tasks with different creation dates, titles, priorities, and due dates; sort by "Priority (High → Low)", verify high-priority tasks at top; sort by "Title (A-Z)", verify alphabetical order; sort by "Due Date (Earliest)", verify overdue/upcoming tasks first.

**Acceptance Scenarios**:

1. **Given** I have tasks with mixed priorities, **When** I select "Sort by: Priority (High → Low)", **Then** tasks reorder with High first, Medium next, Low next, None last
2. **Given** I have tasks created on different dates, **When** I select "Sort by: Created (Newest)", **Then** most recent tasks appear first (default view)
3. **Given** I have tasks titled "Zebra task", "Apple task", "Banana task", **When** I select "Sort by: Title (A-Z)", **Then** tasks reorder alphabetically
4. **Given** I have tasks with due dates, **When** I select "Sort by: Due Date (Earliest)", **Then** tasks with nearest due dates appear first, followed by tasks without due dates
5. **Given** current sort is displayed as "Sorted by: Priority (High → Low)", **When** I change to "Title (Z-A)", **Then** display updates to "Sorted by: Title (Z-A)"

---

### User Story 9 - Recurring Tasks (Priority: P8 - Advanced)

As a user, I can create tasks that repeat automatically on a schedule so that I don't have to manually recreate routine tasks.

**Why this priority**: Recurring tasks save time for routine activities, but require completion toggle to work first.

**Independent Test**: Create task "Daily standup" with Daily recurrence, mark it complete, verify new task auto-created for next day with same title/priority/tags but new ID and reset completion status; create "Monthly report" with Monthly recurrence, complete on Jan 31, verify next occurrence created for Feb 28 (month-end handling).

**Acceptance Scenarios**:

1. **Given** I'm creating a task, **When** I expand "Recurrence" section and select "Daily", **Then** task shows badge "🔄 Daily"
2. **Given** I create a recurring task with "Weekly" and check Mon/Wed/Fri, **When** I mark it complete on Monday, **Then** system auto-creates next occurrence for Wednesday with same details
3. **Given** I have a daily recurring task, **When** I mark it complete, **Then** I see notification "✓ Task completed. Next occurrence created for [date]" and new task appears in list
4. **Given** I create "Monthly" recurring task due Jan 31, **When** I complete it, **Then** next occurrence is created for Feb 28 (handles month-end edge case)
5. **Given** I have a recurring task, **When** viewing task details, **Then** I see parent_task_id linking it to previous occurrence (task history)

---

### User Story 10 - Due Dates & Reminders (Priority: P9 - Advanced)

As a user, I can set due dates and receive notifications before tasks are due so that I don't miss important deadlines.

**Why this priority**: Due dates and reminders add time-sensitive task management, building on all previous features.

**Independent Test**: Create task "Submit report" with due date Jan 3, 2026 9:00 AM and reminder "1 hour before"; verify task shows "Due: Jan 3, 2026 9:00 AM" with countdown "in 2 days"; wait until Jan 3, 2026 8:00 AM, verify browser push notification "⏰ 'Submit report' is due in 1 hour"; create task due yesterday, verify red background and ⚠️ icon for overdue status.

**Acceptance Scenarios**:

1. **Given** I'm creating a task, **When** I select due date Jan 3, 2026 9:00 AM in date/time picker, **Then** task shows "Due: Jan 3, 2026 9:00 AM" and countdown "in 2 days"
2. **Given** I set reminder to "1 hour before" on task due 9:00 AM, **When** time reaches 8:00 AM, **Then** I receive browser push notification "⏰ 'Submit report' is due in 1 hour" (via Service Worker + Web Push API)
3. **Given** I have a task due yesterday, **When** viewing task list, **Then** task has red background, ⚠️ icon, and shows "Overdue by 1 day"
4. **Given** I receive a reminder notification, **When** I click "Snooze 10 min", **Then** notification disappears and reappears 10 minutes later
5. **Given** I click on "Upcoming" tab, **When** viewing results, **Then** I see only tasks due within next 7 days, ordered by due date
6. **Given** I try to set due date in the past, **When** I submit, **Then** I see validation error "Due date must be in the future"

---

### Edge Cases

- What happens when user tries to create task with empty title? → Frontend shows validation error "Title is required (1-200 characters)"
- What happens when user enters 201-character title? → Frontend shows error "Title max 200 characters"
- What happens when user enters 1001-character description? → Frontend shows error "Description max 1000 characters"
- What happens when unauthenticated user calls API directly (e.g., via curl)? → API returns 401 Unauthorized with JSON error
- What happens when user A tries to delete user B's task via API manipulation? → API returns 403 Forbidden (ownership check fails)
- What happens when JWT token expires after 7 days? → Frontend detects 401 response on API call, clears token, redirects to signin page
- What happens when database connection fails during task creation? → Backend returns 500 Internal Server Error, frontend shows "Service unavailable, please try again"
- What happens when user signs out while on task detail page? → Redirect to landing page, clear JWT from localStorage/cookie
- What happens when two users try to register with same email simultaneously? → Database unique constraint prevents duplicate, second request receives "Email already registered" error
- What happens when user marks recurring task complete but next occurrence date is invalid (e.g., Feb 30)? → System calculates last valid day of month (Feb 28/29) using calendar logic
- What happens when reminder notification arrives but user has closed browser? → Service Worker queues notification, displays when user reopens browser (persistent notification)
- What happens when user has 100+ tasks and sorts by due date? → API query uses database index on due_date column, returns results within 100ms (p95 per SC-012)
- What happens when user tags task with "work" but another task has "Work" (different case)? → System normalizes tags to lowercase, treats as same tag "#work"
- What happens when user searches with special regex characters like "task.*"? → Search treats as literal string, not regex pattern (prevents injection)

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Authorization (P0 - Foundation)

- **FR-001**: System MUST provide user registration with name, email, and password
- **FR-002**: System MUST validate email format during registration (standard email regex)
- **FR-003**: System MUST require password minimum 8 characters with at least one letter and one number
- **FR-004**: System MUST hash passwords before storing (handled by Better Auth library)
- **FR-005**: System MUST prevent duplicate email registrations (database unique constraint)
- **FR-006**: System MUST provide sign-in with email/password authentication
- **FR-007**: System MUST issue JWT token on successful authentication with user_id claim in payload
- **FR-008**: System MUST store JWT in httpOnly cookie for security (preferred over localStorage)
- **FR-009**: System MUST validate JWT on every protected API request via middleware
- **FR-010**: System MUST provide sign-out functionality (clear JWT from frontend storage)
- **FR-011**: System MUST redirect unauthenticated users to sign-in page when accessing protected routes
- **FR-012**: System MUST expire JWT tokens after 7 days (per constitution requirement)
- **FR-013**: System MUST include Authorization: Bearer <token> header in all API requests
- **FR-014**: System MUST return 401 Unauthorized for missing or invalid JWT
- **FR-015**: System MUST return 403 Forbidden when user_id in JWT doesn't match resource owner

#### Task CRUD Operations (P1-P3 - Core)

- **FR-016**: System MUST allow authenticated users to create tasks with title (required, 1-200 chars) and description (optional, max 1000 chars)
- **FR-017**: System MUST assign unique auto-incrementing ID to each task
- **FR-018**: System MUST associate every task with creator's user_id (foreign key to users table)
- **FR-019**: System MUST set completed=false and created_at=now() for new tasks
- **FR-020**: System MUST allow users to view list of their own tasks only (filtered by user_id in JWT)
- **FR-021**: System MUST order tasks by created_at descending (newest first) by default
- **FR-022**: System MUST display task with: ID, title, description preview (50 chars), status, created date
- **FR-023**: System MUST allow users to update title and description of their own tasks only (ownership check)
- **FR-024**: System MUST allow users to delete their own tasks only (ownership check returns 403 for violations)
- **FR-025**: System MUST allow users to toggle completion status of their own tasks only
- **FR-026**: System MUST return 404 Not Found when task ID doesn't exist
- **FR-027**: System MUST validate title length (1-200 chars) on create and update
- **FR-028**: System MUST validate description length (max 1000 chars) on create and update
- **FR-029**: System MUST update updated_at timestamp automatically on task modifications

#### Priority System (P4 - Intermediate)

- **FR-030**: System MUST support priority values: "high", "medium", "low", "none" (default: "none")
- **FR-031**: System MUST store priority as string field in database
- **FR-032**: System MUST display priority badges: 🔴 High (red), 🟡 Medium (yellow), 🔵 Low (blue)
- **FR-033**: System MUST allow users to set/change priority when creating or editing tasks
- **FR-034**: System MUST support filtering tasks by priority level
- **FR-035**: System MUST support sorting tasks by priority (High → Medium → Low → None)

#### Tag System (P5 - Intermediate)

- **FR-036**: System MUST allow users to add tags to tasks (max 5 tags per task)
- **FR-037**: System MUST validate tags: alphanumeric only, 1-20 characters, lowercase normalization
- **FR-038**: System MUST store tags as JSONB array in database (default: empty array [])
- **FR-039**: System MUST display tags as badges with "#" prefix (e.g., "#work", "#urgent")
- **FR-040**: System MUST support filtering tasks by tag (single tag filter)
- **FR-041**: System MUST prevent duplicate tags on same task (case-insensitive check)
- **FR-042**: System MUST allow users to remove tags when editing tasks

#### Search & Filter (P6-P7 - Intermediate)

- **FR-043**: System MUST provide search bar that filters tasks by keyword in title or description (case-insensitive)
- **FR-044**: System MUST display "X tasks found" count during search
- **FR-045**: System MUST support filtering by status: All, Pending, Completed
- **FR-046**: System MUST support filtering by priority: All, High, Medium, Low, None
- **FR-047**: System MUST support filtering by tag (dropdown or badges)
- **FR-048**: System MUST apply filters with AND logic (multiple filters narrow results)
- **FR-049**: System MUST provide "Clear filters" button to reset all filters
- **FR-050**: System MUST support sorting by: Created Date (Newest/Oldest), Title (A-Z/Z-A), Priority (High-Low/Low-High), Due Date (Earliest/Latest)
- **FR-051**: System MUST display current sort selection: "Sorted by: [Criteria]"
- **FR-052**: System MUST persist search/filter/sort state in URL query params for bookmarking

#### Recurring Tasks (P8 - Advanced)

- **FR-053**: System MUST support recurrence types: None (default), Daily, Weekly, Monthly
- **FR-054**: System MUST store recurrence as JSONB field with structure: `{"type": "daily"|"weekly"|"monthly", "interval": 1, "days": [0-6]}`
- **FR-055**: System MUST display recurrence badge: 🔄 Daily, 🔄 Weekly (Mon, Wed), 🔄 Monthly
- **FR-056**: System MUST auto-create next occurrence when recurring task is marked complete
- **FR-057**: System MUST calculate next due date based on recurrence type: Daily (+1 day), Weekly (+7 days on selected days), Monthly (same day next month)
- **FR-058**: System MUST handle month-end edge cases: Jan 31 → Feb 28/29, May 31 → Jun 30
- **FR-059**: System MUST set parent_task_id on new occurrence linking to completed task (for history)
- **FR-060**: System MUST copy title, description, priority, tags to next occurrence
- **FR-061**: System MUST reset completed=false and created_at=now() on new occurrence
- **FR-062**: System MUST show notification "✓ Task completed. Next occurrence created for [date]"

#### Due Dates & Reminders (P9 - Advanced)

- **FR-063**: System MUST support due_date as ISO datetime string (nullable)
- **FR-064**: System MUST validate due date is in the future on create/update
- **FR-065**: System MUST display due date as "Due: Jan 3, 2026 9:00 AM" and countdown "in 2 days"
- **FR-066**: System MUST highlight overdue tasks with red background and ⚠️ icon
- **FR-067**: System MUST support reminder_offset_minutes: null, 15 (15 min before), 60 (1 hour before), 1440 (1 day before), 10080 (1 week before)
- **FR-068**: System MUST run backend cron job or service checking reminders every 60 seconds
- **FR-069**: System MUST create notification record in database when reminder time reached
- **FR-070**: System MUST send browser push notification via Service Worker + Web Push API
- **FR-071**: System MUST display notification: "⏰ '[Task Title]' is due in [time]"
- **FR-072**: System MUST support notification actions: Mark as read, Snooze 10 min, Dismiss
- **FR-073**: System MUST show in-app notification bell icon with unread count badge
- **FR-074**: System MUST provide "Overdue" view showing tasks past due date
- **FR-075**: System MUST provide "Upcoming" view showing tasks due within 7 days
- **FR-076**: System MUST create database index on due_date column for query performance

#### Data Persistence (P0 - Foundation)

- **FR-077**: System MUST persist all user data to Neon PostgreSQL database
- **FR-078**: System MUST persist all task data to Neon PostgreSQL database
- **FR-079**: System MUST persist all notification data to Neon PostgreSQL database
- **FR-080**: System MUST use SQLModel for all database operations (async ORM)
- **FR-081**: System MUST use async database operations (no synchronous calls)
- **FR-082**: System MUST enforce foreign key constraint: tasks.user_id → users.id
- **FR-083**: System MUST enforce foreign key constraint: notifications.user_id → users.id
- **FR-084**: System MUST enforce foreign key constraint: notifications.task_id → tasks.id
- **FR-085**: System MUST create index on tasks.user_id for query performance
- **FR-086**: System MUST create index on tasks.completed for filtering performance
- **FR-087**: System MUST create index on tasks.created_at for sorting performance
- **FR-088**: System MUST create index on users.email for login performance

#### API Design (P0-P9 - All Layers)

- **FR-089**: System MUST provide RESTful API endpoints for all operations
- **FR-090**: System MUST return JSON responses with consistent error structure: `{"error": "message", "details": {...}}`
- **FR-091**: System MUST use nested API structure: `/api/users/{user_id}/tasks` for explicit ownership
- **FR-092**: System MUST extract user_id from JWT and validate against path parameter on every request
- **FR-093**: System MUST implement JWT verification middleware on all protected endpoints
- **FR-094**: System MUST support query parameters for filtering: `?status=completed&priority=high&tag=work`
- **FR-095**: System MUST support query parameters for sorting: `?sort=priority&order=desc`
- **FR-096**: System MUST support query parameters for search: `?search=meeting`
- **FR-097**: System MUST return appropriate HTTP status codes: 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error

### Key Entities

- **User**:
  - `id` (UUID or VARCHAR): Unique user identifier, managed by Better Auth
  - `email` (string, unique): User's email address for authentication
  - `name` (string): User's display name
  - `password_hash` (string): Hashed password (managed by Better Auth)
  - `created_at` (datetime): Account creation timestamp
  - `updated_at` (datetime): Last account update timestamp

- **Task**:
  - `id` (integer, auto-increment): Unique task identifier
  - `user_id` (UUID/VARCHAR, foreign key): Owner of the task
  - `title` (string, required): Task name (1-200 chars)
  - `description` (string, optional): Extended details (max 1000 chars)
  - `completed` (boolean): Status indicator (default: false)
  - `priority` (string): Priority level: "high", "medium", "low", "none" (default: "none")
  - `tags` (JSONB array): List of tags (max 5, alphanumeric, lowercase)
  - `recurrence` (JSONB object, nullable): Recurrence config: `{"type": "daily"|"weekly"|"monthly", "interval": 1, "days": []}`
  - `due_date` (datetime, nullable): Task deadline in ISO format
  - `reminder_offset_minutes` (integer, nullable): Reminder time before due date (15, 60, 1440, 10080)
  - `parent_task_id` (integer, nullable, self-referencing FK): Links to previous occurrence for recurring tasks
  - `created_at` (datetime): Task creation timestamp
  - `updated_at` (datetime): Last modification timestamp (auto-updated)

- **Notification**:
  - `id` (integer, auto-increment): Unique notification identifier
  - `user_id` (UUID/VARCHAR, foreign key): Recipient user
  - `task_id` (integer, foreign key): Associated task
  - `message` (string): Notification content (e.g., "⏰ 'Submit report' is due in 1 hour")
  - `read` (boolean): Read status (default: false)
  - `created_at` (datetime): Notification creation timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can sign up for a new account in under 30 seconds
- **SC-002**: Users can sign in to existing account in under 10 seconds
- **SC-003**: Users can create a new task in under 10 seconds
- **SC-004**: Users can view their task list in under 3 seconds
- **SC-005**: Users can update a task in under 15 seconds
- **SC-006**: Users can delete a task in under 10 seconds
- **SC-007**: Users can mark task complete/incomplete in under 5 seconds
- **SC-008**: Users can assign priority and tags to task in under 20 seconds
- **SC-009**: Users can search and filter tasks to find specific item in under 15 seconds
- **SC-010**: Users can sort tasks by different criteria with results appearing in under 2 seconds
- **SC-011**: Users can create recurring task and see auto-creation work within 10 seconds of completion
- **SC-012**: Users can set due date and reminder, receive notification at specified time
- **SC-013**: System maintains complete data isolation (users never see other users' tasks)
- **SC-014**: Application handles 100 concurrent users without performance degradation
- **SC-015**: Task list loads and displays within 2 seconds for users with 100+ tasks
- **SC-016**: All API requests receive response within 500ms (p95)
- **SC-017**: Database queries complete within 100ms (p95)
- **SC-018**: Search returns results within 1 second for databases with 10,000+ tasks
- **SC-019**: Reminders are delivered within 60 seconds of scheduled time (background job check interval)
- **SC-020**: Overdue tasks are identified and highlighted within 1 minute of passing due date
- **SC-021**: Recurring task next occurrence created immediately (<1 sec) after marking complete
- **SC-022**: Full demo workflow (signup → create task with all features → complete recurring task → receive reminder → signout) completes in under 120 seconds
- **SC-023**: Zero data loss during normal operations (all data persisted to database)
- **SC-024**: Application works on Chrome, Firefox, Safari (desktop and mobile)
- **SC-025**: Responsive design adapts to mobile (< 640px), tablet (640-1024px), and desktop (> 1024px)

## Assumptions

1. **Phase 1 Complete**: All Phase 1 features (console app with Basic + Intermediate + Advanced levels) are fully implemented, tested, and validated
2. **Environment Setup**: Developers have Node.js 18+, Python 3.13+, UV, and access to Neon PostgreSQL database
3. **Database Access**: Neon PostgreSQL instance is provisioned with DATABASE_URL environment variable available
4. **Local Development**: Frontend runs on localhost:3000, backend on localhost:8000
5. **CORS Configuration**: Backend CORS middleware allows requests from frontend origin (localhost:3000 in dev, production domain in prod)
6. **Email Uniqueness**: Email addresses are unique identifiers (no multiple accounts per email)
7. **Password Storage**: Better Auth handles password hashing with bcrypt or argon2 (industry-standard algorithms)
8. **JWT Expiration**: Tokens valid for 7 days (per constitution requirement), refresh tokens not included in Phase 2
9. **No Email Verification**: Users can sign in immediately after registration (no email confirmation flow in Phase 2)
10. **No Password Reset**: Forgot password functionality deferred to future phase (placeholder link acceptable)
11. **Single Session**: Users can be signed in on multiple devices simultaneously (JWT is stateless, no session invalidation)
12. **No Rate Limiting**: Authentication and API endpoints not rate-limited in Phase 2 (can add later for production)
13. **UTC Timestamps**: All datetime fields stored in UTC timezone, displayed in user's local timezone in frontend
14. **Hard Deletes**: Tasks are permanently deleted from database (no soft delete or archive feature in Phase 2)
15. **Basic UI**: Clean, functional, responsive UI with Tailwind CSS; advanced animations and polish deferred
16. **Browser Push Notifications**: Reminder notifications use Web Push API with Service Workers (requires HTTPS in production)
17. **Background Job**: Reminder checking runs every 60 seconds (acceptable 1-minute granularity for Phase 2)
18. **Recurring Task History**: parent_task_id provides simple linking; advanced history view (timeline, analytics) deferred
19. **Tag Management**: Tags created inline during task creation/editing; dedicated tag management UI (rename, merge, delete unused) deferred
20. **Calendar View**: Optional calendar view for tasks with due dates is bonus feature, not required for Phase 2 completion

## Out of Scope

The following are explicitly NOT included in Phase 2:

### Deferred to Phase III (AI Chatbot)

- AI chatbot interface for natural language task management
- Voice command input for task creation
- MCP server integration for AI agent capabilities
- Natural language processing for task attributes (e.g., "remind me tomorrow morning" → sets due date and reminder)

### Deferred to Phase IV-V (Infrastructure)

- Kubernetes deployment and orchestration
- Docker containerization (docker-compose.yml for local dev acceptable)
- Horizontal scaling configuration with load balancers
- Kafka event streaming for task events
- Dapr integration for microservices
- Production deployment to cloud platform (Vercel frontend acceptable)

### Deferred to Future Enhancements

- Email notifications (browser push only in Phase 2)
- SMS notifications for reminders
- Email verification for new accounts
- Password reset/forgot password flow (beyond placeholder link)
- Social authentication (Google, GitHub, Microsoft OAuth)
- Two-factor authentication (2FA)
- User profile management (avatar, bio, preferences)
- Account deletion and data export (GDPR compliance)
- Task sharing or collaboration (multi-user tasks, permissions)
- Real-time sync between multiple browser tabs/devices (WebSocket)
- Task comments or activity log
- File attachments on tasks
- Subtasks or nested task hierarchy
- Task dependencies (block/blocked by)
- Task time tracking (start/stop timer)
- Advanced filtering (multiple tags with OR logic, date ranges)
- Saved filters or custom views
- Task templates for common workflows
- Bulk operations (select multiple tasks, bulk edit/delete)
- Export/import tasks (CSV, JSON, iCal)
- Calendar integration (Google Calendar, Outlook sync)
- Dark mode or theme customization
- Internationalization (i18n) / multi-language support
- Accessibility audit (WCAG 2.1 Level AA compliance) - basic accessibility acceptable
- Progressive Web App (PWA) features (offline support, app install)
- Analytics dashboard (task completion rates, productivity insights)
- Notifications settings (choose notification types, frequency)
- Advanced recurring patterns (every 2 weeks, last Friday of month, etc.)
- Task priority auto-adjustment based on due date proximity
- AI-powered task suggestions or auto-categorization

## Implementation Notes

This specification defines Phase 2 of the "Evolution of Todo" hackathon project with expanded scope to include ALL 10 features from Phase 1. Key characteristics:

1. **Migration from Phase 1**: Brings ALL Phase 1 features (5 Basic + 3 Intermediate + 2 Advanced) from console to web interface
2. **Multi-User Architecture**: Adds authentication and complete user isolation (not present in Phase 1)
3. **Persistent Storage**: Replaces in-memory storage with Neon PostgreSQL database
4. **Modern Stack**: Uses Next.js 16+ App Router, TypeScript, Tailwind CSS, FastAPI, Better Auth JWT, SQLModel, Neon PostgreSQL
5. **Monorepo Structure**: Frontend and backend in separate subdirectories under phase2/ (phase2/frontend/, phase2/backend/)
6. **Spec-Driven**: All implementation follows spec → plan → tasks → implement workflow with Claude Code
7. **Context7 Integration**: Use MCP server to fetch up-to-date documentation for Next.js, FastAPI, SQLModel, Better Auth, Web Push API
8. **Constitution Compliance**: Follows all principles from `.specify/memory/constitution.md`
9. **API-First Design**: RESTful API with JWT authentication, ownership validation on every endpoint
10. **Responsive UI**: Mobile-first design with Tailwind CSS breakpoints (sm, md, lg)

## Dependencies

- **Requires**: Phase 1 (console app with ALL features: Basic + Intermediate + Advanced) complete and validated - provides feature baseline and implementation patterns
- **Blocks**: Phase 3 (AI Chatbot) - cannot start until web app foundation with all features exists
- **Related**: Phase 1 Advanced features (recurring tasks, reminders) provide implementation guidance for Phase 2 web equivalents
