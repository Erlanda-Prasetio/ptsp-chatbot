#!/usr/bin/env python3
"""
Test the vector search directly
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from src.vector_store_supabase_rest import SupabaseRestVectorStore

def main():
    print("🔍 Testing vector search")
    
    # Initialize model and vector store
    model = SentenceTransformer('all-MiniLM-L6-v2')
    vs = SupabaseRestVectorStore()
    
    # Test query
    query = "cara mengurus izin usaha di PTSP"
    query_embedding = model.encode(query)
    
    print(f"🔍 Query: {query}")
    print(f"📊 Query embedding shape: {query_embedding.shape}")
    
    # Try search
    results = vs.search(query_embedding, top_k=3)
    
    print(f"📋 Results: {len(results)}")
    for i, result in enumerate(results):
        print(f"  {i+1}. Content: {result.get('content', '')[:100]}...")
        print(f"     Similarity: {result.get('similarity', 'unknown')}")
        print()

if __name__ == "__main__":
    main()