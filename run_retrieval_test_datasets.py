"""
Multi-Dataset Retrieval Test
=============================

Runs retrieval tests against different datasets (NEW, OLD, COMBINED).
Saves results with dataset label in CSV for easy comparison.

Usage:
    python run_retrieval_test_datasets.py --dataset OLD --limit 50
    python run_retrieval_test_datasets.py --dataset COMBINED --limit 50
"""

import os
import sys
import json
import requests
import time
import csv
from datetime import datetime
from typing import Dict, List, Tuple, Any
import argparse
from pathlib import Path

# Add evaluation to path
sys.path.append('evaluation')

from metrics_logger import MetricsLogger


def load_test_questions(limit: int = 50) -> List[Dict[str, Any]]:
    """Load test questions from JSON file"""
    
    questions_file = 'evaluation/sample_30_balanced.json'
    
    if not os.path.exists(questions_file):
        print(f"❌ Questions file not found: {questions_file}")
        return []
    
    with open(questions_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('sample', []) if isinstance(data, dict) else data
    
    print(f"📋 Loaded {len(questions)} test questions")
    
    if limit:
        questions = questions[:limit]
        print(f"🔢 Using first {limit} questions")
    
    return questions


def retrieve_chunks(
    question: str,
    api_url: str = "http://localhost:8001",
    dataset: str = "NEW"
) -> Tuple[List[str], str, float]:
    """
    Retrieve chunks for a question using the API
    
    Returns: (chunk_ids, search_method, retrieval_time)
    """
    try:
        query_start = time.time()
        
        response = requests.post(
            f"{api_url}/retrieve?dataset={dataset}",
            json={"messages": [{"role": "user", "content": question}]},
            timeout=60
        )
        
        query_time = time.time() - query_start
        
        if response.status_code != 200:
            print(f"    ❌ API error: {response.status_code}")
            return [], "error", query_time
        
        data = response.json()
        sources = data.get("sources", [])
        search_method = data.get("search_method", "unknown")
        
        chunk_ids = [source.get("chunk_id", f"chunk_{i+1}") for i, source in enumerate(sources)]
        
        return chunk_ids, search_method, query_time
        
    except requests.exceptions.ConnectionError:
        print(f"    ❌ Cannot connect to API at {api_url}")
        return [], "connection_error", 0
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return [], "error", 0


def save_retrieval_results_csv(
    results: List[Dict[str, Any]],
    dataset: str,
    output_dir: str = "evaluation"
) -> str:
    """Save retrieval results to CSV"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(
        output_dir,
        f"retrieval_test_result_{dataset}_{timestamp}.csv"
    )
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define CSV columns
    fieldnames = [
        'query_id', 'question', 'category', 'dataset_source',
        'retrieved_chunks', 'chunk1_id', 'chunk2_id', 'chunk3_id', 'chunk4_id', 'chunk5_id',
        'generated_chunks', 'search_method', 'retrieval_time_seconds',
        'precision', 'recall', 'f1_score', 'notes'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            # Get up to 5 chunk IDs
            chunk_ids = result.get('retrieved_chunks', [])
            chunk_row = {
                'chunk1_id': chunk_ids[0] if len(chunk_ids) > 0 else '',
                'chunk2_id': chunk_ids[1] if len(chunk_ids) > 1 else '',
                'chunk3_id': chunk_ids[2] if len(chunk_ids) > 2 else '',
                'chunk4_id': chunk_ids[3] if len(chunk_ids) > 3 else '',
                'chunk5_id': chunk_ids[4] if len(chunk_ids) > 4 else '',
            }
            
            row = {
                'query_id': result.get('query_id', ''),
                'question': result.get('question', ''),
                'category': result.get('category', ''),
                'dataset_source': result.get('dataset_source', dataset),
                'retrieved_chunks': '|'.join(chunk_ids),
                'generated_chunks': '|'.join(result.get('generated_chunks', [])),
                'search_method': result.get('search_method', ''),
                'retrieval_time_seconds': f"{result.get('retrieval_time_seconds', 0):.2f}",
                'precision': f"{result.get('precision', 0):.3f}",
                'recall': f"{result.get('recall', 0):.3f}",
                'f1_score': f"{result.get('f1_score', 0):.3f}",
                'notes': result.get('notes', ''),
            }
            row.update(chunk_row)
            
            writer.writerow(row)
    
    print(f"✅ Results saved to: {output_file}")
    return output_file


def analyze_results(results: List[Dict[str, Any]], dataset: str) -> Dict[str, Any]:
    """Analyze retrieval results"""
    
    if not results:
        return {}
    
    total_queries = len(results)
    
    # Calculate metrics
    precisions = [r.get('precision', 0) for r in results]
    recalls = [r.get('recall', 0) for r in results]
    f1_scores = [r.get('f1_score', 0) for r in results]
    retrieval_times = [r.get('retrieval_time_seconds', 0) for r in results]
    search_methods = {}
    
    for result in results:
        method = result.get('search_method', 'unknown')
        search_methods[method] = search_methods.get(method, 0) + 1
    
    # Count issues
    zero_precision = sum(1 for p in precisions if p == 0)
    fallback_queries = [r for r in results if r.get('search_method') == 'internet_fallback']
    fallback_count = len(fallback_queries)
    real_zero_precision = zero_precision - fallback_count
    
    return {
        'dataset': dataset,
        'total_queries': total_queries,
        'avg_precision': sum(precisions) / len(precisions) if precisions else 0,
        'avg_recall': sum(recalls) / len(recalls) if recalls else 0,
        'avg_f1': sum(f1_scores) / len(f1_scores) if f1_scores else 0,
        'avg_retrieval_time': sum(retrieval_times) / len(retrieval_times) if retrieval_times else 0,
        'max_retrieval_time': max(retrieval_times) if retrieval_times else 0,
        'min_retrieval_time': min(retrieval_times) if retrieval_times else 0,
        'search_methods': search_methods,
        'zero_precision_count': zero_precision,
        'real_zero_precision': real_zero_precision,
        'fallback_zero_precision': fallback_count,
    }


def main():
    parser = argparse.ArgumentParser(description='Multi-Dataset Retrieval Test')
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['NEW', 'OLD', 'COMBINED'],
        default='NEW',
        help='Dataset to test'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Number of questions to test'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8001',
        help='API URL'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(f"RETRIEVAL TEST - {args.dataset} DATASET")
    print("="*70)
    
    # Load questions
    questions = load_test_questions(limit=args.limit)
    
    if not questions:
        print("❌ No questions loaded")
        return
    
    # Run retrieval tests
    results = []
    all_retrieval_times = []
    
    print(f"\n🔍 Running retrieval tests with {args.dataset} dataset...\n")
    
    for i, question_data in enumerate(questions, 1):
        query_id = question_data.get('id', f'q_{i}')
        question = question_data.get('question', '')
        category = question_data.get('category', 'unknown')
        generated_chunks = question_data.get('answer', question_data.get('generated_chunks', []))
        
        if isinstance(generated_chunks, str):
            generated_chunks = [generated_chunks]
        elif not isinstance(generated_chunks, list):
            generated_chunks = []
        
        print(f"  [{i:2d}/{len(questions)}] Query {query_id}: {question[:60]}...")
        
        # Retrieve chunks
        chunk_ids, search_method, retrieval_time = retrieve_chunks(
            question,
            api_url=args.api_url,
            dataset=args.dataset
        )
        
        all_retrieval_times.append(retrieval_time)
        
        # Calculate metrics
        retrieved_set = set(chunk_ids)
        generated_set = set(generated_chunks)
        
        if len(retrieved_set) > 0 or len(generated_set) > 0:
            intersection = len(retrieved_set & generated_set)
            precision = intersection / len(retrieved_set) if len(retrieved_set) > 0 else 0
            recall = intersection / len(generated_set) if len(generated_set) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        else:
            precision = recall = f1 = 0
        
        # Determine notes
        notes = ""
        if search_method == 'internet_fallback' and precision == 0:
            notes = "[🌐 FALLBACK] Expected zero precision"
        elif precision == 0 and len(chunk_ids) > 0:
            notes = "[⚠️ ISSUE] Retrieved chunks don't match ground truth"
        
        result = {
            'query_id': query_id,
            'question': question,
            'category': category,
            'dataset_source': args.dataset,
            'retrieved_chunks': chunk_ids,
            'generated_chunks': generated_chunks,
            'search_method': search_method,
            'retrieval_time_seconds': retrieval_time,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'notes': notes,
        }
        
        results.append(result)
        
        # Print metrics
        status = "✅" if f1 > 0 else "⚠️" if search_method == "internet_fallback" else "❌"
        print(f"        {status} {search_method:20s} | {retrieval_time:6.2f}s | P/R/F1: {precision:.3f}/{recall:.3f}/{f1:.3f}")
    
    # Analyze results
    analysis = analyze_results(results, args.dataset)
    
    # Save CSV
    csv_file = save_retrieval_results_csv(results, args.dataset)
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n📊 Dataset: {args.dataset}")
    print(f"📋 Total Queries: {analysis['total_queries']}")
    print(f"⏱️  Retrieval Time:")
    print(f"   Average: {analysis['avg_retrieval_time']:.2f}s")
    print(f"   Max: {analysis['max_retrieval_time']:.2f}s")
    print(f"   Min: {analysis['min_retrieval_time']:.2f}s")
    print(f"\n📈 Metrics:")
    print(f"   Avg Precision: {analysis['avg_precision']:.3f}")
    print(f"   Avg Recall: {analysis['avg_recall']:.3f}")
    print(f"   Avg F1 Score: {analysis['avg_f1']:.3f}")
    print(f"\n🔍 Search Methods:")
    for method, count in sorted(analysis['search_methods'].items()):
        pct = 100 * count / analysis['total_queries']
        print(f"   {method:20s}: {count:3d} ({pct:5.1f}%)")
    print(f"\n⚠️  Zero Precision: {analysis['zero_precision_count']}/{analysis['total_queries']} ({100*analysis['zero_precision_count']/analysis['total_queries']:.1f}%)")
    print(f"   Real Issues: {analysis['real_zero_precision']}")
    print(f"   From Fallback: {analysis['fallback_zero_precision']}")
    print(f"\n💾 Results: {csv_file}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
