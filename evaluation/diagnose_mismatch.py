"""Diagnose why P/R/F1 are all 0.000."""

import json
from pathlib import Path

def diagnose_retrieval_mismatch():
    """Check what's wrong with retrieval metrics."""
    
    # Load results
    results_file = Path('evaluation/raw_results/baseline_old_dataset.json')
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data['results']
    
    print("\n" + "="*80)
    print("[SEARCH] DIAGNOSING RETRIEVAL MISMATCH")
    print("="*80)
    
    # Check first few questions in detail
    for i, r in enumerate(results[:5], 1):
        query_text = r.get('query_text') or r.get('query', 'N/A')
        print(f"\n[Q{i:02d}] {r['eval_id']}: {query_text[:60]}...")
        
        ground_truth_ids = r.get('relevant_chunks', [])
        retrieved_items = r.get('retrieved_chunks', [])
        
        print(f"   Ground Truth Chunk IDs: {ground_truth_ids}")
        print(f"   Retrieved Items:        {retrieved_items[:5]}... (top 5 of {len(retrieved_items)})")
        
        # Check types
        if retrieved_items:
            print(f"   Retrieved type: {type(retrieved_items[0])}")
        if ground_truth_ids:
            print(f"   Ground truth type: {type(ground_truth_ids[0])}")
        
        if ground_truth_ids and retrieved_items:
            overlap = set(ground_truth_ids) & set(retrieved_items)
            print(f"   Overlap: {len(overlap)} chunks")
            if overlap:
                print(f"   Matching IDs: {list(overlap)}")
        
        precision = r.get('precision', 'N/A')
        recall = r.get('recall', 'N/A')
        f1 = r.get('f1_score', 'N/A')
        print(f"   Metrics: P={precision}, R={recall}, F1={f1}")
    
    # Check if ground truth IDs exist
    print(f"\n{'='*80}")
    print("[STATS] Data Status:")
    print("="*80)
    
    has_ground_truth = sum(1 for r in results if r.get('relevant_chunks'))
    has_retrieved = sum(1 for r in results if r.get('retrieved_chunks'))
    
    print(f"Questions with ground truth chunk IDs: {has_ground_truth}/{len(results)}")
    print(f"Questions with retrieved items:        {has_retrieved}/{len(results)}")
    
    if has_ground_truth == 0:
        print("\n[WARN]  PROBLEM: No ground truth chunk IDs found!")
        print("   This means the import from CSV didn't work properly.")
        print("   Check: evaluation/sample_50_balanced.json for 'relevant_chunks' field")
    
    if has_retrieved == 0:
        print("\n[WARN]  PROBLEM: No retrieved items found!")
        print("   The API isn't returning any sources.")
        return
    
    # Analyze type mismatch
    print(f"\n{'='*80}")
    print("[SEARCH] Type Mismatch Analysis:")
    print("="*80)
    
    for r in results[:5]:
        retrieved = r.get('retrieved_chunks', [])
        relevant = r.get('relevant_chunks', [])
        
        if retrieved and relevant:
            print(f"\n{r['eval_id']}:")
            print(f"  Retrieved[0]: {repr(retrieved[0])} (type: {type(retrieved[0]).__name__})")
            print(f"  Relevant[0]:  {repr(relevant[0])} (type: {type(relevant[0]).__name__})")
            
            # Try comparison
            if isinstance(retrieved[0], str) and isinstance(relevant[0], int):
                print(f"  [FAIL] TYPE MISMATCH: Can't compare strings to integers!")
            elif retrieved[0] == relevant[0]:
                print(f"  [OK] Match found")
            else:
                print(f"  [WARN]  No match")
    
    # Summary
    print(f"\n{'='*80}")
    print(" DIAGNOSIS SUMMARY:")
    print("="*80)
    
    zero_metrics = sum(1 for r in results if r.get('precision') == 0.0 and r.get('recall') == 0.0)
    print(f"Questions with P=0, R=0: {zero_metrics}/{len(results)} ({zero_metrics/len(results)*100:.1f}%)")
    
    # Check if it's a type mismatch issue
    type_mismatches = 0
    for r in results:
        retrieved = r.get('retrieved_chunks', [])
        relevant = r.get('relevant_chunks', [])
        if retrieved and relevant:
            if isinstance(retrieved[0], str) and isinstance(relevant[0], int):
                type_mismatches += 1
    
    if type_mismatches > 0:
        print(f"\n[FAIL] TYPE MISMATCH DETECTED in {type_mismatches} questions!")
        print("   Problem: API returns filenames (strings), but ground truth has chunk IDs (integers)")
        print("   Solution: Modify src/smart_enhanced_rag.py to include chunk_id in sources")
        print("   Then update evaluation/run_balanced_evaluation.py to extract integer chunk IDs")
    else:
        print(f"\n[OK] No type mismatch detected")
        print("   If metrics are still zero, check retrieval quality or chunk ID mapping")
    
    print(f"\n{'='*80}\n")

if __name__ == '__main__':
    diagnose_retrieval_mismatch()
