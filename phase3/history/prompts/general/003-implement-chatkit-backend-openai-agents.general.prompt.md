---
id: 003
title: Implement ChatKit Backend with OpenAI Agents SDK
stage: general
date: 2026-01-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: chatkit-backend
branch: main
user: orchestrator-agent
command: implementation
labels: ["backend", "openai-agents", "mcp-tools", "chatbot", "multi-agent"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\pyproject.toml
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\database.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\models\__init__.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\models\conversation.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\models\message.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\services\__init__.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\services\conversation.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\tools\__init__.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\tools\mcp_tools.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\agents\__init__.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\agents\config.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\agents\intent_parser.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\agents\mcp_validator.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\agents\task_manager.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\agents\response_formatter.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\agents\context_manager.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\agents\orchestrator.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\api\__init__.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\api\chat.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\src\main.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\main.py
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\.env.example
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\README.md
  - G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend\IMPLEMENTATION_SUMMARY.md
tests:
  - Not yet run - backend needs to be started and tested
---

## Prompt

Implement the complete backend for the ChatKit chatbot using OpenAI Agents SDK.

**Location**: G:\Hackathon_Qtr_04\Hackathon_02\Waqas\Hackathon_02_qtr04\phase3\chatkit\backend

**Detailed Backend Requirements**:

### 1. Project Setup
- Create pyproject.toml with dependencies:
  - fastapi, uvicorn
  - sqlmodel, asyncpg
  - openai-agents SDK
  - python-jose (JWT)
  - python-dotenv
  - pydantic

### 2. Database Connection
- Connect to existing phase3 backend database
- Reuse existing User, Task, Notification models
- Create Conversation and Message models for chat history
- ConversationService for loading/saving messages

### 3. Backend Agents (6 coordinating agents)
- **IntentParser** - Parse natural language input
- **MCPValidator** - Validate extracted parameters
- **TaskManager** - Execute MCP tools
- **ResponseFormatter** - Format responses for user
- **ContextManager** - Manage conversation history
- **MainOrchestrator** - Coordinate all agents

### 4. MCP Tools (5 tools for task operations)
- add_task(user_id, title, description)
- list_tasks(user_id, status)
- complete_task(user_id, task_id)
- update_task(user_id, task_id, title)
- delete_task(user_id, task_id)

### 5. Chat API Endpoint
- POST /api/{user_id}/chat
- Request: message, conversation_id (optional)
- Response: conversation_id, response, tool_calls, success
- Authorization: Bearer TOKEN

### 6-10. Additional requirements for conversation persistence, error handling, file structure, integration points, and testing readiness.

## Response snapshot

Successfully implemented complete ChatKit backend with multi-agent architecture:

### Orchestration Workflow Executed:

1. **Context Gathering** - Read existing phase2 backend code to understand database models, JWT configuration, and service patterns.

2. **Task Breakdown** - Created 14 tracked tasks covering all components from dependencies to documentation.

3. **Implementation** - Created 23 files implementing:
   - **6 Coordinating Agents**: IntentParser (GPT-4 powered NLP), MCPValidator (parameter validation), TaskManager (MCP tool execution), ResponseFormatter (user-friendly responses), ContextManager (conversation history), MainOrchestrator (workflow coordination)
   - **5 MCP Tools**: add_task, list_tasks, complete_task, update_task, delete_task with full ownership validation
   - **2 Data Models**: Conversation and Message for chat history
   - **ConversationService**: Methods for creating, loading, saving conversations and messages
   - **Chat API Endpoints**: POST /api/{user_id}/chat and GET /api/{user_id}/conversations with JWT authentication
   - **FastAPI Application**: Complete app with CORS, lifespan management, health checks
   - **Documentation**: README.md with architecture, setup, usage, and testing instructions

### Agent Architecture Highlights:

**IntentParser Agent**:
- Uses OpenAI GPT-4 with JSON mode
- System prompt with intent examples
- Confidence scoring (< 0.7 triggers clarification)
- Recognizes 5 intents + unknown

**MCPValidator Agent**:
- Validates field lengths (title max 200, description max 2000)
- Type checking (task_id as positive integer)
- Status validation (all/pending/completed)
- Returns sanitized parameters

**TaskManager Agent**:
- Executes appropriate MCP tool based on intent
- Enforces user ownership on all operations
- Structured error handling
- Returns success/error dictionaries

**ResponseFormatter Agent**:
- User-friendly messages with emojis
- Task details with IDs
- Error messages with guidance
- Formatted task lists

**ContextManager Agent**:
- Loads last 20 messages from conversation
- Creates new conversations automatically
- Validates conversation ownership
- Saves messages with tool call tracking

**MainOrchestrator Agent**:
- Coordinates all 5 agents in sequence
- Handles clarification flow (confidence < 0.7)
- Error handling throughout pipeline
- Returns structured response with metadata

### Integration Points:

- **Database**: Connects to same PostgreSQL database as phase2 backend
- **Authentication**: Uses identical JWT configuration (secret, algorithm)
- **CORS**: Compatible with all existing frontends
- **Port**: Runs on 8002 (phase2: 8000, phase3: 8001)

### Key Files Created:

**Configuration**:
- pyproject.toml - Dependencies
- .env.example - Environment template
- src/database.py - Database connection

**Models & Services**:
- src/models/conversation.py - Conversation model
- src/models/message.py - Message model
- src/services/conversation.py - ConversationService

**MCP Tools**:
- src/tools/mcp_tools.py - 5 task operation tools

**Agents**:
- src/agents/config.py - OpenAI configuration
- src/agents/intent_parser.py - NLP agent
- src/agents/mcp_validator.py - Validation agent
- src/agents/task_manager.py - Execution agent
- src/agents/response_formatter.py - Formatting agent
- src/agents/context_manager.py - History agent
- src/agents/orchestrator.py - Coordination agent

**API**:
- src/api/chat.py - Chat endpoints with JWT
- src/main.py - FastAPI application
- main.py - Entry point

**Documentation**:
- README.md - Complete documentation
- IMPLEMENTATION_SUMMARY.md - Implementation details

## Outcome

- ✅ Impact: Complete multi-agent chatbot backend ready for frontend integration
- 🧪 Tests: Not yet run - requires database setup and OpenAI API key
- 📁 Files: 23 files created across agents, tools, models, services, API
- 🔁 Next prompts: Setup database migrations, start server, test endpoints, integrate with frontend
- 🧠 Reflection: Multi-agent architecture provides excellent separation of concerns - each agent has clear responsibility and can be tested/improved independently

## Evaluation notes (flywheel)

- Failure modes observed: None during implementation
- Graders run and results (PASS/FAIL): Not yet tested
- Prompt variant (if applicable): Standard orchestration workflow
- Next experiment (smallest change to try): Test with real database and OpenAI API key, verify agent handoffs work correctly

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
