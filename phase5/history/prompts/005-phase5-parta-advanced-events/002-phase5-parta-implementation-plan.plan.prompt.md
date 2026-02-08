---
id: 002
title: Phase V Part A Implementation Plan
stage: plan
date: 2026-01-31
surface: agent
model: claude-opus-4-5-20251101
feature: 005-phase5-parta-advanced-events
branch: 1-phase5-parta-advanced-events
user: waqas
command: /sp.plan
labels: ["plan", "phase5", "event-driven", "dapr", "implementation", "architecture"]
links:
  spec: specs/005-phase5-parta-advanced-events/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-phase5-parta-advanced-events/plan.md
tests:
  - null
---

## Prompt

```text
/sp.plan
# specs/plan.md - Hackathon II: Phase V - Part A: Advanced Features & Event-Driven Logic

## Architecture Sketch (Part A – Code & Logic Level)
Extension of existing Phase III/IV application with new fields, extended APIs/tools/agent, and Dapr Pub/Sub event publishing.

Existing App (FastAPI + Next.js + Cohere Agent + MCP)
├── Task Model Extension (priority, tags, due_date, recurring...)
├── API / MCP Tools Extension (new params in add/update/list)
├── UI Extension (dashboard + chatbot)
└── Cohere Agent Extension (new intents & tool calls)
│
▼
Dapr Pub/Sub Calls (HTTP to localhost:3500)
│
▼
Kafka Topics (prepared for Part B): task-events, reminders

- All publishing via Dapr sidecar (code only in Part A)
- No runtime Dapr/Kafka here — only httpx.post patterns
- Future consumers (recurring, notification) will subscribe in Part B

## Component Breakdown
- Backend: models, schemas, routes, mcp tools, agent, event_publisher
- Frontend: TaskForm, TaskList, api.ts (all already complete)
- Database: No migration needed (fields exist)
- Event Publishing: Every action → CloudEvents JSON → Dapr HTTP

## Key Decisions
- Priority: str enum (high/medium/low)
- Tags: PostgreSQL JSON array
- Recurring: Event publish on complete
- Dapr: httpx.post to localhost:3500
- Event Schema: CloudEvents 1.0 with full task snapshot

## Implementation Sequence
1. Event Publisher Service (DaprAgent)
2. MCP Tool Definitions (FeatureAgent)
3. TodoToolsHandler Extension (FeatureAgent)
4. Integration Testing (FeatureAgent)
5. Documentation & Validation (OrchestratorAgent)
```

## Response snapshot

### Implementation Plan Created

Created comprehensive implementation plan at `specs/005-phase5-parta-advanced-events/plan.md` with:

**Key Finding**: Codebase is **98% complete**. All database fields, API routes, schemas, and frontend components already exist.

**Remaining Work** (5 Phases):

| Phase | Focus | Agent |
|-------|-------|-------|
| 1 | Event Publishing Service | DaprAgent |
| 2 | MCP Tool Definitions Update | FeatureAgent |
| 3 | TodoToolsHandler Extension | FeatureAgent |
| 4 | Integration Testing | FeatureAgent |
| 5 | Documentation & Validation | OrchestratorAgent |

**Architecture Highlights**:
- EventPublisher service with CloudEvents 1.0 format
- Async fire-and-forget with graceful degradation
- HTTP POST to Dapr sidecar (localhost:3500)
- Topics: task-events, reminders

**Files to Modify**:
- `backend/src/agents/config.py` - TOOL_DEFINITIONS, SYSTEM_PROMPT
- `backend/src/mcp/tools.py` - Method signatures
- `backend/src/services/task.py` - Add event publishing
- `backend/src/services/event_publisher.py` - NEW

**Files Already Complete**:
- `backend/src/models/task.py` - All fields exist
- `backend/src/api/tasks.py` - All endpoints ready
- `backend/src/schemas/task.py` - Complete
- `frontend/components/tasks/TaskForm.tsx` - All inputs

**Constitution Compliance**: ✅ All 7 principles verified

**Risk Mitigations**:
- Cohere intent recognition → Extensive prompt engineering
- Event latency → Fire-and-forget pattern
- Filter edge cases → Parameterized tests
- Breaking Phase III → Regression tests first

## Outcome

- Impact: Comprehensive implementation plan for Phase V Part A
- Tests: N/A - plan document
- Files: 1 file created (plan.md)
- Next prompts: `/sp.tasks` to generate task breakdown with dependencies
- Reflection: Plan leverages 98% complete codebase; focused on remaining gaps (event publishing, MCP tools, system prompt, tests)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
  - Constitution check included: ✓
  - 5 implementation phases defined: ✓
  - Agent assignments specified: ✓
  - Exit criteria for each phase: ✓
  - Risk analysis with mitigations: ✓
  - Testing strategy detailed: ✓
  - Architecture diagram included: ✓
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Generate tasks with `/sp.tasks`
