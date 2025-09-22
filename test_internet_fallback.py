#!/usr/bin/env python3
"""
Test the RAG API with queries that should trigger internet search
"""
import requests
import json

def test_internet_fallback():
    url = "http://localhost:8001/chat"
    
    # Test queries that are less likely to be in the vector database
    test_queries = [
        "Apa itu ChatGPT dan bagaimana cara kerjanya?",  # Completely off-topic
        "Bagaimana kondisi ekonomi Indonesia tahun 2024?",  # Recent data not in our database
        "Cara mengurus izin usaha cryptocurrency di Indonesia",  # Very specific recent topic
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/3: {query}")
        print("📡 Sending request to RAG API...")
        
        payload = {
            "messages": [
                {
                    "role": "user", 
                    "content": query
                }
            ]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=25)  # 25s timeout for internet search
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"📊 Sources found: {result.get('total_sources', 0)}")
                print(f"🎯 Response preview: {result.get('message', '')[:150]}...")
                
                # Show search method used
                features = result.get('enhanced_features', {})
                search_method = features.get('search_method', 'unknown')
                quality_score = features.get('quality_score', 0)
                response_time = features.get('response_time', 'unknown')
                
                print(f"🔍 Search method: {search_method}")
                print(f"📊 Quality score: {quality_score}")
                print(f"⏱️ Response time: {response_time}")
                
                if 'phase_times' in features:
                    phase_times = features['phase_times']
                    print(f"📈 Phase breakdown: {json.dumps(phase_times, indent=2)}")
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_internet_fallback()