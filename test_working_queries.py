#!/usr/bin/env python3
"""
Mock questions that work well with the PTSP RAG system
These are proven queries that return good results from our Indonesian dataset
"""

import sys
sys.path.append('src')

from vector_store import store
from embed import embed_texts
from ask import build_context, query_llm
import time

# Successful queries from our testing
WORKING_QUERIES = [
    {
        "id": "employment_kendal",
        "question": "Kabupaten Kendal tenaga kerja",
        "category": "Ketenagakerjaan",
        "expected_type": "employment_data"
    },
    {
        "id": "poverty_percentage", 
        "question": "persentase penduduk miskin",
        "category": "Kemiskinan",
        "expected_type": "poverty_statistics"
    },
    {
        "id": "employment_brebes",
        "question": "Kabupaten Brebes penempatan 2023", 
        "category": "Ketenagakerjaan",
        "expected_type": "employment_placement"
    },
    {
        "id": "employment_general",
        "question": "data tenaga kerja Jawa Tengah",
        "category": "Ketenagakerjaan", 
        "expected_type": "employment_overview"
    },
    {
        "id": "investment_projection",
        "question": "proyeksi investasi Jawa Tengah",
        "category": "Investasi",
        "expected_type": "investment_forecast"
    },
    {
        "id": "regional_statistics",
        "question": "statistik Kabupaten Temanggung",
        "category": "Statistik Daerah",
        "expected_type": "regional_data"
    },
    {
        "id": "ptsp_services",
        "question": "layanan PTSP perizinan",
        "category": "Pelayanan",
        "expected_type": "service_information"
    },
    {
        "id": "population_data",
        "question": "data kependudukan Jawa Tengah",
        "category": "Kependudukan",
        "expected_type": "population_statistics"
    }
]

def test_working_queries():
    """Test all known working queries"""
    print("🚀 Testing Known Working Queries")
    print("=" * 60)
    
    # Load the local vector store
    store.load()
    if store.embeddings is None:
        print("❌ Vector store is empty. Need to run ingest first.")
        return
    
    print(f"✅ Vector store loaded with {len(store.texts)} chunks\n")
    
    results = []
    
    for i, query_info in enumerate(WORKING_QUERIES, 1):
        question = query_info["question"]
        category = query_info["category"]
        
        print(f"🔍 Test {i}: {question}")
        print(f"📂 Category: {category}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            
            # Embed the query
            q_emb = embed_texts([question])[0]
            
            # Search for similar chunks
            hits = store.search(q_emb, k=8)
            
            # Build context and query LLM
            context = build_context(hits)
            answer = query_llm(question, context)
            
            response_time = time.time() - start_time
            
            print(f"⏱️ Response time: {response_time:.2f}s")
            print(f"📊 Found {len(hits)} relevant chunks")
            print(f"🤖 Answer: {answer}")
            print()
            
            results.append({
                "question": question,
                "category": category,
                "answer": answer,
                "response_time": response_time,
                "chunks_found": len(hits),
                "success": "I don't know" not in answer
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "question": question,
                "category": category,
                "answer": f"Error: {e}",
                "response_time": 0,
                "chunks_found": 0,
                "success": False
            })
            print()
    
    # Summary
    print("\n" + "="*60)
    print("📈 Test Results Summary")
    print("="*60)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    avg_time = sum(r["response_time"] for r in results if r["response_time"] > 0) / max(1, successful)
    
    print(f"✅ Success rate: {successful}/{total} ({successful/total*100:.1f}%)")
    print(f"⏱️ Average response time: {avg_time:.2f}s")
    print(f"📊 Total test queries: {total}")
    print()
    
    # Show successful queries for UI integration
    print("🎯 Successful queries for UI integration:")
    for r in results:
        if r["success"]:
            print(f"   • {r['question']} ({r['category']})")
    
    return results

if __name__ == "__main__":
    test_working_queries()
