#!/usr/bin/env python3
"""
Test with partially relevant queries to trigger internet search
"""
import requests
import json

def test_partial_relevance():
    url = "http://localhost:8001/chat"
    
    # Test queries that are somewhat relevant but might have low similarity
    test_queries = [
        "Bagaimana cara mengurus izin usaha startup teknologi blockchain di Jawa Tengah tahun 2024?",
        "Apa persyaratan terbaru untuk izin ekspor impor komoditas pertanian di Jawa Tengah?",
        "Prosedur izin usaha pariwisata berbasis digital nomad di Jawa Tengah",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"🔍 Test {i}/3: {query}")
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
                
                features = result.get('enhanced_features', {})
                
                print(f"\n📊 Analysis:")
                print(f"  Search method: {features.get('search_method', 'unknown')}")
                print(f"  Quality score: {features.get('quality_score', 'unknown')}")
                print(f"  Top similarity: {features.get('top_similarity', 'unknown')}")
                print(f"  Sources found: {result.get('total_sources', 0)}")
                print(f"  Response time: {features.get('response_time', 'unknown')}")
                
                if 'phase_times' in features:
                    print(f"  Phase breakdown:")
                    for phase, time_taken in features['phase_times'].items():
                        print(f"    - {phase}: {time_taken:.3f}s")
                
                print(f"\n📝 Response preview:")
                print(f"  {result.get('message', '')[:200]}...")
                
                # Check if internet search was used
                if features.get('search_method') in ['internet_only', 'internet_enhanced']:
                    print(f"\n🌐 INTERNET SEARCH TRIGGERED! ✅")
                else:
                    print(f"\n📚 Vector search was sufficient")
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_partial_relevance()