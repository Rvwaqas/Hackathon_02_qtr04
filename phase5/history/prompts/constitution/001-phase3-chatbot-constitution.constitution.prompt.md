---
id: 001
title: Phase III Chatbot Constitution
stage: constitution
date: 2026-01-15
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: main
user: waqas
command: /sp.constitution
labels: ["constitution", "phase3", "chatbot", "governance", "spec-driven"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests: []
---

## Prompt

# speckit.constitution - Hackathon II: Evolution of Todo (Phase III - AI-Powered Todo Chatbot)

## Project
Phase III: Todo AI Chatbot
Integrate a fully functional AI-powered conversational interface into the existing full-stack multi-user todo application (Phase II) without breaking any previous functionality.

## Core Principles
- Strictly Spec-Driven Development: No code without direct reference to a file in /specs/
- No manual coding allowed: All implementation and refinements must be generated via Claude Code using specs
- Backward compatibility: Existing REST API, task dashboard, authentication, and data isolation must remain fully functional
- Seamless integration: The AI chatbot must work on the same database, same users, same tasks as the current full-stack app
- User data isolation is absolute: Chatbot can only access and modify tasks of the authenticated user
- Stateless server architecture: No in-memory conversation state — all history persisted in database
- Reusability and maintainability: MCP tools must wrap existing task logic where possible

## Key Standards
- Tech Stack Additions (must use exactly these):
  - AI Provider: Cohere (Command R+ or latest model) via Cohere API
  - Agent Framework: OpenAI Agents SDK adapted to use Cohere as the LLM backend
  - MCP Server: Official MCP SDK (Python)
  - Chat UI: OpenAI ChatKit (configured with domain allowlist)
- Existing Stack Remains:
  - Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS, Better Auth + JWT
  - Backend: Python FastAPI, SQLModel, Neon Serverless PostgreSQL
- Database Extensions:
  - New tables: conversations and messages (linked to authenticated user_id)
  - Existing tasks table unchanged
- Authentication:
  - Chat endpoint protected via existing JWT middleware
  - user_id from JWT used throughout MCP tools and conversation storage
- MCP Tools (exactly 5):
  - add_task, list_tasks, complete_task, delete_task, update_task
  - All tools receive user_id (string, required) from authenticated context
  - Tools are stateless and perform direct DB operations
- Agent Behavior:
  - Always confirm actions with friendly, natural responses
  - Graceful error handling (task not found, invalid ID, etc.)
  - Support tool chaining when needed
  - Use Cohere model for reasoning and tool selection

## Constraints
- Must use Cohere API (not OpenAI) for all LLM calls
- OpenAI Agents SDK must be configured to route through Cohere (via custom LLM wrapper if needed)
- Chat endpoint: POST /api/{user_id}/chat (matches existing path pattern)
- Conversation history stored in database for stateless restarts
- No new authentication system — reuse Better Auth JWT flow
- No in-memory state in backend — fully stateless request cycle
- Frontend must use OpenAI ChatKit component (hosted or self-hosted with domain key)
- No WebSockets — simple POST-based chat

## Success Criteria
- Authenticated user can open chat interface and manage tasks via natural language
- Chatbot correctly handles all basic commands:
  - Add tasks with title/description
  - List all/pending/completed tasks
  - Mark complete, update, delete by ID or description
- Conversation persists across page refresh and server restart
- Multiple users have isolated chat histories and tasks
- Agent always confirms actions and handles errors gracefully
- Existing dashboard and REST API remain fully functional
- Cohere API is used for all LLM reasoning

## Response snapshot

Created Phase III: Todo AI Chatbot Constitution (v1.0.0) with:
- 5 core principles covering spec-driven development, seamless integration, user data isolation, stateless architecture, and tech stack standardization
- 4 key standards sections: tech stack, database extensions, authentication, MCP tools, and agent behavior
- 3 constraint sections: technology, architecture, and frontend integration
- Success criteria checklist with 7 verifiable acceptance criteria
- Governance rules for amendments, compliance review, and version management

Constitution written to: `.specify/memory/constitution.md`

## Outcome

- ✅ Impact: Foundation governance document established for Phase III chatbot project; all principles, standards, and constraints now formally defined; enables spec-driven development workflow and alignment across team
- 🧪 Tests: None (governance document; no executable tests)
- 📁 Files: 1 file created/modified (`.specify/memory/constitution.md`)
- 🔁 Next prompts: Create `/specs/chatbot-core/spec.md` with feature requirements aligned to constitution; Create `/specs/chatbot-core/plan.md` with architectural decisions; Create `/specs/chatbot-core/tasks.md` with implementation tasks
- 🧠 Reflection: Constitution successfully captures all user-provided requirements in structured, enforceable form. Ready for specification and planning phases.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (governance document)
- Prompt variant (if applicable): N/A
- Next experiment: Verify templates align with constitution requirements before proceeding to spec phase
