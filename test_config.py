import sys
sys.path.append('src')

from config import OPENROUTER_API_KEY, GEN_MODEL

print(f"✅ Config loaded successfully!")
print(f"API Key Length: {len(OPENROUTER_API_KEY) if OPENROUTER_API_KEY else 'None'}")
print(f"API Key (first 20): {OPENROUTER_API_KEY[:20] if OPENROUTER_API_KEY else 'None'}")
print(f"API Key (last 10): {OPENROUTER_API_KEY[-10:] if OPENROUTER_API_KEY else 'None'}")
print(f"Has spaces: {' ' in OPENROUTER_API_KEY if OPENROUTER_API_KEY else 'N/A'}")
print(f"Model: {GEN_MODEL}")
print(f"\nRepr: {repr(OPENROUTER_API_KEY) if OPENROUTER_API_KEY else 'None'}")

# Test the exact same way ask.py does it
import requests

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "http://localhost",
    "X-Title": "ptspRag"
}

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

print("\n🧪 Testing with EXACT ask.py headers...")
try:
    r = requests.post(CHAT_URL, headers=HEADERS, json={
        "model": GEN_MODEL,
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("✅ API call SUCCESSFUL!")
        print(f"Response: {r.json()}")
    else:
        print(f"❌ API call FAILED!")
        print(f"Response: {r.text}")
except Exception as e:
    print(f"❌ Error: {e}")
