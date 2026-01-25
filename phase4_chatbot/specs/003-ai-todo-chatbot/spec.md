# Feature Specification: AI-Powered Todo Chatbot with Natural Language Interface

**Feature Branch**: `003-ai-todo-chatbot`
**Created**: 2026-01-15
**Status**: Draft
**Input**: User description: "Phase III AI-Powered Todo Chatbot with Cohere integration, natural language task management, conversation persistence, and seamless backend integration"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Task via Natural Language (Priority: P1)

Authenticated user wants to add a new task by typing in natural language without using forms. The chatbot understands the intent and creates the task with friendly confirmation.

**Why this priority**: Core feature — adding tasks is fundamental to a todo app. Natural language input is the primary value proposition of the chatbot. Without this, the chatbot cannot deliver basic value.

**Independent Test**: Can be fully tested by opening chat → typing a task creation command → verifying task appears in dashboard. Delivers immediate value: user can manage tasks without UI forms.

**Acceptance Scenarios**:

1. **Given** user is logged in and opens chat, **When** user types "Add a task to buy groceries tomorrow", **Then** chatbot confirms "Task 'Buy groceries tomorrow' added! ✅" and task appears in dashboard with title "Buy groceries tomorrow"
2. **Given** user is logged in and opens chat, **When** user types "Create task: Call mom tonight, priority high", **Then** chatbot creates task with title "Call mom tonight" and marks priority as high, confirms with emoji
3. **Given** user is logged in and opens chat, **When** user types "Add: Review PR before deadline", **Then** chatbot creates task with title "Review PR before deadline" and confirms creation

---

### User Story 2 - View Tasks via Natural Language Query (Priority: P1)

Authenticated user wants to list and view their tasks by asking in natural language. The chatbot retrieves and displays tasks grouped by status with friendly formatting.

**Why this priority**: Core feature — viewing tasks is as fundamental as adding them. Users need to see what they've created before managing them.

**Independent Test**: Can be fully tested by opening chat → requesting task list → verifying all user's tasks are displayed with correct statuses. Delivers immediate value: user can query tasks without navigating UI.

**Acceptance Scenarios**:

1. **Given** user has 3 pending and 2 completed tasks, **When** user types "Show my pending tasks", **Then** chatbot displays exactly 3 tasks with pending status and IDs
2. **Given** user has tasks, **When** user types "List all my tasks", **Then** chatbot displays all tasks grouped by status (Pending | Completed) with task IDs, titles, and descriptions
3. **Given** user has no tasks, **When** user types "What tasks do I have?", **Then** chatbot responds "You don't have any tasks yet. You can add one by telling me what you need to do."

---

### User Story 3 - Complete Task via Natural Language (Priority: P1)

Authenticated user wants to mark a task as complete by referring to it by ID or description. The chatbot finds the task and updates its status with confirmation.

**Why this priority**: Core feature — marking tasks complete is essential todo functionality. Users should complete this action through chat without switching to UI.

**Independent Test**: Can be fully tested by having pending tasks → typing completion command → verifying task status changes in dashboard. Delivers immediate value: user can manage task lifecycle via chat.

**Acceptance Scenarios**:

1. **Given** user has pending task with ID 1 titled "Buy milk", **When** user types "Mark task 1 as complete", **Then** chatbot confirms "Task 1 marked as complete! 🎉" and dashboard shows task as completed
2. **Given** user has pending task "Call mom", **When** user types "Mark 'Call mom' as done", **Then** chatbot finds task by description, marks it complete, and confirms with ID and emoji
3. **Given** user has no pending tasks, **When** user types "Complete task 5", **Then** chatbot responds "I couldn't find task 5 in your pending tasks."

---

### User Story 4 - Update Task via Natural Language (Priority: P2)

Authenticated user wants to modify a task's properties (title, description, priority, etc.) by referring to it by ID or description. The chatbot updates the task and confirms the change.

**Why this priority**: Important for task lifecycle management but less frequent than add/list/complete. Needed for refinement and reprioritization workflows.

**Independent Test**: Can be fully tested by modifying task property → verifying change in dashboard. Delivers value: user can adjust tasks without UI forms.

**Acceptance Scenarios**:

1. **Given** user has task 2 with title "Buy groceries", **When** user types "Change task 2 to 'Buy groceries and cook dinner'", **Then** chatbot confirms "Task 2 updated to 'Buy groceries and cook dinner'! ✏️" and dashboard reflects change
2. **Given** user has task with ID 3, **When** user types "Set task 3 priority to high", **Then** chatbot updates priority and confirms change
3. **Given** user types incomplete update command, **When** user types "Update task description", **Then** chatbot asks "Which task would you like to update? You can say 'Update task 1' or 'Change the grocery task'."

---

### User Story 5 - Delete Task via Natural Language (Priority: P2)

Authenticated user wants to remove a task by referring to it by ID or description. The chatbot deletes the task and confirms removal.

**Why this priority**: Important but secondary — less frequently used than other operations. Users may be hesitant to delete without confirmation.

**Independent Test**: Can be fully tested by deleting task → verifying it no longer appears in dashboard or list. Delivers value: user can clean up tasks via chat.

**Acceptance Scenarios**:

1. **Given** user has task 3 titled "Old project", **When** user types "Delete task 3", **Then** chatbot confirms "Task 3 deleted. ✂️" and task is no longer visible in dashboard
2. **Given** user has pending task "Buy milk", **When** user types "Remove the milk task", **Then** chatbot finds task by description, deletes it, and confirms
3. **Given** user has ambiguous task deletion request, **When** user types "Delete the first task", **Then** chatbot asks for clarification: "Do you mean task 1: 'Buy groceries'?"

---

### User Story 6 - Conversation Persistence Across Sessions (Priority: P1)

Authenticated user closes and reopens the chat (page refresh or server restart). Previous conversation history loads automatically, and user can resume chatting without losing context.

**Why this priority**: Critical for user experience. Without persistence, chatbot feels stateless and unreliable. Users expect to resume conversations.

**Independent Test**: Can be fully tested by having conversation → refreshing page → verifying chat history loads. Delivers critical value: continuity across sessions.

**Acceptance Scenarios**:

1. **Given** user has sent 5 messages in chat, **When** user refreshes page, **Then** all 5 previous messages reappear in correct order with correct roles (user/assistant)
2. **Given** user has conversation history, **When** server restarts, **Then** reopening chat reloads conversation without loss
3. **Given** user has new conversation, **When** user opens chat, **Then** conversation ID is generated and stored in database

---

### User Story 7 - Chatbot UI Integration in Dashboard (Priority: P1)

Authenticated user sees a prominent chatbot icon/button in the dashboard. Clicking it opens a chat panel (slide-in or modal) with OpenAI ChatKit UI. Panel can be closed and reopened.

**Why this priority**: Core integration point. Without visible UI, users can't access the chatbot. This is the primary entry point.

**Independent Test**: Can be fully tested by logging in → verifying icon visible → clicking → panel opens. Delivers immediate value: discoverable interface.

**Acceptance Scenarios**:

1. **Given** user is on dashboard, **When** user looks for chat interface, **Then** floating chatbot icon is visible in bottom-right corner
2. **Given** user sees chatbot icon, **When** user clicks icon, **Then** chat panel opens with previous conversation (if any) loaded and ChatKit UI styled with Tailwind
3. **Given** chat panel is open, **When** user clicks close button, **Then** panel closes and icon remains visible

---

### Edge Cases

- What happens when user sends message while agent is processing (loading state)?
  → Show loading indicator; disable input; queue message or show "thinking..." state
- How does system handle ambiguous task references (e.g., "Delete the first task" when multiple exist)?
  → Chatbot asks clarification: list options with IDs and ask which one user means
- What happens when task ID doesn't exist (e.g., "Mark task 999 complete")?
  → Chatbot responds gracefully: "I couldn't find task 999 in your tasks. Do you mean task 5?"
- How does chatbot handle non-task requests (e.g., "What's the weather?")?
  → Chatbot stays in-domain: "I'm a todo assistant. I can help you manage tasks. What would you like to do?"
- What if user is not authenticated when accessing chat?
  → Chat endpoint returns 401 Unauthorized; frontend redirects to login
- What if database connection fails during chat?
  → Agent returns error message: "I'm having trouble accessing your tasks. Please try again in a moment."
- What happens if Cohere API fails or times out?
  → Fallback message: "I'm having trouble thinking right now. Please try again."
- How does system handle concurrent requests from same user?
  → Each request is independent; stateless handler processes in isolation; database ensures consistency

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to initiate a chat session via prominent UI button/icon
- **FR-002**: System MUST accept natural language messages from user and route to Cohere-powered agent
- **FR-003**: System MUST parse user intent and extract task parameters (title, description, priority, status) from natural language
- **FR-004**: System MUST call MCP tools to perform task operations: add_task, list_tasks, complete_task, update_task, delete_task
- **FR-005**: System MUST confirm every action with friendly, natural language responses before and after execution
- **FR-006**: System MUST persist conversation history (user messages and assistant responses) in database linked to authenticated user_id
- **FR-007**: System MUST load previous conversation history when user opens chat (within current session and across server restarts)
- **FR-008**: System MUST restrict chatbot access to tasks belonging only to the authenticated user (user_id isolation)
- **FR-009**: System MUST handle errors gracefully: missing tasks, invalid IDs, ambiguous references, network failures
- **FR-010**: System MUST integrate OpenAI ChatKit UI component in frontend with Tailwind CSS styling
- **FR-011**: System MUST use Cohere Command R+ (or latest available model) exclusively for LLM reasoning and tool selection
- **FR-012**: System MUST use OpenAI Agents SDK configured with custom AsyncOpenAI client pointing to Cohere API
- **FR-013**: System MUST operate as stateless backend: no in-memory conversation state; all history in database
- **FR-014**: System MUST accept POST /api/{user_id}/chat requests with message content and optional conversation_id
- **FR-015**: System MUST return structured chat response with assistant message, updated conversation_id, and any error information
- **FR-016**: System MUST support tool chaining when needed (e.g., list tasks → identify task → mark complete in single conversation turn)
- **FR-017**: System MUST preserve existing REST API and dashboard functionality; no breaking changes to Phase II features
- **FR-018**: System MUST handle multi-user isolation: users A and B have separate conversations and separate task access

### Key Entities *(include if feature involves data)*

- **Conversation**: Represents a chat session for a user
  - Attributes: id (UUID), user_id (string, FK), created_at (timestamp), updated_at (timestamp), title (optional, auto-generated)
  - Relationships: belongs_to User (1:1 for active conversation), has_many Messages (1:M)

- **Message**: Represents a single message in a conversation
  - Attributes: id (UUID), conversation_id (FK), role (enum: "user" | "assistant"), content (text), created_at (timestamp)
  - Relationships: belongs_to Conversation (M:1)

- **Task**: Existing entity, unchanged in schema
  - Attributes: id, user_id (FK), title, description, status, priority, created_at, updated_at
  - Relationships: belongs_to User (M:1), has_many Messages (indirectly via agent actions)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Chatbot UI accessible via visible icon/button; clicking opens chat panel in under 2 seconds
- **SC-002**: User can add a task via natural language ("Add task: Buy groceries") and task appears in dashboard within 5 seconds
- **SC-003**: User can list their tasks and chatbot displays all tasks with correct status groups (Pending | Completed) within 3 seconds
- **SC-004**: User can complete a task via chat ("Mark task 1 complete") and task status updates in dashboard within 5 seconds
- **SC-005**: User can update a task via chat ("Change task 2 to high priority") and updates appear in dashboard within 5 seconds
- **SC-006**: User can delete a task via chat and task no longer appears in list within 5 seconds
- **SC-007**: Conversation history persists: user sends 10 messages → refreshes page → all 10 messages reload in correct order
- **SC-008**: Server restart scenario: user has conversation → server restarts → user reopens chat → conversation history intact
- **SC-009**: Multi-user isolation: User A and User B chat simultaneously → no cross-user data leakage; each user only sees their own tasks
- **SC-010**: Agent confirms 95% of actions with appropriate emojis and friendly language (e.g., "✅", "🎉", "✂️")
- **SC-011**: Error handling: ambiguous/invalid task references handled gracefully (no 500 errors); user receives helpful message within 3 seconds
- **SC-012**: Cohere API confirmed as only LLM provider: logs show Cohere calls only (no OpenAI SDK calls)
- **SC-013**: MCP tools successfully invoked: chatbot operations (add, list, complete, update, delete) all call corresponding tools
- **SC-014**: Chatbot responses generated in under 3 seconds for 95th percentile of requests (network + Cohere latency)
- **SC-015**: Existing Phase II dashboard and REST API remain fully functional; all previous tests pass

## Assumptions

- Users have valid JWT tokens and are authenticated before accessing chat
- Cohere API is available and accessible via standard HTTP endpoint with API key in environment variable
- Existing task service layer (from Phase II) can be wrapped by MCP tools without modification
- OpenAI ChatKit is available as npm package and can be styled with Tailwind CSS
- Database connection pool is shared across chat and existing REST API handlers
- Chat sessions do not require multiple concurrent threads per user (single active conversation per user)
- Natural language understanding is sufficient to extract task properties from sentences (exact parameter validation not required)
- Users expect friendly, conversational tone (emojis, confirmations) rather than robot-like responses

## Constraints

- **Technology Stack**: Must use Cohere API exclusively; OpenAI Agents SDK configured to route through Cohere; no direct OpenAI LLM calls
- **Architecture**: Stateless backend; conversation history only in database; no in-memory state or Redis cache
- **API Pattern**: Chat endpoint must follow REST POST pattern; no WebSockets or real-time streaming
- **User Isolation**: user_id from JWT is mandatory for all MCP tool calls; tools must reject any request without valid user_id
- **Backward Compatibility**: Existing Phase II features must remain fully functional; no schema changes to tasks or users tables
- **Frontend Integration**: Must use OpenAI ChatKit component as specified; no custom chat UI development
- **Environment**: COHERE_API_KEY must be provided; NEXT_PUBLIC_OPENAI_DOMAIN_KEY for ChatKit domain allowlist

## Out of Scope (Explicitly Excluded)

- Multiple conversation threads per user (only single active conversation)
- Voice input or audio output
- File attachments or image handling
- Advanced agent memory beyond DB-stored messages (no vector embeddings or RAG)
- Real-time multi-user collaborative chat
- Custom LLM training or fine-tuning
- Mobile app or PWA changes
- Browser-specific optimization
- Analytics or usage tracking beyond conversation logging
