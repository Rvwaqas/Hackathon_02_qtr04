---
id: 001
title: "Phase III AI Chatbot Constitution"
stage: constitution
date: 2026-01-14
surface: agent
model: claude-opus-4-5
feature: none
branch: main
user: system
command: /sp.constitution
labels: ["constitution", "phase3", "ai-chatbot", "cohere", "mcp"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .specify/templates/spec-template.md
  - .specify/templates/plan-template.md
  - .specify/templates/tasks-template.md
  - .specify/templates/phr-template.prompt.md
tests: []
---

# Phase III AI Chatbot Constitution

## Prompt

```text
cohere api key Ik1ziqg6vN9wui3DwFsKVtPyHMOR1YNjMXpcTe0o
Hackathon II: Evolution of Todo (Phase III - AI-Powered Todo Chatbot)

## Project Phase III: Todo AI Chatbot
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
- Cohere API is used for agent reasoning and response generation
- MCP tools successfully called and affect the same database as the web UI
- OpenAI ChatKit UI displays full conversation with proper styling
- All specifications in /specs/ updated (chatbot.md, mcp-tools.md, updated schema.md, ui/chat-page.md)
## Non-Negotiables
- Never bypass JWT authentication or user_id isolation
- Never store conversation state in memory
- Never use OpenAI API directly — all LLM calls must go through Cohere
- Never duplicate task logic — MCP tools should call existing service layer if possible
- Never break existing task CRUD functionality
- Domain allowlist configured for production ChatKit deployment
- Environment variables added: Cohere_api Ik1ziqg6vN9wui3DwFsKVtPyHMOR1YNjMXpcTe0o
## Bonus Alignment
- Clean, natural, confirmatory responses from agent
- Robust handling of ambiguous requests (asks for clarification when needed)
- Tool chaining support (e.g., list then delete in one turn)
```

## Response Summary

Created the Phase III AI Chatbot constitution at `.specify/memory/constitution.md` version 1.0.0 with 10 core principles:

1. **Spec-Driven Development** - All code must reference specs
2. **Backward Compatibility** - Phase II functionality preserved
3. **User Data Isolation** - Absolute user_id filtering
4. **Stateless Architecture** - No in-memory conversation state
5. **Cohere-Only LLM** - All LLM calls via Cohere API
6. **MCP Tool Design** - 5 stateless tools with user_id
7. **Conversation Persistence** - Database storage for conversations
8. **JWT Authentication Reuse** - Better Auth flow preserved
9. **ChatKit Frontend** - OpenAI ChatKit integration
10. **Graceful Agent Behavior** - Confirmations and error handling

Also created supporting templates:
- spec-template.md
- plan-template.md
- tasks-template.md
- phr-template.prompt.md

Technical standards documented: Cohere API, OpenAI Agents SDK (routed to Cohere), MCP SDK (Python), ChatKit, Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL.

## Outcome

- **Success**: Yes
- **Follow-ups**: Create specs for Phase III features (chatbot.md, mcp-tools.md, schema-updates.md, chat-page.md)

## Evaluation

- **Accuracy**: High - All user requirements captured in constitution
- **Completeness**: Full - 10 principles covering all aspects of Phase III
- **Constitution Compliance**: N/A - This is the constitution creation itself
