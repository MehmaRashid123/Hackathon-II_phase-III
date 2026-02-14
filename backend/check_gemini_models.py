"""
Check available Gemini models with your API key
"""
import google.generativeai as genai
from src.config import settings

# Configure with your API key
genai.configure(api_key=settings.GEMINI_API_KEY)

print("Checking available Gemini models...\n")
print(f"Using API Key: {settings.GEMINI_API_KEY[:10]}...\n")

try:
    # List all available models
    models = genai.list_models()
    
    print("Available models that support generateContent:\n")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
            print(f"    Display Name: {model.display_name}")
            print(f"    Description: {model.description}")
            print()
    
except Exception as e:
    print(f"Error: {e}")
