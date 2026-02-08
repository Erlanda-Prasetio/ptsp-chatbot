"""
Helper script to preview retrieved chunks for each question.
This helps you identify relevant_chunk_ids for ground truth.

Marks questions that use internet fallback (will be evaluated differently).

Usage:
    python evaluation/preview_chunks_for_questions.py --all
    python evaluation/preview_chunks_for_questions.py --question 1
"""

import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.hybrid_rag import HybridRAGSystem

# Initialize RAG system once
rag_system = None

def get_rag_system():
    """Get or initialize RAG system."""
    global rag_system
    if rag_system is None:
        rag_system = HybridRAGSystem()
    return rag_system


def preview_chunks_for_question(query_text, query_id, k=10):
    """
    Preview top K chunks for a question.
    
    Args:
        query_text: The question text
        query_id: Question ID (e.g., Q001)
        k: Number of chunks to retrieve
        
    Returns:
        dict with chunk_ids, uses_internet_fallback flag, and phase info
    """
    print(f"\n{'='*80}")
    print(f"[SEARCH] {query_id}: {query_text}")
    print(f"{'='*80}\n")
    
    try:
        # Add small delay before each query to avoid rate limits
        import time
        time.sleep(2)
        
        rag = get_rag_system()
        result = rag.ask_with_fallback(query_text, k=k)
        
        # Check which phase succeeded (from enhanced_features)
        enhanced = result.get('enhanced_features', {})
        search_method = enhanced.get('search_method', 'unknown')
        quality = enhanced.get('quality_score', 0.0)
        
        print(f" Search method: {search_method}")
        print(f"[STATS] Quality score: {quality:.2f}")
        
        # Determine if internet fallback was used
        uses_internet_fallback = (search_method == 'internet_fallback')
        
        if uses_internet_fallback:
            print(f" [WARN]  INTERNET FALLBACK USED")
            print(f"[INFO] This question will be evaluated with accuracy/response time only (no P/R/F1)")
        else:
            print(f"[OK] Used Supabase chunks (will calculate P/R/F1)")
        print()
        
        if not result.get('sources'):
            print("[FAIL] No chunks retrieved!\n")
            return {
                'chunk_ids': [],
                'suggested_relevant': [],
                'uses_internet_fallback': True,
                'phase': search_method,
                'quality': quality
            }
        
        sources = result['sources']
        
        # Internet sources have 'text' field and metadata with 'source' URL
        # Supabase sources have 'content' or 'text' field and metadata with 'chunk_id'
        supabase_sources = []
        for s in sources:
            metadata = s.get('metadata', {})
            # Check if it has a chunk_id in metadata (Supabase source)
            if 'chunk_id' in metadata or ('source' in metadata and 'chunk' in str(metadata.get('source', ''))):
                supabase_sources.append(s)
        
        if not supabase_sources:
            print("[WARN]  No Supabase chunks found - system used internet fallback")
            print("[WARN]  This question will be marked as 'uses_internet_fallback=TRUE'\n")
            return {
                'chunk_ids': [],
                'suggested_relevant': [],
                'uses_internet_fallback': True,
                'phase': search_method,
                'quality': quality
            }
        
        print(f"[STATS] Retrieved {len(supabase_sources)} Supabase chunks:\n")
        
        chunk_ids = []
        for i, chunk in enumerate(supabase_sources, 1):
            metadata = chunk.get('metadata', {})
            chunk_id = metadata.get('chunk_id') or metadata.get('id')
            similarity = metadata.get('similarity', metadata.get('relevance_score', 0.0))
            text = chunk.get('text', chunk.get('content', ''))
            
            if chunk_id:
                chunk_ids.append(chunk_id)
            
            # Color code by similarity
            if similarity >= 0.75:
                relevance = "[OK] HIGH"
            elif similarity >= 0.65:
                relevance = "🟡 GOOD"
            elif similarity >= 0.50:
                relevance = "🟠 LOW"
            else:
                relevance = " VERY LOW"
            
            print(f"[{i}] {relevance} | Chunk ID: {chunk_id} | Similarity: {similarity:.3f}")
            print(f"    Text: {text[:200]}...")
            print()
        
        # Suggest only high-quality chunks
        suggested = [cid for i, cid in enumerate(chunk_ids) 
                    if i < len(supabase_sources) and supabase_sources[i].get('similarity', 0) >= 0.65]
        
        if suggested:
            print(f"[INFO] Suggested relevant_chunk_ids (similarity ≥ 0.65): {','.join(map(str, suggested))}")
        else:
            print(f"[WARN]  No high-quality chunks (similarity ≥ 0.65)")
            print(f"[INFO] All chunk IDs: {','.join(map(str, chunk_ids[:5]))}")
        
        print(f"{'='*80}\n")
        
        return {
            'chunk_ids': chunk_ids,
            'suggested_relevant': suggested if suggested else chunk_ids[:5],
            'uses_internet_fallback': uses_internet_fallback,
            'phase': search_method,
            'quality': quality
        }
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return {
            'chunk_ids': [],
            'suggested_relevant': [],
            'uses_internet_fallback': True,
            'phase': 'error',
            'quality': 0.0
        }


def preview_all_questions(limit=None):
    """Preview chunks for all questions in the dataset."""
    
    # Load questions
    sample_file = Path(__file__).parent / "sample_50_balanced.json"
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    queries = data['queries']
    
    if limit:
        queries = queries[:limit]
    
    print(f" Previewing chunks for {len(queries)} questions...")
    print("This will help you identify relevant_chunk_ids for ground truth.\n")
    
    # Ask user
    response = input(f"Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    results = {}
    internet_fallback_questions = []
    
    for i, q in enumerate(queries, 1):
        query_id = q['eval_id']
        query_text = q['query']
        
        print(f"\n\n{'#'*80}")
        print(f"QUESTION {i}/{len(queries)}")
        print(f"{'#'*80}")
        
        preview_result = preview_chunks_for_question(query_text, query_id, k=10)
        
        results[query_id] = {
            'query': query_text,
            'retrieved_chunk_ids': preview_result['chunk_ids'],
            'suggested_relevant': preview_result['suggested_relevant'],
            'uses_internet_fallback': preview_result['uses_internet_fallback'],
            'search_phase': preview_result['phase'],
            'quality_score': preview_result['quality']
        }
        
        # Track internet fallback questions
        if preview_result['uses_internet_fallback']:
            internet_fallback_questions.append({
                'id': query_id,
                'query': query_text,
                'phase': preview_result['phase']
            })
        
        # Add delay to avoid rate limits (wait 3 seconds between questions)
        if i < len(queries):
            print(f"⏳ Waiting 3 seconds to avoid rate limits...")
            import time
            time.sleep(3)
        
        # Pause every 5 questions
        if i % 5 == 0 and i < len(queries):
            response = input("\n⏸  Pause. Press ENTER to continue, or 'q' to quit: ").strip().lower()
            if response == 'q':
                print("Stopped early.")
                break
    
    # Save results
    output_file = Path(__file__).parent / "chunk_preview_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n{'='*80}")
    print(f"[OK] Results saved to: {output_file}")
    print(f"{'='*80}\n")
    
    # Summary
    total = len(results)
    with_chunks = sum(1 for r in results.values() if not r['uses_internet_fallback'])
    with_internet = len(internet_fallback_questions)
    
    print(f"[STATS] SUMMARY:")
    print(f"  Total questions: {total}")
    print(f"  With Supabase chunks: {with_chunks} ({with_chunks/total*100:.1f}%)")
    print(f"  Uses internet fallback: {with_internet} ({with_internet/total*100:.1f}%)")
    
    if internet_fallback_questions:
        print(f"\n Questions that use INTERNET FALLBACK:")
        print(f"{'='*80}")
        for q in internet_fallback_questions:
            print(f"  {q['id']}: {q['query'][:70]}...")
        print(f"{'='*80}")
        print(f"\n[INFO] For these {with_internet} questions in CSV:")
        print(f"   1. Leave 'relevant_chunk_ids' column EMPTY")
        print(f"   2. Set 'uses_internet_fallback' column to TRUE")
        print(f"   3. Still fill 'ground_truth' for accuracy checking")
        print(f"   4. These will be evaluated with ACCURACY & RESPONSE TIME only (no P/R/F1)")
    
    print(f"\n Next step: Use {output_file} to fill ground_truth_template.csv")


def preview_single_question(question_number=None):
    """Preview chunks for a single question by number."""
    
    # Load questions
    sample_file = Path(__file__).parent / "sample_50_balanced.json"
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    queries = data['queries']
    
    if question_number is None:
        # Show list
        print("\n 50 Questions:")
        print("="*80)
        for i, q in enumerate(queries, 1):
            print(f"{i:2d}. [{q['eval_id']}] {q['query'][:70]}...")
        print("="*80)
        
        question_number = int(input("\nEnter question number (1-50): ").strip())
    
    if 1 <= question_number <= len(queries):
        q = queries[question_number - 1]
        preview_chunks_for_question(q['query'], q['eval_id'], k=10)
    else:
        print(f"[FAIL] Invalid question number. Must be 1-{len(queries)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Preview chunks for ground truth setup")
    parser.add_argument('--all', action='store_true', help='Preview all 50 questions')
    parser.add_argument('--limit', type=int, help='Limit number of questions to preview')
    parser.add_argument('--question', type=int, help='Preview single question by number (1-50)')
    
    args = parser.parse_args()
    
    if args.all:
        preview_all_questions(limit=args.limit)
    elif args.question:
        preview_single_question(question_number=args.question)
    else:
        # Interactive mode
        print("\n" + "="*80)
        print(" CHUNK PREVIEW TOOL - Ground Truth Helper")
        print("="*80)
        print("\nOptions:")
        print("1. Preview single question")
        print("2. Preview all 50 questions (saves to chunk_preview_results.json)")
        print("3. Exit")
        print()
        
        choice = input("Choose (1-3): ").strip()
        
        if choice == '1':
            preview_single_question()
        elif choice == '2':
            preview_all_questions()
        else:
            print("Exiting.")
