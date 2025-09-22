#!/usr/bin/env python3
"""
Detailed test to debug the domain relevance detection
"""
import requests
import json

def test_domain_detection():
    url = "http://localhost:8001/chat"
    
    # Test with clearly off-topic query
    query = "What is the weather in New York today?"
    
    print(f"🔍 Testing: {query}")
    print("📡 Sending request...")
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=25)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            
            # Detailed analysis
            features = result.get('enhanced_features', {})
            
            print(f"\n📊 Detailed Analysis:")
            print(f"  Domain relevant: {features.get('domain_relevant', 'unknown')}")
            print(f"  Top similarity: {features.get('top_similarity', 'unknown')}")
            print(f"  Quality score: {features.get('quality_score', 'unknown')}")
            print(f"  Search method: {features.get('search_method', 'unknown')}")
            print(f"  Sources: {result.get('total_sources', 0)}")
            
            print(f"\n📝 Response preview:")
            print(f"  {result.get('message', '')[:200]}...")
            
            print(f"\n🔍 All Enhanced Features:")
            print(json.dumps(features, indent=2))
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_domain_detection()