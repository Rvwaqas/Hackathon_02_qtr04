---
id: 002
title: Create AI Chatbot Implementation Plan
stage: plan
date: 2026-01-13
surface: agent
model: claude-opus-4-5
feature: 003-ai-chatbot-mcp
branch: main
user: developer
command: /sp.plan
labels: ["chatbot", "mcp", "planning", "multi-agent", "phase3"]
links:
  spec: phase3/specs/003-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - phase3/specs/003-ai-chatbot-mcp/plan.md
  - phase3/specs/003-ai-chatbot-mcp/research.md
  - phase3/specs/003-ai-chatbot-mcp/data-model.md
  - phase3/specs/003-ai-chatbot-mcp/quickstart.md
  - phase3/specs/003-ai-chatbot-mcp/contracts/chat-api.yaml
  - phase3/specs/003-ai-chatbot-mcp/contracts/mcp-tools.md
  - phase3/specs/003-ai-chatbot-mcp/checklists/plan-quality-checklist.md
tests:
  - Plan quality checklist validation (PASS)
---

## Prompt

/sp.plan

Create: Multi-agent architecture with MCP tools, API endpoint structure, database schema extensions, frontend ChatKit integration, agent coordination workflow

Decisions needing documentation:
1. Agent orchestration pattern (sequential vs parallel handoffs)
2. AI service provider (Cohere via OpenAI SDK compatibility)
3. MCP tool implementation approach
4. Conversation persistence strategy
5. Frontend integration approach
6. API endpoint design
7. Error handling strategy
8. Authentication integration

User provided detailed technical specifications including:
- Cohere API setup with command-r-plus model
- Agent definitions for IntentParser, TaskManager, ContextManager, ResponseFormatter, MCPValidator, MainOrchestrator
- FastAPI endpoint implementation
- Frontend ChatKit integration
- Testing approach with natural language variations
- Performance targets and quality gates

## Response snapshot

Created comprehensive implementation plan with 6 phases:

**Phase 1: Database & Models** - Conversation and Message SQLModel definitions, migration script

**Phase 2: MCP Tools** - 5 tools (add_task, list_tasks, complete_task, update_task, delete_task) with @function_tool decorators

**Phase 3: Agent System** - 6 agents with sequential handoff orchestration:
- MainOrchestrator: Coordinates workflow
- IntentParser: NL to structured operations
- MCPValidator: Input sanitization
- TaskManager: MCP tool execution
- ContextManager: Conversation persistence
- ResponseFormatter: User-friendly messages

**Phase 4: FastAPI Endpoint** - POST /api/{user_id}/chat with JWT auth

**Phase 5: Frontend** - Custom React chat components (ChatWidget, ChatMessage, ChatInput, ChatToggle)

**Phase 6: Testing & Refinement** - 50+ NL variations, load testing, performance optimization

**Artifacts Created**:
- plan.md: Full implementation plan with code samples
- research.md: 8 technical decisions with rationale
- data-model.md: ER diagram, SQLModel definitions, migration SQL
- quickstart.md: Setup guide
- contracts/chat-api.yaml: OpenAPI 3.1 specification
- contracts/mcp-tools.md: MCP tool contracts
- checklists/plan-quality-checklist.md: Validation results

## Outcome

- Impact: Complete implementation roadmap ready for task generation
- Tests: Plan quality checklist - all items PASS
- Files: 7 files created
- Next prompts: /sp.tasks to generate implementation tasks
- Reflection: Comprehensive plan with detailed code samples for all agents. Sequential handoff pattern chosen for predictability and debuggability. Cohere API integration via OpenAI SDK compatibility layer.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generated successfully with all required artifacts
- Graders run and results (PASS/FAIL): Plan quality checklist - PASS
- Prompt variant (if applicable): User provided detailed implementation hints in prompt
- Next experiment (smallest change to try): Proceed to /sp.tasks for task generation
