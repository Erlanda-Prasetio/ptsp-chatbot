"""
Test MADAM Retrieval with 10s phase delays and 60s between questions.
Tests with 2 CSV files: retrieval_test_result.csv and old_dataset_retrieval_test_template.csv
"""
import csv
import time
from pathlib import Path
import sys
from typing import List, Dict, Any

sys.path.append('src')

from madam_hybrid_system import MadamHybridRAGSystem

# Test files
TEST_FILES = [
    "evaluation/retrieval_test_result.csv",
    "evaluation/old_dataset_retrieval_test_template.csv",
]

def load_queries_from_csv(filepath: str, limit: int = 2) -> List[Dict[str, str]]:
    """Load queries from CSV file."""
    queries = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                if idx >= limit:
                    break
                queries.append(row)
        print(f"✅ Loaded {len(queries)} queries from {filepath}")
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
    return queries

def test_madam_system(test_file: str, queries: List[Dict[str, str]], file_index: int) -> None:
    """Test MADAM system with queries from a file."""
    
    print(f"\n{'='*100}")
    print(f"🔬 TESTING FILE {file_index}: {test_file}")
    print(f"{'='*100}\n")
    
    try:
        print("🚀 Initializing MADAM Hybrid RAG System...")
        rag_system = MadamHybridRAGSystem()
        print("✅ MADAM system initialized!\n")
    except Exception as e:
        print(f"❌ Failed to initialize MADAM system: {e}")
        return
    
    results = []
    total_queries = len(queries)
    
    for query_idx, query_row in enumerate(queries, 1):
        query_text = query_row.get('question', query_row.get('Q', ''))
        query_id = query_row.get('query_id', query_row.get('id', f'q_{query_idx}'))
        category = query_row.get('category', 'Unknown')
        
        if not query_text:
            print(f"⚠️  Query {query_idx}/{total_queries}: Empty question text, skipping")
            continue
        
        print(f"\n{'─'*100}")
        print(f"📋 Query {query_idx}/{total_queries}: {query_id} [{category}]")
        print(f"Q: {query_text[:80]}...")
        print(f"{'─'*100}")
        
        query_start = time.time()
        
        try:
            result = rag_system.ask_with_fallback(query_text.strip())
            query_elapsed = time.time() - query_start
            
            search_method = result.get("enhanced_features", {}).get("search_method", "unknown")
            answer = result.get("answer", "")[:100]
            sources_count = result.get("total_sources", 0)
            
            print(f"✅ Query processed: {search_method}")
            print(f"   • Time: {query_elapsed:.2f}s")
            print(f"   • Sources: {sources_count}")
            print(f"   • Answer: {answer}...")
            
            results.append({
                "query_id": query_id,
                "question": query_text,
                "category": category,
                "search_method": search_method,
                "time_seconds": query_elapsed,
                "sources_retrieved": sources_count,
                "status": "success"
            })
            
        except Exception as e:
            query_elapsed = time.time() - query_start
            print(f"❌ Query failed: {str(e)[:100]}")
            
            results.append({
                "query_id": query_id,
                "question": query_text,
                "category": category,
                "search_method": "failed",
                "time_seconds": query_elapsed,
                "sources_retrieved": 0,
                "status": "error"
            })
    
    # Summary
    print(f"\n{'='*100}")
    print(f"📊 SUMMARY FOR FILE {file_index}: {test_file}")
    print(f"{'='*100}\n")
    
    successful = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "error")
    avg_time = sum(r["time_seconds"] for r in results) / len(results) if results else 0
    total_sources = sum(r["sources_retrieved"] for r in results)
    
    print(f"✅ Successful: {successful}/{total_queries}")
    print(f"❌ Failed: {failed}/{total_queries}")
    print(f"⏱️  Avg Time: {avg_time:.2f}s")
    print(f"📦 Total Sources: {total_sources}")
    
    # Method breakdown
    method_counts = {}
    for r in results:
        method = r["search_method"]
        method_counts[method] = method_counts.get(method, 0) + 1
    
    print(f"\n📈 Search Methods Used:")
    for method, count in method_counts.items():
        print(f"   • {method}: {count}")
    
    # Save results
    output_file = f"test_madam_delays_file{file_index}_results.csv"
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"\n💾 Results saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Failed to save results: {e}")

def main():
    """Main test function."""
    print("\n" + "="*100)
    print("🔬 MADAM RETRIEVAL TEST WITH DELAYS (10s between phases, 60s between questions)")
    print("="*100 + "\n")
    
    print("📁 Test Files:")
    for idx, file in enumerate(TEST_FILES, 1):
        file_path = Path(file)
        if file_path.exists():
            print(f"   {idx}. {file} ✅")
        else:
            print(f"   {idx}. {file} ❌ (not found)")
    
    print("\n⚙️  Testing Configuration:")
    print("   • Delay between phases: 10 seconds")
    print("   • Delay between questions: 60 seconds")
    print("   • Queries per file: 2")
    print("\n" + "="*100 + "\n")
    
    overall_start = time.time()
    
    for file_idx, test_file in enumerate(TEST_FILES, 1):
        if not Path(test_file).exists():
            print(f"⚠️  Skipping {test_file}: file not found")
            continue
        
        queries = load_queries_from_csv(test_file, limit=2)
        if queries:
            test_madam_system(test_file, queries, file_idx)
            
            # Gap between files
            if file_idx < len(TEST_FILES):
                print(f"\n⏳ 60 second gap before next file...")
                time.sleep(60)
    
    overall_elapsed = time.time() - overall_start
    
    print(f"\n{'='*100}")
    print(f"🎉 ALL TESTS COMPLETED")
    print(f"{'='*100}")
    print(f"Total time: {overall_elapsed:.2f}s ({overall_elapsed/60:.2f}m)")
    print(f"\n✅ Test files completed:")
    for idx, file in enumerate(TEST_FILES, 1):
        print(f"   {idx}. Results saved to: test_madam_delays_file{idx}_results.csv")

if __name__ == "__main__":
    main()
