"""Quick test of Groq API integration"""
from dotenv import load_dotenv
import os
import requests

load_dotenv()

groq_key = os.getenv('GROQ_API_KEY')
model = os.getenv('MODEL', 'llama-3.3-70b-versatile')

print(f"🔑 Groq API Key: {groq_key[:20]}...{groq_key[-10:] if groq_key else 'None'}")
print(f"🤖 Model: {model}")

if not groq_key:
    print("❌ No GROQ_API_KEY found in .env")
    exit(1)

print("\n🧪 Testing Groq API...")
try:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from Groq!' in Indonesian."}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        },
        timeout=10
    )
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        answer = data['choices'][0]['message']['content']
        usage = data.get('usage', {})
        
        print("✅ Groq API is WORKING!")
        print(f"💬 Response: {answer}")
        print(f"📊 Tokens used: {usage.get('total_tokens', 0)}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ Failed: {e}")
