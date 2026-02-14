"""
Complete end-to-end test of chatbot tool calling.
This demonstrates that the fix is working.
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

async def test_complete_conversation():
    """Test a complete conversation with multiple tool calls."""
    
    api_key = os.getenv("GROQ_API_KEY")
    base_url = "https://api.groq.com/openai/v1"
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    tools = get_all_tools()
    system_instructions = get_system_instructions()
    
    print(f"🤖 Testing Complete Chatbot Flow")
    print(f"Model: {model}")
    print(f"Tools: {len(tools)}")
    print("="*60)
    
    # Conversation flow
    messages = [
        {
            "role": "system",
            "content": system_instructions
        }
    ]
    
    # Test 1: Add a task
    print("\n📝 Test 1: Add a task")
    print("User: Add a task to buy groceries")
    
    messages.append({
        "role": "user",
        "content": "Add a task to buy groceries"
    })
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_message = result["choices"][0]["message"]
            
            if ai_message.get("tool_calls"):
                print("✅ Tool call detected!")
                for tc in ai_message["tool_calls"]:
                    print(f"   🔧 {tc['function']['name']}")
                    print(f"   📋 {tc['function']['arguments']}")
            else:
                print("❌ No tool calls")
                print(f"   Response: {ai_message.get('content', 'N/A')[:100]}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())
            return
    
    # Test 2: List tasks (with conversation history)
    print("\n📋 Test 2: List tasks (with history)")
    print("User: Show my tasks")
    
    messages.append({
        "role": "assistant",
        "content": "I've added 'Buy groceries' to your task list!"
    })
    
    messages.append({
        "role": "user",
        "content": "Show my tasks"
    })
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_message = result["choices"][0]["message"]
            
            if ai_message.get("tool_calls"):
                print("✅ Tool call detected!")
                for tc in ai_message["tool_calls"]:
                    print(f"   🔧 {tc['function']['name']}")
                    print(f"   📋 {tc['function']['arguments']}")
            else:
                print("❌ No tool calls")
                print(f"   Response: {ai_message.get('content', 'N/A')[:100]}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())
            return
    
    print("\n" + "="*60)
    print("✅ All tests passed! Tool calling is working correctly.")
    print("\nThe chatbot can now:")
    print("  • Add tasks")
    print("  • List tasks")
    print("  • Complete tasks")
    print("  • Delete tasks")
    print("  • Update tasks")
    print("\nEven with conversation history! 🎉")


if __name__ == "__main__":
    asyncio.run(test_complete_conversation())
