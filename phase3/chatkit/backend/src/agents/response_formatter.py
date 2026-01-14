"""ResponseFormatter agent - Formats responses for user display."""

from typing import Dict, Any, List


class ResponseFormatter:
    """
    Agent responsible for formatting responses in a user-friendly way.

    Creates natural language responses with:
    - Emojis and formatting
    - Task details (IDs, titles, descriptions)
    - Success/error messages
    - Lists of tasks
    """

    @staticmethod
    def format(
        intent: str,
        result: Dict[str, Any],
        clarification_question: str = None
    ) -> str:
        """
        Format the result into a user-friendly response.

        Args:
            intent: The executed intent
            result: Result from TaskManager or validation errors
            clarification_question: Optional clarification question

        Returns:
            Formatted response string
        """
        # Handle clarification questions
        if clarification_question:
            return f"🤔 {clarification_question}"

        # Handle validation errors
        if "errors" in result and result.get("errors"):
            errors = result["errors"]
            error_text = "\n".join([f"- {err}" for err in errors])
            return f"❌ Validation errors:\n{error_text}"

        # Handle MCP tool results
        success = result.get("success", False)

        if not success:
            error = result.get("error", "Unknown error occurred")
            return f"❌ {error}"

        # Format based on intent
        if intent == "add_task":
            task = result.get("task", {})
            task_id = task.get("id")
            title = task.get("title")
            description = task.get("description", "")

            response = f"✅ Task #{task_id} created: **{title}**"
            if description:
                response += f"\n📝 {description}"
            return response

        elif intent == "list_tasks":
            tasks = result.get("tasks", [])
            count = result.get("count", 0)
            status_filter = result.get("status_filter", "all")

            if count == 0:
                status_text = status_filter if status_filter != "all" else ""
                return f"📋 You have no {status_text} tasks."

            # Format task list
            task_lines = []
            for task in tasks:
                task_id = task.get("id")
                title = task.get("title")
                completed = task.get("completed", False)

                checkbox = "✅" if completed else "⬜"
                task_lines.append(f"{checkbox} #{task_id}: {title}")

            status_text = f" ({status_filter})" if status_filter != "all" else ""
            header = f"📋 Your tasks{status_text} ({count}):\n\n"
            return header + "\n".join(task_lines)

        elif intent == "complete_task":
            task = result.get("task", {})
            task_id = task.get("id")
            title = task.get("title")
            return f"✅ Task #{task_id} completed: **{title}**"

        elif intent == "update_task":
            task = result.get("task", {})
            task_id = task.get("id")
            title = task.get("title")
            return f"✏️ Task #{task_id} updated: **{title}**"

        elif intent == "delete_task":
            message = result.get("message", "Task deleted")
            return f"🗑️ {message}"

        else:
            # Fallback for unknown intent
            return result.get("message", "Operation completed")

    @staticmethod
    def format_error(error: str) -> str:
        """
        Format an error message.

        Args:
            error: Error message

        Returns:
            Formatted error string
        """
        return f"❌ {error}"
