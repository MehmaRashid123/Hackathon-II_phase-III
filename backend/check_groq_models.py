"""
Check which Groq models support tool calling.
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def check_models():
    """List available Groq models."""
    
    api_key = os.getenv("GROQ_API_KEY")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.groq.com/openai/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            models = response.json()["data"]
            print("Available Groq models:\n")
            for model in models:
                print(f"  - {model['id']}")
                if 'owned_by' in model:
                    print(f"    Owner: {model['owned_by']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(check_models())
