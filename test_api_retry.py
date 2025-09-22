#!/usr/bin/env python3
"""
Test the RAG API with the failing query
"""
import requests
import json

def test_api():
    url = "http://localhost:8001/chat"
    
    # Test the query that was failing
    test_query = "Saya mau buka toko retail pakaian, bagaimana cara mengurus SIUP dan TDP-nya?"
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": test_query
            }
        ]
    }
    
    print(f"🔍 Testing query: {test_query}")
    print("📡 Sending request to RAG API...")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📊 Sources found: {result.get('total_sources', 0)}")
            print(f"🎯 Response preview: {result.get('message', '')[:200]}...")
            
            # Show enhanced features
            features = result.get('enhanced_features', {})
            print(f"⚡ Enhanced features: {json.dumps(features, indent=2)}")
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api()