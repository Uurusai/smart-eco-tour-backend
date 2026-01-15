"""Test Groq API connection."""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print(f"API Key found: {bool(GROQ_API_KEY)}")
print(f"API Key prefix: {GROQ_API_KEY[:15]}..." if GROQ_API_KEY else "No key")

try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Say hello in one word"}
        ],
        max_tokens=10,
    )
    
    print(f"✅ Groq API Connected Successfully!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Groq API Error: {type(e).__name__}: {e}")
