import sys
sys.path.append('src')

from vector_store_supabase_rest import SupabaseRestVectorStore
from embed import embed_texts

def test_retrieval_quality():
    """Test retrieval quality with sample PTSP queries"""
    store = SupabaseRestVectorStore()
    
    test_queries = [
        "Bagaimana cara mengurus izin usaha?",
        "Prosedur PTSP untuk perizinan",
        "Syarat izin investasi",
        "Pelayanan terpadu satu pintu"
    ]
    
    print("🔍 Testing retrieval quality with PTSP queries...\n")
    
    for query in test_queries:
        print(f"Query: '{query}'")
        print("-" * 50)
        
        try:
            # Get query embedding
            query_embedding = embed_texts([query])[0]
            
            # Search for relevant chunks
            results = store.search(query_embedding, top_k=5)
            
            print(f"Found {len(results)} results:")
            
            for i, result in enumerate(results, 1):
                content = result.get('content', '')[:200]
                similarity = result.get('similarity', 0)
                metadata = result.get('metadata', {})
                source = metadata.get('source', 'Unknown')
                
                print(f"\n{i}. Similarity: {similarity:.3f}")
                print(f"   Source: {source}")
                print(f"   Content: {content}...")
                
                # Check if content is relevant to PTSP
                relevant_keywords = ['ptsp', 'izin', 'perizinan', 'pelayanan', 'terpadu', 'usaha']
                has_relevant = any(keyword in content.lower() for keyword in relevant_keywords)
                print(f"   PTSP Relevant: {'✅' if has_relevant else '❌'}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_retrieval_quality()