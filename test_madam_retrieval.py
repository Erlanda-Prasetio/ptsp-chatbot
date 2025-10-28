"""
Retrieval Test for MADAM RAG API
Tests the /retrieve endpoint against 50 queries from the template CSV
"""
import csv
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# Configuration
API_URL = "http://localhost:8001/retrieve"
CSV_FILE = Path("evaluation/sample_50_balanced_template.csv")
OUTPUT_FILE = Path(f"evaluation/madam_retrieval_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

def load_queries_from_csv(csv_path):
    """Load queries from the template CSV"""
    queries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['query']:  # Skip empty queries
                queries.append({
                    'eval_id': row['eval_id'],
                    'query': row['query'],
                    'category': row.get('category', 'Unknown'),
                    'ground_truth': row.get('ground_truth', ''),
                    'relevant_chunk_ids': row.get('relevant_chunk_ids', '')
                })
    return queries

def test_retrieval(query):
    """Test retrieval for a single query"""
    payload = {
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ]
    }
    
    start_time = time.time()
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                'status': 'success',
                'method': data.get('search_method', 'unknown'),
                'total_sources': data.get('total_sources', 0),
                'elapsed': elapsed,
                'sources': data.get('sources', [])
            }
        else:
            return {
                'status': 'error',
                'error': f"HTTP {response.status_code}",
                'elapsed': elapsed
            }
    except requests.exceptions.Timeout:
        return {
            'status': 'timeout',
            'error': 'Request timeout after 60s',
            'elapsed': 60.0
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'elapsed': time.time() - start_time
        }

def extract_chunk_ids(sources):
    """Extract chunk IDs from sources"""
    chunk_ids = []
    for source in sources:
        if isinstance(source, dict) and 'chunk_id' in source:
            chunk_ids.append(source['chunk_id'])
    return chunk_ids

def main():
    print("🔍 MADAM RAG API Retrieval Test")
    print(f"📝 Loading queries from: {CSV_FILE}")
    
    # Load queries
    queries = load_queries_from_csv(CSV_FILE)
    print(f"✅ Loaded {len(queries)} queries\n")
    
    # Prepare results file
    results = []
    
    print("🚀 Running retrieval tests...\n")
    for idx, q in enumerate(queries, 1):
        print(f"[{idx}/{len(queries)}] Testing: {q['query'][:60]}...", end=" ")
        
        result = test_retrieval(q['query'])
        
        # Build result record
        record = {
            'eval_id': q['eval_id'],
            'category': q['category'],
            'query': q['query'],
            'ground_truth_chunks': q['relevant_chunk_ids'],
            'search_method': result.get('method', 'N/A'),
            'retrieved_sources': result.get('total_sources', 0),
            'response_time': f"{result.get('elapsed', 0):.2f}s",
            'status': result.get('status', 'unknown'),
            'error': result.get('error', ''),
            'retrieved_chunk_ids': ','.join(extract_chunk_ids(result.get('sources', [])))
        }
        
        results.append(record)
        
        # Print status
        if result['status'] == 'success':
            print(f"✅ ({result['method']}, {result.get('total_sources', 0)} chunks, {result.get('elapsed', 0):.2f}s)")
        else:
            print(f"❌ ({result['status']}: {result.get('error', 'unknown')})")
        
        # Add delay between requests to respect rate limiting
        if idx < len(queries):
            time.sleep(2)
    
    # Write results to CSV
    print(f"\n📊 Writing results to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'eval_id', 'category', 'query', 'ground_truth_chunks',
            'search_method', 'retrieved_sources', 'response_time', 'status', 'error', 'retrieved_chunk_ids'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Print summary statistics
    print("\n" + "="*70)
    print("📈 SUMMARY STATISTICS")
    print("="*70)
    
    total = len(results)
    success = sum(1 for r in results if r['status'] == 'success')
    timeout = sum(1 for r in results if r['status'] == 'timeout')
    error = sum(1 for r in results if r['status'] == 'error')
    
    avg_time = sum(float(r['response_time'].rstrip('s')) for r in results) / total if total > 0 else 0
    avg_sources = sum(int(r['retrieved_sources']) for r in results) / total if total > 0 else 0
    
    print(f"Total Queries: {total}")
    print(f"✅ Successful: {success} ({success/total*100:.1f}%)")
    print(f"⏱️  Timeouts: {timeout} ({timeout/total*100:.1f}%)")
    print(f"❌ Errors: {error} ({error/total*100:.1f}%)")
    print(f"\n⏳ Average Response Time: {avg_time:.2f}s")
    print(f"📦 Average Sources Retrieved: {avg_sources:.1f}")
    
    # Search method breakdown
    print("\n🔍 Search Method Breakdown:")
    methods = {}
    for r in results:
        method = r['search_method']
        methods[method] = methods.get(method, 0) + 1
    for method, count in sorted(methods.items()):
        print(f"  {method}: {count} ({count/total*100:.1f}%)")
    
    print("\n✅ Test complete! Results saved to:", OUTPUT_FILE)

if __name__ == "__main__":
    main()
