"""
Simple chunk preview - just retrieval, no LLM calls
Helps identify relevant_chunk_ids for ground truth
"""

import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.smart_enhanced_rag import SmartEnhancedRAG


def preview_chunks(query_text, query_id, k=10):
    """Preview top K chunks for a question (retrieval only)."""
    
    print(f"\n{'='*80}")
    print(f"🔍 {query_id}: {query_text}")
    print(f"{'='*80}\n")
    
    try:
        # Initialize RAG (only once)
        if not hasattr(preview_chunks, 'rag'):
            print("🚀 Initializing RAG system...")
            preview_chunks.rag = SmartEnhancedRAG()
            print("✅ Ready!\n")
        
        rag = preview_chunks.rag
        
        # Just retrieve chunks using vector store directly
        from src.embed import embed_texts
        
        query_embedding = embed_texts([query_text])[0]
        results = rag.store.search(query_embedding, top_k=k)
        
        if not results:
            print("❌ No chunks retrieved!\n")
            return []
        
        print(f"📊 Retrieved {len(results)} chunks:\n")
        
        chunk_ids = []
        chunk_details = []
        for i, result in enumerate(results, 1):
            chunk_id = result.get('id') or result.get('chunk_id')
            similarity = result.get('similarity', 0.0)
            text = result.get('text', result.get('content', ''))
            
            chunk_ids.append(chunk_id)
            chunk_details.append({
                'chunk_id': chunk_id,
                'similarity': round(similarity, 3),
                'text': text[:300]  # Store first 300 chars for review
            })
            
            # Color code by similarity
            if similarity >= 0.7:
                marker = "🟢"  # High relevance
            elif similarity >= 0.5:
                marker = "🟡"  # Medium relevance
            else:
                marker = "🔴"  # Low relevance
            
            print(f"{marker} [{i}] Chunk ID: {chunk_id} | Similarity: {similarity:.3f}")
            print(f"    Text: {text[:150]}...")
            print()
        
        # Suggest relevant chunks (similarity >= 0.5)
        relevant = [str(cid) for cid, res in zip(chunk_ids, results) if res.get('similarity', 0) >= 0.5]
        
        if relevant:
            print(f"💡 Suggested relevant_chunk_ids (≥0.5): {','.join(relevant)}")
        else:
            print(f"⚠️  Low similarity scores - might need better chunks in database")
        
        print(f"{'='*80}\n")
        
        return chunk_ids, chunk_details
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return [], []


def preview_all(limit=None):
    """Preview chunks for all questions."""
    
    sample_file = Path(__file__).parent / "sample_50_balanced.json"
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    queries = data['queries']
    if limit:
        queries = queries[:limit]
    
    print(f"\n📝 Previewing chunks for {len(queries)} questions...\n")
    
    results = {}
    
    for i, q in enumerate(queries, 1):
        query_id = q['eval_id']
        query_text = q['query']
        
        print(f"\n{'#'*80}")
        print(f"QUESTION {i}/{len(queries)}")
        print(f"{'#'*80}")
        
        chunk_ids, chunk_details = preview_chunks(query_text, query_id, k=10)
        
        results[query_id] = {
            'query': query_text,
            'retrieved_chunk_ids': chunk_ids,
            'chunks': chunk_details,
            'suggested_relevant': [c['chunk_id'] for c in chunk_details if c['similarity'] >= 0.5]
        }
        
        # Pause every 10 questions
        if i % 10 == 0 and i < len(queries):
            response = input("\n⏸️  Pause. Press ENTER to continue, or 'q' to quit: ").strip().lower()
            if response == 'q':
                print("Stopped.")
                break
    
    # Save results
    output_file = Path(__file__).parent / "chunk_preview_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n✅ Results saved to: {output_file}")
    print(f"📋 Use these chunk IDs to fill 'relevant_chunk_ids' in ground_truth_template.csv")


def preview_single(question_number=None):
    """Preview chunks for a single question."""
    
    sample_file = Path(__file__).parent / "sample_50_balanced.json"
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    queries = data['queries']
    
    if question_number is None:
        print("\n📝 50 Questions:")
        print("="*80)
        for i, q in enumerate(queries, 1):
            print(f"{i:2d}. [{q['eval_id']}] {q['query'][:70]}...")
        print("="*80)
        
        question_number = int(input("\nEnter question number (1-50): ").strip())
    
    if 1 <= question_number <= len(queries):
        q = queries[question_number - 1]
        chunk_ids, chunk_details = preview_chunks(q['query'], q['eval_id'], k=10)
    else:
        print(f"❌ Invalid question number. Must be 1-{len(queries)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Preview chunks for ground truth setup")
    parser.add_argument('--all', action='store_true', help='Preview all 50 questions')
    parser.add_argument('--limit', type=int, help='Limit number of questions')
    parser.add_argument('--question', type=int, help='Preview single question (1-50)')
    
    args = parser.parse_args()
    
    if args.all:
        preview_all(limit=args.limit)
    elif args.question:
        preview_single(question_number=args.question)
    else:
        # Interactive mode
        print("\n" + "="*80)
        print("📋 CHUNK PREVIEW TOOL - Ground Truth Helper")
        print("="*80)
        print("\nOptions:")
        print("1. Preview single question")
        print("2. Preview all 50 questions (saves to chunk_preview_results.json)")
        print("3. Exit")
        print()
        
        choice = input("Choose (1-3): ").strip()
        
        if choice == '1':
            preview_single()
        elif choice == '2':
            preview_all()
        else:
            print("Exiting.")
