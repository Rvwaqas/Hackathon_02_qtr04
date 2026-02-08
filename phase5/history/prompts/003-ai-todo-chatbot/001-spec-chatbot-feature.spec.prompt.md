---
id: 001
title: Specification for AI-Powered Todo Chatbot
stage: spec
date: 2026-01-15
surface: agent
model: claude-haiku-4-5-20251001
feature: 003-ai-todo-chatbot
branch: 003-ai-todo-chatbot
user: waqas
command: /sp.specify
labels: ["spec", "chatbot", "phase3", "natural-language", "todo-management"]
links:
  spec: specs/003-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-todo-chatbot/spec.md
  - specs/003-ai-todo-chatbot/checklists/requirements.md
tests: []
---

## Prompt

# specs/specify.md - Hackathon II: Phase III - AI-Powered Todo Chatbot with Cohere

## Project Overview
Integrate a fully conversational AI chatbot into the existing Phase II full-stack multi-user todo application. The chatbot must allow authenticated users to manage their tasks completely through natural language while maintaining strict data isolation and stateless architecture.

## Current Phase
Phase III: AI-Powered Todo Chatbot (integrated on top of Phase II)

## Target User
- Authenticated user of the existing todo web app
- Wants to manage tasks (add, list, complete, update, delete) via natural language chat
- Expects friendly confirmations, error handling, and conversation continuity

## Focus & Core Functionality
- Natural language interface for all 5 basic task operations
- Chatbot understands intent and extracts parameters correctly
- Full integration with existing database and authentication system
- Conversation history persists across sessions and server restarts
- UI accessible via a prominent chatbot icon/button in the existing frontend
- Powered by Cohere LLM (Command R+ recommended) via OpenAI Agents SDK with custom client

## User Journeys

1. **Accessing Chatbot**
   - User logs in → sees dashboard → clicks floating chatbot icon
   - Chat panel opens (slide-in or modal) with OpenAI ChatKit UI
   - Previous conversation (if any) automatically loads

2. **Managing Tasks via Chat**
   - User: "Add a task to buy groceries tomorrow"
     → Chatbot: "Task 'Buy groceries tomorrow' added! ✅"
   - User: "Show me my pending tasks"
     → Chatbot lists all pending tasks with IDs
   - User: "Mark task 3 as complete"
     → Chatbot: "Task 3 marked as complete! 🎉"
   - User: "Delete the grocery task"
     → Chatbot may list first if ambiguous → then deletes → confirms
   - User: "Change task 1 to 'Call mom tonight'"
     → Chatbot: "Task 1 updated to 'Call mom tonight'! ✏️"

3. **Conversation Continuity**
   - User refreshes page or restarts server → opens chat → history resumes
   - Multiple conversations per user not required (single active thread)

## Success Criteria
- Chatbot UI accessible via visible icon/button in existing dashboard
- OpenAI ChatKit fully integrated and styled with Tailwind
- All natural language examples from hackathon doc work correctly
- Agent always confirms actions with friendly, natural responses
- Errors handled gracefully ("I couldn't find task 5" etc.)
- Conversation history persisted in Neon DB (conversations + messages tables)
- Stateless /api/{user_id}/chat endpoint follows exact request cycle
- Cohere API used for all reasoning and response generation
- OpenAI Agents SDK configured with Cohere via AsyncOpenAI client (base_url + api_key)
- MCP tools (5 exact tools) successfully called and modify same tasks as web UI
- User isolation 100% maintained — chatbot only accesses authenticated user's data
- Existing dashboard, REST API, and task management remain fully functional

## Constraints
- Must use Cohere API (Command R+ or latest available model)
- OpenAI Agents SDK must be adapted with custom AsyncOpenAI client pointing to Cohere
- No direct OpenAI API calls allowed
- Reuse existing Better Auth JWT for authentication — no new auth
- MCP Server using Official MCP SDK (Python)
- No multiple conversation threads per user
- No voice input/output
- No file attachments in chat
- No advanced agent memory beyond DB-stored messages
- No real-time collaborative chat
- No custom trained model or RAG beyond basic history
- No separate mobile app or PWA changes

## Technical Requirements
- Cohere model accessed via OpenAI-compatible endpoint pattern
- Agent configured with tool_use_behavior for proper MCP calling
- All MCP tools receive authenticated user_id and operate only on that user's tasks
- Environment variables: COHERE_API_KEY, NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- Chat icon prominently placed (bottom-right floating button recommended)

This chatbot will transform the todo app into a truly intelligent, natural-language-driven experience while maintaining all security, isolation, and scalability guarantees of Phase II.

## Response snapshot

Created comprehensive specification for Phase III AI-Powered Todo Chatbot (feature 003-ai-todo-chatbot):

**User Scenarios**: 7 prioritized user stories (5 P1, 2 P2) with acceptance scenarios covering:
- Add task via natural language
- View tasks via query
- Complete task by ID or description
- Update task properties
- Delete task
- Conversation persistence across sessions
- Chatbot UI integration

**Functional Requirements**: 18 FRs covering:
- Chat session initiation and UI integration
- Natural language parsing and intent extraction
- MPC tool invocation for all 5 task operations
- Friendly confirmations and error handling
- Conversation persistence in database
- User data isolation via user_id
- Stateless architecture with no in-memory state
- Cohere and OpenAI Agents SDK integration
- Tool chaining and multi-user isolation

**Key Entities**: Conversation and Message models with relationships to User and existing Task entity

**Success Criteria**: 15 measurable outcomes covering:
- UI responsiveness (under 2-5 seconds)
- Task operation completion (add, list, complete, update, delete)
- Conversation persistence across restarts
- Multi-user isolation with zero cross-user leakage
- Action confirmation (95% with appropriate emojis)
- Error handling within 3 seconds
- Cohere API as only LLM provider
- Existing Phase II functionality remains intact

**Quality Validation**: All checklist items pass (completeness, clarity, measurability, scope, alignment)

**Files Created**:
- `specs/003-ai-todo-chatbot/spec.md` (comprehensive specification)
- `specs/003-ai-todo-chatbot/checklists/requirements.md` (quality validation)

## Outcome

- ✅ Impact: Feature specification complete and validated; ready for architectural planning; provides clear, testable requirements for implementation; aligns with Phase III Constitution
- 🧪 Tests: 0 tests (specification document); quality checklist passes all items
- 📁 Files: 2 files created (`spec.md`, `requirements.md`)
- 🔁 Next prompts: Run `/sp.plan` to create architecture design and implementation strategy; Create ADR for Cohere + OpenAI Agents SDK integration decision if needed
- 🧠 Reflection: Specification captures all user journeys, functional requirements, success criteria, and constraints from initial description. Ready for planning phase. No clarifications needed.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Specification Quality Checklist = PASS (all 12 items)
- Prompt variant (if applicable): N/A
- Next experiment: Proceed to architectural planning with `/sp.plan`; validate that plan addresses all FR and SC from spec
