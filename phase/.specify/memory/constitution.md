# Phase V Part A: Advanced Features & Event-Driven Logic Constitution

<!--
SYNC IMPACT REPORT
Version Change: 2.0.0 → 3.0.0 (MAJOR: Phase transition from K8s Deployment to Advanced Features + Event-Driven Architecture)

Modified Principles:
  1. "Strictly Spec-Driven Development" → retained, extended for events/Dapr
  2. "AI-Assisted Operations Only" → replaced with "Event-Driven Priority"
  3. "Backward Compatibility" → retained, expanded for Phase III + IV
  4. "Reusable Blueprints" → replaced with "Dapr-Exclusive Distributed Concerns"
  5. "Demonstrable AIOps" → replaced with "Stateless & Scalable Design"
  6. "Tech Stack Standardization (Phase IV)" → replaced with "Tech Stack Standardization (Phase V Part A)"

New Sections:
  - Model Extensions Standards (priority, tags, recurring, due dates)
  - API Extensions Standards (filter/sort/search)
  - Event-Driven Architecture Standards (Kafka topics, Dapr Pub/Sub)
  - Dapr Usage Standards (code-level patterns)
  - Cohere Agent Updates section
  - Updated Success Criteria for Part A features

Removed Sections:
  - Docker Images Standards (Phase IV specific)
  - Helm Chart Standards (Phase IV specific)
  - Kubernetes Resources Standards (Phase IV specific)
  - AI-Assisted Operations Standards (replaced with event patterns)

Templates requiring review:
  ✅ .specify/templates/plan-template.md (Constitution Check section generic, no update needed)
  ✅ .specify/templates/spec-template.md (User Stories structure generic, no update needed)
  ✅ .specify/templates/tasks-template.md (Phase structure generic, no update needed)

Deferred Items: None
-->

## Core Principles

### I. Strictly Spec-Driven Development

No new feature, field, endpoint, event, or Dapr usage without direct reference to a specification file or task in `/specs/`. All implementation—including model extensions, API changes, event publishing, and chatbot updates—MUST be generated via Claude Code using approved specifications. Every code artifact must have a corresponding spec document that precedes implementation. This ensures traceability, reduces manual errors, and maintains alignment between features and infrastructure.

### II. Event-Driven Priority (NON-NEGOTIABLE)

Every state-changing operation MUST publish events via Dapr Pub/Sub. This includes:
- Task creation, update, completion, and deletion
- Due date assignment and modification
- Recurring task completion (triggers next instance creation)
- Reminder scheduling

Events are the source of truth for distributed operations. No state change is complete until its corresponding event is successfully published.

### III. Backward Compatibility (NON-NEGOTIABLE)

The application MUST retain ALL Phase III and Phase IV functionality without regression:

**Phase III Requirements (Must Work)**:
- Cohere-powered AI chatbot responding to natural language
- Full task management (CRUD via dashboard and chatbot)
- User isolation (multi-user data separation)
- Stateless chat endpoint with database-backed persistence
- Better Auth + JWT authentication flow

**Phase IV Requirements (Must Work)**:
- Docker images build successfully
- Helm charts deploy to Minikube
- All pods reach Running state
- Services accessible via port-forward

Breaking Phase III or Phase IV functionality is a failure regardless of new feature success.

### IV. Dapr-Exclusive Distributed Concerns (NON-NEGOTIABLE)

All distributed infrastructure access MUST go through Dapr. This includes:
- **Event Publishing**: Via Dapr Pub/Sub HTTP API (`localhost:3500/v1.0/publish/...`)
- **State Management**: Via Dapr State API (if needed for conversation history)
- **Secrets**: Via Dapr Secrets API (optional, can use K8s secrets)

**Prohibited**:
- No direct Kafka client imports (`kafka-python`, `aiokafka`, `confluent-kafka`)
- No direct database polling for events
- No in-memory event queues

This ensures infrastructure portability and aligns with hackathon bonus criteria.

### V. Stateless & Scalable Design

No in-memory state for any distributed concern. All state MUST be externalized:
- Task data in Neon PostgreSQL
- Conversation history in database or Dapr State Store
- Events in Kafka (via Dapr Pub/Sub)

Application pods can be restarted, scaled, or replaced without data loss.

### VI. Tech Stack Standardization (Phase V Part A)

The following technologies are mandatory for Phase V Part A:

**Application Stack** (from Phase III/IV):
- Next.js 16+ (frontend)
- FastAPI (backend)
- Cohere/Gemini API (chatbot)
- Neon PostgreSQL (database)
- SQLModel (ORM)

**Event-Driven Stack** (new in Phase V):
- Dapr Pub/Sub (event abstraction)
- Kafka topics: `task-events`, `reminders`
- CloudEvents format for all events

**No Deployment Changes in Part A**:
- Code patterns only
- Dapr HTTP calls prepared but not deployed
- Infrastructure changes deferred to Part B

## Key Standards

### Model Extensions

The Task model MUST be extended with the following fields:

```python
class Task(SQLModel, table=True):
    # Existing fields retained
    id: int
    user_id: str
    title: str
    description: str | None = None
    completed: bool = False
    created_at: datetime
    updated_at: datetime

    # NEW: Priority (Phase V Part A)
    priority: str | None = None  # "high", "medium", "low"

    # NEW: Tags (Phase V Part A)
    tags: list[str] | None = None  # ["work", "personal", "urgent"]

    # NEW: Due Date & Reminders (Phase V Part A)
    due_date: datetime | None = None
    remind_before: int | None = None  # minutes before due_date

    # NEW: Recurring (Phase V Part A)
    recurring_interval: str | None = None  # "daily", "weekly", "monthly"
    recurring_end: datetime | None = None
```

**Rules**:
- All new fields MUST have default values (nullable or explicit default)
- Existing CRUD MUST continue working without new fields (backward compatible)
- Field validation MUST be added for enum-like values (priority, recurring_interval)

### API Extensions

Existing endpoints MUST be extended (not replaced):

**GET /api/tasks**:
- Add query params: `priority`, `tags`, `sort_by`, `search`, `due_before`, `due_after`
- Default behavior unchanged when no params provided

**POST /api/tasks**:
- Accept new optional fields: `priority`, `tags`, `due_date`, `remind_before`, `recurring_interval`, `recurring_end`
- Basic task creation still works with just `title`

**PUT /api/tasks/{id}**:
- Accept updates to all new fields
- Partial updates supported

**MCP Tools**:
- `add_task`: Add optional params for priority, tags, due_date, recurring
- `update_task`: Add support for modifying new fields
- `list_tasks`: Add filter/sort params

### Event-Driven Architecture

**Kafka Topics** (via Dapr Pub/Sub):

| Topic | Events | Purpose |
|-------|--------|---------|
| `task-events` | task.created, task.updated, task.completed, task.deleted | Task lifecycle |
| `reminders` | reminder.scheduled, reminder.triggered | Due date reminders |

**Event Publishing Rules**:
- Every CRUD operation MUST publish to `task-events`
- Setting due_date MUST publish to `reminders` (for future scheduler)
- Completing recurring task MUST publish `task.completed` (for next instance creation)
- All events MUST use CloudEvents 1.0 format

**Event Schema**:
```json
{
  "specversion": "1.0",
  "type": "com.taskmanager.task.created",
  "source": "/tasks/backend-service",
  "id": "<uuid>",
  "time": "<ISO8601>",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "user_id": "user-abc",
    "title": "Buy milk",
    "priority": "high",
    "tags": ["shopping"]
  }
}
```

### Dapr Usage (Code-Level Only)

In Part A, Dapr calls are implemented in code but not deployed:

```python
# Event publishing pattern
import httpx

DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

async def publish_event(topic: str, event: dict):
    """Publish event via Dapr sidecar (will work when Dapr deployed)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}",
                json=event,
                timeout=5.0
            )
            response.raise_for_status()
    except Exception as e:
        # Log but don't fail the operation
        print(f"Event publish failed (Dapr not running): {e}")
```

**Rules**:
- All event publishing code MUST be implemented
- Failures MUST be logged but NOT block the primary operation
- Code MUST work with or without Dapr sidecar running

### Cohere Agent Updates

The chatbot instructions MUST be updated to recognize new intents:

**New Commands to Support**:
- "add high priority task buy milk"
- "add task meeting due tomorrow at 3pm"
- "show tasks tagged work"
- "sort tasks by priority"
- "make task 1 recur weekly until December 2026"
- "show overdue tasks"
- "add urgent task with tag personal"

**Tool Descriptions**:
- Update `add_task` tool description with new parameters
- Update `list_tasks` tool description with filter/sort options
- Add examples for priority, tags, due dates, recurring

## Constraints

### Code Constraints
- No deployment or infrastructure changes in Part A (code only)
- No direct Kafka imports—only Dapr Pub/Sub patterns
- Extend existing MCP tools—do not create new ones unless necessary
- All new logic MUST support natural language via chatbot

### UI Constraints
- Changes minimal and additive (no breaking dashboard/chatbot)
- New fields displayed but not required
- Existing workflows unchanged

### Breaking Change Prevention
- No modifications to existing endpoint response structure
- No removal of existing fields
- No changes to authentication flow
- No changes to database connection handling

## Success Criteria (Part A Only)

### Database & Model
- [ ] New fields (priority, tags, due_date, remind_before, recurring_interval, recurring_end) saved correctly
- [ ] Existing tasks without new fields continue to work
- [ ] Field validation enforces allowed values

### API
- [ ] GET /api/tasks with filter/sort params returns correct results
- [ ] POST /api/tasks with new fields creates task correctly
- [ ] Basic CRUD still works without new fields (backward compatible)

### Event Publishing
- [ ] Task creation publishes `task.created` event (visible in logs)
- [ ] Task update publishes `task.updated` event
- [ ] Task completion publishes `task.completed` event
- [ ] Due date assignment publishes to `reminders` topic
- [ ] Events follow CloudEvents format

### Chatbot
- [ ] "add high priority task buy milk due tomorrow" creates correct task
- [ ] "show tasks tagged work" returns filtered list
- [ ] "sort tasks by priority" returns ordered list
- [ ] "make task 1 recur weekly until Dec 2026" sets recurring fields
- [ ] Basic commands still work (add, list, complete, delete)

### Backward Compatibility
- [ ] Phase III chatbot functionality verified
- [ ] Phase III dashboard functionality verified
- [ ] Phase IV Docker builds still work
- [ ] Phase IV Helm deploy still works

## Non-Negotiables

These are absolute requirements with no exceptions:

1. **Never** bypass Dapr for event publishing (no direct Kafka client)
2. **Never** use database polling for event detection
3. **Never** break Phase III chatbot or basic CRUD features
4. **Never** break Phase IV containerization or deployment
5. **Never** implement features not traced to specs
6. **Never** deploy infrastructure in Part A (code patterns only)
7. **Always** publish events for state-changing operations
8. **Always** use CloudEvents format for all events
9. **Always** handle Dapr unavailability gracefully (log, don't fail)

## Bonus Alignment

These align with hackathon bonus criteria:

- **Event-Driven Architecture**: Kafka topics via Dapr Pub/Sub with CloudEvents
- **Dapr Portability**: All distributed concerns through Dapr sidecar abstraction
- **Extensibility**: Model and API designed for future services (recurring engine, notifications)
- **Natural Language**: All features accessible via chatbot commands
- **Spec-Driven**: Every feature traceable to specification documents

## Governance

**Amendment Procedure**:
- Constitution supersedes all other practices and specifications.
- Amendments require written justification (PR description or issue) and explicit approval from project lead.
- Each amendment must update the `LAST_AMENDED_DATE` and increment `CONSTITUTION_VERSION` according to semantic versioning.
- Breaking changes (principle removals or redefinitions) require MAJOR version bump; new principles or sections require MINOR; clarifications require PATCH.

**Compliance & Review**:
- All PRs and code reviews must verify compliance with core principles (especially Event-Driven Priority, Backward Compatibility, and Dapr-Exclusive).
- Specification documents must explicitly reference principles they enforce or violate.
- Event publishing code must be present for all state-changing operations.

**Runtime Guidance**:
- See `CLAUDE.md` in project root for development workflow, tool usage, and coding standards.
- See `.claude/agents/` for specialized agent definitions (FeatureAgent, DaprAgent, KafkaAgent, OrchestratorAgent).
- See `.claude/Skills/` for implementation skills (dapr-sidecar-integration.md, kafka-event-architecture.md).
- See `docs/` for API contracts, deployment guides, and architecture decisions.

**Version**: 3.0.0 | **Ratified**: 2026-01-15 | **Last Amended**: 2026-01-31
