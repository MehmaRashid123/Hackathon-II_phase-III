"""
Test the complete chat flow with Groq assistant.
"""

import asyncio
import sys
from uuid import uuid4
from sqlmodel import Session

# Add src to path
sys.path.insert(0, 'src')

from src.core.database import engine
from src.agents.context import AgentContext
from src.agents.groq_assistant import GroqAssistant
from src.agents.system_instructions import get_system_instructions
from src.agents.tool_definitions import get_all_tools


async def test_chat():
    """Test chat with tool calling."""
    
    # Create test context
    user_id = uuid4()
    context = AgentContext(
        user_id=user_id,
        conversation_history=[],
        system_instructions=get_system_instructions(),
        available_tools=get_all_tools(),
        conversation_id=str(uuid4()),
        mcp_server_url="http://localhost:8000/api/mcp"
    )
    
    # Create assistant
    assistant = GroqAssistant()
    
    # Test message
    test_message = "Add a task to buy groceries"
    
    print(f"Testing message: '{test_message}'")
    print(f"User ID: {user_id}")
    print(f"Tools available: {len(get_all_tools())}")
    print("\n" + "="*60 + "\n")
    
    try:
        result = await assistant.process_message(
            message=test_message,
            context=context,
            conversation_history=[]
        )
        
        print("✅ SUCCESS!")
        print(f"\nAssistant response: {result['message']}")
        print(f"\nTool calls: {len(result.get('tool_calls', []))}")
        
        if result.get('tool_calls'):
            print("\nTool call details:")
            for tc in result['tool_calls']:
                print(f"  - {tc['tool_name']}")
                print(f"    Parameters: {tc['parameters']}")
                print(f"    Result: {tc['result']}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_chat())
