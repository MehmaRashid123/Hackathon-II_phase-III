"""
Test different Groq models for tool calling support.
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_model_tools(model_name: str):
    """Test a specific model with tool calling."""
    
    api_key = os.getenv("GROQ_API_KEY")
    base_url = "https://api.groq.com/openai/v1"
    
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
    
    print(f"\nTesting model: {model_name}")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_name,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto",
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_message = result["choices"][0]["message"]
                
                if ai_message.get("tool_calls"):
                    print("✅ Tool calling WORKS!")
                    for tc in ai_message["tool_calls"]:
                        print(f"   Function: {tc['function']['name']}")
                        print(f"   Args: {tc['function']['arguments']}")
                else:
                    print("❌ No tool calls - text response only")
                    print(f"   Content: {ai_message.get('content', 'N/A')[:100]}")
            else:
                print(f"❌ API Error: {response.status_code}")
                error_data = response.json()
                if 'error' in error_data:
                    print(f"   Message: {error_data['error'].get('message', 'Unknown')}")
                    if 'failed_generation' in error_data['error']:
                        print(f"   Failed gen: {error_data['error']['failed_generation'][:100]}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")


async def main():
    """Test multiple models."""
    
    # Models to test - focusing on ones that might support tool calling
    models_to_test = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "groq/compound",
        "groq/compound-mini",
    ]
    
    for model in models_to_test:
        await test_model_tools(model)
        await asyncio.sleep(1)  # Rate limiting


if __name__ == "__main__":
    asyncio.run(main())
