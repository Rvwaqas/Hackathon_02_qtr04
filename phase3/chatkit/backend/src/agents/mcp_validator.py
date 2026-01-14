"""MCPValidator agent - Validates and sanitizes extracted parameters."""

from typing import Dict, Any


class MCPValidator:
    """
    Agent responsible for validating extracted parameters.

    Validates:
    - Field lengths (title max 200 chars, description max 2000 chars)
    - Task IDs are positive integers
    - Status values are valid ("all", "pending", "completed")
    - Required parameters are present for each intent
    """

    @staticmethod
    def validate(intent: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters for the given intent.

        Args:
            intent: The detected intent
            parameters: Extracted parameters to validate

        Returns:
            Dict containing:
            - valid: Boolean indicating if parameters are valid
            - sanitized_params: Cleaned and validated parameters
            - errors: List of validation errors (if any)
        """
        errors = []
        sanitized_params = {}

        # Validate based on intent
        if intent == "add_task":
            # Title is required
            title = parameters.get("title", "").strip()
            if not title:
                errors.append("Task title is required")
            elif len(title) > 200:
                errors.append("Task title must be 200 characters or less")
            else:
                sanitized_params["title"] = title

            # Description is optional
            description = parameters.get("description", "").strip()
            if description:
                if len(description) > 2000:
                    errors.append("Task description must be 2000 characters or less")
                else:
                    sanitized_params["description"] = description
            else:
                sanitized_params["description"] = ""

        elif intent == "list_tasks":
            # Status is optional, defaults to "all"
            status = parameters.get("status", "all").lower().strip()
            if status not in ["all", "pending", "completed"]:
                errors.append(f"Invalid status '{status}'. Must be 'all', 'pending', or 'completed'")
            else:
                sanitized_params["status"] = status

        elif intent == "complete_task":
            # Task ID is required
            task_id = parameters.get("task_id")
            if task_id is None:
                errors.append("Task ID is required")
            elif not isinstance(task_id, int) or task_id <= 0:
                errors.append("Task ID must be a positive integer")
            else:
                sanitized_params["task_id"] = task_id

        elif intent == "update_task":
            # Task ID is required
            task_id = parameters.get("task_id")
            if task_id is None:
                errors.append("Task ID is required")
            elif not isinstance(task_id, int) or task_id <= 0:
                errors.append("Task ID must be a positive integer")
            else:
                sanitized_params["task_id"] = task_id

            # Title is required
            title = parameters.get("title", "").strip()
            if not title:
                errors.append("New task title is required")
            elif len(title) > 200:
                errors.append("Task title must be 200 characters or less")
            else:
                sanitized_params["title"] = title

        elif intent == "delete_task":
            # Task ID is required
            task_id = parameters.get("task_id")
            if task_id is None:
                errors.append("Task ID is required")
            elif not isinstance(task_id, int) or task_id <= 0:
                errors.append("Task ID must be a positive integer")
            else:
                sanitized_params["task_id"] = task_id

        elif intent == "unknown":
            # No validation needed for unknown intent
            pass

        else:
            errors.append(f"Unsupported intent: {intent}")

        return {
            "valid": len(errors) == 0,
            "sanitized_params": sanitized_params,
            "errors": errors
        }
