#!/usr/bin/env python3
"""
Test Indonesian language capabilities
"""

from enhanced_rag import EnhancedRAG

def test_indonesian_query(rag, query):
    print(f'🔍 Query: {query}')
    try:
        response = rag.ask(query, top_k=5)
        
        print(f'📄 Found {len(response.get("documents", []))} documents')
        
        for i, doc in enumerate(response.get("documents", [])[:3]):
            content = doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content']
            print(f'{i+1}. Source: {doc.get("source", "Unknown")}')
            print(f'   Content: {content}')
            print()
        
        print(f'🤖 Answer: {response.get("answer", "No answer generated")}')
        print('='*80)
        
    except Exception as e:
        print(f'❌ Error: {e}')
        print('='*80)

if __name__ == "__main__":
    print("🚀 Initializing Enhanced RAG system...")
    rag = EnhancedRAG()
    
    # Test Indonesian language queries
    queries = [
        "apa itu dpmptsp?",
        "ada apa aja di dpmptsp?",
        "bagaimana cara mengurus perizinan di jawa tengah?",
        "apa saja layanan yang tersedia di dpmptsp jawa tengah?"
    ]
    
    for query in queries:
        test_indonesian_query(rag, query)
