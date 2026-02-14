"""
Test list_tasks tool specifically.
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

async def test_list_tasks():
    """Test list_tasks tool."""
    
    api_key = os.getenv("GROQ_API_KEY")
    base_url = "https://api.groq.com/openai/v1"
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    tools = get_all_tools()
    system_instructions = get_system_instructions()
    
    print("Testing list_tasks tool...")
    
    messages = [
        {
            "role": "system",
            "content": system_instructions
        },
        {
            "role": "user",
            "content": "What tasks do I have?"
        }
    ]
    
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
                "temperature": 0.1,
                "max_tokens": 1000
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_message = result["choices"][0]["message"]
            
            if ai_message.get("tool_calls"):
                print("✅ list_tasks tool called!")
                for tc in ai_message["tool_calls"]:
                    print(f"   Tool: {tc['function']['name']}")
                    print(f"   Args: {tc['function']['arguments']}")
            else:
                print("❌ No tool calls")
                print(f"   Response: {ai_message.get('content', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.json())


if __name__ == "__main__":
    asyncio.run(test_list_tasks())
