---
id: 002
title: "AI Chatbot Implementation Plan"
stage: plan
date: 2026-01-14
surface: agent
model: claude-opus-4-5
feature: 003-ai-todo-chatbot
branch: 003-ai-todo-chatbot
user: system
command: /sp.plan
labels: ["plan", "phase3", "ai-chatbot", "cohere", "mcp", "architecture"]
links:
  spec: specs/003-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-todo-chatbot/plan.md
  - specs/003-ai-todo-chatbot/research.md
  - specs/003-ai-todo-chatbot/data-model.md
  - specs/003-ai-todo-chatbot/contracts/chat-api.yaml
  - specs/003-ai-todo-chatbot/contracts/mcp-tools.md
  - specs/003-ai-todo-chatbot/quickstart.md
tests: []
---

# AI Chatbot Implementation Plan

## Prompt

```text
Hackathon II: Phase III - AI-Powered Todo Chatbot with Cohere Integration

## Architecture Sketch
Extension of Phase II full-stack monorepo with stateless AI chatbot layer:
- Frontend: Floating chatbot icon → opens ChatKit panel → sends messages to chat endpoint
- Backend: Stateless chat endpoint → loads history → runs agent with Cohere → calls MCP tools → saves response

## Component Breakdown & Section Structure

### Frontend (/frontend)
- New page/route: /app/chat/page.tsx (protected)
- Floating chatbot button (bottom-right, Tailwind styled)
- OpenAI ChatKit component integration
- API call wrapper for /api/{user_id}/chat with conversation management

### Backend (/backend)
- New models: Conversation, Message (SQLModel)
- New folder: /mcp/tools.py → 5 MCP tools wrapping existing task service
- New service: /agents/todo_agent.py → Agent with Cohere client + MCP tools
- New route: /routes/chat.py → POST /api/{user_id}/chat endpoint
- Updated dependencies.py → pass user_id to tools

### Database Extensions
- conversations: id, user_id (str, FK), created_at, updated_at
- messages: id, conversation_id, role (user/assistant), content, created_at

## Key Decisions & Tradeoffs
- LLM Provider: Cohere (Command R+) via OpenAI-compatible client
- Agents Framework: OpenAI Agents SDK with custom AsyncOpenAI client
- Chat UI: OpenAI ChatKit
- Conversation storage: Single thread per user in DB
- Tool implementation: MCP tools call existing task service layer
- Chat access: Floating icon on dashboard
- History loading: On chat open (conversation_id optional)

## Implementation Sequence
1. Database schema extension
2. Cohere client setup
3. MCP tools implementation
4. Agent with tools
5. Chat endpoint
6. Frontend chat UI
7. Integration testing
```

## Response Summary

Created comprehensive implementation plan with supporting artifacts:

**Artifacts Generated:**
1. `plan.md` - Full implementation plan with:
   - Architecture overview with ASCII diagram
   - 4 key architecture decisions with rationales
   - Component breakdown (backend + frontend)
   - 30-step implementation sequence
   - Risk analysis and mitigations
   - Full constitution compliance checklist

2. `research.md` - Technical research covering:
   - Cohere API integration pattern
   - MCP tool implementation strategy
   - Conversation persistence design
   - ChatKit integration approach
   - Stateless endpoint design

3. `data-model.md` - Database schema:
   - Conversation table (UUID, user_id, title, timestamps)
   - Message table (id, conversation_id, role, content, tool fields)
   - SQLModel definitions
   - Query patterns
   - Migration script

4. `contracts/chat-api.yaml` - OpenAPI specification:
   - POST /api/users/{user_id}/chat endpoint
   - GET /api/users/{user_id}/conversations endpoint
   - Request/response schemas
   - Error responses

5. `contracts/mcp-tools.md` - Tool contracts:
   - 5 tools: add_task, list_tasks, complete_task, update_task, delete_task
   - Parameter tables
   - Response formats
   - Error handling patterns

6. `quickstart.md` - Setup guide:
   - Environment variables
   - Quick start commands
   - Project structure
   - Key files to create
   - Testing checklist

**Key Decisions:**
- Cohere via OpenAI-compatible client (base_url swap)
- MCP tools wrap existing TaskService
- Single conversation thread per user
- Floating chat icon with slide-in panel

**Constitution Compliance:** 10/10 principles verified

## Outcome

- **Success**: Yes
- **Follow-ups**: Run `/sp.tasks` to generate implementation tasks

## Evaluation

- **Accuracy**: High - All architecture decisions aligned with spec and constitution
- **Completeness**: Full - All required artifacts generated
- **Constitution Compliance**: 10/10 principles addressed with implementation guidance
