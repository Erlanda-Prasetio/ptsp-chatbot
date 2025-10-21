from dotenv import load_dotenv
import os
import requests

load_dotenv()

key = os.getenv('OPENROUTER_API_KEY')
print(f"API Key Length: {len(key) if key else 'None'}")
print(f"First 20 chars: {key[:20] if key else 'None'}")
print(f"Last 10 chars: {key[-10:] if key else 'None'}")
print(f"Has leading/trailing spaces: '{key[0] if key else ''}' ... '{key[-1] if key else ''}'")
print(f"Repr: {repr(key[:30]) if key else 'None'}...")

# Test the API key
print("\n🧪 Testing API key with OpenRouter...")
try:
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {key}"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ API key is VALID!")
    elif response.status_code == 401:
        print("❌ API key is INVALID or EXPIRED!")
        print(f"Response: {response.text[:200]}")
    else:
        print(f"⚠️ Unexpected status: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")
