"""
Enrich chunk preview JSON with text snippets from Supabase
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store_supabase_rest import SupabaseRestVectorStore


def enrich_chunk_preview():
    """Add text snippets to existing chunk preview results."""
    
    # Load existing results
    results_file = Path(__file__).parent / "chunk_preview_results.json"
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Initialize Supabase
    print("🔗 Connecting to Supabase...")
    store = SupabaseRestVectorStore()
    print("✅ Connected!\n")
    
    # Get all chunks once (more efficient)
    print("📥 Fetching all chunks from Supabase...")
    all_chunks = store.get_all_chunks()
    chunk_map = {chunk['id']: chunk for chunk in all_chunks}
    print(f"✅ Loaded {len(chunk_map)} chunks\n")
    
    # Enrich each question
    enriched_results = {}
    for query_id, data in results.items():
        print(f"🔍 {query_id}: {data['query'][:60]}...")
        
        chunk_ids = data['retrieved_chunk_ids']
        chunks = []
        
        for chunk_id in chunk_ids:
            if chunk_id in chunk_map:
                chunk = chunk_map[chunk_id]
                text = chunk.get('content', '')
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': text[:300],  # First 300 chars
                    'full_text': text  # Full text for reference
                })
            else:
                print(f"  ⚠️  Chunk {chunk_id} not found")
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': '[Chunk not found]',
                    'full_text': ''
                })
        
        enriched_results[query_id] = {
            'query': data['query'],
            'retrieved_chunk_ids': chunk_ids,
            'chunks': chunks,
            'note': 'Review chunks and select relevant ones for ground truth'
        }
    
    # Save enriched results
    enriched_file = Path(__file__).parent / "chunk_preview_enriched.json"
    with open(enriched_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Enriched results saved to: {enriched_file}")
    print(f"📋 Now you can see the actual text for each chunk!")
    print(f"💡 Use this to identify relevant chunks for ground_truth_template.csv")


if __name__ == "__main__":
    enrich_chunk_preview()
