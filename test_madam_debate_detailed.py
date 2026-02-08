"""
Detailed MADAM Debate Visualization Test
Uses queries from retrieval_test_3queries.csv
Shows complete debate process with agent responses and aggregation
"""
import sys
sys.path.insert(0, 'src')

import time
import csv
from datetime import datetime
from madam_hybrid_system import MadamHybridRAGSystem

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def print_subheader(phase, title):
    """Print a formatted subheader"""
    print(f"\n[{phase}] {title}")
    print("-" * 80)

def load_queries_from_csv(csv_path):
    """Load test queries from CSV file"""
    queries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            queries.append({
                'id': row['query_id'],
                'question': row['question'],
                'category': row['category']
            })
    return queries

def test_madam_debate_detailed():
    """Test MADAM debate with detailed logging"""
    
    # Load queries from CSV
    csv_path = r"D:\backup\ptspRag\evaluation\retrieval_test_3queries.csv"
    queries = load_queries_from_csv(csv_path)
    
    print_header("MADAM DEBATE DETAILED TEST")
    print(f"Test Queries: {len(queries)}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize system
    print("\n[INIT] Initializing MADAM Hybrid RAG System...")
    try:
        rag_system = MadamHybridRAGSystem(
            debate_rounds=3,
            debate_top_k=4
        )
        print("[OK] System initialized successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize system: {e}")
        return
    
    # Track results
    results = []
    successful = 0
    failed = 0
    
    # Test each query
    for query_data in queries:
        query_id = query_data['id']
        question = query_data['question']
        category = query_data['category']
        
        print_header(f"{query_id}: {question}")
        print(f"Category: {category}")
        
        start_time = time.time()
        
        try:
            print_subheader("EXECUTING", "Running MADAM Debate System...")
            
            # Call the system
            result = rag_system.ask_with_fallback(
                question=question,
                k=12
            )
            
            elapsed = time.time() - start_time
            
            # Display results
            print_subheader("RESULTS", "System Response")
            print(f"\n  Method: {result.get('method', 'unknown')}")
            print(f"  Quality Score: {result.get('quality_score', 0):.2f}")
            print(f"  Total Time: {elapsed:.2f}s")
            
            # Show phase breakdown
            if 'phase_times' in result:
                print(f"\n  Phase Times:")
                for phase, timing in result['phase_times'].items():
                    print(f"    - {phase}: {timing}")
            
            # Show answer preview
            answer = result.get('answer', 'No answer')
            print(f"\n  Answer Preview:")
            print(f"    {answer[:300]}..." if len(answer) > 300 else f"    {answer}")
            
            # Show MADAM debate details if available
            if 'enhanced_features' in result and 'madam_debate' in result['enhanced_features']:
                debate_info = result['enhanced_features']['madam_debate']
                print(f"\n  MADAM Debate Info:")
                print(f"    - Documents Used: {debate_info.get('documents_used', 'N/A')}")
                print(f"    - Rounds: {debate_info.get('rounds', 'N/A')}")
                if 'final_aggregation' in debate_info:
                    agg = debate_info['final_aggregation']
                    print(f"    - Final Aggregation: {agg[:200]}..." if len(agg) > 200 else f"    - Final Aggregation: {agg}")
            
            # Show phase log if available
            if 'phase_log' in result:
                print(f"\n  Phase Log:")
                for log_entry in result['phase_log']:
                    phase = log_entry.get('phase', 'unknown')
                    if log_entry.get('skipped'):
                        print(f"    - {phase}: SKIPPED ({log_entry.get('reason', 'no reason')})")
                    elif 'error' in log_entry:
                        print(f"    - {phase}: ERROR - {log_entry['error']}")
                    else:
                        quality = log_entry.get('quality', 'N/A')
                        print(f"    - {phase}: Quality={quality}")
            
            results.append({
                'query_id': query_id,
                'question': question,
                'method': result.get('method', 'unknown'),
                'time': elapsed,
                'success': True
            })
            successful += 1
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"\n[ERROR] {str(e)}")
            print(f"Time elapsed: {elapsed:.2f}s")
            import traceback
            traceback.print_exc()
            
            results.append({
                'query_id': query_id,
                'question': question,
                'error': str(e),
                'time': elapsed,
                'success': False
            })
            failed += 1
        
        # Wait between queries (except after last one)
        if query_data != queries[-1]:
            print_header("Waiting 10 seconds before next query...")
            time.sleep(10)
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"Total Queries: {len(queries)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        methods = {}
        for r in results:
            if r['success']:
                method = r['method']
                methods[method] = methods.get(method, 0) + 1
        
        print(f"\nSearch Methods Used:")
        for method, count in methods.items():
            print(f"  - {method}: {count}")
    
    print("\n[DONE] Test completed!")
    print(f"\n[INFO] Check the logs directory for detailed MADAM debate logs")
    print(f"       Location: logs/madam_debate_*.log")

if __name__ == "__main__":
    test_madam_debate_detailed()
