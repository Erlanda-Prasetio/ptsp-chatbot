"""
Enhanced Chunk Confidence Test - With Timing & Search Method Metrics
=====================================================================

Like run_retrieval_test.py but queries Supabase directly (no API).
Captures timing, search method (always "direct_supabase"), and outputs CSV.

Usage:
    python evaluation/chunk_test_with_metrics.py --csv evaluation/chunk_test_metrics.csv
"""

import os
import sys
import csv
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add src to path
sys.path.append('src')
sys.path.append('.')

from dotenv import load_dotenv

load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY not found in .env")
    sys.exit(1)

from supabase import create_client
from src.embed import embed_texts


def load_query_template(csv_file: str) -> list:
    """Load queries from CSV template"""
    questions = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            questions = list(reader)
        print(f"✅ Loaded {len(questions)} queries from {csv_file}")
        return questions
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_file}")
        return []


def get_top_chunks_direct(supabase, table_name: str, query_text: str, limit: int = 5) -> dict:
    """
    Query Supabase directly using RPC to get top chunks with timing.
    Returns dict with chunk_ids list and search details.
    """
    try:
        start_time = time.time()
        
        # Embed the query
        query_embedding = embed_texts([query_text])[0]
        
        # Query using appropriate RPC function based on table
        if table_name == 'documents_old':
            rpc_name = 'match_documents_old'
        elif table_name == 'documents_new':
            rpc_name = 'match_documents_new'
        else:
            rpc_name = 'match_documents'
        
        result = supabase.rpc(rpc_name, {
            'query_embedding': query_embedding,
            'match_count': limit
        }).execute()
        
        elapsed = time.time() - start_time
        
        # Parse result - extract chunk IDs from response
        chunk_ids = []
        chunks = []
        try:
            if hasattr(result, 'data'):
                chunks = result.data if result.data else []
            elif isinstance(result, dict) and 'data' in result:
                chunks = result.get('data', [])
            elif isinstance(result, list):
                chunks = result
        except Exception as e:
            return {
                'chunk_ids': [],
                'count': 0,
                'time_seconds': elapsed,
                'status': 'error',
                'error': f'Failed to extract chunks: {e}'
            }
        
        # Extract IDs from chunks
        for chunk in chunks:
            chunk_id = chunk[0] if isinstance(chunk, (list, tuple)) else chunk.get('id', '')
            if chunk_id:
                chunk_ids.append(str(chunk_id))
        
        return {
            'chunk_ids': chunk_ids[:limit],
            'count': len(chunk_ids),
            'time_seconds': elapsed,
            'status': 'success'
        }
    except Exception as e:
        return {
            'chunk_ids': [],
            'count': 0,
            'time_seconds': time.time() - start_time,
            'status': 'error',
            'error': str(e)
        }


def run_chunk_test_csv(csv_file: str, output_csv: str = None):
    """Run chunk test with metrics and save to CSV"""
    if output_csv is None:
        output_csv = csv_file.replace('.csv', '_chunk_metrics.csv')
    
    print("\n" + "=" * 70)
    print("🧪 CHUNK CONFIDENCE TEST WITH METRICS")
    print("=" * 70)
    print()
    
    # Load queries
    questions = load_query_template(csv_file)
    if not questions:
        return False
    
    # Initialize Supabase
    print("🔌 Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("📂 Querying documents...")
    print()
    print("=" * 70)
    print("🔍 TESTING CHUNK RETRIEVAL")
    print("=" * 70)
    print()
    
    results = []
    timings = []
    search_methods = defaultdict(int)
    start_all = time.time()
    
    for i, query_data in enumerate(questions, 1):
        query_text = query_data.get('question') or query_data.get('query')
        query_id = query_data.get('id', f'Q{i:03d}')
        dataset_source = query_data.get('dataset_source', 'unknown')
        
        print(f"[{i}/{len(questions)}] {query_id}: {query_text[:60]}...")
        
        # Determine table based on dataset_source
        table = 'documents_old' if dataset_source == 'OLD' else 'documents_new'
        
        # Query chunks
        query_result = get_top_chunks_direct(supabase, table, query_text, limit=5)
        chunk_ids = query_result['chunk_ids']
        query_time = query_result['time_seconds']
        status = query_result['status']
        
        # Record result
        search_method = 'direct_supabase'  # Always direct for chunk test
        search_methods[search_method] += 1
        timings.append(query_time)
        
        result_row = {
            'query_id': query_id,
            'question': query_text,
            'category': query_data.get('category', 'uncategorized'),
            'dataset_source': dataset_source,
            'retrieved_chunks': ','.join(chunk_ids) if chunk_ids else '',
            'chunk1_id': chunk_ids[0] if len(chunk_ids) > 0 else '',
            'chunk2_id': chunk_ids[1] if len(chunk_ids) > 1 else '',
            'chunk3_id': chunk_ids[2] if len(chunk_ids) > 2 else '',
            'chunk4_id': chunk_ids[3] if len(chunk_ids) > 3 else '',
            'chunk5_id': chunk_ids[4] if len(chunk_ids) > 4 else '',
            'search_method': search_method,
            'query_time_seconds': round(query_time, 2),
            'chunks_found': len(chunk_ids),
            'status': status
        }
        results.append(result_row)
        
        if chunk_ids:
            print(f"   ✅ {search_method} | {query_time:.2f}s | Found {len(chunk_ids)} chunks")
        else:
            print(f"   ⚠️  {search_method} | {query_time:.2f}s | No chunks found")
    
    total_time = time.time() - start_all
    
    # Save results to CSV
    print()
    print("=" * 70)
    print("💾 SAVING RESULTS TO CSV")
    print("=" * 70)
    print()
    
    if results:
        fieldnames = results[0].keys()
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"✅ Results saved to: {output_csv}")
    
    # Print statistics
    print()
    print("=" * 70)
    print("📊 SUMMARY STATISTICS")
    print("=" * 70)
    print()
    print(f"Total Queries: {len(questions)}")
    print(f"Successful: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed: {sum(1 for r in results if r['status'] == 'error')}")
    print()
    print(f"Timing:")
    if timings:
        print(f"  Average: {sum(timings) / len(timings):.2f}s")
        print(f"  Max: {max(timings):.2f}s")
        print(f"  Min: {min(timings):.2f}s")
        print(f"  Total: {total_time:.1f}s ({total_time/60:.1f} min)")
    print()
    print(f"Search Methods Used:")
    for method, count in sorted(search_methods.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(questions) * 100) if questions else 0
        print(f"  {method}: {count} ({pct:.1f}%)")
    print()
    
    chunks_found = sum(1 for r in results if r['chunks_found'] > 0)
    print(f"Queries with Chunks Found: {chunks_found}/{len(questions)} ({chunks_found/len(questions)*100:.1f}%)")
    print()
    
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run chunk test with metrics")
    parser.add_argument("--csv", default="evaluation/old_dataset_retrieval_test_template.csv",
                       help="Input CSV template file")
    parser.add_argument("--output", default=None,
                       help="Output CSV file (default: input_chunk_metrics.csv)")
    
    args = parser.parse_args()
    
    success = run_chunk_test_csv(args.csv, args.output)
    
    if success:
        print("✅ Chunk test with metrics complete!\n")
    else:
        print("❌ Chunk test failed!\n")
        sys.exit(1)
