# ChatKit Backend

Task management chatbot backend powered by OpenAI Agents SDK and MCP Tools.

## Overview

ChatKit provides a natural language interface for task management, using a coordinated multi-agent architecture:

- **6 Coordinating Agents**: IntentParser, MCPValidator, TaskManager, ResponseFormatter, ContextManager, MainOrchestrator
- **5 MCP Tools**: add_task, list_tasks, complete_task, update_task, delete_task
- **Full Integration**: Connects to existing phase2/phase3 database with JWT authentication

## Architecture

### Agents

1. **IntentParser**: Parses natural language to extract intent and parameters
   - Recognizes: add_task, list_tasks, complete_task, update_task, delete_task
   - Confidence scoring and clarification questions
   - Powered by OpenAI GPT-4

2. **MCPValidator**: Validates extracted parameters
   - Field length validation (title max 200, description max 2000)
   - Type validation (task_id as positive integer)
   - Status validation (all/pending/completed)

3. **TaskManager**: Executes MCP tools
   - Database operations with ownership validation
   - Error handling and structured responses
   - SQLModel integration

4. **ResponseFormatter**: Formats user-friendly responses
   - Emojis and formatting
   - Task details display
   - Error messages

5. **ContextManager**: Manages conversation history
   - Loads last 20 messages
   - Saves user and assistant messages
   - Creates/validates conversations

6. **MainOrchestrator**: Coordinates all agents
   - Orchestrates the complete workflow
   - Handles errors gracefully
   - Returns structured responses

### MCP Tools

```python
- add_task(user_id, title, description) -> dict
- list_tasks(user_id, status) -> dict
- complete_task(user_id, task_id) -> dict
- update_task(user_id, task_id, title) -> dict
- delete_task(user_id, task_id) -> dict
```

## Project Structure

```
chatkit/backend/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── config.py              # OpenAI configuration
│   │   ├── intent_parser.py       # Intent parsing agent
│   │   ├── mcp_validator.py       # Parameter validation agent
│   │   ├── task_manager.py        # MCP tool execution agent
│   │   ├── response_formatter.py  # Response formatting agent
│   │   ├── context_manager.py     # Conversation history agent
│   │   └── orchestrator.py        # Main orchestration agent
│   ├── tools/
│   │   ├── __init__.py
│   │   └── mcp_tools.py           # 5 MCP tools
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py                # Chat endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── conversation.py        # Conversation model
│   │   └── message.py             # Message model
│   ├── services/
│   │   ├── __init__.py
│   │   └── conversation.py        # ConversationService
│   ├── database.py                # Database connection
│   └── main.py                    # FastAPI application
├── main.py                        # Entry point
├── pyproject.toml                 # Dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

## Setup

### 1. Install Dependencies

```bash
cd phase3/chatkit/backend
pip install poetry
poetry install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string (same as phase2 backend)
- `OPENAI_API_KEY`: Your OpenAI API key
- `JWT_SECRET`: JWT secret (must match phase2 backend)

### 3. Database Setup

The backend connects to the existing phase2/phase3 database. Ensure:
- Database is running
- User, Task models exist
- Run migrations to create Conversation and Message tables:

```bash
# From backend directory
alembic revision --autogenerate -m "Add conversation and message tables"
alembic upgrade head
```

### 4. Run the Server

```bash
poetry run python main.py
# Server runs on http://0.0.0.0:8002
```

## API Endpoints

### POST /api/{user_id}/chat

Chat with the task management bot.

**Request:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": null  // optional, null for new conversation
}
```

**Response:**
```json
{
  "conversation_id": 1,
  "response": "✅ Task #5 created: **buy groceries**",
  "tool_calls": ["add_task"],
  "success": true
}
```

**Headers:**
- `Authorization: Bearer <JWT_TOKEN>` (required)

### GET /api/{user_id}/conversations

List all conversations for a user.

**Response:**
```json
{
  "conversations": [
    {
      "id": 1,
      "title": "New Conversation",
      "created_at": "2025-01-14T10:00:00",
      "updated_at": "2025-01-14T10:05:00"
    }
  ]
}
```

**Headers:**
- `Authorization: Bearer <JWT_TOKEN>` (required)

## Usage Examples

### Natural Language Examples

```
User: "Add a task to buy groceries"
Bot: ✅ Task #5 created: **buy groceries**

User: "Show me my pending tasks"
Bot: 📋 Your tasks (pending) (3):
     ⬜ #5: buy groceries
     ⬜ #6: finish report
     ⬜ #7: call mom

User: "Mark task 5 as done"
Bot: ✅ Task #5 completed: **buy groceries**

User: "Rename task 6 to complete quarterly report"
Bot: ✏️ Task #6 updated: **complete quarterly report**

User: "Delete task 7"
Bot: 🗑️ Task #7 'call mom' deleted successfully
```

## Agent Workflow

```
User Message
    ↓
ContextManager: Load conversation history
    ↓
IntentParser: Parse intent and parameters
    ↓
MCPValidator: Validate parameters
    ↓
TaskManager: Execute MCP tool
    ↓
ResponseFormatter: Format response
    ↓
ContextManager: Save messages
    ↓
Return Response
```

## Error Handling

All agents handle errors gracefully:
- **Validation errors**: User-friendly messages with guidance
- **Database errors**: Rollback and error reporting
- **Authentication errors**: 401/403 with clear messages
- **Unknown intents**: Clarification questions

## Integration with Phase2 Backend

ChatKit backend integrates seamlessly with the existing phase2 backend:

- **Same database**: Shares User and Task models
- **Same authentication**: Uses identical JWT configuration
- **Same CORS**: Compatible with existing frontends
- **Port 8002**: Runs alongside phase2 backend (port 8000)

## Testing

```bash
# Get JWT token from phase2 backend
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Test chat endpoint
curl -X POST http://localhost:8002/api/1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"message": "Add a task to buy groceries"}'
```

## Development

### Adding New Intents

1. Update `IntentParser.SYSTEM_PROMPT` with new intent
2. Add validation logic in `MCPValidator.validate()`
3. Create new MCP tool in `tools/mcp_tools.py`
4. Add execution logic in `TaskManager.execute()`
5. Update `ResponseFormatter.format()` for new intent

### Debugging

Enable debug logging:
```python
# In src/database.py
echo=True  # Already enabled
```

Check logs for:
- Intent parsing results
- Validation errors
- Database queries
- Tool execution results

## License

Part of the Hackathon Q4 Phase 3 project.
