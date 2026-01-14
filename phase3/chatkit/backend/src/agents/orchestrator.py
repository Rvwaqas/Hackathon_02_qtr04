"""MainOrchestrator agent - Coordinates all other agents."""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from .intent_parser import IntentParser
from .mcp_validator import MCPValidator
from .task_manager import TaskManager
from .response_formatter import ResponseFormatter
from .context_manager import ContextManager


class MainOrchestrator:
    """
    Main orchestrator agent that coordinates all other agents.

    Workflow:
    1. ContextManager: Load conversation history
    2. IntentParser: Parse user message to extract intent and parameters
    3. MCPValidator: Validate extracted parameters
    4. TaskManager: Execute MCP tool
    5. ResponseFormatter: Format response for user
    6. ContextManager: Save messages to conversation

    Returns final response and conversation metadata.
    """

    def __init__(
        self,
        session: AsyncSession,
        openai_client: AsyncOpenAI
    ):
        """Initialize the MainOrchestrator."""
        self.session = session
        self.openai_client = openai_client

        # Initialize agents
        self.intent_parser = IntentParser(openai_client)
        self.validator = MCPValidator()
        self.task_manager = TaskManager(session)
        self.formatter = ResponseFormatter()
        self.context_manager = ContextManager(session)

    async def process_message(
        self,
        user_message: str,
        user_id: int,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the agent pipeline.

        Args:
            user_message: User's natural language input
            user_id: User ID (from JWT)
            conversation_id: Conversation ID (None for new conversation)

        Returns:
            Dict containing:
            - conversation_id: Conversation ID (new or existing)
            - response: Formatted response for user
            - tool_calls: List of tools that were called
            - success: Overall success status
        """
        tool_calls = []
        response_text = ""

        try:
            # Step 1: Load conversation history
            conversation_id, messages = await self.context_manager.load_history(
                conversation_id=conversation_id,
                user_id=user_id,
                limit=20
            )

            # Save user message
            await self.context_manager.save_message(
                conversation_id=conversation_id,
                role="user",
                content=user_message
            )

            # Step 2: Parse intent and extract parameters
            parse_result = await self.intent_parser.parse(user_message)

            intent = parse_result.get("intent", "unknown")
            confidence = parse_result.get("confidence", 0.0)
            parameters = parse_result.get("parameters", {})
            clarification_question = parse_result.get("clarification_question")

            # Check if clarification is needed
            if confidence < 0.7 and clarification_question:
                response_text = self.formatter.format(
                    intent=intent,
                    result={},
                    clarification_question=clarification_question
                )

                # Save assistant response
                await self.context_manager.save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response_text,
                    metadata={"clarification": True, "confidence": confidence}
                )

                return {
                    "conversation_id": conversation_id,
                    "response": response_text,
                    "tool_calls": [],
                    "success": False,
                    "needs_clarification": True
                }

            # Step 3: Validate parameters
            validation_result = self.validator.validate(intent, parameters)

            if not validation_result["valid"]:
                # Validation failed
                response_text = self.formatter.format(
                    intent=intent,
                    result=validation_result
                )

                # Save assistant response
                await self.context_manager.save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response_text,
                    metadata={"validation_errors": validation_result["errors"]}
                )

                return {
                    "conversation_id": conversation_id,
                    "response": response_text,
                    "tool_calls": [],
                    "success": False,
                    "validation_errors": validation_result["errors"]
                }

            sanitized_params = validation_result["sanitized_params"]

            # Step 4: Execute task operation via TaskManager
            execution_result = await self.task_manager.execute(
                intent=intent,
                parameters=sanitized_params,
                user_id=user_id
            )

            # Track which tool was called
            if intent in ["add_task", "list_tasks", "complete_task", "update_task", "delete_task"]:
                tool_calls.append(intent)

            # Step 5: Format response
            response_text = self.formatter.format(
                intent=intent,
                result=execution_result
            )

            # Step 6: Save assistant response
            await self.context_manager.save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
                tool_calls=tool_calls,
                metadata={
                    "intent": intent,
                    "confidence": confidence,
                    "success": execution_result.get("success", False)
                }
            )

            return {
                "conversation_id": conversation_id,
                "response": response_text,
                "tool_calls": tool_calls,
                "success": execution_result.get("success", False)
            }

        except Exception as e:
            # Handle unexpected errors
            error_response = self.formatter.format_error(
                f"An unexpected error occurred: {str(e)}"
            )

            # Try to save error message
            try:
                if conversation_id:
                    await self.context_manager.save_message(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=error_response,
                        metadata={"error": str(e)}
                    )
            except:
                pass  # If saving fails, just return the error

            return {
                "conversation_id": conversation_id,
                "response": error_response,
                "tool_calls": tool_calls,
                "success": False,
                "error": str(e)
            }
