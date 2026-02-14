"""
Test script to verify Groq API tool calling format.
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_groq_tools():
    """Test Groq API with tool calling."""
    
    api_key = os.getenv("GROQ_API_KEY")
    base_url = "https://api.groq.com/openai/v1"
    
    # Simple tool definition
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description"
                        }
                    },
                    "required": ["title"]
                }
            }
        }
    ]
    
    messages = [
        {
            "role": "system",
            "content": "You are a task assistant. Use the add_task tool when users want to create tasks."
        },
        {
            "role": "user",
            "content": "Add a task to buy groceries"
        }
    ]
    
    print("Testing Groq API with tools...")
    print(f"Tools: {json.dumps(tools, indent=2)}")
    
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
                "max_tokens": 1000
            },
            timeout=30.0
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            result = response.json()
            ai_message = result["choices"][0]["message"]
            
            if ai_message.get("tool_calls"):
                print("\n✅ Tool calls detected!")
                for tool_call in ai_message["tool_calls"]:
                    print(f"  - {tool_call['function']['name']}: {tool_call['function']['arguments']}")
            else:
                print("\n❌ No tool calls - AI responded with text only")
                print(f"Content: {ai_message.get('content')}")

if __name__ == "__main__":
    asyncio.run(test_groq_tools())
