---
id: 002
title: Implementation Plan for Chatbot Architecture
stage: plan
date: 2026-01-15
surface: agent
model: claude-haiku-4-5-20251001
feature: 003-ai-todo-chatbot
branch: 003-ai-todo-chatbot
user: waqas
command: /sp.plan
labels: ["plan", "architecture", "phase3", "chatbot", "cohere", "mcp"]
links:
  spec: specs/003-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-todo-chatbot/plan.md
  - specs/003-ai-todo-chatbot/data-model.md
  - specs/003-ai-todo-chatbot/contracts/chat-api.md
  - specs/003-ai-todo-chatbot/contracts/mcp-tools.md
  - specs/003-ai-todo-chatbot/quickstart.md
tests: []
---

## Prompt

Hackathon II: Phase III - AI-Powered Todo Chatbot with Cohere Integration

## Architecture Sketch
Extension of Phase II full-stack monorepo with stateless AI chatbot layer:
|   Frontend      |                               |    Backend      |
| (Next.js)       |   POST /api/{user_id}/chat    | (FastAPI)       |
| - Dashboard     | <---------------------------> | - Existing CRUD |
| - ChatKit UI    |   JWT + conversation_id       | - JWT Middleware|
| - Chat Icon     |                               | - Chat Endpoint |
+-----------------+                               | - OpenAI Agents |
^        |   (Cohere LLM)  |
|        | - MCP Server    |
Neon DB     | - Tools (5)     |

- Frontend: Floating chatbot icon → opens ChatKit panel → sends messages to chat endpoint
- Backend: Stateless chat endpoint → loads history → runs agent with Cohere → calls MCP tools → saves response

[... architecture details and implementation sequence ...]

## Response snapshot

Created comprehensive implementation plan for Phase III AI-Powered Todo Chatbot with 5 Phase 1 design artifacts:

**Plan (plan.md)**:
- 10-phase implementation sequence (foundation → agent → endpoint → frontend → testing → deployment)
- Technical context (Python 3.11+, FastAPI, OpenAI Agents SDK, AsyncOpenAI for Cohere, Official MCP SDK)
- Constitution Check: ✅ All 5 principles fully compliant
- Project structure with web application monorepo layout
- Key architectural decisions with tradeoffs (Cohere LLM, OpenAI Agents SDK, database-only persistence, floating chat UI)
- Risks & mitigations (tool calling consistency, conversation history growth, user isolation security)

**Data Model (data-model.md)**:
- Conversation entity: id, user_id (FK), created_at, updated_at, title
- Message entity: id, conversation_id (FK), role (user/assistant), content, created_at, metadata
- SQL migrations for both tables with appropriate indexes
- Data flow diagram (request → load history → save user message → run agent → save response → return)
- Message immutability guarantee and conversation lifecycle
- Performance targets: <10ms conversation lookup, <50ms history load, <5ms insert

**API Contract (contracts/chat-api.md)**:
- Endpoint: POST /api/{user_id}/chat with authentication
- Request: message (required), conversation_id (optional)
- Response: response text, conversation_id, message_id
- 4 error types: 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error
- Behavior specs: conversation creation/reuse, agent execution flow, error handling, rate limiting (optional)
- 3 detailed workflow examples (add task, list tasks, error handling)
- Implementation notes on idempotency, timeouts, concurrency, logging

**MCP Tools Contract (contracts/mcp-tools.md)**:
- 5 tools fully specified with parameters, returns, error responses:
  - add_task(user_id, title, description?, priority?, due_date?)
  - list_tasks(user_id, status?, priority?)
  - complete_task(user_id, task_id)
  - update_task(user_id, task_id, title?, description?, priority?, status?)
  - delete_task(user_id, task_id)
- Tool registration code with OpenAI Agents SDK
- Tool execution flow diagram
- User isolation guarantee (CRITICAL): every tool validates user_id
- Error handling strategy (agent catches errors, responds naturally)
- Testing strategy (unit, integration, contract tests)

**Quickstart Guide (quickstart.md)**:
- Prerequisites (Phase II complete, Python 3.11+, Cohere API key)
- Setup instructions: database migrations, environment variables, client setup
- Minimal working implementation (30 lines backend endpoint, 100 lines agent, 150 lines frontend component)
- Test scenarios with curl examples and browser integration
- Debugging guide for common issues
- Next steps for production deployment

**Files Generated**: 5 artifacts in specs/003-ai-todo-chatbot/
- plan.md (2000+ lines comprehensive plan)
- data-model.md (full schema design with migrations)
- contracts/chat-api.md (OpenAPI-style API contract)
- contracts/mcp-tools.md (MCP tool specifications)
- quickstart.md (minimal working example)

## Outcome

- ✅ Impact: Complete architectural plan ready for implementation; all design decisions documented with tradeoffs; Phase 1 design artifacts (data model, API contracts, MCP tools) complete; quickstart enables rapid MVP implementation; ready for `/sp.tasks` phase
- 🧪 Tests: 0 tests (planning phase); automated tests will be generated in `/sp.tasks`
- 📁 Files: 5 files created/updated in specs/003-ai-todo-chatbot/
- 🔁 Next prompts: Run `/sp.tasks` to generate tasks.md with detailed implementation breakdown organized by user story; implement and test according to task checklist
- 🧠 Reflection: Plan fully addresses spec requirements and constitutional constraints. Architecture is straightforward: extend Phase II with chat endpoint + agent layer + UI component. Stateless design enables horizontal scaling. MCP tools wrap existing task service for code reuse. Ready for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check = PASS (all 5 principles compliant)
- Prompt variant (if applicable): N/A
- Next experiment: Implement Phase 1 tasks (database + Cohere client + models) and validate with unit tests

