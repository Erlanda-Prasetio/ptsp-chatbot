#!/usr/bin/env python3
"""Quick script to verify new chunks are searchable in Supabase."""
import sys
sys.path.append('src')

from vector_store_supabase_rest import SupabaseRestVectorStore
from embed import embed_texts

def main():
    print("🔍 Testing new chunk search...")
    
    # Initialize store
    store = SupabaseRestVectorStore()
    
    # Test query from new OSS data
    test_query = "Bagaimana cara ubah NPWP?"
    print(f"\nQuery: {test_query}")
    
    # Embed and search
    query_embedding = embed_texts([test_query])[0]
    results = store.search(query_embedding, top_k=5)
    
    print(f"\n✅ Search works! Found {len(results)} results")
    
    # Show first result
    if results:
        print(f"\n📄 Top result preview:")
        print(f"Content: {results[0]['content'][:200]}...")
        print(f"Similarity: {results[0]['similarity']:.4f}")
        if 'metadata' in results[0]:
            print(f"Source: {results[0]['metadata'].get('source', 'N/A')}")
    
    print("\n✅ Verification complete! New chunks are searchable.")

if __name__ == '__main__':
    main()
