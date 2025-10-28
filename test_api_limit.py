"""
Test script to run a single query and check API response/limits
"""
import requests
import json
import time

# Test query
test_query = "Apa itu PTSP?"

# RAG API endpoint
api_url = "http://localhost:8001/chat"

print(f"🧪 Testing RAG API with query: '{test_query}'")
print(f"📍 Endpoint: {api_url}")
print("-" * 70)

try:
    start_time = time.time()
    
    # Make request with proper message format
    payload = {
        "messages": [
            {"role": "user", "content": test_query}
        ]
    }
    
    response = requests.post(
        api_url,
        json=payload,
        timeout=60
    )
    
    elapsed = time.time() - start_time
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"⏱️  Response Time: {elapsed:.2f}s")
    print(f"📏 Response Size: {len(response.text)} bytes")
    print("-" * 70)
    
    if response.status_code == 200:
        data = response.json()
        print("\n📊 Response Structure:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Check for limits/errors in response
        if "error" in data:
            print(f"\n⚠️  Error in response: {data['error']}")
        
        if "results" in data:
            print(f"\n✨ Retrieved {len(data['results'])} results")
            
        if "metadata" in data:
            print(f"\n🔧 Metadata:")
            print(json.dumps(data['metadata'], indent=2))
    else:
        print(f"\n❌ Error Response:")
        print(response.text)

except requests.exceptions.Timeout:
    print(f"❌ Request timeout after 60 seconds")
except requests.exceptions.ConnectionError:
    print(f"❌ Connection error - is the API running on localhost:8000?")
except Exception as e:
    print(f"❌ Error: {e}")

print("-" * 70)
