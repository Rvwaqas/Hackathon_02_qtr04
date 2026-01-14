"""IntentParser agent - Parses natural language input to extract intent and parameters."""

from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from .config import OPENAI_MODEL


class IntentParser:
    """
    Agent responsible for parsing natural language input.

    Recognizes intents:
    - add_task: Create a new task
    - list_tasks: List existing tasks
    - complete_task: Mark a task as completed
    - update_task: Update a task's title
    - delete_task: Delete a task
    - unknown: Cannot determine intent

    Extracts parameters:
    - title: Task title (for add_task, update_task)
    - description: Task description (for add_task)
    - task_id: Task ID (for complete_task, update_task, delete_task)
    - status: Status filter (for list_tasks: "all", "pending", "completed")
    """

    SYSTEM_PROMPT = """You are an intent parser for a task management chatbot.

Your job is to analyze user messages and extract:
1. The intent (what the user wants to do)
2. The parameters needed to fulfill that intent
3. A confidence score (0.0 to 1.0)

Supported intents:
- add_task: User wants to create a new task
- list_tasks: User wants to see their tasks
- complete_task: User wants to mark a task as done
- update_task: User wants to change a task's title
- delete_task: User wants to remove a task
- unknown: Cannot determine what user wants

Parameters to extract:
- title: Task title (string, for add_task and update_task)
- description: Task description (string, optional for add_task)
- task_id: Task ID number (integer, for complete_task, update_task, delete_task)
- status: Status filter (string: "all", "pending", or "completed" for list_tasks)

Return your analysis in this JSON format:
{
  "intent": "intent_name",
  "confidence": 0.95,
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "clarification_question": "Ask this if confidence < 0.7"
}

Examples:

User: "Add a task to buy groceries"
{
  "intent": "add_task",
  "confidence": 1.0,
  "parameters": {
    "title": "buy groceries"
  }
}

User: "Show me my pending tasks"
{
  "intent": "list_tasks",
  "confidence": 1.0,
  "parameters": {
    "status": "pending"
  }
}

User: "Mark task 5 as done"
{
  "intent": "complete_task",
  "confidence": 1.0,
  "parameters": {
    "task_id": 5
  }
}

User: "Rename task 3 to finish report"
{
  "intent": "update_task",
  "confidence": 0.95,
  "parameters": {
    "task_id": 3,
    "title": "finish report"
  }
}

User: "Delete task 7"
{
  "intent": "delete_task",
  "confidence": 1.0,
  "parameters": {
    "task_id": 7
  }
}

User: "What's the weather?"
{
  "intent": "unknown",
  "confidence": 0.0,
  "parameters": {},
  "clarification_question": "I'm a task management assistant. I can help you add, list, complete, update, or delete tasks. What would you like to do?"
}

Be flexible with phrasing but accurate with intent detection. Extract all available parameters."""

    def __init__(self, client: AsyncOpenAI):
        """Initialize the IntentParser agent."""
        self.client = client

    async def parse(self, user_message: str) -> Dict[str, Any]:
        """
        Parse user message to extract intent and parameters.

        Args:
            user_message: Natural language input from user

        Returns:
            Dict containing:
            - intent: Detected intent
            - confidence: Confidence score (0.0-1.0)
            - parameters: Extracted parameters
            - clarification_question: Question to ask if confidence < 0.7
        """
        try:
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            # Parse JSON response
            import json
            result = json.loads(response.choices[0].message.content)

            # Ensure required fields
            result.setdefault("intent", "unknown")
            result.setdefault("confidence", 0.0)
            result.setdefault("parameters", {})

            return result

        except Exception as e:
            # Fallback on error
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "parameters": {},
                "error": str(e),
                "clarification_question": "I'm having trouble understanding. Could you rephrase your request?"
            }
