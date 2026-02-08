---
id: 003
title: Phase V Part A Advanced Events Constitution
stage: constitution
date: 2026-01-31
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 1-phase5-parta-advanced-events
user: waqas
command: /sp.constitution
labels: ["constitution", "phase5", "event-driven", "dapr", "kafka", "advanced-features"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

```text
/sp.constitution
# speckit.constitution - Hackathon II: Evolution of Todo (Phase V - Part A: Advanced Features & Event-Driven Logic)

## Project
Phase V – Part A: Implement Intermediate & Advanced Todo Features + Event-Driven Architecture with Kafka & Dapr (code & logic only – no deployment yet)

## Core Principles
- Strictly Spec-Driven Development: No new feature, field, endpoint, event, or Dapr usage without approved spec/task
- No manual coding allowed: All implementation via Claude Code using specs and agents
- Backward compatibility mandatory: Phase III chatbot, basic CRUD, user isolation, and Phase IV local deployment must remain fully functional
- Event-driven priority: Every state-changing operation (create/update/complete/recurring/due-date) must publish events via Dapr Pub/Sub
- Use Dapr exclusively for distributed concerns: No direct Kafka client, no direct DB calls for events/state
- Stateless & scalable design: No in-memory state — use Dapr state if needed
- Reusability: Extend existing models, APIs, MCP tools, Cohere agent instructions

## Key Standards
- New Features to Implement:
  - Intermediate Level:
    - Priorities: high / medium / low (enum/string)
    - Tags/Categories: array of strings
    - Search: keyword in title/description
    - Filter: by status, priority, tags
    - Sort: by created_at, due_date, priority, title
  - Advanced Level:
    - Recurring Tasks: interval (daily/weekly/monthly), end_date optional
    - Due Dates & Reminders: due_date (datetime), remind_at (datetime or relative)
- Database Extensions (SQLModel):
  - Add to Task model:
    - priority: str | None = None
    - tags: list[str] = Field(default_factory=list, sa_column=ARRAY(String))
    - due_date: datetime | None = None
    - remind_at: datetime | None = None
    - recurring_interval: str | None = None
    - recurring_end: datetime | None = None
- API Extensions:
  - Extend existing endpoints to accept new fields
  - Add query params for filter/sort/search
  - MCP tools must support new params (add_task, update_task, list_tasks)
- Event-Driven Architecture:
  - Kafka topics (via Dapr Pub/Sub): task-events, reminders
  - Every CRUD + due-date set + recurring complete → publish event
  - Events used for future services (recurring engine, notification) in Part B
- Dapr Usage (code-level only in Part A):
  - Publish events via Dapr Pub/Sub HTTP (localhost:3500/v1.0/publish/...)
  - No Dapr deployment here — only code patterns
- Cohere Agent:
  - Update instructions to recognize new intents
  - Extend tool descriptions with new parameters

## Constraints
- No deployment or infra changes in Part A (only app code + Dapr calls)
- No direct Kafka import — only Dapr Pub/Sub
- Extend existing MCP tools — do not create new ones unless necessary
- UI changes minimal and additive (no breaking dashboard/chatbot)
- All new logic must support natural language via chatbot
- No breaking changes to existing endpoints or DB schema usage

## Success Criteria (Part A only)
- New fields saved & retrieved correctly in DB
- Priorities, tags, search/filter/sort working in API and UI
- Recurring tasks create next instance logic ready (event publish)
- Due date/reminder fields saved & event published on set
- Chatbot understands commands like:
  - "add high priority task buy milk due tomorrow"
  - "show tasks tagged work"
  - "sort tasks by priority"
  - "make task 1 recur weekly until Dec 2026"
- All operations publish correct events via Dapr Pub/Sub (logs show publish calls)
- Backward compatibility verified (basic add/list/complete/delete still work)

## Non-Negotiables
- Never bypass Dapr for event publishing
- Never use direct Kafka or DB polling for events
- Never break Phase III chatbot or basic features
- All new code traceable to specs
- No premature deployment — Part A is logic/features only

## Bonus Alignment
- Clean extension of MCP tools and Cohere agent
- Event schema readiness for Part B services
- Natural language coverage for all new features
```

## Response snapshot

Successfully created constitution v3.0.0 for Phase V Part A: Advanced Features & Event-Driven Logic.

**Key Changes from v2.0.0 (Phase IV K8s Deployment):**

### Version Bump: MAJOR (2.0.0 → 3.0.0)
Rationale: Phase transition from infrastructure deployment to feature development with event-driven architecture.

### Modified Principles:
1. "AI-Assisted Operations Only" → "Event-Driven Priority"
2. "Reusable Blueprints" → "Dapr-Exclusive Distributed Concerns"
3. "Demonstrable AIOps" → "Stateless & Scalable Design"

### Added Sections:
- **Features Matrix**: Intermediate (priorities, tags, search/filter/sort) and Advanced (recurring, due dates, reminders)
- **Database Extensions**: SQLModel field specifications with JSON columns
- **API Extensions**: Query parameters table and schema updates
- **Event-Driven Architecture**: Kafka topics, CloudEvents schema, event types
- **Dapr Usage Standards**: HTTP publish pattern with graceful degradation
- **Cohere Agent Updates**: New intents and MCP tool parameter extensions

### Removed Sections (Phase IV specific):
- Docker Images standards
- Helm Chart standards
- Kubernetes Resources details
- AI-Assisted Operations table

### Success Criteria Organized:
- Database & Model verification
- API Layer functionality
- Recurring Tasks logic
- Due Dates & Reminders
- Chatbot Integration (with example commands)
- Event Publishing verification
- Backward Compatibility checks

### Files Created:
- `.specify/memory/constitution.md` (new directory structure created)

## Outcome

- Impact: MAJOR constitution update establishing event-driven architecture principles for Phase V Part A
- Tests: N/A - constitution document
- Files: 1 file created (.specify/memory/constitution.md)
- Next prompts: `/sp.specify` to create or verify feature specification for Phase V Part A
- Reflection: Constitution successfully transitioned from Phase IV K8s focus to Phase V event-driven architecture. Non-negotiables clearly enforce Dapr-only event publishing and backward compatibility requirements.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
  - All 7 core principles defined with rationale
  - Features matrix covers all intermediate + advanced requirements
  - Database extensions match user input specifications
  - Event-driven architecture fully specified (topics, schema, types)
  - Dapr usage pattern includes code example
  - Success criteria comprehensive with checkboxes
  - Non-negotiables aligned with user constraints
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin spec verification to ensure existing spec aligns with constitution
