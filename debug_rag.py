import sys
sys.path.append('src')

from vector_store import store
from embed import embed_texts
from ask import build_context, query_llm
import json

def debug_rag_query(question):
    """Debug RAG query to see what context is being used"""
    print(f"🔍 Debug Query: {question}")
    print("=" * 60)
    
    # Load the local vector store
    store.load()
    if store.embeddings is None:
        print("❌ Vector store is empty.")
        return
    
    # Embed the query
    q_emb = embed_texts([question])[0]
    
    # Search for similar chunks
    hits = store.search(q_emb, k=8)
    
    print(f"📊 Found {len(hits)} results:")
    for i, hit in enumerate(hits):
        score = hit.get('score', 0)
        source = hit.get('meta', {}).get('source', 'Unknown')
        text_preview = hit.get('text', '')[:100] + "..."
        print(f"  {i+1}. Score: {score:.3f} | Source: {source}")
        print(f"     Preview: {text_preview}")
        print()
    
    # Build context
    context = build_context(hits)
    print(f"📄 Context length: {len(context)} characters")
    print("📄 Context preview:")
    print(context[:1000] + "...\n")
    
    # Query LLM
    try:
        answer = query_llm(question, context)
        print(f"🤖 LLM Answer: {answer}")
    except Exception as e:
        print(f"❌ LLM Error: {e}")

if __name__ == "__main__":
    # Test a few Indonesian queries
    queries = [
        "Bagaimana proyeksi investasi Jawa Tengah tahun 2023?",
        "data tenaga kerja Jawa Tengah",
        "jumlah wisatawan Jawa Tengah"
    ]
    
    for query in queries:
        debug_rag_query(query)
        print("\n" + "="*80 + "\n")
