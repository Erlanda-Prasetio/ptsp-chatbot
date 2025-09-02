#!/usr/bin/env python3
"""
Test the improved RAG system
"""
from src.enhanced_rag import EnhancedRAG

def test_improved_rag():
    # Test DPMPTSP-specific queries with improved system
    rag = EnhancedRAG()
    
    print('🔍 Testing improved RAG system...')
    print()
    
    queries = [
        'apa itu dpmptsp',
        'layanan apa saja yang ada di dpmptsp',
        'bagaimana cara mengurus perizinan'
    ]
    
    for i, query in enumerate(queries, 1):
        print(f'{i}. Query: {query}')
        response = rag.ask(query)
        answer = response['answer']
        sources_count = len(response['sources'])
        response_time = response.get('response_time', 0)
        
        print(f'   Answer: {answer[:200]}...')
        print(f'   Sources: {sources_count} relevant documents')
        print(f'   Response time: {response_time:.2f}s')
        
        # Check if answer contains unwanted references
        if 'Dokumen' in answer or 'Data Source' in answer:
            print('   ⚠️  WARNING: Answer still contains document references!')
        else:
            print('   ✅ Answer is clean (no document references)')
        print()

if __name__ == "__main__":
    test_improved_rag()
