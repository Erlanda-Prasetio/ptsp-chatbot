import requests
import json
import time

API_URL = "http://localhost:8001/chat"

queries = [
    "Apa itu DPMPTSP Jawa Tengah?",
    "Bagaimana cara mengurus izin usaha?",
    "Syarat investasi di Jawa Tengah",
    "Jam operasional layanan?",
    "Dimana lokasi kantor DPMPTSP?"
]

def test_query(query, index):
    print(f"\n[{index}/5] Testing query: '{query}'")
    payload = {
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ]
    }
    
    try:
        start_time = time.time()
        response = requests.post(API_URL, json=payload, timeout=60) # Increased timeout for RAG
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", "")
            sources = data.get("sources", [])
            print(f"✅ Success ({duration:.2f}s)")
            print(f"Response preview: {message[:100]}...")
            print(f"Sources found: {len(sources)}")
        else:
            print(f"❌ Failed (Status {response.status_code})")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("Starting 5-query test for RAG API...")
    
    # First check health
    try:
        health = requests.get("http://localhost:8001/health", timeout=5)
        if health.status_code == 200:
            print("Server is healthy.")
        else:
            print(f"Server returned unhealthy status: {health.status_code}")
    except Exception as e:
        print(f"Could not connect to health endpoint: {e}")
        return

    for i, q in enumerate(queries, 1):
        test_query(q, i)
        
    print("\nTest complete.")

if __name__ == "__main__":
    main()
