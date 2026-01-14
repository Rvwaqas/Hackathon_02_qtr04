# Handle Errors & Confirmations

Implement graceful error handling and user confirmations across backend and frontend.

## Error Response Patterns

| Error Type | User-Friendly Response |
|------------|----------------------|
| Task not found | "Task not found. Please try again or check your task list." |
| Invalid ID | "I couldn't find that task. Here are your current tasks:" (then list) |
| Empty title | "Please provide a title for your task." |
| Unauthorized | "You need to be logged in to manage tasks." |
| Server error | "Something went wrong. Please try again in a moment." |

## Confirmation Messages

### Success Responses
```
Add task    → "Task added! ✅ '{title}'"
Complete    → "Marked as complete ✓ '{title}'"
Delete      → "Deleted successfully 🗑️ '{title}'"
Update      → "Task updated! ✏️ '{title}'"
List (empty)→ "You have no tasks. Add one to get started!"
```

### Destructive Action Confirmations
For delete/update operations, always confirm with the task title:
```
"Are you sure you want to delete '{task_title}'?"
"Deleted '{Buy groceries}' successfully 🗑️"
"Updated '{Meeting notes}' ✏️"
```

## Frontend Implementation

### Toast Notifications
- **Success**: Green toast, auto-dismiss after 3s
- **Error**: Red toast, requires manual dismiss
- **Warning**: Yellow toast, auto-dismiss after 5s

### Loading States
- Show spinner/skeleton during API calls
- Disable buttons while action is processing
- "Adding task..." / "Deleting..." placeholder text

### Error Toasts
```typescript
// Example patterns
showToast.error("Task not found. Please refresh and try again.")
showToast.success("Task added! ✅")
showToast.warning("Connection slow, please wait...")
```

## Backend Implementation

### Response Structure
```python
# Success
{"success": True, "message": "Task added!", "data": {...}}

# Error
{"success": False, "error": "Task not found", "suggestion": "Here are your tasks:"}
```

### Never Silent Fail
- Always return a response to the user
- Log errors server-side for debugging
- Provide actionable next steps in error messages

## Golden Rules

1. **Acknowledge every action** - User should always know what happened
2. **Be specific** - Include task title in confirmations
3. **Suggest next steps** - On error, guide user to resolution
4. **Use appropriate tone** - Friendly but informative
5. **Visual feedback** - Loading → Success/Error state transition
