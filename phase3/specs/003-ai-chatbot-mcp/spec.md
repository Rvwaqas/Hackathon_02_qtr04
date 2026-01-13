# Feature Specification: Todo AI Chatbot Integration with MCP Architecture

**Feature Branch**: `003-ai-chatbot-mcp`
**Created**: 2026-01-13
**Status**: Draft
**Input**: User description: "Phase 3: AI Chatbot Integration - Conversational AI interface using OpenAI Agents SDK with MCP tools for stateless task operations, multi-agent system with specialized subagents"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation (Priority: P0 - Foundation)

As an authenticated user, I can create tasks by typing natural language commands in the chat interface so that I can quickly add tasks without navigating forms.

**Why this priority**: Task creation is the most frequent operation. If users cannot add tasks via chat, the chatbot provides no core value. This must work before any other feature.

**Independent Test**: Sign in, open chat interface, type "Add buy groceries", verify task appears in task list with title "buy groceries" and pending status, verify chat shows confirmation message with task details.

**Acceptance Scenarios**:

1. **Given** I'm signed in and on the dashboard with chat open, **When** I type "Add buy groceries" and send, **Then** a new task is created with title "buy groceries", I see confirmation "Task created: buy groceries" with task ID
2. **Given** I'm in the chat, **When** I type "Remind me to call mom", **Then** a new task is created with title "call mom" and confirmation shown
3. **Given** I'm in the chat, **When** I type "I need to pay bills tomorrow", **Then** a new task is created with title "pay bills tomorrow" and confirmation shown
4. **Given** I try to add a task with empty title like "Add ", **When** I send the message, **Then** I see friendly error "Please provide a task title. Example: 'Add buy groceries'"
5. **Given** I type "add buy milk and eggs from the store for dinner tonight", **When** I send, **Then** task is created with full title preserved

---

### User Story 2 - View and List Tasks via Chat (Priority: P1 - Core)

As an authenticated user, I can ask the chatbot to show my tasks so that I can see my todo list without leaving the conversation.

**Why this priority**: After creating tasks, users need to see them. Listing tasks is essential for any task management interaction and enables subsequent operations (complete, update, delete).

**Independent Test**: Create 3 tasks via chat, type "Show my tasks", verify all 3 tasks displayed in chat with ID, title, and status; type "What's pending?", verify only pending tasks shown.

**Acceptance Scenarios**:

1. **Given** I have 5 tasks (3 pending, 2 completed), **When** I type "Show my tasks", **Then** I see all 5 tasks listed with ID, title, and status indicator
2. **Given** I have tasks, **When** I type "What's pending?", **Then** I see only pending tasks with count "3 pending tasks"
3. **Given** I have tasks, **When** I type "List completed todos", **Then** I see only completed tasks with count
4. **Given** I have no tasks, **When** I type "Show my tasks", **Then** I see "You have no tasks yet. Try 'Add buy groceries' to create one!"
5. **Given** I have 10+ tasks, **When** I list them, **Then** tasks are displayed in a readable format with clear numbering

---

### User Story 3 - Mark Tasks Complete via Chat (Priority: P2)

As an authenticated user, I can mark tasks as complete by telling the chatbot so that I can track my progress conversationally.

**Why this priority**: Completing tasks is the primary workflow after viewing. Users need to mark progress without switching to the manual UI.

**Independent Test**: Create task "Buy milk", note task ID, type "Mark task [ID] done", verify task status changes to completed, verify chat shows "Task completed: Buy milk" with celebration emoji.

**Acceptance Scenarios**:

1. **Given** I have pending task with ID 5 titled "Buy milk", **When** I type "Mark task 5 done", **Then** task is marked complete, I see "Task completed: Buy milk"
2. **Given** I have pending task "Meeting notes", **When** I type "I finished the meeting notes", **Then** chatbot identifies the task and marks it complete
3. **Given** I type "Complete task 999" (non-existent), **When** I send, **Then** I see "Task #999 not found. Type 'show my tasks' to see your task list"
4. **Given** I have already completed task 5, **When** I type "Mark task 5 done", **Then** I see "Task #5 is already completed"
5. **Given** another user owns task 10, **When** I type "Complete task 10", **Then** I see "Task not found" (not revealing other users' data)

---

### User Story 4 - Update Tasks via Chat (Priority: P3)

As an authenticated user, I can update task details through conversation so that I can modify tasks without navigating to edit forms.

**Why this priority**: Users need to correct or clarify task titles. Update functionality completes the CRUD operations for tasks.

**Independent Test**: Create task "Call mom", type "Change task [ID] to 'Call mom tonight'", verify task title updated, verify confirmation message shows old and new title.

**Acceptance Scenarios**:

1. **Given** I have task ID 3 with title "Call mom", **When** I type "Change task 3 to 'Call mom tonight'", **Then** task title updates, I see "Task updated: 'Call mom' -> 'Call mom tonight'"
2. **Given** I have task "Groceries", **When** I type "Rename groceries task to 'Buy groceries and fruits'", **Then** task is found and updated with confirmation
3. **Given** I type "Update task 999 to 'New title'", **When** I send, **Then** I see "Task #999 not found"
4. **Given** I try to update to empty title, **When** I type "Change task 3 to ''", **Then** I see "Task title cannot be empty"

---

### User Story 5 - Delete Tasks via Chat (Priority: P4)

As an authenticated user, I can delete tasks by telling the chatbot so that I can remove tasks I no longer need.

**Why this priority**: Delete completes CRUD operations. Lower priority than update since users typically complete rather than delete tasks.

**Independent Test**: Create task "Test task", note ID, type "Delete task [ID]", verify task removed from list, verify confirmation "Task deleted: Test task".

**Acceptance Scenarios**:

1. **Given** I have task ID 7 titled "Test task", **When** I type "Delete task 7", **Then** task is permanently removed, I see "Task deleted: Test task"
2. **Given** I have task "Meeting reminder", **When** I type "Remove the meeting reminder", **Then** chatbot identifies and deletes the task with confirmation
3. **Given** I type "Delete task 999", **When** I send, **Then** I see "Task #999 not found"
4. **Given** I have multiple tasks with "meeting" in title, **When** I type "Delete meeting task", **Then** chatbot asks "Which task? 1) Team meeting 2) Meeting notes"

---

### User Story 6 - Compound Commands (Priority: P5)

As an authenticated user, I can issue multiple commands in one message so that I can be more efficient with complex requests.

**Why this priority**: Power-user feature that improves efficiency once basic operations work. Builds on all previous stories.

**Independent Test**: Type "Add buy milk and show all my tasks", verify new task created AND task list displayed in single response.

**Acceptance Scenarios**:

1. **Given** I'm in chat, **When** I type "Add buy milk and show all my tasks", **Then** task is created AND list is displayed in one response
2. **Given** I have tasks, **When** I type "Complete task 3 and show pending", **Then** task is completed AND pending list shown
3. **Given** I'm in chat, **When** I type "Add eggs, add bread, add butter", **Then** three tasks are created with confirmation for each

---

### User Story 7 - Conversation Context Persistence (Priority: P6)

As an authenticated user, I can continue my conversation after closing and reopening the chat so that I don't lose my conversation history.

**Why this priority**: Persistence enables natural, ongoing conversations. Required for production-quality chatbot but not essential for MVP functionality.

**Independent Test**: Open chat, create task via chat, close browser, reopen browser and chat, verify conversation history preserved with previous messages visible.

**Acceptance Scenarios**:

1. **Given** I had a chat session yesterday with 5 messages, **When** I open chat today, **Then** I see my previous conversation history (last 20 messages max)
2. **Given** I created a task in previous session, **When** I ask "What was my last task?", **Then** chatbot recalls from context "Your last task was 'Buy groceries'"
3. **Given** server restarts between my sessions, **When** I return to chat, **Then** my conversation is intact (database persistence)
4. **Given** I have 50 messages in history, **When** I open chat, **Then** only last 20 messages are loaded (performance limit)

---

### User Story 8 - Clarification for Ambiguous Commands (Priority: P7)

As a user, when my command is unclear, the chatbot asks for clarification so that I can complete my intended action.

**Why this priority**: Improves user experience for edge cases. Not critical for basic operations but enhances overall usability.

**Independent Test**: Type ambiguous command "Delete the task", verify chatbot asks "Which task would you like to delete?" and lists options.

**Acceptance Scenarios**:

1. **Given** I have 3 tasks, **When** I type "Delete the task", **Then** chatbot asks "Which task? Please specify task ID or title"
2. **Given** I type "Complete meeting", **When** I have multiple tasks with "meeting", **Then** chatbot lists matches and asks me to choose
3. **Given** I type "fdsjklfds" (gibberish), **When** I send, **Then** chatbot says "I didn't understand that. Try 'Add [task]', 'Show tasks', 'Complete [task]', or 'Delete [task]'"
4. **Given** confidence score is below 0.7, **When** I type ambiguous command, **Then** chatbot asks clarifying question rather than guessing wrong

---

### Edge Cases

- What happens when user sends empty message? -> Chat shows "Please type a command. Examples: 'Add buy groceries', 'Show my tasks', 'Complete task 3'"
- What happens when user sends message over 1000 characters? -> Message is truncated with warning "Message truncated to 1000 characters"
- What happens when AI service (Gemini) is unavailable? -> User sees "Chat service temporarily unavailable. Please use the task list directly or try again later"
- What happens when database connection fails? -> User sees "Unable to save your request. Please try again in a moment"
- What happens when user's JWT token expires mid-conversation? -> Chat detects 401, shows "Session expired. Please sign in again" and redirects to login
- What happens when user tries to access another user's tasks via manipulated request? -> Server validates user_id from JWT, returns "Task not found" (no data leakage)
- What happens when user issues 10 commands in rapid succession? -> System processes sequentially, may show "Processing..." indicator, rate limiting applied if needed
- What happens when task title contains special characters or SQL injection attempts? -> Input sanitized, special characters preserved in title safely
- What happens when user references task by partial title match with multiple results? -> Chatbot lists all matches and asks user to specify
- What happens when conversation context becomes too large (>20 messages)? -> Oldest messages trimmed, most recent 20 preserved

## Requirements *(mandatory)*

### Functional Requirements

#### Chat Interface (Frontend)

- **FR-001**: System MUST display a chat interface accessible from the todo dashboard
- **FR-002**: System MUST show chat as either a floating button or dedicated chat page
- **FR-003**: System MUST display messages in chronological order with clear user/assistant distinction
- **FR-004**: System MUST show typing indicator while waiting for AI response
- **FR-005**: System MUST display task confirmations with appropriate formatting and indicators
- **FR-006**: System MUST preserve conversation history when navigating away and returning
- **FR-007**: System MUST limit user message input to 1000 characters with character count display

#### Chat API (Backend)

- **FR-008**: System MUST provide chat endpoint that accepts user messages
- **FR-009**: System MUST authenticate requests using existing authentication from Phase 2
- **FR-010**: System MUST validate user ownership before any task operation
- **FR-011**: System MUST return structured responses with conversation ID, response text, and tool calls made
- **FR-012**: System MUST handle requests asynchronously for performance
- **FR-013**: System MUST log all chat interactions for debugging (excluding sensitive data)

#### Natural Language Processing

- **FR-014**: System MUST recognize task creation intents ("add", "create", "remind me", "I need to")
- **FR-015**: System MUST recognize task listing intents ("show", "list", "what's pending", "my tasks")
- **FR-016**: System MUST recognize task completion intents ("done", "complete", "finished", "mark")
- **FR-017**: System MUST recognize task update intents ("change", "rename", "update", "modify")
- **FR-018**: System MUST recognize task deletion intents ("delete", "remove", "cancel")
- **FR-019**: System MUST extract task IDs from messages (numeric references)
- **FR-020**: System MUST extract task titles from natural language context
- **FR-021**: System MUST handle compound commands (multiple operations in one message)
- **FR-022**: System MUST ask clarifying questions when confidence is below threshold

#### MCP Tools

- **FR-023**: System MUST provide add_task tool for creating new tasks
- **FR-024**: System MUST provide list_tasks tool for retrieving user's tasks with status filter
- **FR-025**: System MUST provide complete_task tool for marking tasks done
- **FR-026**: System MUST provide update_task tool for modifying task details
- **FR-027**: System MUST provide delete_task tool for removing tasks
- **FR-028**: All MCP tools MUST validate user_id ownership before database operations
- **FR-029**: All MCP tools MUST return structured results with success/error status

#### Multi-Agent System

- **FR-030**: System MUST use main orchestrator agent to coordinate request handling
- **FR-031**: System MUST use intent parser agent to extract structured operations from text
- **FR-032**: System MUST use task manager agent to execute MCP tool operations
- **FR-033**: System MUST use context manager agent to load/save conversation history
- **FR-034**: System MUST use response formatter agent to create user-friendly messages
- **FR-035**: System MUST use MCP validator agent to sanitize inputs before database operations
- **FR-036**: Agents MUST hand off to appropriate specialist based on operation type

#### Conversation Persistence

- **FR-037**: System MUST create conversation record on first message from user
- **FR-038**: System MUST store each message with role (user/assistant), content, and timestamp
- **FR-039**: System MUST associate conversations with authenticated user
- **FR-040**: System MUST load conversation history when user opens chat (limited to last 20 messages)
- **FR-041**: System MUST support continuing existing conversation via conversation_id
- **FR-042**: System MUST create new conversation if no conversation_id provided

#### Error Handling

- **FR-043**: System MUST return friendly error messages for invalid operations
- **FR-044**: System MUST handle AI service unavailability gracefully
- **FR-045**: System MUST handle database connection failures with retry logic
- **FR-046**: System MUST validate all inputs before processing (sanitization)
- **FR-047**: System MUST not expose internal errors or stack traces to users
- **FR-048**: System MUST log errors with sufficient context for debugging

#### Integration with Phase 2

- **FR-049**: System MUST reuse existing user authentication (JWT)
- **FR-050**: System MUST operate on existing tasks table from Phase 2
- **FR-051**: System MUST not duplicate or conflict with existing task CRUD endpoints
- **FR-052**: System MUST maintain consistent data model with Phase 2

### Key Entities

- **Conversation**: Represents a chat session between user and AI
  - Belongs to one user
  - Contains multiple messages
  - Tracks creation and last update time

- **Message**: Represents a single message in a conversation
  - Belongs to one conversation
  - Has role: user or assistant
  - Contains message content
  - Tracks creation time

- **Task** (existing from Phase 2): Todo item owned by user
  - ID, title, description, completed status
  - Belongs to one user
  - Chat operations modify existing tasks

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task via chat in under 5 seconds (from sending message to seeing confirmation)
- **SC-002**: Users can view their task list via chat in under 3 seconds
- **SC-003**: Users can complete, update, or delete a task via chat in under 5 seconds
- **SC-004**: Chat correctly interprets 95% of standard todo commands (add, list, complete, update, delete)
- **SC-005**: Chat responses are returned within 2 seconds for 95% of requests
- **SC-006**: Conversation history persists across browser sessions with zero data loss
- **SC-007**: Users can resume conversations after server restart without losing context
- **SC-008**: Chat handles 50 concurrent users without performance degradation
- **SC-009**: All error scenarios result in helpful, actionable user messages
- **SC-010**: Chat maintains complete user data isolation (users cannot access other users' tasks)
- **SC-011**: Compound commands execute all operations correctly in a single response
- **SC-012**: Ambiguous commands result in clarifying questions rather than wrong actions

## Assumptions

1. **Phase 2 Complete**: Phase 2 web application with authentication and task CRUD is fully functional
2. **Database Available**: Neon PostgreSQL database from Phase 2 is accessible and has capacity for 2 new tables
3. **AI Service Access**: API key for AI service (Gemini 2.0 Flash) is available and functional
4. **Authentication Working**: Better Auth JWT authentication from Phase 2 works correctly
5. **Single User Context**: Each chat session operates in context of single authenticated user
6. **English Language**: Natural language processing assumes English input
7. **Text Only**: No voice input/output; purely text-based chat interface
8. **Basic Tasks**: Tasks have title, description, and completion status (no priorities, tags, or due dates in chat)
9. **Stateless Backend**: Any server instance can handle any request (horizontal scaling ready)
10. **Browser-Based**: Chat interface runs in web browser, not native mobile app
11. **Context Window**: Last 20 messages provide sufficient context for conversation continuity
12. **Response Time**: 2-second response time acceptable for conversational interactions

## Out of Scope

The following are explicitly NOT included in Phase 3:

### Not Building

- Voice input/output (text-only chat)
- Multi-user collaboration on tasks (single user context)
- Task categories, tags, or priorities via chat (basic todo only)
- Scheduled tasks or reminders via chat (no time-based features)
- Task attachments or file uploads
- Mobile native app (web-based chat only)
- Analytics dashboard for chat interactions
- Custom MCP tools beyond the 5 specified (add, list, complete, update, delete)
- Training custom AI models (use AI service as-is)
- Complex NLP preprocessing (rely on LLM understanding)
- Real-time typing indicators from AI
- Read receipts for messages
- Message editing or deletion
- Rich media in chat (images, links, etc.)
- Offline chat functionality
- Chat export functionality

### Deferred to Future Phases

- Advanced task attributes via chat (priorities, due dates, tags)
- Task search within chat
- Bulk operations via chat
- Chat notifications/alerts
- Multi-language support
- Voice commands
- Integration with external calendars via chat
- Smart suggestions based on user patterns

## Dependencies

- **Requires**: Phase 2 (Full-stack web app with authentication and task CRUD) complete and functional
- **Blocks**: Phase 4 (Infrastructure) - cannot deploy scaled system until chat feature works
- **External**: AI service API (Gemini 2.0 Flash via OpenAI-compatible API)
- **External**: Neon PostgreSQL database (existing from Phase 2)

## Implementation Notes

This specification defines Phase 3 of the "Evolution of Todo" hackathon project. Key characteristics:

1. **AI-Powered Interface**: Natural language chat as alternative to form-based task management
2. **Multi-Agent Architecture**: Specialized agents handle different aspects of request processing
3. **MCP Integration**: Model Context Protocol tools provide structured task operations
4. **Stateless Design**: Server instances share no state; all persistence in database
5. **Phase 2 Integration**: Builds on existing authentication and task infrastructure
6. **Conversation Continuity**: Users can pick up conversations across sessions
7. **Error Resilience**: Graceful handling of AI service and database failures
