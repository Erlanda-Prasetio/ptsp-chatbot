"""
Retrieval Test: Vector Search Quality Evaluation
=================================================

Tests ONLY the retrieval quality without LLM generation.
Measures: Precision, Recall, F1-Score, Search Method Distribution

This test focuses on how well the vector search retrieves relevant chunks
WITHOUT generating answers. Fast and cheap to run.

Usage:
    # Test with CSV baseline
    python evaluation/run_retrieval_test.py --csv evaluation/retrieval_test_baseline.csv
    
    # Test with JSON sample file
    python evaluation/run_retrieval_test.py --name retrieval_baseline --sample sample_50_balanced.json

Author: RAG Evaluation Framework
Date: October 2025
"""

import json
import time
import requests
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import subprocess
import sys


class RetrievalTester:
    """
    Tests vector search retrieval quality only (no LLM generation)
    """
    
    def __init__(
        self, 
        sample_file: str,
        api_url: str = "http://localhost:8001",
        timeout: int = 30
    ):
        self.sample_file = sample_file
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.queries = []
        
        # Load sample queries
        print(f"[DIR] Loading sample from: {sample_file}")
        with open(sample_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.queries = data if isinstance(data, list) else data.get('queries', [])
        
        print(f"[OK] Loaded {len(self.queries)} queries")
        old_count = sum(1 for q in self.queries if q.get('dataset_source') == 'OLD')
        new_count = sum(1 for q in self.queries if q.get('dataset_source') == 'NEW')
        print(f"   Old Dataset: {old_count}")
        print(f"   New Dataset: {new_count}")
        if self.queries and 'random_seed' in (self.queries[0] if isinstance(self.queries[0], dict) else {}):
            print(f"   Random Seed: {self.queries[0].get('random_seed', 'N/A')}")
        print()
    
    def test_api_connection(self) -> bool:
        """Test if RAG API is reachable"""
        print(f"[CONNECT] Testing connection to {self.api_url}...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("[OK] API is healthy")
                print(f"   Backend: {data.get('vector_backend', 'unknown')}")
                print(f"   Chunks: {data.get('chunks_status', 'unknown')}")
                print(f"   Hybrid Search: {data.get('hybrid_search_enabled', False)}")
                print(f"   Internet Fallback: {data.get('internet_fallback_enabled', False)}")
                print()
                return True
            else:
                print(f"[FAIL] API returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] Cannot connect to API at {self.api_url}")
            print(f"   Error: {e}")
            print("\n[INFO] Make sure rag_api.py is running:")
            print("   python rag_api.py")
            return False
    
    def retrieve_chunks(self, query_text: str) -> Dict:
        """
        Call RAG API to retrieve chunks only (no generation)
        Returns the sources/chunks retrieved
        """
        try:
            payload = {
                "messages": [{"role": "user", "content": query_text}],
                "retrieve_only": True  # Tell API to skip LLM generation
            }
            
            response = requests.post(
                f"{self.api_url}/retrieve",  # Use /retrieve endpoint instead of /chat
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "sources": [],
                    "search_method": "error"
                }
                
        except requests.exceptions.Timeout:
            return {
                "error": "Request timeout",
                "sources": [],
                "search_method": "timeout"
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "sources": [],
                "search_method": "error"
            }
    
    def calculate_retrieval_metrics(
        self, 
        retrieved_sources: List[Dict],
        ground_truth_chunks: List[str],
        query_data: Dict
    ) -> Dict:
        """
        Calculate Precision, Recall, F1 based on retrieved chunks vs ground truth
        """
        if not ground_truth_chunks:
            return {
                "precision": None,
                "recall": None,
                "f1_score": None,
                "reason": "No ground truth chunks available"
            }
        
        # Extract chunk IDs from retrieved sources
        retrieved_chunk_ids = set()
        for source in retrieved_sources:
            chunk_id = source.get('chunk_id') or source.get('id')
            if chunk_id:
                retrieved_chunk_ids.add(str(chunk_id))
        
        # Convert ground truth to set
        ground_truth_set = set(str(cid) for cid in ground_truth_chunks)
        
        if len(retrieved_chunk_ids) == 0:
            return {
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "retrieved_count": 0,
                "ground_truth_count": len(ground_truth_set),
                "relevant_retrieved": 0
            }
        
        # Calculate metrics
        relevant_retrieved = len(retrieved_chunk_ids & ground_truth_set)
        precision = relevant_retrieved / len(retrieved_chunk_ids) if retrieved_chunk_ids else 0
        recall = relevant_retrieved / len(ground_truth_set) if ground_truth_set else 0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1_score, 3),
            "retrieved_count": len(retrieved_chunk_ids),
            "ground_truth_count": len(ground_truth_set),
            "relevant_retrieved": relevant_retrieved
        }
    
    def run_test(
        self, 
        output_name: str,
        verbose: bool = True
    ) -> str:
        """
        Run retrieval test on all queries
        Returns path to results file
        """
        if not self.test_api_connection():
            raise RuntimeError("Cannot connect to RAG API. Start it with: python rag_api.py")
        
        print("=" * 70)
        print(f"[TEST] RETRIEVAL TEST: {output_name}")
        print("=" * 70)
        print()
        
        results = []
        start_time = time.time()
        
        for i, query_data in enumerate(self.queries, 1):
            query_text = query_data.get('question') or query_data.get('query')
            query_id = query_data.get('id', f'Q{i:03d}')
            dataset_source = query_data.get('dataset_source', 'unknown')
            category = query_data.get('category', 'uncategorized')
            
            if verbose:
                print(f"[{i}/{len(self.queries)}] {query_id} ({dataset_source}): {query_text[:60]}...")
            
            # Retrieve chunks only
            retrieve_start = time.time()
            retrieval_response = self.retrieve_chunks(query_text)
            retrieve_time = time.time() - retrieve_start
            
            # Extract metrics
            sources = retrieval_response.get('sources', [])
            search_method = retrieval_response.get('search_method', 'unknown')
            
            # Calculate precision/recall/F1
            ground_truth_chunks = query_data.get('relevant_chunk_ids', [])
            metrics = self.calculate_retrieval_metrics(
                sources, 
                ground_truth_chunks,
                query_data
            )
            
            result = {
                "query_id": query_id,
                "question": query_text,
                "dataset_source": dataset_source,
                "category": category,
                "search_method": search_method,
                "retrieval_time_seconds": round(retrieve_time, 2),
                "sources_count": len(sources),
                "precision": metrics.get('precision'),
                "recall": metrics.get('recall'),
                "f1_score": metrics.get('f1_score'),
                "retrieved_count": metrics.get('retrieved_count'),
                "ground_truth_count": metrics.get('ground_truth_count'),
                "relevant_retrieved": metrics.get('relevant_retrieved'),
                "error": retrieval_response.get('error')
            }
            
            results.append(result)
            
            if verbose:
                if result.get('error'):
                    print(f"   [FAIL] Error: {result['error']}")
                else:
                    prec = result['precision']
                    rec = result['recall']
                    f1 = result['f1_score']
                    print(f"   [OK] {retrieve_time:.2f}s | {search_method} | P={prec} R={rec} F1={f1}")
        
        total_time = time.time() - start_time
        
        # Save results
        output_dir = Path("evaluation/raw_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{output_name}.json"
        
        output_data = {
            "test_name": output_name,
            "test_type": "retrieval",
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(results),
            "total_time_seconds": round(total_time, 2),
            "sample_file": self.sample_file,
            "api_url": self.api_url,
            "results": results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print()
        print("=" * 70)
        print(f"[OK] RETRIEVAL TEST COMPLETE!")
        print("=" * 70)
        print(f"[FILE] Results saved to: {output_file}")
        print(f"[TIME]  Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
        print()
        
        return str(output_file)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Run retrieval test to measure vector search quality"
    )
    
    # Support both CSV and JSON inputs
    parser.add_argument(
        '--csv',
        type=str,
        default=None,
        help='Path to CSV file with retrieved_chunks baseline (e.g., retrieval_test_baseline.csv)'
    )
    parser.add_argument(
        '--name', 
        type=str, 
        default=None,
        help='Name for this test run (only if using --sample)'
    )
    parser.add_argument(
        '--sample',
        type=str,
        default=None,
        help='Path to sample queries JSON file (alternative to --csv)'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8001',
        help='URL of RAG API endpoint'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=40,
        help='Timeout for API requests in seconds'
    )
    parser.add_argument(
        '--no-analyze',
        action='store_true',
        help='Skip automatic analysis after test'
    )
    
    args = parser.parse_args()
    
    # Determine input source
    if args.csv:
        # CSV mode
        csv_file = args.csv
        if not Path(csv_file).exists():
            print(f"[FAIL] CSV file not found: {csv_file}")
            sys.exit(1)
        
        run_retrieval_test_csv(csv_file, args.api_url, args.timeout)
    elif args.sample and args.name:
        # JSON mode (original behavior)
        try:
            tester = RetrievalTester(
                sample_file=args.sample,
                api_url=args.api_url,
                timeout=args.timeout
            )
            
            results_file = tester.run_test(
                output_name=args.name,
                verbose=True
            )
            
            # Auto-analyze results
            if not args.no_analyze:
                print("[SEARCH] Running automatic analysis...")
                print()
                subprocess.run([
                    sys.executable,
                    'evaluation/analyze_retrieval_test.py',
                    results_file
                ])
        
        except KeyboardInterrupt:
            print("\n[WARN]  Test interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n[FAIL] Test failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("[FAIL] Please provide either:")
        print("   --csv <path_to_csv>  (for CSV baseline mode)")
        print("   OR")
        print("   --name <test_name> --sample <path_to_json>  (for JSON sample mode)")
        sys.exit(1)


def run_retrieval_test_csv(csv_file: str, api_url: str = "http://localhost:8001", timeout: int = 30):
    """
    Run retrieval test using CSV file with retrieved_chunks baseline
    Fills in: generated_chunks, precision, recall, f1_score
    """
    print()
    print("=" * 70)
    print("[TEST] RETRIEVAL TEST - CSV MODE")
    print("=" * 70)
    print()
    
    # Test API connection
    api_url = api_url.rstrip('/')
    print(f"[CONNECT] Testing connection to {api_url}...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"[FAIL] API returned status {response.status_code}")
            sys.exit(1)
        print("[OK] API is healthy")
        print()
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Cannot connect to API at {api_url}")
        print(f"   Error: {e}")
        print("\n[INFO] Make sure rag_api.py is running: python rag_api.py")
        sys.exit(1)
    
    # Read CSV
    print(f"[DIR] Loading CSV from: {csv_file}")
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"[OK] Loaded {len(rows)} queries")
    print()
    
    print("=" * 70)
    print(f"[SEARCH] RETRIEVING CHUNKS FOR {len(rows)} QUERIES")
    print("=" * 70)
    print()
    
    start_time = time.time()
    all_retrieval_times = []
    
    for i, row in enumerate(rows, 1):
        query_id = row['query_id']
        question = row['question']
        
        print(f"[{i}/{len(rows)}] {query_id}: {question[:60]}...")
        
        # Parse ground truth chunks from retrieved_chunks column
        retrieved_chunks_str = row['retrieved_chunks']
        ground_truth_chunks = [str(cid.strip()) for cid in retrieved_chunks_str.split(',') if cid.strip()]
        
        # Call /retrieve endpoint - measure time
        query_start = time.time()
        try:
            response = requests.post(
                f"{api_url}/retrieve",
                json={"messages": [{"role": "user", "content": question}], "retrieve_only": True},
                timeout=timeout
            )
            query_time = time.time() - query_start
            all_retrieval_times.append(query_time)
            
            if response.status_code == 200:
                result_data = response.json()
                sources = result_data.get('sources', [])
                search_method = result_data.get('search_method', 'unknown')
                
                # Extract generated chunk IDs
                generated_chunk_ids = [str(source.get('chunk_id', source.get('id', ''))) for source in sources]
                generated_chunks_str = ','.join(generated_chunk_ids)
                
                # Calculate metrics
                retrieved_set = set(generated_chunk_ids)
                ground_truth_set = set(ground_truth_chunks)
                
                relevant = len(retrieved_set & ground_truth_set)
                precision = relevant / len(retrieved_set) if retrieved_set else 0.0
                recall = relevant / len(ground_truth_set) if ground_truth_set else 0.0
                f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
                
                # Update row - add search_method and retrieval_time
                row['generated_chunks'] = generated_chunks_str
                row['precision'] = f"{precision:.3f}"
                row['recall'] = f"{recall:.3f}"
                row['f1_score'] = f"{f1:.3f}"
                if 'search_method' in row:
                    row['search_method'] = search_method
                if 'retrieval_time_seconds' in row:
                    row['retrieval_time_seconds'] = f"{query_time:.2f}"
                
                status = f"{search_method} | {query_time:.2f}s | P={precision:.3f}, R={recall:.3f}, F1={f1:.3f}"
                print(f"   [OK] {status}")

            else:
                print(f"   [FAIL] API error {response.status_code}")
                row['generated_chunks'] = ''
                row['precision'] = ''
                row['recall'] = ''
                row['f1_score'] = ''
                if 'search_method' in row:
                    row['search_method'] = ''
                if 'retrieval_time_seconds' in row:
                    row['retrieval_time_seconds'] = f"{query_time:.2f}"
        
        except Exception as e:
            query_time = time.time() - query_start
            all_retrieval_times.append(query_time)
            print(f"   [FAIL] Error: {e}")
            row['generated_chunks'] = ''
            row['precision'] = ''
            row['recall'] = ''
            row['f1_score'] = ''
            if 'search_method' in row:
                row['search_method'] = ''
            if 'retrieval_time_seconds' in row:
                row['retrieval_time_seconds'] = f"{query_time:.2f}"
    
    total_time = time.time() - start_time
    
    print()
    print("=" * 70)
    print("[SAVE] SAVING RESULTS TO CSV")
    print("=" * 70)
    print()
    
    # Write updated CSV with _run suffix
    from pathlib import Path
    csv_path = Path(csv_file)
    output_csv = csv_path.parent / f"{csv_path.stem}_run{csv_path.suffix}"
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = rows[0].keys() if rows else []
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"[OK] Results saved to: {output_csv}")
    print(f"[TIME]  Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    if all_retrieval_times:
        avg_time = sum(all_retrieval_times) / len(all_retrieval_times)
        max_time = max(all_retrieval_times)
        min_time = min(all_retrieval_times)
        print(f"[TIME]  Avg Retrieval Time: {avg_time:.2f}s")
        print(f"[TIME]  Max Retrieval Time: {max_time:.2f}s")
        print(f"[TIME]  Min Retrieval Time: {min_time:.2f}s")
    print()

    # Calculate summary statistics
    precisions = [float(row['precision']) for row in rows if row['precision']]
    recalls = [float(row['recall']) for row in rows if row['recall']]
    f1s = [float(row['f1_score']) for row in rows if row['f1_score']]
    
    if precisions:
        print("=" * 70)
        print("[STATS] SUMMARY STATISTICS")
        print("=" * 70)
        print(f"Average Precision: {sum(precisions) / len(precisions):.3f}")
        print(f"Average Recall:    {sum(recalls) / len(recalls):.3f}")
        print(f"Average F1-Score:  {sum(f1s) / len(f1s):.3f}")
        print("=" * 70)
        print()


if __name__ == "__main__":
    main()
