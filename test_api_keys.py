import os
import sys
from pathlib import Path

# Add the project root to Python path to import backend modules
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file if it exists
except ImportError:
    print("dotenv module not found. Environment variables must be set manually.")

# Print current environment variables (masked for security)
openai_key = os.environ.get("OPENAI_API_KEY", "")
openrouter_key = os.environ.get("OPEN_ROUTER_API_KEY", "")

print(f"OpenAI API Key: {'*' * (len(openai_key) - 4) + openai_key[-4:] if openai_key else 'Not set'}")
print(f"OpenRouter API Key: {'*' * (len(openrouter_key) - 4) + openrouter_key[-4:] if openrouter_key else 'Not set'}")

# Test OpenAI API
print("\n===== Testing OpenAI API =====")
try:
    import openai
    client = openai.OpenAI(api_key=openai_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, this is a test!"}],
        max_tokens=10
    )
    print(f"OpenAI API test: SUCCESS")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"OpenAI API test: FAILED")
    print(f"Error: {str(e)}")

# Test OpenRouter API
print("\n===== Testing OpenRouter API =====")
try:
    import httpx
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openrouter_key}",
            "HTTP-Referer": "http://localhost:8501",  # Your site URL
            "Content-Type": "application/json"
        },
        json={
            "model": "anthropic/claude-3-haiku-20240307",
            "messages": [{"role": "user", "content": "Hello, this is a test!"}],
            "max_tokens": 10
        },
        timeout=30.0
    )
    if response.status_code == 200:
        result = response.json()
        print(f"OpenRouter API test: SUCCESS")
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"OpenRouter API test: FAILED")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"OpenRouter API test: FAILED")
    print(f"Error: {str(e)}")

# Print instructions for fixing API key issues
print("\n===== INSTRUCTIONS =====")
print("If any tests failed, you need to set the correct API keys:")
print("1. Create a .env file in the project root with:")
print("   OPENAI_API_KEY=your_openai_key_here")
print("   OPEN_ROUTER_API_KEY=your_openrouter_key_here")
print("2. OR set environment variables in your terminal:")
print("   export OPENAI_API_KEY=your_openai_key_here")
print("   export OPEN_ROUTER_API_KEY=your_openrouter_key_here")
print("3. OR modify backend/chains.py to hardcode the API keys")
print("   os.environ['OPENAI_API_KEY'] = 'your_openai_key_here'")
print("   os.environ['OPEN_ROUTER_API_KEY'] = 'your_openrouter_key_here'") 