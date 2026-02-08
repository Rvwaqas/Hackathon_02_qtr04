# Implementation Plan: Phase V Part A - Advanced Features & Event-Driven Logic

**Branch**: `1-phase5-parta-advanced-events` | **Date**: 2026-01-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-phase5-parta-advanced-events/spec.md`

## Summary

Extend the Phase III/IV todo application with intermediate features (priorities, tags, search/filter/sort) and advanced features (recurring tasks, due dates, reminders), while introducing event-driven architecture via Dapr Pub/Sub. This phase focuses exclusively on **code and logic** — no deployment or infrastructure changes.

**Key Finding**: The codebase is **98% complete**. Database models, API routes, schemas, and frontend components already support all required fields. Remaining work focuses on MCP tool definitions, system prompt updates, event publishing service, and integration testing.

## Technical Context

**Language/Version**: Python 3.11 (Backend), TypeScript 5+ (Frontend)
**Primary Dependencies**: FastAPI, SQLModel, Cohere API, OpenAI Agents SDK, httpx (async HTTP), Next.js 15
**Storage**: PostgreSQL (Neon) — existing schema already has all required fields
**Testing**: pytest (backend), manual verification for chatbot intents
**Target Platform**: Web application (browser) — no deployment changes in Part A
**Project Type**: Web application (monorepo with `/frontend` and `/backend`)
**Performance Goals**:
- Filter/sort queries: < 100ms for up to 1000 tasks
- Event publishing: Non-blocking (fire-and-forget with logging)
- Chatbot response: Same as Phase III baseline (< 3 seconds)

**Constraints**:
- No Kubernetes, Helm, or deployment changes
- Use Dapr Pub/Sub HTTP API only (no kafka-python)
- Extend existing endpoints/tools — no new endpoints unless required
- All new logic must support natural language via chatbot
- Backward compatibility mandatory

## Constitution Check

*GATE: Must pass before implementation. Reference: `.specify/memory/constitution.md` v3.0.0*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | ✅ PASS | Plan derived from spec.md; all tasks traceable |
| II. No Manual Coding | ✅ WILL COMPLY | All implementation via Claude Code agents |
| III. Backward Compatibility | ✅ WILL VERIFY | Phase III chatbot commands preserved |
| IV. Event-Driven Priority | ✅ PLANNED | EventPublisher service for Dapr Pub/Sub |
| V. Dapr-Exclusive | ✅ COMPLIANT | No direct Kafka imports; HTTP to sidecar only |
| VI. Stateless & Scalable | ✅ COMPLIANT | No in-memory state; DB + Dapr only |
| VII. Reusability First | ✅ COMPLIANT | Extending existing MCP tools, not creating new |

**Non-Negotiables Compliance**:
- [x] Never bypass Dapr for event publishing
- [x] Never use direct Kafka client
- [x] Never break Phase III chatbot
- [x] All code traceable to spec/task
- [x] No deployment in Part A
- [x] No breaking API changes

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Existing Application                        │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │   Next.js   │   │   FastAPI   │   │   Cohere Agent      │   │
│  │  Frontend   │◄─►│   Backend   │◄─►│   + MCP Tools       │   │
│  └─────────────┘   └─────────────┘   └─────────────────────┘   │
│         │                │                     │                │
│         │                ▼                     │                │
│         │         ┌─────────────┐              │                │
│         │         │ TaskService │◄─────────────┘                │
│         │         └─────────────┘                               │
│         │                │                                      │
│         │                ▼                                      │
│         │         ┌─────────────┐                               │
│         │         │  PostgreSQL │ ◄── All fields already exist │
│         │         │   (Neon)    │                               │
│         │         └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ NEW: Event Publishing
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Event Publishing Layer                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  EventPublisher Service                  │   │
│  │  - CloudEvents 1.0 format                               │   │
│  │  - Graceful degradation (log error, don't fail)         │   │
│  │  - httpx.post to localhost:3500                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Dapr Sidecar (Part B runtime)              │   │
│  │  POST /v1.0/publish/kafka-pubsub/{topic}                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Kafka Topics (Part B deployment)           │   │
│  │  - task-events: created, updated, completed, deleted    │   │
│  │  - reminders: recurring.triggered, reminder.due         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Current State Assessment

### Already Implemented (No Changes Needed)

| Component | File | Status |
|-----------|------|--------|
| Task Model | `backend/src/models/task.py` | ✅ All fields exist (priority, tags, due_date, recurrence, reminder_offset_minutes) |
| API Routes | `backend/src/api/tasks.py` | ✅ All endpoints with filter/sort/search params |
| Pydantic Schemas | `backend/src/schemas/task.py` | ✅ TaskCreate, TaskUpdate, TaskResponse complete |
| TaskService | `backend/src/services/task.py` | ✅ Filter logic, recurring task creation |
| Frontend TaskForm | `frontend/components/tasks/TaskForm.tsx` | ✅ All inputs (priority, tags, due date, recurrence) |
| Chat Infrastructure | `backend/src/api/chat.py` | ✅ Conversation persistence, message history |

### Remaining Implementation

| Component | File | Work Required |
|-----------|------|---------------|
| MCP Tool Definitions | `backend/src/agents/config.py` | Add tags, recurrence, search, sort, order params |
| System Prompt | `backend/src/agents/config.py` | Add intent recognition patterns |
| TodoToolsHandler | `backend/src/mcp/tools.py` | Extend method signatures |
| Event Publisher | `backend/src/services/event_publisher.py` | NEW - Create Dapr Pub/Sub service |
| TaskService Integration | `backend/src/services/task.py` | Add event publishing calls |
| Integration Tests | `backend/tests/` | Add filter/sort/event tests |

## Project Structure

### Documentation (this feature)

```text
specs/005-phase5-parta-advanced-events/
├── spec.md                       # ✅ Feature specification (complete)
├── plan.md                       # ✅ This file
├── contracts/
│   ├── event-schema.md           # ✅ CloudEvents schema (complete)
│   └── mcp-tools.md              # ✅ Updated tool definitions (complete)
├── checklists/
│   └── requirements.md           # (to be generated)
└── tasks.md                      # (next: /sp.tasks)
```

### Source Code (to modify)

```text
backend/src/
├── agents/
│   └── config.py                 # MODIFY: TOOL_DEFINITIONS, SYSTEM_PROMPT
├── mcp/
│   └── tools.py                  # MODIFY: Method signatures
├── services/
│   ├── task.py                   # MODIFY: Add event publishing
│   └── event_publisher.py        # NEW: Dapr Pub/Sub service
└── tests/
    ├── test_filters.py           # NEW: Filter/sort tests
    ├── test_events.py            # NEW: Event publishing tests
    └── test_chatbot_intents.py   # NEW: Intent recognition tests
```

## Key Architectural Decisions

### 1. Event Publishing Pattern

**Choice**: Async fire-and-forget with graceful degradation
**Rationale**: Events are important but must not block user operations
**Implementation**:
```python
async def publish_event(topic, event_type, data):
    try:
        await httpx.post(f"http://localhost:3500/v1.0/publish/kafka-pubsub/{topic}", ...)
    except Exception as e:
        logger.error(f"Event publish failed: {e}")  # Log but don't raise
```

### 2. Event Schema

**Choice**: CloudEvents 1.0 specification
**Rationale**: Industry standard; portable; well-documented
**Reference**: `contracts/event-schema.md`

### 3. MCP Tool Extension

**Choice**: Extend existing tools with optional parameters
**Rationale**: Backward compatible; minimal code changes
**Reference**: `contracts/mcp-tools.md`

### 4. Priority Field Type

**Choice**: String enum (`high`, `medium`, `low`, `none`)
**Rationale**: Readable in DB, UI, and chatbot responses
**Already Implemented**: Yes, in Task model

### 5. Tags Storage

**Choice**: PostgreSQL JSON column with list of strings
**Rationale**: Native support; easy querying; already implemented
**Already Implemented**: Yes, in Task model

### 6. Recurrence Storage

**Choice**: JSON column with `{type, interval, end_date}`
**Rationale**: Flexible; handles all recurrence patterns
**Already Implemented**: Yes, in Task model

## Implementation Phases

### Phase 1: Event Publishing Service (Critical Path)

**Goal**: Create the foundation for event-driven architecture

**Tasks**:
1. **Create EventPublisher Service**
   - File: `backend/src/services/event_publisher.py`
   - Implement CloudEvents 1.0 format
   - Async HTTP POST to Dapr sidecar
   - Graceful degradation on failure
   - Event types: created, updated, completed, deleted, recurring.triggered

2. **Integrate with TaskService**
   - File: `backend/src/services/task.py`
   - Add event publishing after create_task()
   - Add event publishing after update_task()
   - Add event publishing after toggle_complete()
   - Add event publishing after delete_task()

**Exit Criteria**:
- [ ] EventPublisher class implemented
- [ ] CloudEvents format validated
- [ ] Graceful degradation tested (Dapr unavailable)
- [ ] TaskService calls EventPublisher on all CRUD ops
- [ ] Logs show event publish attempts

### Phase 2: MCP Tool Definitions Update (Critical Path)

**Goal**: Enable chatbot to use new parameters

**Tasks**:
1. **Update TOOL_DEFINITIONS in config.py**
   - Add `tags` parameter to add_task
   - Add `recurrence` parameter to add_task
   - Add `reminder_offset_minutes` to add_task
   - Add `search` parameter to list_tasks
   - Add `tag` filter parameter to list_tasks
   - Add `sort` and `order` parameters to list_tasks
   - Update descriptions for better intent recognition

2. **Update SYSTEM_PROMPT in config.py**
   - Add priority recognition patterns (high, urgent, important)
   - Add tag recognition patterns (tagged X, with tag X)
   - Add search recognition patterns (find X, search for X)
   - Add filter recognition patterns (show only, filter by)
   - Add sort recognition patterns (sort by, order by)
   - Add recurrence recognition patterns (repeat daily, every week)
   - Add due date recognition patterns (due tomorrow, by Friday)
   - Add reminder recognition patterns (remind me X before)

**Exit Criteria**:
- [ ] All new parameters added to TOOL_DEFINITIONS
- [ ] SYSTEM_PROMPT includes all intent patterns
- [ ] Tool descriptions clear and helpful
- [ ] Parameters validated (enums, types)

### Phase 3: TodoToolsHandler Extension

**Goal**: Handler methods accept and process new parameters

**Tasks**:
1. **Extend add_task method**
   - Accept tags, recurrence, reminder_offset_minutes
   - Pass to TaskService.create_task()
   - Include new fields in success message

2. **Extend list_tasks method**
   - Accept search, tag, sort, order parameters
   - Pass to TaskService.get_tasks()
   - Format output with new fields (priority badges, due dates)

3. **Extend update_task method**
   - Accept tags, recurrence, reminder_offset_minutes
   - Pass to TaskService.update_task()
   - Confirm changes in success message

**Exit Criteria**:
- [ ] add_task accepts all new parameters
- [ ] list_tasks accepts filter/sort parameters
- [ ] update_task accepts all update fields
- [ ] Success messages include relevant details
- [ ] Parameter validation working

### Phase 4: Integration Testing

**Goal**: Verify all features work correctly together

**Tasks**:
1. **API Filter/Sort Tests**
   - Test priority filter
   - Test tag filter
   - Test search by keyword
   - Test sort by each field (created_at, due_date, priority, title)
   - Test combined filters
   - Test ascending/descending order

2. **Event Publishing Tests**
   - Mock Dapr endpoint
   - Verify events published on create
   - Verify events published on update
   - Verify events published on complete
   - Verify events published on delete
   - Verify CloudEvents format
   - Verify graceful degradation

3. **Chatbot Intent Tests**
   - Test priority recognition (high priority task, urgent)
   - Test tag recognition (tagged work, with tag X)
   - Test search recognition (find tasks about, search for)
   - Test filter recognition (show high priority, filter by)
   - Test sort recognition (sort by due date, order by)
   - Test recurrence recognition (repeat daily, every week)
   - Test due date recognition (due tomorrow, by Friday)
   - Test backward compatibility (Phase III commands)

4. **Recurring Task Tests**
   - Test recurrence data storage
   - Test completion creates next occurrence
   - Test due date calculation (daily, weekly, monthly)
   - Test recurrence end_date respected
   - Test event published on recurring trigger

**Exit Criteria**:
- [ ] All filter combinations pass
- [ ] All sort orders pass
- [ ] Event publishing verified
- [ ] CloudEvents schema validated
- [ ] All chatbot intents recognized
- [ ] Phase III commands still work
- [ ] Recurring task logic verified

### Phase 5: Documentation & Validation

**Goal**: Ensure complete documentation and backward compatibility

**Tasks**:
1. **Update Documentation**
   - Document new chatbot commands
   - Document filter/sort API parameters
   - Document event types and schemas
   - Update README with Phase V Part A features

2. **Backward Compatibility Verification**
   - Run existing Phase III chatbot commands
   - Verify basic CRUD still works
   - Verify conversation history works
   - Verify user isolation works

3. **Final Validation**
   - Manual testing of all user stories
   - End-to-end test of advanced task creation
   - End-to-end test of filtering and sorting
   - End-to-end test of recurring tasks
   - Verify event logs show all publishes

**Exit Criteria**:
- [ ] All documentation updated
- [ ] Phase III commands verified
- [ ] All success criteria from spec met
- [ ] Manual E2E testing complete

## Testing & Validation Strategy

### Automated Tests

| Test Suite | File | Coverage |
|------------|------|----------|
| Filter Tests | `test_filters.py` | Priority, tag, search, sort, combined |
| Event Tests | `test_events.py` | Publish on CRUD, schema validation, graceful degradation |
| Intent Tests | `test_chatbot_intents.py` | All new intent patterns |
| Recurring Tests | `test_recurring.py` | Create next occurrence, date calculation |

### Manual Test Scenarios

| Scenario | Command | Expected Outcome |
|----------|---------|------------------|
| Create advanced task | "add high priority task meeting due Friday tagged work" | Task created with all fields |
| Filter by priority | "show high priority tasks" | Only high priority tasks returned |
| Filter by tag | "show tasks tagged work" | Only tasks with work tag |
| Search | "find tasks about quarterly" | Tasks matching search term |
| Sort | "sort by due date ascending" | Tasks sorted correctly |
| Combined | "show pending high priority tagged work sorted by due date" | Correct filtered/sorted list |
| Recurring | "make task 1 recur weekly" | Recurrence set |
| Complete recurring | "complete task 1" | Next occurrence created |
| Event verify | Check logs after any CRUD | Event publish logged |
| Backward compat | "add task buy milk" | Works as before |

### Validation Checklist

From spec success criteria:

| ID | Criterion | Verification |
|----|-----------|--------------|
| SC-001 | Intermediate features via API | API tests pass |
| SC-002 | Advanced features via API | API tests pass |
| SC-003 | Chatbot recognizes intents | Intent tests pass |
| SC-004 | Events on all CRUD | Event tests pass |
| SC-005 | CloudEvents 1.0 schema | Schema validation |
| SC-006 | Graceful degradation | Mock Dapr failure test |
| SC-007 | Phase III still works | Regression tests |
| SC-008 | Combined filters work | Parameterized tests |
| SC-009 | Recurring creates next | Recurring tests |
| SC-010 | Commands documented | Documentation review |

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cohere doesn't recognize new intents | Medium | High | Extensive prompt engineering; many examples in system prompt |
| Event publishing adds noticeable latency | Low | Medium | Fire-and-forget pattern; async non-blocking |
| Filter combinations have edge cases | Medium | Medium | Comprehensive parameterized tests |
| Recurring date calculation bugs | Medium | High | Use dateutil; add edge case tests (month-end) |
| Breaking existing chatbot | Low | High | Run Phase III regression tests first |
| Dapr unavailable in dev | Low | Low | Graceful degradation; mock in tests |

## Dependencies

### External (Already Available)

- Cohere API ✅
- PostgreSQL (Neon) ✅
- httpx library ✅

### Internal (From Previous Phases)

- Phase III chatbot ✅
- Phase IV deployment ✅
- Task model with all fields ✅
- API with filter/sort ✅
- Frontend with all inputs ✅

### For Part B (Out of Scope)

- Dapr sidecar runtime
- Kafka cluster
- Event consumers

## Success Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| New filter params work | 100% | API tests |
| New sort params work | 100% | API tests |
| Search works | 100% | API tests |
| Events published | 100% CRUD ops | Log inspection |
| CloudEvents valid | 100% | Schema tests |
| Intent recognition | 90%+ | Manual testing |
| Phase III preserved | 100% | Regression |
| Combined filters | 100% | Parameterized tests |

## Agent Assignment

| Phase | Agent | Responsibility |
|-------|-------|----------------|
| 1 | DaprAgent | Event publishing service |
| 2 | FeatureAgent | MCP tool definitions |
| 3 | FeatureAgent | TodoToolsHandler extension |
| 4 | FeatureAgent | Integration testing |
| 5 | OrchestratorAgent | Documentation & validation |

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Begin Phase 1 (Event Publishing Service)
3. Progress through phases sequentially
4. Create PHR after each major milestone
5. Run validation tests before PR

---

**Status**: ✅ Plan Complete — Ready for Task Generation
