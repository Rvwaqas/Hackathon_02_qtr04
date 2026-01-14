"""TaskManager agent - Executes MCP tools to perform task operations."""

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.tools import mcp_tools


class TaskManager:
    """
    Agent responsible for executing MCP tools.

    Uses the 5 MCP tools to perform task operations:
    - add_task
    - list_tasks
    - complete_task
    - update_task
    - delete_task

    All operations enforce user_id ownership.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the TaskManager agent."""
        self.session = session

    async def execute(
        self,
        intent: str,
        parameters: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Execute the appropriate MCP tool based on intent.

        Args:
            intent: The intent to execute
            parameters: Validated parameters
            user_id: User ID (from JWT)

        Returns:
            Dict with execution result from MCP tool
        """
        try:
            if intent == "add_task":
                return await mcp_tools.add_task(
                    session=self.session,
                    user_id=user_id,
                    title=parameters["title"],
                    description=parameters.get("description", "")
                )

            elif intent == "list_tasks":
                return await mcp_tools.list_tasks(
                    session=self.session,
                    user_id=user_id,
                    status=parameters.get("status", "all")
                )

            elif intent == "complete_task":
                return await mcp_tools.complete_task(
                    session=self.session,
                    user_id=user_id,
                    task_id=parameters["task_id"]
                )

            elif intent == "update_task":
                return await mcp_tools.update_task(
                    session=self.session,
                    user_id=user_id,
                    task_id=parameters["task_id"],
                    title=parameters["title"]
                )

            elif intent == "delete_task":
                return await mcp_tools.delete_task(
                    session=self.session,
                    user_id=user_id,
                    task_id=parameters["task_id"]
                )

            elif intent == "unknown":
                return {
                    "success": False,
                    "error": "I couldn't understand your request. Try asking me to add, list, complete, update, or delete a task."
                }

            else:
                return {
                    "success": False,
                    "error": f"Unsupported intent: {intent}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to execute task operation: {str(e)}"
            }
