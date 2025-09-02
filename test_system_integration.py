"""
Test the full system integration with the new smart enhanced RAG
"""
import requests
import json
import time

API_BASE = "http://localhost:8001"

def test_health():
    """Test API health"""
    print("🏥 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"📊 Database chunks: {data['database_chunks']}")
            print(f"🚀 Smart features: {data['smart_features']}")
            print(f"🔧 Features: {data['features']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_chat_api(query):
    """Test chat API with a query"""
    print(f"\n💬 Testing query: '{query}'")
    try:
        payload = {
            "messages": [
                {"role": "user", "content": query}
            ]
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/chat", json=payload)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received in {response_time:.2f}s")
            print(f"📝 Answer length: {len(data['message'])} chars")
            print(f"📚 Sources: {len(data['sources'])}")
            print(f"🎯 Enhanced features: {data['enhanced_features']}")
            print(f"💬 Answer preview: {data['message'][:150]}...")
            return True
        else:
            print(f"❌ Chat API failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat API error: {e}")
        return False

def test_suggestions():
    """Test suggestions endpoint"""
    print("\n💡 Testing suggestions...")
    try:
        response = requests.get(f"{API_BASE}/suggestions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {len(data['suggestions'])} suggestions:")
            for i, suggestion in enumerate(data['suggestions'][:5]):
                print(f"  {i+1}. {suggestion}")
        else:
            print(f"❌ Suggestions failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Suggestions error: {e}")

def main():
    print("🧪 Testing Enhanced PTSP RAG System Integration")
    print("=" * 60)
    
    # Test health
    test_health()
    
    # Test suggestions
    test_suggestions()
    
    # Test relevant queries
    print("\n🎯 Testing RELEVANT queries:")
    relevant_queries = [
        "Apa itu DPMPTSP?",
        "Bagaimana cara mengurus izin usaha?",
        "Syarat investasi di Jawa Tengah"
    ]
    
    for query in relevant_queries:
        test_chat_api(query)
    
    # Test irrelevant queries
    print("\n❌ Testing IRRELEVANT queries:")
    irrelevant_queries = [
        "What is the weather today?",
        "Bitcoin price",
        "How to make pizza"
    ]
    
    for query in irrelevant_queries:
        test_chat_api(query)
    
    print("\n" + "=" * 60)
    print("🎉 Integration test completed!")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend: http://localhost:8001")
    print("📋 API Docs: http://localhost:8001/docs")

if __name__ == "__main__":
    main()
