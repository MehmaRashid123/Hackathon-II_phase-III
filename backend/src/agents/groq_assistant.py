"""
Todo Assistant implementation using Groq API (Free & Fast).

Groq provides free API access with fast inference.
"""

import logging
import json
from typing import List, Dict, Any
import httpx

from src.core.config import settings
from src.agents.context import AgentContext
from src.agents.system_instructions import get_system_instructions
from src.agents.tool_definitions import get_all_tools
from src.agents.tool_executors import get_tool_function
from src.schemas.chat import ToolCall


logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class AgentProcessingError(AgentError):
    """Raised when agent fails to process a message."""
    pass


class GroqAssistant:
    """
    Todo Assistant powered by Groq API (Free).
    
    Groq provides fast inference with generous free tier.
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None
    ):
        """Initialize the Groq Assistant."""
        self.api_key = api_key or getattr(settings, 'GROQ_API_KEY', '')
        self.model_name = model or getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.max_tokens = max_tokens or getattr(settings, 'GROQ_MAX_TOKENS', 4000)
        self.temperature = temperature or getattr(settings, 'GROQ_TEMPERATURE', 0.7)
        self.base_url = "https://api.groq.com/openai/v1"
        
        logger.info(
            f"Initialized GroqAssistant with model={self.model_name}, "
            f"max_tokens={self.max_tokens}, temperature={self.temperature}"
        )
    
    async def process_message(
        self,
        message: str,
        context: AgentContext,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return AI response with tool execution.
        
        Args:
            message: User's message
            context: Agent context with database session and user info
            conversation_history: Previous messages in conversation
            
        Returns:
            Dict with 'message' and optional 'tool_calls'
        """
        try:
            # Build messages
            messages = []
            
            # Add system message
            messages.append({
                "role": "system",
                "content": get_system_instructions()
            })
            
            # Add conversation history (exclude system messages to avoid conflicts)
            if conversation_history:
                for msg in conversation_history:
                    # Skip system messages in history - we already have one
                    if msg.get("role") != "system":
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Get tools
            tools = get_all_tools()
            
            # Call Groq API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "tools": tools,
                        "tool_choice": "auto",
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    raise AgentProcessingError(f"Groq API error: {response.status_code}")
                
                result = response.json()
                ai_message = result["choices"][0]["message"]
                
                # Check for tool calls
                tool_calls_data = []
                if ai_message.get("tool_calls"):
                    # Execute tools
                    for tool_call in ai_message["tool_calls"]:
                        function_name = tool_call["function"]["name"]
                        # Handle null/None arguments
                        args_str = tool_call["function"]["arguments"]
                        if args_str and args_str != "null":
                            function_args = json.loads(args_str)
                        else:
                            function_args = {}
                        
                        logger.info(f"Executing tool: {function_name} with args: {function_args}")
                        
                        # Get tool function and execute
                        tool_func = get_tool_function(function_name)
                        if tool_func:
                            try:
                                result = await tool_func(context, **function_args)
                                tool_calls_data.append({
                                    "tool_name": function_name,
                                    "parameters": function_args,
                                    "result": result
                                })
                            except Exception as e:
                                logger.error(f"Tool execution error: {e}")
                                tool_calls_data.append({
                                    "tool_name": function_name,
                                    "parameters": function_args,
                                    "result": {"error": str(e)}
                                })
                    
                    # If tools were called, get final response
                    if tool_calls_data:
                        # Add tool results to messages
                        messages.append(ai_message)
                        for i, tool_call in enumerate(ai_message["tool_calls"]):
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": json.dumps(tool_calls_data[i]["result"])
                            })
                        
                        # Get final response
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                f"{self.base_url}/chat/completions",
                                headers={
                                    "Authorization": f"Bearer {self.api_key}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "model": self.model_name,
                                    "messages": messages,
                                    "temperature": self.temperature,
                                    "max_tokens": self.max_tokens
                                },
                                timeout=30.0
                            )
                            
                            if response.status_code != 200:
                                logger.error(f"Groq API error: {response.status_code}")
                                raise AgentProcessingError(f"Groq API error: {response.status_code}")
                            
                            result = response.json()
                            final_message = result["choices"][0]["message"]["content"]
                            
                            return {
                                "message": final_message,
                                "tool_calls": tool_calls_data
                            }
                
                # No tool calls, return direct response
                return {
                    "message": ai_message.get("content", ""),
                    "tool_calls": []
                }
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            raise AgentProcessingError(f"Failed to process message: {str(e)}") from e
