# Map NL to Tools

Guide the agent to map user input to appropriate MCP tool calls:

## Intent Mapping

| User Intent | Tool | Parameters |
|-------------|------|------------|
| "Add task", "remind me", "create" | `add_task` | title, description (optional) |
| "List pending", "what's pending" | `list_tasks` | status="pending" |
| "Show me everything", "all tasks" | `list_tasks` | status="all" |
| "Mark done", "finish", "complete" | `complete_task` | task_id |
| "Delete", "remove", "cancel" | `delete_task` | task_id (list first if no ID) |
| "Change", "update", "rename" | `update_task` | task_id, fields to update |

## Execution Rules

1. **Chained Operations**: For commands like "delete the first one" or "complete task 3":
   - First call `list_tasks` to show available tasks if no explicit ID
   - Then execute the target operation with the identified task_id

2. **Natural Language Extraction**:
   - Extract task title from phrases like "add buy groceries" → title: "Buy groceries"
   - Extract description from "add X with note Y" → title: X, description: Y

3. **User Context**:
   - Extract user email from JWT token for personalization
   - Respond in natural, conversational language

4. **Ambiguity Handling**:
   - If intent is unclear, ask a clarification question
   - Never guess - prefer asking over making assumptions
   - Example: "Which task would you like to complete?" instead of guessing

## Example Mappings

```
User: "remind me to buy milk"
→ add_task(title="Buy milk")

User: "what do I need to do?"
→ list_tasks(status="pending")

User: "I finished the groceries task"
→ complete_task(task_id=<identified from context or list>)

User: "remove task 5"
→ delete_task(task_id=5)

User: "show me everything"
→ list_tasks(status="all")
```
