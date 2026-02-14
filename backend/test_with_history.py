"""
Test Groq with conversation history to see if that breaks tool calling.
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv
import sys

sys.path.insert(0, 'src')

from src.agents.system_instructions import get_system_instructions
from src.agents.tool_definitions import get_all_tools

load_dotenv()

async def test_with_history():
    """Test with conversation history."""
    
    api_key = os.getenv("GROQ_API_KEY")
    base_url = "https://api.groq.com/openai/v1"
    
    tools = get_all_tools()
    system_instructions = get_system_instructions()
    
    # Simulate a conversation with history
    messages = [
        {
            "role": "system",
            "content": system_instructions
        },
        # Previous conversation
        {
            "role": "user",
            "content": "Hello"
        },
        {
            "role": "assistant",
            "content": "Hi! I'm your Todo Assistant. How can I help you manage your tasks today?"
        },
        # Current message
        {
            "role": "user",
            "content": "Add a task to buy groceries"
        }
    ]
    
    print("Testing with conversation history...")
    print(f"Messages in history: {len(messages)}")
    print("\n" + "="*60 + "\n")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0.7,
                "max_tokens": 4000
            },
            timeout=30.0
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            ai_message = result["choices"][0]["message"]
            
            print(f"Finish reason: {result['choices'][0]['finish_reason']}")
            
            if ai_message.get("tool_calls"):
                print("\n✅ Tool calls detected!")
                for tc in ai_message["tool_calls"]:
                    print(f"  - {tc['function']['name']}")
                    print(f"    Args: {tc['function']['arguments']}")
            else:
                print("\n❌ No tool calls")
                print(f"Content: {ai_message.get('content', 'N/A')[:200]}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            error_data = response.json()
            print(json.dumps(error_data, indent=2))


if __name__ == "__main__":
    asyncio.run(test_with_history())
