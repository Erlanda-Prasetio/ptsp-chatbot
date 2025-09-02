"""
Simple test script for Supabase RAG system
"""
import sys
import os
sys.path.append('src')

from vector_store_supabase_rest import SupabaseRestVectorStore
from embed import embed_texts
import requests
from dotenv import load_dotenv

load_dotenv()

def test_supabase_rag():
    print("🧪 Testing Supabase RAG System")
    print("=" * 40)
    
    # Test question
    question = "What data is available about employment in Central Java?"
    print(f"❓ Question: {question}")
    
    try:
        # Initialize Supabase store
        store = SupabaseRestVectorStore()
        count = store.get_count()
        print(f"📊 Database has {count} chunks")
        
        if count == 0:
            print("❌ No data found. Migration may have failed.")
            return
        
        # Get question embedding
        print("🔍 Getting question embedding...")
        question_embedding = embed_texts([question])[0]
        print(f"✅ Question embedding: {len(question_embedding)} dimensions")
        
        # Search for relevant chunks
        print("🔎 Searching for relevant information...")
        results = store.search(question_embedding, top_k=3)
        
        if results:
            print(f"✅ Found {len(results)} relevant chunks:")
            for i, result in enumerate(results, 1):
                content = result.get('content', '')[:100]
                metadata = result.get('metadata', {})
                source = metadata.get('source', 'Unknown')
                similarity = result.get('similarity', 'N/A')
                print(f"  {i}. [{source}] {content}... (similarity: {similarity})")
        else:
            print("❌ No relevant chunks found")
            
        # Test with a different question
        print("\n" + "=" * 40)
        question2 = "population data"
        print(f"❓ Question 2: {question2}")
        
        question2_embedding = embed_texts([question2])[0]
        results2 = store.search(question2_embedding, top_k=2)
        
        if results2:
            print(f"✅ Found {len(results2)} relevant chunks for question 2:")
            for i, result in enumerate(results2, 1):
                content = result.get('content', '')[:100]
                metadata = result.get('metadata', {})
                source = metadata.get('source', 'Unknown')
                print(f"  {i}. [{source}] {content}...")
        
        print("\n🎉 Supabase RAG system is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_supabase_rag()
