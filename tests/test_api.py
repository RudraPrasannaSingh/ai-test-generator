import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ No API key found in .env file")
    exit()

if not api_key.startswith('sk-'):
    print("❌ Invalid API key format")
    exit()

print(f"✅ API key loaded: {api_key[:20]}...")

# Test the connection
try:
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'Hello, World!'"}],
        max_tokens=10
    )
    print("✅ OpenAI connection successful!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Error: {e}")
