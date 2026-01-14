<!--
Sync Impact Report
==================
Version change: 1.0.0 (initial)
Ratification Date: 2026-01-14
Last Amended: 2026-01-14

Added sections:
- Full constitution with 10 principles for Phase III AI Chatbot
- Governance framework
- Technical standards for Cohere + OpenAI Agents SDK + MCP

Templates status:
- .specify/templates/spec-template.md: ✅ created
- .specify/templates/plan-template.md: ✅ created
- .specify/templates/tasks-template.md: ✅ created
- .specify/templates/phr-template.prompt.md: ✅ created

Follow-up TODOs: None
-->

# Project Constitution

**Project Name**: Hackathon II: Evolution of Todo - Phase III (AI-Powered Todo Chatbot)
**Constitution Version**: 1.0.0
**Ratification Date**: 2026-01-14
**Last Amended**: 2026-01-14

## Purpose Statement

This constitution establishes the non-negotiable principles, technical standards, and governance framework for Phase III of the Evolution of Todo hackathon project. Phase III integrates a fully functional AI-powered conversational interface into the existing full-stack multi-user todo application (Phase II) without breaking any previous functionality.

The AI chatbot MUST use Cohere API (Command R+ or latest model) for all LLM calls, OpenAI Agents SDK adapted to route through Cohere, and MCP Server using the Official MCP SDK (Python). The frontend chat UI MUST use OpenAI ChatKit configured with domain allowlist.

---

## Principle 1: Spec-Driven Development

All implementation MUST be driven by specifications in `/specs/`. No code changes are permitted without direct reference to a specification file.

**Rationale**: Specifications provide traceability, enable review before implementation, and ensure alignment between stakeholders. This is the foundation of the hackathon workflow.

**Rules**:
- Every feature MUST have a corresponding spec file before implementation begins
- Code changes MUST reference the spec file they implement
- Specs MUST be updated when requirements change, before code is modified
- Claude Code MUST generate all implementation code based on specs

---

## Principle 2: Backward Compatibility

The existing REST API, task dashboard, authentication flow, and data isolation MUST remain fully functional after Phase III integration.

**Rationale**: Phase III extends Phase II; it does not replace it. Users relying on the web dashboard MUST continue to have full functionality.

**Rules**:
- All existing API endpoints MUST continue to function identically
- The `/dashboard` route MUST remain accessible and fully functional
- Better Auth JWT authentication MUST be preserved
- Existing database schema (users, tasks, notifications tables) MUST NOT be altered in breaking ways
- New tables (conversations, messages) MUST be additive only

---

## Principle 3: User Data Isolation

The chatbot MUST only access and modify tasks belonging to the authenticated user. User data isolation is absolute and non-negotiable.

**Rationale**: Multi-tenant security requires strict data boundaries. A user MUST never see, modify, or delete another user's data through any interface.

**Rules**:
- Every MCP tool MUST accept `user_id` as a required parameter
- `user_id` MUST be extracted from the JWT token, never from user input
- All database queries MUST filter by `user_id`
- API responses MUST never include data from other users
- 403 Forbidden MUST be returned for any cross-user access attempt

---

## Principle 4: Stateless Server Architecture

No in-memory conversation state is permitted. All history MUST be persisted in the database.

**Rationale**: Stateless architecture enables horizontal scaling, prevents data loss on server restart, and ensures conversation continuity across sessions.

**Rules**:
- Conversation history MUST be stored in the `messages` table
- Server restart MUST NOT lose any conversation data
- Each request MUST load conversation context from the database
- No global variables or in-memory caches for conversation state
- Context window MUST be limited to last 20-30 messages for performance

---

## Principle 5: Cohere-Only LLM Backend

All LLM calls MUST use Cohere API. OpenAI API MUST NOT be called directly.

**Rationale**: Hackathon requirement specifies Cohere as the AI provider. OpenAI Agents SDK is used for agent orchestration but MUST route to Cohere.

**Rules**:
- Environment variable `COHERE_API_KEY` MUST be configured
- OpenAI Agents SDK MUST use a custom LLM wrapper routing to Cohere
- No `openai.` API calls for completion or chat
- Cohere Command R+ (or latest available model) MUST be used
- Agent reasoning and tool selection MUST be powered by Cohere

---

## Principle 6: MCP Tool Design

Exactly 5 MCP tools MUST be implemented: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`. All tools MUST be stateless and receive `user_id` from authenticated context.

**Rationale**: MCP tools provide the interface between the AI agent and the database. Consistent design ensures predictability and security.

**Rules**:
- Each tool MUST accept `user_id` (string, required) as first parameter
- Tools MUST perform direct database operations via SQLModel
- Tools MUST return structured JSON matching hackathon spec format
- Tools MUST NOT store any state between calls
- Tool chaining MUST be supported for complex operations
- All tool calls MUST be logged for debugging

---

## Principle 7: Conversation Persistence

Conversations and messages MUST be stored in dedicated database tables linked to `user_id`.

**Rationale**: Persistent conversations enable context across sessions, debugging, and user experience continuity.

**Rules**:
- `conversations` table: `id`, `user_id`, `title`, `created_at`, `updated_at`
- `messages` table: `id`, `conversation_id`, `user_id`, `role`, `content`, `tool_call_id`, `tool_name`, `created_at`
- Composite index on `(conversation_id, user_id)` for fast lookups
- Messages MUST include `role` values: "user", "assistant", "tool", "system"
- Conversation MUST resume perfectly after page refresh or server restart

---

## Principle 8: JWT Authentication Reuse

The chat endpoint MUST reuse the existing Better Auth JWT flow. No new authentication system is permitted.

**Rationale**: Single authentication mechanism reduces complexity and attack surface.

**Rules**:
- Chat endpoint: `POST /api/{user_id}/chat`
- JWT MUST be validated via existing middleware
- `user_id` MUST be extracted from JWT payload
- Path `user_id` MUST match JWT `user_id` (return 403 if mismatch)
- JWT expiration (7 days) MUST be enforced

---

## Principle 9: OpenAI ChatKit Frontend

The chat UI MUST use OpenAI ChatKit component configured with domain allowlist.

**Rationale**: ChatKit provides a production-ready chat interface that matches the agent SDK patterns.

**Rules**:
- ChatKit MUST be integrated into Next.js frontend
- Domain allowlist MUST be configured for production deployment
- Chat interface MUST display full conversation with proper styling
- Loading states, error toasts, and success notifications MUST be implemented
- POST-based chat only; no WebSockets required

---

## Principle 10: Graceful Agent Behavior

The agent MUST always confirm actions, handle errors gracefully, and ask for clarification when needed.

**Rationale**: User trust requires predictable, friendly, and helpful agent responses.

**Rules**:
- Every action MUST be confirmed with natural language response
- Errors MUST return user-friendly messages (not stack traces)
- Ambiguous requests MUST prompt clarification questions
- Tool chaining MUST be supported (e.g., "list then delete")
- Failed operations MUST suggest next steps
- Responses MUST include task titles in confirmations

---

## Governance

### Amendment Process

1. Propose amendment with rationale in a pull request
2. Review against existing principles for conflicts
3. Increment version number per semantic versioning:
   - MAJOR: Principle removal or backward-incompatible change
   - MINOR: New principle or significant expansion
   - PATCH: Clarification or typo fix
4. Update `Last Amended` date
5. Merge after approval

### Compliance Review

- All specs MUST be reviewed against constitution before approval
- Implementation MUST be verified against spec and constitution
- PHR records MUST document compliance decisions
- ADRs MUST be created for architecturally significant deviations

### Version History

| Version | Date       | Changes                                      |
|---------|------------|----------------------------------------------|
| 1.0.0   | 2026-01-14 | Initial constitution for Phase III AI Chatbot |

---

## Technical Standards Summary

| Component        | Technology                                    |
|------------------|-----------------------------------------------|
| AI Provider      | Cohere API (Command R+ or latest)             |
| Agent Framework  | OpenAI Agents SDK (routed to Cohere)          |
| MCP Server       | Official MCP SDK (Python)                     |
| Chat UI          | OpenAI ChatKit                                |
| Frontend         | Next.js 16+, TypeScript, Tailwind CSS         |
| Backend          | Python FastAPI, SQLModel                      |
| Database         | Neon Serverless PostgreSQL                    |
| Authentication   | Better Auth + JWT                             |
| Chat Endpoint    | `POST /api/{user_id}/chat`                    |

---

## Environment Variables

| Variable         | Description                                   |
|------------------|-----------------------------------------------|
| `COHERE_API_KEY` | Cohere API key for LLM calls                  |
| `DATABASE_URL`   | Neon PostgreSQL connection string             |
| `JWT_SECRET`     | Secret for JWT signing (existing)             |
| `CHATKIT_DOMAIN` | Domain allowlist for ChatKit (production)     |

---

## Success Criteria (Phase III)

- [ ] Authenticated user can open chat interface and manage tasks via natural language
- [ ] Chatbot handles: add, list, complete, update, delete tasks
- [ ] Conversation persists across page refresh and server restart
- [ ] Multiple users have isolated chat histories and tasks
- [ ] Agent confirms actions and handles errors gracefully
- [ ] Existing dashboard and REST API remain fully functional
- [ ] Cohere API is used for all agent reasoning
- [ ] MCP tools affect the same database as web UI
- [ ] ChatKit UI displays conversation with proper styling
