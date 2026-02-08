---
id: 001
title: Phase V Part A Specification Creation
stage: spec
date: 2026-01-31
surface: agent
model: claude-opus-4-5-20251101
feature: 1-phase5-parta-advanced-events
branch: 1-phase5-parta-advanced-events
user: waqas
command: /sp.specify
labels: ["spec", "phase5", "advanced-features", "event-driven", "dapr"]
links:
  spec: specs/1-phase5-parta-advanced-events/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/1-phase5-parta-advanced-events/spec.md
  - specs/1-phase5-parta-advanced-events/checklists/requirements.md
tests:
  - null
---

## Prompt

/sp.specify

# specs/specify.md - Hackathon II: Phase V - Part A: Advanced Features & Event-Driven Logic

## Project Overview
Implement intermediate and advanced todo features, extend the task model, API, UI, and Cohere-powered chatbot to support new capabilities, and introduce event-driven architecture using Dapr Pub/Sub (Kafka) for decoupled processing of recurring tasks, reminders, and updates — all in code/logic only (no deployment yet).

## Current Phase
Phase V – Part A: Advanced Features Implementation + Event-Driven Logic (code, schema, API, UI, chatbot, Dapr calls)

## Target User
Authenticated users of the todo app who want richer task management:
- Assign priorities and tags
- Search/filter/sort tasks
- Set recurring tasks and due dates with reminders
- Manage everything via natural language chatbot

## Focus & Core Functionality
- Extend task model with new fields
- Update REST API and MCP tools to handle new fields
- Add UI controls (dropdowns, tags, date picker, sort/filter)
- Update Cohere agent to understand new commands
- Publish events via Dapr Pub/Sub for every relevant action
- Prepare event schemas for future consumers (recurring engine, notification service)

## User Journeys

1. **Creating advanced task**
   - Dashboard: Select priority, add tags, set due date/recurring
   - Chatbot: "Add high priority task 'Meeting' due next Friday recur weekly"
   → Task saved, event published to task-events

2. **Managing & viewing tasks**
   - Filter: "Show only high priority tasks tagged work"
   - Sort: "Sort by due date"
   - Search: "Find tasks with 'milk'"

3. **Recurring & reminders**
   - Set recurring: "Make this task repeat monthly until Dec 2026"
   - Set reminder: "Remind me 1 day before due date"
   → Event published to reminders topic

4. **Task completion**
   - Mark complete → if recurring → publish event for next instance creation

## Success Criteria (Part A only)
- Database schema updated with new fields (priority, tags, due_date, remind_at, recurring_interval, recurring_end)
- API endpoints accept & return new fields
- MCP tools extended (add_task, update_task, list_tasks with new params)
- Dashboard UI supports new inputs (priority dropdown, tags input, date picker, filter/sort UI)
- Chatbot handles new commands naturally (e.g., "add urgent task due tomorrow", "show pending high priority tasks")
- Every state change publishes correct event via Dapr Pub/Sub (logs show httpx.post to /publish/)
- Event schemas defined (JSON) for task-events and reminders
- Backward compatibility verified (basic add/list/complete/delete unchanged)
- No deployment or Dapr runtime in Part A — only code patterns for Dapr calls

## Constraints
- No Kubernetes, Helm, or deployment changes in Part A
- Use Dapr Pub/Sub HTTP API only (no kafka-python or confluent-kafka)
- Extend existing endpoints/tools — no new endpoints unless required
- UI changes additive (no redesign of existing dashboard/chatbot)
- All new logic must be natural-language compatible via Cohere agent
- Events published but no consumers yet (Part B)

## Not Building (Out of Scope for Part A)
- Dapr sidecar deployment or Kafka cluster (Part B)
- Cloud deployment (Part C)
- Actual reminder delivery or recurring instance creation (logic only)
- WebSocket real-time sync (future)
- Notification

## Response snapshot

Created comprehensive specification for Phase V Part A:
- Branch: `1-phase5-parta-advanced-events`
- Spec file: `specs/1-phase5-parta-advanced-events/spec.md`
- 6 user stories (4 P1, 2 P2) covering: advanced task creation, due dates/reminders, filter/sort, search, recurring, event publishing
- 37 functional requirements across model, API, MCP tools, UI, chatbot, and events
- 10 measurable success criteria (technology-agnostic)
- 6 edge cases identified
- Assumptions documented
- Quality checklist created and validated - all items pass

## Outcome

- Impact: Complete specification ready for planning phase
- Tests: N/A - specification document
- Files: 2 files created (spec.md, checklists/requirements.md)
- Next prompts: /sp.clarify (if needed) or /sp.plan to create implementation plan
- Reflection: Specification covers all user journeys from input, aligns with constitution v3.0.0 principles, maintains backward compatibility focus

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All checklist items validated
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.plan for implementation planning
