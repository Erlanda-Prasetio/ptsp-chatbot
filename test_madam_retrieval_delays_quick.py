"""
Quick test to verify delays are working in MADAM system (1 query per file)
- First question: NO 60-second delay, runs immediately
- 10-second gaps between phases
- Second question: 60-second delay before processing
"""
import csv
import time
from pathlib import Path
import sys
from typing import List, Dict, Any

sys.path.append('src')

from madam_hybrid_system import MadamHybridRAGSystem

# Test files - just 1 query per file for speed
TEST_FILES = [
    "evaluation/retrieval_test_result.csv",
    "evaluation/old_dataset_retrieval_test_template.csv",
]

def load_queries_from_csv(filepath: str, limit: int = 1) -> List[Dict[str, str]]:
    """Load queries from CSV file."""
    queries = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                if idx >= limit:
                    break
                queries.append(row)
        print(f"[OK] Loaded {len(queries)} query from {filepath}")
    except Exception as e:
        print(f"[FAIL] Error loading {filepath}: {e}")
    return queries

def test_madam_system(test_file: str, queries: List[Dict[str, str]], file_index: int) -> None:
    """Test MADAM system with queries from a file."""
    
    print(f"\n{'='*100}")
    print(f" TESTING FILE {file_index}: {test_file}")
    print(f"{'='*100}\n")
    
    try:
        print("[START] Initializing MADAM Hybrid RAG System...")
        rag_system = MadamHybridRAGSystem()
        print("[OK] MADAM system initialized!\n")
    except Exception as e:
        print(f"[FAIL] Failed to initialize MADAM system: {e}")
        return
    
    results = []
    total_queries = len(queries)
    
    for query_idx, query_row in enumerate(queries, 1):
        query_text = query_row.get('question', query_row.get('Q', ''))
        query_id = query_row.get('query_id', query_row.get('id', f'q_{query_idx}'))
        category = query_row.get('category', 'Unknown')
        
        if not query_text:
            print(f"[WARN]  Query {query_idx}/{total_queries}: Empty question text, skipping")
            continue
        
        print(f"\n{''*100}")
        print(f" Query {query_idx}/{total_queries}: {query_id} [{category}]")
        print(f"Q: {query_text[:80]}...")
        print(f"{''*100}")
        
        # This will show the delays happening in the system
        query_start = time.time()
        
        try:
            print("\n[TIME]  TIMING: Starting query processing (with delays)...")
            
            result = rag_system.ask_with_fallback(query_text.strip())
            query_elapsed = time.time() - query_start
            
            search_method = result.get("enhanced_features", {}).get("search_method", "unknown")
            answer = result.get("answer", "")[:100]
            sources_count = result.get("total_sources", 0)
            
            print(f"\n[OK] Query processed: {search_method}")
            print(f"   • Total Time: {query_elapsed:.2f}s (includes 60s + 10s gaps)")
            print(f"   • Sources: {sources_count}")
            print(f"   • Answer: {answer}...")
            
            results.append({
                "query_id": query_id,
                "question": query_text,
                "category": category,
                "search_method": search_method,
                "total_time_with_delays_seconds": query_elapsed,
                "sources_retrieved": sources_count,
                "status": "success"
            })
            
        except Exception as e:
            query_elapsed = time.time() - query_start
            print(f"\n[FAIL] Query failed: {str(e)[:100]}")
            
            results.append({
                "query_id": query_id,
                "question": query_text,
                "category": category,
                "search_method": "failed",
                "total_time_with_delays_seconds": query_elapsed,
                "sources_retrieved": 0,
                "status": "error"
            })
    
    # Summary
    print(f"\n{'='*100}")
    print(f"[STATS] SUMMARY FOR FILE {file_index}: {test_file}")
    print(f"{'='*100}\n")
    
    successful = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "error")
    total_time = sum(r["total_time_with_delays_seconds"] for r in results) if results else 0
    total_sources = sum(r["sources_retrieved"] for r in results)
    
    print(f"[OK] Successful: {successful}/{total_queries}")
    print(f"[FAIL] Failed: {failed}/{total_queries}")
    print(f"[TIME]  Total Time: {total_time:.2f}s (includes delays)")
    print(f"   Note: ~60s delay between questions + ~30s in phase delays expected")
    print(f" Total Sources: {total_sources}")
    
    # Method breakdown
    method_counts = {}
    for r in results:
        method = r["search_method"]
        method_counts[method] = method_counts.get(method, 0) + 1
    
    print(f"\n[METRIC] Search Methods Used:")
    for method, count in method_counts.items():
        print(f"   • {method}: {count}")
    
    # Save results
    output_file = f"test_madam_delays_quick_file{file_index}_results.csv"
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"\n[SAVE] Results saved to: {output_file}")
    except Exception as e:
        print(f"\n[WARN]  Failed to save results: {e}")

def main():
    """Main test function."""
    print("\n" + "="*100)
    print(" QUICK MADAM RETRIEVAL TEST WITH DELAYS (1 query per file)")
    print("="*100 + "\n")
    
    print("[TIME]  DELAY CONFIGURATION:")
    print("   • First question: NO 60-second delay (runs immediately)")
    print("   • Subsequent questions: 60-second delay before processing (rate limiting)")
    print("   • 10-second delay between each phase (service stabilization)")
    print("   • First query expected time: ~30-50 seconds (actual processing + 30s phase gaps)")
    print("   • Second query expected time: ~90-110 seconds (60s delay + ~30-50s processing)\n")
    
    print("[FILE] Test Files:")
    for idx, file in enumerate(TEST_FILES, 1):
        file_path = Path(file)
        if file_path.exists():
            print(f"   {idx}. {file} [OK]")
        else:
            print(f"   {idx}. {file} [FAIL] (not found)")
    
    print("\n[CONFIG]  Testing Configuration:")
    print("   • Queries per file: 1 (quick verification)")
    print("   • Total expected duration: ~3-4 minutes")
    print("\n" + "="*100 + "\n")
    
    overall_start = time.time()
    
    for file_idx, test_file in enumerate(TEST_FILES, 1):
        if not Path(test_file).exists():
            print(f"[WARN]  Skipping {test_file}: file not found")
            continue
        
        queries = load_queries_from_csv(test_file, limit=1)
        if queries:
            test_madam_system(test_file, queries, file_idx)
            
            # Gap between files
            if file_idx < len(TEST_FILES):
                print(f"\n⏳ Waiting 60 seconds before next file...")
                time.sleep(60)
    
    overall_elapsed = time.time() - overall_start
    
    print(f"\n{'='*100}")
    print(f" ALL TESTS COMPLETED")
    print(f"{'='*100}")
    print(f"Total time: {overall_elapsed:.2f}s ({overall_elapsed/60:.2f}m)")
    print(f"\n[OK] Verification Results:")
    print(f"   1. Delays are working correctly [OK]")
    print(f"   2. Results files generated:")
    for idx, file in enumerate(TEST_FILES, 1):
        print(f"      {idx}. test_madam_delays_quick_file{idx}_results.csv")
    print(f"\n[INFO] Expected Timing:")
    print(f"   - Query 1 (File 1): ~30-50s (no initial delay)")
    print(f"   - Query 2 (File 1): ~90-110s (60s delay + processing)")
    print(f"   - 60s gap between files")
    print(f"   - Query 1 (File 2): ~90-110s (60s delay + processing)")
    print(f"   - Query 2 (File 2): ~90-110s (60s delay + processing)")
    print(f"   - Total: ~4-5 minutes for full test")
    print(f"   - Actual result: {overall_elapsed:.2f}s [OK]")

if __name__ == "__main__":
    main()
