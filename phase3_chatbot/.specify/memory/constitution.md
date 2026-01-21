# Phase III: Todo AI Chatbot Constitution

<!--
SYNC IMPACT REPORT
Version Change: 0.0.0 → 1.0.0 (initial constitution for Phase III chatbot)
New Principles (5):
  1. Strictly Spec-Driven Development
  2. Seamless Backend Integration
  3. User Data Isolation & Security
  4. Stateless Server Architecture
  5. Tech Stack Standardization
New Sections:
  - Key Standards (Tech Stack, Database Extensions, Authentication, MCP Tools, Agent Behavior)
  - Constraints (Cohere API requirement, Chat endpoint pattern, Database approach)
  - Success Criteria (User-facing functionality validation)
Templates requiring review:
  - .specify/templates/spec-template.md (ensure spec sections align with constitution requirements)
  - .specify/templates/plan-template.md (ensure architectural decisions align with principles)
  - .specify/templates/tasks-template.md (ensure task structure reflects constitution principles)
  - .specify/templates/commands/*.md (verify no outdated references remain)
Deferred Items: None
-->

## Core Principles

### I. Strictly Spec-Driven Development
No code without direct reference to a specification file in `/specs/`. All implementation and refinements must be generated via Claude Code using approved specifications. Every feature must have a corresponding spec document that precedes any implementation. This ensures traceability, reduces assumptions, and keeps code aligned with business intent.

### II. Seamless Backend Integration
The AI chatbot must integrate with the existing full-stack application without breaking any previous functionality. The same database (PostgreSQL via Neon), same authentication system (Better Auth + JWT), and same task logic must be reused. New tables (`conversations`, `messages`) are extensions only; the existing `tasks`, `users`, and related tables remain unchanged and functional.

### III. User Data Isolation & Security (NON-NEGOTIABLE)
The chatbot can only access and modify tasks of the authenticated user. The `user_id` derived from JWT middleware must be passed to all MCP tools and used throughout conversation storage and task operations. Multi-user isolation is absolute; no cross-user data leakage is acceptable. Conversation history is per-user and per-session.

### IV. Stateless Server Architecture
No in-memory conversation state or session memory in the backend. All conversation history is persisted in the database (`conversations` and `messages` tables) keyed by `user_id`. The server can restart or scale horizontally without loss of context. Each request cycle is independent and fully stateless, with all state loaded from the database on demand.

### V. Tech Stack Standardization
The following technologies are mandatory and must be used exactly as specified:
- **AI Provider**: Cohere (Command R+ or latest model) via Cohere API (not OpenAI)
- **Agent Framework**: OpenAI Agents SDK, configured to route through Cohere as the LLM backend (custom wrapper if needed)
- **MCP Server**: Official MCP SDK (Python)
- **Chat UI**: OpenAI ChatKit (configured with domain allowlist)
- **Frontend**: Next.js 16+ (App Router), TypeScript, Tailwind CSS, Better Auth + JWT
- **Backend**: Python FastAPI, SQLModel, Neon Serverless PostgreSQL

## Key Standards

### Tech Stack (Mandatory)
- **AI & Agents**: Cohere API (LLM), OpenAI Agents SDK (framework), Official MCP SDK (Python)
- **Chat Interface**: OpenAI ChatKit (frontend component)
- **Existing Stack**: Next.js 16+ (App Router), FastAPI, SQLModel, Neon PostgreSQL, Better Auth + JWT

### Database Extensions
- **New Tables**:
  - `conversations` — stores chat sessions linked to `user_id`
  - `messages` — stores individual chat messages (role, content, timestamp) linked to conversation
- **Existing Tables**: Fully preserved (`tasks`, `users`, `user_sessions`, `better_auth_*`); no schema changes to existing data

### Authentication & Request Context
- Chat endpoint protected via existing JWT middleware: `POST /api/{user_id}/chat`
- `user_id` derived from JWT payload is required for all MCP tool invocations
- Tools are stateless; they perform direct DB operations with user context
- No new authentication system; reuse existing Better Auth + JWT flow

### MCP Tools (Exactly 5 Required)
1. **add_task** — Create a new task (title, description, optional fields) for user
2. **list_tasks** — Retrieve user's tasks (all, filtered by status: pending, completed)
3. **complete_task** — Mark a task complete by ID or natural description
4. **delete_task** — Remove a task by ID or natural description
5. **update_task** — Modify task fields (title, description, status, priority) by ID

Each tool signature must accept `user_id` as a required string parameter, plus domain-specific arguments. Tools return structured responses (success/error, task data, validation messages).

### Agent Behavior Standards
- Always confirm actions with friendly, natural responses before and after execution
- Graceful error handling: task not found, invalid ID, permission denied, etc.
- Support tool chaining (e.g., "list tasks" → "mark first incomplete task complete") where needed
- Use Cohere model for reasoning, tool selection, and multi-turn conversation
- Never expose raw errors to user; translate to conversational error messages

## Constraints

### Technology
- **LLM Provider**: Must use Cohere API exclusively (not OpenAI, Claude, or other providers) for all LLM reasoning and tool selection
- **Agent SDK Configuration**: OpenAI Agents SDK must be adapted to route LLM calls through Cohere (implement custom LLM wrapper if needed)
- **No WebSockets**: Chat is request-response only (POST-based); no persistent WebSocket connections

### Architecture
- **Chat Endpoint**: `POST /api/{user_id}/chat` — matches existing API path pattern; user_id from JWT
- **Conversation Persistence**: All history stored in database tables (`conversations`, `messages`); no in-memory state
- **No New Auth**: Reuse existing Better Auth JWT flow; no separate chatbot login
- **Stateless Request Cycle**: Each request must be fully self-contained; state loaded from DB on demand

### Frontend Integration
- **ChatKit Component**: OpenAI ChatKit (must be configured with domain allowlist for security)
- **Self-Hosting Option**: ChatKit can be hosted independently or embedded; domain key required

## Success Criteria

- ✅ Authenticated user can open chat interface and manage tasks via natural language
- ✅ Chatbot correctly handles all basic commands:
  - Add tasks with title and optional description
  - List all tasks, pending tasks, or completed tasks
  - Mark a task complete by ID or natural description
  - Update task fields (title, description, priority, etc.) by ID or description
  - Delete a task by ID or natural description
- ✅ Conversation history persists across page refresh and server restart
- ✅ Multiple users have isolated chat histories and tasks; zero cross-user data leakage
- ✅ Agent always confirms actions and handles errors gracefully (task not found, invalid input, etc.)
- ✅ Existing dashboard, REST API, and database remain fully functional; no breaking changes
- ✅ Cohere API is used for all LLM reasoning and tool selection; no other LLM provider is invoked

## Governance

**Amendment Procedure**:
- Constitution supersedes all other practices and specifications.
- Amendments require written justification (PR description or issue) and explicit approval from project lead.
- Each amendment must update the `LAST_AMENDED_DATE` and increment `CONSTITUTION_VERSION` according to semantic versioning.
- Breaking changes (principle removals or redefinitions) require MAJOR version bump; new principles or sections require MINOR; clarifications require PATCH.

**Compliance & Review**:
- All PRs and code reviews must verify compliance with core principles (especially User Data Isolation, Spec-Driven Development, and Tech Stack Standardization).
- Specification documents must explicitly reference principles they enforce or violate.
- Tests and task definitions must reflect constitution-mandated requirements (e.g., multi-user isolation tests, spec coverage).

**Runtime Guidance**:
- See `CLAUDE.md` in project root for development workflow, tool usage, and coding standards.
- See `docs/` for API contracts, deployment guides, and architecture decisions.

**Version**: 1.0.0 | **Ratified**: 2026-01-15 | **Last Amended**: 2026-01-15
