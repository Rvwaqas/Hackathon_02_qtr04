"""Cohere LLM client using official Cohere SDK with function calling."""

import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Get Cohere API key and settings (reload env each time)
def get_cohere_config():
    """Get Cohere configuration, reloading from .env."""
    load_dotenv(override=True)  # Force reload from .env
    return {
        "api_key": os.getenv("COHERE_API_KEY"),
        "base_url": os.getenv("COHERE_BASE_URL", "https://api.cohere.ai"),
        "model": os.getenv("COHERE_MODEL", "command-r-plus")
    }


class CohereAgentClient:
    """Cohere client using official Cohere SDK with function calling."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize Cohere client.

        Args:
            api_key: Cohere API key (defaults to COHERE_API_KEY env var)
            model: Model name (defaults to COHERE_MODEL env var)
            base_url: Cohere base URL (defaults to https://api.cohere.ai)
        """
        # Get config from env (this will reload .env)
        config = get_cohere_config()

        self.api_key = api_key or config["api_key"]
        self.model = model or config["model"]
        self.base_url = base_url or config["base_url"]

        if not self.api_key:
            raise ValueError("COHERE_API_KEY environment variable not set")

        # Import here to avoid issues if not installed
        try:
            import cohere
        except ImportError:
            raise ImportError(
                "cohere package not installed. "
                "Install it with: pip install cohere"
            )

        # Initialize Cohere async client with base URL
        self.client = cohere.AsyncClient(
            api_key=self.api_key,
        )

    async def execute_agent(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tools_handler=None,  # Optional tools handler to execute tools
    ) -> str:
        """Execute agent with user message using Cohere API with function calling.

        Args:
            user_message: User's message/query
            conversation_history: Previous messages for context
            system_prompt: System instructions for the agent
            tools: List of available tools for the agent
            tools_handler: Handler to execute tools when called by the model

        Returns:
            Agent's response text
        """
        try:
            # Build messages for Cohere - using the chat endpoint format
            chat_history = []

            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    # Map role and content to Cohere format
                    role = "USER" if msg.get("role") == "user" else "CHATBOT"
                    chat_history.append({
                        "role": role,
                        "message": msg.get("content", "")
                    })

            # Prepare the call with tools if provided
            # Note: Cohere uses "tools" parameter for function definitions
            # and "tool_results" for providing results back to the model
            api_kwargs = {
                "message": user_message,
                "model": self.model,
                "chat_history": chat_history,
                "temperature": 0.7,
                "max_tokens": 1024,
            }

            # Add preamble (system prompt) if provided
            if system_prompt:
                api_kwargs["preamble"] = system_prompt

            # Include tools if provided
            if tools:
                # Convert OpenAI-style tools to Cohere functions
                cohere_tools = []
                for tool in tools:
                    cohere_tool = {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameter_definitions": {}
                    }

                    # Convert parameters from OpenAI format to Cohere format
                    for param_name, param_details in tool["parameters"]["properties"].items():
                        param_info = {
                            "description": param_details.get("description", ""),
                        }

                        # Determine type
                        if "type" in param_details:
                            param_info["type"] = param_details["type"]

                        # Handle enums
                        if "enum" in param_details:
                            param_info["enum"] = param_details["enum"]

                        # Handle required fields
                        cohere_tool["parameter_definitions"][param_name] = param_info

                    cohere_tools.append(cohere_tool)

                api_kwargs["tools"] = cohere_tools

            # Call Cohere API using the /v1/chat endpoint format
            response = await self.client.chat(**api_kwargs)

            # Process the response
            # Check if the response contains tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Execute the tools if we have a tools handler
                if tools_handler:
                    # Execute each tool call
                    tool_results = []
                    for tool_call in response.tool_calls:
                        function_name = tool_call.name
                        function_args = tool_call.parameters

                        # Execute the tool
                        try:
                            # Get the tool method from the tools handler
                            tool_method = getattr(tools_handler, function_name, None)

                            if tool_method:
                                # Execute the tool
                                tool_result = await tool_method(**function_args)

                                # Format the result for Cohere
                                tool_results.append({
                                    "call": {
                                        "name": function_name,
                                        "parameters": function_args
                                    },
                                    "outputs": [tool_result]
                                })
                            else:
                                # Tool not found
                                error_result = {
                                    "success": False,
                                    "error": "tool_not_found",
                                    "message": f"Tool '{function_name}' not found"
                                }
                                tool_results.append({
                                    "call": {
                                        "name": function_name,
                                        "parameters": function_args
                                    },
                                    "outputs": [error_result]
                                })
                        except Exception as tool_error:
                            # Handle tool execution error
                            error_result = {
                                "success": False,
                                "error": "tool_execution_error",
                                "message": f"Error executing {function_name}: {str(tool_error)}"
                            }
                            tool_results.append({
                                "call": {
                                    "name": function_name,
                                    "parameters": function_args
                                },
                                "outputs": [error_result]
                            })

                    # Make another API call with the tool results
                    final_response = await self.client.chat(
                        message=user_message,
                        model=self.model,
                        chat_history=chat_history + [{"role": "USER", "message": user_message}],
                        tool_results=tool_results,
                        force_single_step=True,  # Required when using tool_results
                        temperature=0.7,
                        max_tokens=1024
                    )

                    if hasattr(final_response, 'text') and final_response.text:
                        return final_response.text.strip()
                    elif hasattr(final_response, 'generations') and final_response.generations:
                        return final_response.generations[0].text.strip()
                    else:
                        return "I processed your request using tools."
                else:
                    # No tools handler provided, return info about tool calls
                    tool_calls_info = []
                    for tool_call in response.tool_calls:
                        tool_calls_info.append(f"Tool '{tool_call.name}' called with arguments: {tool_call.parameters}")
                    return f"Processing tool calls: {'; '.join(tool_calls_info)}"

            # If no tool calls, return the regular content
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            elif hasattr(response, 'generations') and response.generations:
                return response.generations[0].text.strip()

            return "I couldn't process that request. Please try again."

        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[ERROR] Cohere API Error: {error_msg}".encode('utf-8', errors='replace').decode('utf-8'))
            print(f"[DEBUG] Exception type: {type(e).__name__}".encode('utf-8', errors='replace').decode('utf-8'))
            import traceback
            traceback.print_exc()
            raise


# Singleton instance
_cohere_agent_client: Optional[CohereAgentClient] = None


def get_cohere_agent_client() -> CohereAgentClient:
    """Get or create singleton Cohere Agent client."""
    global _cohere_agent_client
    if _cohere_agent_client is None:
        _cohere_agent_client = CohereAgentClient()
    return _cohere_agent_client


def reset_cohere_agent_client():
    """Reset singleton for testing."""
    global _cohere_agent_client
    _cohere_agent_client = None
