"""
Chat Service

Orchestrates the complete stateless request cycle for chat interactions.
Coordinates conversation history, agent processing, and message persistence.
"""

from typing import Optional
from uuid import UUID
from sqlmodel import Session
import logging

from src.schemas.chat import ChatRequest, ChatResponse, ToolCall
from src.agents.context import AgentContext
from src.agents.system_instructions import get_system_instructions
from src.agents.tool_definitions import get_all_tools
from src.agents.groq_assistant import GroqAssistant, AgentError
from src.services.conversation_service import ConversationService, ConversationServiceError


logger = logging.getLogger(__name__)


class ChatServiceError(Exception):
    """Base exception for chat service errors."""
    pass


class ChatService:
    """
    Service for processing chat requests in a stateless manner.
    
    Implements the complete request cycle:
    1. Fetch conversation history from database
    2. Build agent context with history and tools
    3. Process user message through AI agent
    4. Save messages to database
    5. Return response
    
    Each request is completely stateless - all context is loaded from
    and saved to the database.
    """
    
    @staticmethod
    async def process_chat_request(
        session: Session,
        user_id: str,
        request: ChatRequest
    ) -> ChatResponse:
        """
        Process a chat request through the complete stateless cycle.
        
        This is the main entry point for chat interactions. It orchestrates
        all the components to provide a seamless conversational experience.
        
        Args:
            session: Database session
            user_id: User ID (UUID string)
            request: ChatRequest with user message and optional conversation_id
        
        Returns:
            ChatResponse with agent message, conversation_id, and tool calls
        
        Raises:
            ChatServiceError: If processing fails at any step
        
        Example:
            response = await ChatService.process_chat_request(
                session,
                user_id="550e8400-e29b-41d4-a716-446655440000",
                request=ChatRequest(
                    message="Add a task to buy groceries",
                    conversation_id=None
                )
            )
        """
        try:
            logger.info(
                f"Processing chat request for user {user_id}: "
                f"'{request.message[:50]}...'"
            )
            
            # Step 1: Get or create conversation
            conversation = ConversationService.get_or_create_conversation(
                session,
                user_id=user_id,
                conversation_id=request.conversation_id
            )
            
            logger.info(f"Using conversation {conversation.id}")
            
            # Step 2: Fetch conversation history
            history = ConversationService.get_conversation_history(
                session,
                conversation_id=str(conversation.id),
                user_id=user_id,
                limit=50
            )
            
            logger.info(f"Loaded {len(history)} messages from history")
            
            # Step 3: Build agent context
            context = ChatService._build_agent_context(
                user_id=user_id,
                conversation_id=str(conversation.id),
                history=history
            )
            
            # Step 4: Process message through agent
            assistant = GroqAssistant()
            
            try:
                agent_result = await assistant.process_message(
                    message=request.message,
                    context=context,
                    conversation_history=context.conversation_history
                )
            except AgentError as e:
                logger.error(f"Agent processing failed: {e}")
                raise ChatServiceError(
                    "I'm having trouble processing your request. Please try again."
                ) from e
            
            # Step 5: Save messages to database
            try:
                ConversationService.save_messages(
                    session,
                    conversation_id=str(conversation.id),
                    user_id=user_id,
                    user_message=request.message,
                    assistant_message=agent_result["message"]
                )
            except ConversationServiceError as e:
                logger.error(f"Failed to save messages: {e}")
                # Don't fail the request if save fails - user got their response
                logger.warning("Continuing despite save failure")
            
            # Step 6: Build and return response
            response = ChatResponse(
                conversation_id=str(conversation.id),
                message=agent_result["message"],
                tool_calls=agent_result.get("tool_calls")
            )
            
            tool_calls = agent_result.get('tool_calls') or []
            logger.info(
                f"Chat request processed successfully. "
                f"Tool calls: {len(tool_calls)}"
            )
            
            return response
            
        except ChatServiceError:
            # Re-raise chat service errors
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error processing chat request: {e}", exc_info=True)
            raise ChatServiceError(
                "An unexpected error occurred. Please try again."
            ) from e
    
    @staticmethod
    def _build_agent_context(
        user_id: str,
        conversation_id: str,
        history: list
    ) -> AgentContext:
        """
        Build agent context from conversation history.
        
        Args:
            user_id: User ID (UUID string)
            conversation_id: Conversation ID (UUID string)
            history: List of ConversationMessage objects
        
        Returns:
            AgentContext ready for agent processing
        
        Example:
            context = ChatService._build_agent_context(
                user_id="550e8400-e29b-41d4-a716-446655440000",
                conversation_id="650e8400-e29b-41d4-a716-446655440001",
                history=[...]
            )
        """
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id format: {user_id}")
        
        # Convert history to context format
        conversation_history = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in history
        ]
        
        # Build context
        context = AgentContext(
            user_id=user_uuid,
            conversation_history=conversation_history,
            system_instructions=get_system_instructions(),
            available_tools=get_all_tools(),
            conversation_id=conversation_id,
            mcp_server_url="http://localhost:8000/api/mcp"
        )
        
        logger.debug(
            f"Built agent context with {len(conversation_history)} messages "
            f"and {len(context.available_tools)} tools"
        )
        
        return context


# Convenience function for common use case
async def process_chat(
    user_id: str,
    request: ChatRequest,
    session: Session
) -> ChatResponse:
    """
    Convenience function to process a chat message.
    
    Args:
        user_id: User ID (UUID string)
        request: ChatRequest with message and optional conversation_id
        session: Database session
    
    Returns:
        ChatResponse with agent's reply
    
    Example:
        response = await process_chat(
            user_id="550e8400-e29b-41d4-a716-446655440000",
            request=ChatRequest(message="Add a task to buy groceries"),
            session=session
        )
        print(response.message)  # "Done! I've added 'Buy groceries'..."
    """
    return await ChatService.process_chat_request(
        session,
        user_id,
        request
    )
