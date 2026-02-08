# Feature Specification: Phase V Part A - Advanced Features & Event-Driven Logic

**Feature Branch**: `1-phase5-parta-advanced-events`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "Implement intermediate and advanced todo features, extend the task model, API, UI, and Cohere-powered chatbot to support new capabilities, and introduce event-driven architecture using Dapr Pub/Sub (Kafka) for decoupled processing of recurring tasks, reminders, and updates — all in code/logic only (no deployment yet)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Task with Priority and Tags (Priority: P1)

As an authenticated user, I want to create a new task with priority level and tags so that I can organize and categorize my work effectively.

**Why this priority**: Priority and tags are fundamental organizational features that directly enhance task management. They provide immediate value by enabling users to identify important tasks and group related work.

**Independent Test**: Can be fully tested by creating a task via dashboard or chatbot with priority="high" and tags=["work", "urgent"], verifying the task is saved and displayed with these attributes.

**Acceptance Scenarios**:

1. **Given** a logged-in user on the dashboard, **When** they create a task with title "Meeting", priority "high", and tags ["work"], **Then** the task is saved with all attributes and displayed in the task list with priority indicator and tag badges.

2. **Given** a logged-in user in the chatbot, **When** they say "Add high priority task Meeting tagged work", **Then** the system creates the task with priority="high" and tags=["work"] and confirms creation.

3. **Given** a logged-in user, **When** they create a task without specifying priority or tags, **Then** the task is created with default priority (none) and empty tags (backward compatible).

---

### User Story 2 - Set Due Date and Reminder (Priority: P1)

As an authenticated user, I want to set a due date and reminder for my tasks so that I never miss important deadlines.

**Why this priority**: Due dates are essential for time-sensitive task management. Users need to know when tasks are due and receive timely reminders.

**Independent Test**: Can be fully tested by creating a task with due_date="2026-02-15" and remind_before=1440 (1 day), verifying the task displays the due date and reminder is scheduled.

**Acceptance Scenarios**:

1. **Given** a logged-in user on the dashboard, **When** they create a task with due date "Feb 15, 2026" and reminder "1 day before", **Then** the task is saved with due_date and remind_before fields set correctly.

2. **Given** a logged-in user in the chatbot, **When** they say "Add task Buy groceries due tomorrow at 3pm remind me 1 hour before", **Then** the system creates the task with appropriate due_date and remind_before values.

3. **Given** a task with a due date that has passed, **When** the user views the task list, **Then** the task is visually marked as overdue.

---

### User Story 3 - Filter and Sort Tasks (Priority: P1)

As an authenticated user, I want to filter and sort my tasks by various criteria so that I can quickly find and focus on specific tasks.

**Why this priority**: With many tasks having priorities, tags, and due dates, users need efficient ways to find and organize their view without scrolling through everything.

**Independent Test**: Can be fully tested by creating multiple tasks with different priorities and tags, then applying filters and verifying correct task subsets are returned.

**Acceptance Scenarios**:

1. **Given** a user with multiple tasks of varying priorities, **When** they filter by priority="high", **Then** only high-priority tasks are displayed.

2. **Given** a user with tagged tasks, **When** they filter by tag="work", **Then** only tasks with the "work" tag are displayed.

3. **Given** a user with tasks having due dates, **When** they sort by due_date ascending, **Then** tasks are ordered by soonest due date first.

4. **Given** a logged-in user in the chatbot, **When** they say "Show high priority tasks tagged work sorted by due date", **Then** the filtered and sorted list is returned.

---

### User Story 4 - Search Tasks (Priority: P2)

As an authenticated user, I want to search my tasks by keyword so that I can quickly locate specific tasks by their content.

**Why this priority**: Search is a convenience feature that becomes more valuable as the task list grows. Core organization (P1 features) should work first.

**Independent Test**: Can be fully tested by creating tasks with specific keywords, searching for those keywords, and verifying matching tasks are returned.

**Acceptance Scenarios**:

1. **Given** a user with multiple tasks, **When** they search for "milk", **Then** all tasks containing "milk" in title or description are returned.

2. **Given** a logged-in user in the chatbot, **When** they say "Find tasks with grocery", **Then** matching tasks are listed.

---

### User Story 5 - Set Recurring Tasks (Priority: P2)

As an authenticated user, I want to set tasks as recurring on a schedule so that I don't have to manually recreate regular tasks.

**Why this priority**: Recurring tasks reduce manual effort for routine work but require the foundation of due dates (P1) to function properly.

**Independent Test**: Can be fully tested by creating a task with recurring_interval="weekly" and recurring_end="2026-12-31", verifying the fields are saved correctly.

**Acceptance Scenarios**:

1. **Given** a logged-in user on the dashboard, **When** they create a task with recurring="weekly" until "Dec 2026", **Then** the task is saved with recurring_interval="weekly" and recurring_end set.

2. **Given** a logged-in user in the chatbot, **When** they say "Make task 5 recur monthly until December 2026", **Then** the task is updated with recurring settings.

3. **Given** a recurring task, **When** the user marks it complete, **Then** the system publishes an event for the next instance to be created (by future consumer).

---

### User Story 6 - Event Publishing for All State Changes (Priority: P1)

As a system operator, I want every task state change to publish an event so that future services can consume these events for reminders, recurring logic, and notifications.

**Why this priority**: Event-driven architecture is a core requirement for Phase V. All state changes must emit events to enable future decoupled processing.

**Independent Test**: Can be fully tested by performing CRUD operations and checking logs for Dapr Pub/Sub HTTP calls with correct CloudEvents payloads.

**Acceptance Scenarios**:

1. **Given** the backend is running, **When** a task is created, **Then** a `task.created` event is published to the `task-events` topic via Dapr Pub/Sub.

2. **Given** the backend is running, **When** a task is updated, **Then** a `task.updated` event is published to the `task-events` topic.

3. **Given** the backend is running, **When** a task is completed, **Then** a `task.completed` event is published to the `task-events` topic.

4. **Given** the backend is running, **When** a task is deleted, **Then** a `task.deleted` event is published to the `task-events` topic.

5. **Given** a task with a due date is created, **When** the task is saved, **Then** a `reminder.scheduled` event is published to the `reminders` topic.

6. **Given** Dapr sidecar is not running, **When** an event publish is attempted, **Then** the operation logs a warning but does not fail the primary CRUD operation.

---

### Edge Cases

- What happens when a user creates a recurring task without a due date? System should accept it (next instance logic deferred to Part B).
- What happens when a user sets remind_before but no due_date? System should ignore remind_before or return validation error (recommend: ignore silently).
- What happens when filtering returns zero results? System displays an empty state with appropriate message.
- What happens when Dapr sidecar is unavailable? System logs warning and continues with CRUD operation (graceful degradation).
- What happens when a user provides an invalid priority value? System returns validation error ("priority must be one of: high, medium, low").
- What happens when searching with an empty query? System returns all tasks (same as no filter).

## Requirements *(mandatory)*

### Functional Requirements

**Model Extensions**:
- **FR-001**: System MUST extend the Task model with `priority` field accepting values: "high", "medium", "low", or null.
- **FR-002**: System MUST extend the Task model with `tags` field as a list of strings.
- **FR-003**: System MUST extend the Task model with `due_date` field as an optional datetime.
- **FR-004**: System MUST extend the Task model with `remind_before` field as an optional integer (minutes before due_date).
- **FR-005**: System MUST extend the Task model with `recurring_interval` field accepting values: "daily", "weekly", "monthly", or null.
- **FR-006**: System MUST extend the Task model with `recurring_end` field as an optional datetime.

**API Extensions**:
- **FR-007**: GET /api/tasks endpoint MUST accept query parameters: `priority`, `tags`, `sort_by`, `search`, `due_before`, `due_after`.
- **FR-008**: POST /api/tasks endpoint MUST accept optional fields: `priority`, `tags`, `due_date`, `remind_before`, `recurring_interval`, `recurring_end`.
- **FR-009**: PUT /api/tasks/{id} endpoint MUST accept updates to all new fields with partial update support.
- **FR-010**: All existing API behavior MUST remain unchanged when new fields are not provided (backward compatibility).

**MCP Tool Extensions**:
- **FR-011**: `add_task` MCP tool MUST accept optional parameters for priority, tags, due_date, remind_before, recurring_interval, recurring_end.
- **FR-012**: `update_task` MCP tool MUST support modifying all new fields.
- **FR-013**: `list_tasks` MCP tool MUST accept filter parameters: priority, tags, sort_by, search, due_before, due_after.

**UI Extensions**:
- **FR-014**: Dashboard MUST display priority dropdown (high/medium/low) when creating or editing tasks.
- **FR-015**: Dashboard MUST display tags input allowing multiple tag entry.
- **FR-016**: Dashboard MUST display date picker for due date selection.
- **FR-017**: Dashboard MUST display filter controls for priority and tags.
- **FR-018**: Dashboard MUST display sort options (by due date, priority, created date).
- **FR-019**: Dashboard MUST display search input for keyword search.
- **FR-020**: Task list items MUST visually indicate priority level and display tags.

**Chatbot Extensions**:
- **FR-021**: Chatbot MUST understand priority in natural language (e.g., "high priority", "urgent").
- **FR-022**: Chatbot MUST understand tags in natural language (e.g., "tagged work", "with tag personal").
- **FR-023**: Chatbot MUST understand due dates in natural language (e.g., "due tomorrow", "due next Friday at 3pm").
- **FR-024**: Chatbot MUST understand recurring patterns (e.g., "recur weekly", "repeat monthly until December").
- **FR-025**: Chatbot MUST understand filter/sort commands (e.g., "show high priority tasks", "sort by due date").
- **FR-026**: Chatbot MUST understand search commands (e.g., "find tasks with milk").

**Event Publishing**:
- **FR-027**: System MUST publish `task.created` event to `task-events` topic when a task is created.
- **FR-028**: System MUST publish `task.updated` event to `task-events` topic when a task is updated.
- **FR-029**: System MUST publish `task.completed` event to `task-events` topic when a task is marked complete.
- **FR-030**: System MUST publish `task.deleted` event to `task-events` topic when a task is deleted.
- **FR-031**: System MUST publish `reminder.scheduled` event to `reminders` topic when a task with due_date and remind_before is created or updated.
- **FR-032**: All events MUST use CloudEvents 1.0 format with specversion, type, source, id, time, datacontenttype, and data fields.
- **FR-033**: Event publishing MUST use Dapr Pub/Sub HTTP API (POST to localhost:3500/v1.0/publish/{pubsub}/{topic}).
- **FR-034**: Event publishing failures MUST be logged but MUST NOT fail the primary CRUD operation.

**Validation**:
- **FR-035**: System MUST validate priority values against allowed enum ("high", "medium", "low").
- **FR-036**: System MUST validate recurring_interval values against allowed enum ("daily", "weekly", "monthly").
- **FR-037**: System MUST validate that recurring_end is after due_date if both are provided.

### Key Entities

- **Task**: Represents a todo item. Extended with: priority (enum), tags (list of strings), due_date (datetime), remind_before (integer minutes), recurring_interval (enum), recurring_end (datetime).
- **TaskEvent**: Represents a CloudEvents-formatted event published for task lifecycle changes. Contains: specversion, type, source, id, time, datacontenttype, data (task details).
- **ReminderEvent**: Represents a CloudEvents-formatted event published for scheduled reminders. Contains: task_id, user_id, due_date, remind_at, title.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create tasks with priority, tags, and due dates in under 30 seconds via dashboard.
- **SC-002**: Users can filter tasks by priority and get results within 1 second.
- **SC-003**: Users can sort tasks by due date and see ordered results immediately.
- **SC-004**: Users can search tasks by keyword and get matching results within 1 second.
- **SC-005**: Chatbot successfully interprets and executes advanced commands (priority, tags, due dates, recurring) with 90% accuracy on standard phrases.
- **SC-006**: Every task creation, update, completion, and deletion generates a corresponding event visible in application logs.
- **SC-007**: All existing Phase III chatbot commands continue to work without modification.
- **SC-008**: All existing Phase III dashboard functionality works without regression.
- **SC-009**: System gracefully handles Dapr unavailability without failing user operations.
- **SC-010**: All new fields are optional and existing tasks without these fields display and function correctly.

## Assumptions

- Dapr sidecar will not be running during Part A development; event publishing code is prepared but will only succeed when Dapr is deployed in Part B.
- Date/time handling uses ISO 8601 format and stores in UTC.
- Tags are case-insensitive for filtering purposes.
- Priority display order: high > medium > low > none.
- remind_before value of 0 or null means no reminder.
- recurring_end of null means recurring indefinitely (until manually stopped).
- Search is case-insensitive and matches partial words in title and description.

## Constraints

- No Kubernetes, Helm, or deployment changes in Part A.
- No direct Kafka client libraries (kafka-python, confluent-kafka, aiokafka) - only Dapr Pub/Sub HTTP API.
- Extend existing endpoints - no new REST endpoints unless absolutely required.
- UI changes are additive - no redesign of existing dashboard layout.
- All new features must be accessible via natural language chatbot.
- Events are published but not consumed in Part A (consumers built in Part B).

## Out of Scope

- Dapr sidecar deployment or Kafka cluster setup (Part B).
- Cloud deployment to DOKS/AKS/GKE (Part C).
- Actual reminder delivery or notification sending (future).
- Recurring task instance creation logic (future consumer service).
- WebSocket real-time sync between clients.
- Email or push notification integration.
