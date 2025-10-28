"""
Multi-Dataset Results Analyzer
================================

Analyzes and compares retrieval test results across different datasets.
Reads CSV files and provides comparative statistics.

Usage:
    python analyze_retrieval_test_datasets.py
    python analyze_retrieval_test_datasets.py --datasets NEW OLD COMBINED
"""

import os
import csv
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse
from collections import defaultdict


def find_latest_results(dataset: str, results_dir: str = "evaluation") -> str:
    """Find the latest retrieval test results for a dataset"""
    
    results_path = Path(results_dir)
    matching_files = list(results_path.glob(f"retrieval_test_result_{dataset}_*.csv"))
    
    if not matching_files:
        return None
    
    # Sort by modification time, get latest
    latest = max(matching_files, key=lambda p: p.stat().st_mtime)
    return str(latest)


def parse_csv_results(filepath: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Parse retrieval test CSV results"""
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return [], {}
    
    results = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse metrics
                try:
                    result = {
                        'query_id': row.get('query_id', ''),
                        'question': row.get('question', '')[:100],
                        'category': row.get('category', ''),
                        'dataset_source': row.get('dataset_source', ''),
                        'search_method': row.get('search_method', ''),
                        'retrieval_time_seconds': float(row.get('retrieval_time_seconds', 0)),
                        'precision': float(row.get('precision', 0)),
                        'recall': float(row.get('recall', 0)),
                        'f1_score': float(row.get('f1_score', 0)),
                        'notes': row.get('notes', ''),
                    }
                    results.append(result)
                except ValueError as e:
                    print(f"⚠️  Skipping malformed row: {e}")
                    continue
        
        print(f"✅ Loaded {len(results)} results from {filepath}")
        return results, {}
        
    except Exception as e:
        print(f"❌ Error parsing CSV: {e}")
        return [], {}


def calculate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics from results"""
    
    if not results:
        return {}
    
    precisions = [r['precision'] for r in results]
    recalls = [r['recall'] for r in results]
    f1_scores = [r['f1_score'] for r in results]
    times = [r['retrieval_time_seconds'] for r in results]
    
    search_methods = defaultdict(int)
    for r in results:
        search_methods[r['search_method']] += 1
    
    categories = defaultdict(int)
    for r in results:
        categories[r['category']] += 1
    
    zero_precision = sum(1 for p in precisions if p == 0)
    fallback_queries = [r for r in results if r.get('search_method') == 'internet_fallback']
    fallback_with_zero = sum(1 for r in fallback_queries if r['precision'] == 0)
    real_zero_precision = zero_precision - fallback_with_zero
    
    perfect_f1 = sum(1 for f in f1_scores if f == 1.0)
    avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0
    
    return {
        'total_queries': len(results),
        'avg_precision': sum(precisions) / len(precisions),
        'avg_recall': sum(recalls) / len(recalls),
        'avg_f1': avg_f1,
        'median_f1': sorted(f1_scores)[len(f1_scores)//2] if f1_scores else 0,
        'max_f1': max(f1_scores) if f1_scores else 0,
        'min_f1': min(f1_scores) if f1_scores else 0,
        'perfect_f1_count': perfect_f1,
        'avg_time': sum(times) / len(times),
        'max_time': max(times) if times else 0,
        'min_time': min(times) if times else 0,
        'total_time': sum(times),
        'search_methods': dict(search_methods),
        'categories': dict(categories),
        'zero_precision_count': zero_precision,
        'real_zero_precision': real_zero_precision,
        'fallback_zero_precision': fallback_with_zero,
        'results': results,
    }


def print_comparison_table(datasets_stats: Dict[str, Dict[str, Any]]):
    """Print comparison table across datasets"""
    
    print("\n" + "="*100)
    print("MULTI-DATASET COMPARISON")
    print("="*100)
    
    # Header
    header = f"{'Metric':<30} | "
    for dataset_name in datasets_stats.keys():
        header += f"{dataset_name:>18} | "
    print(header)
    print("-" * (30 + 4 + len(datasets_stats) * 22))
    
    # Metrics to compare
    metrics = [
        ('Total Queries', 'total_queries', '{}'),
        ('Avg Precision', 'avg_precision', '{:.4f}'),
        ('Avg Recall', 'avg_recall', '{:.4f}'),
        ('Avg F1 Score', 'avg_f1', '{:.4f}'),
        ('Median F1 Score', 'median_f1', '{:.4f}'),
        ('Perfect F1 (1.0)', 'perfect_f1_count', '{}'),
        ('Avg Retrieval Time (s)', 'avg_time', '{:.2f}'),
        ('Max Retrieval Time (s)', 'max_time', '{:.2f}'),
        ('Min Retrieval Time (s)', 'min_time', '{:.2f}'),
        ('Total Time (min)', lambda s: s['total_time']/60, '{:.1f}'),
        ('Zero Precision', 'zero_precision_count', '{}'),
        ('Real Issues', 'real_zero_precision', '{}'),
        ('From Fallback', 'fallback_zero_precision', '{}'),
    ]
    
    for metric_name, metric_key, fmt in metrics:
        row = f"{metric_name:<30} | "
        for dataset_name, stats in datasets_stats.items():
            if callable(metric_key):
                value = metric_key(stats)
            else:
                value = stats.get(metric_key, 'N/A')
            
            if isinstance(value, (int, float)):
                row += f"{fmt.format(value):>18} | "
            else:
                row += f"{str(value):>18} | "
        
        print(row)
    
    print("="*100)


def print_search_methods_breakdown(datasets_stats: Dict[str, Dict[str, Any]]):
    """Print search methods breakdown"""
    
    print("\n" + "="*100)
    print("SEARCH METHODS BREAKDOWN")
    print("="*100)
    
    for dataset_name, stats in datasets_stats.items():
        print(f"\n{dataset_name}:")
        methods = stats.get('search_methods', {})
        total = stats.get('total_queries', 1)
        
        for method, count in sorted(methods.items(), key=lambda x: x[1], reverse=True):
            pct = 100 * count / total
            print(f"  {method:<25} {count:3d} ({pct:5.1f}%)")
    
    print("="*100)


def print_category_breakdown(datasets_stats: Dict[str, Dict[str, Any]]):
    """Print category breakdown"""
    
    print("\n" + "="*100)
    print("CATEGORY BREAKDOWN")
    print("="*100)
    
    for dataset_name, stats in datasets_stats.items():
        print(f"\n{dataset_name}:")
        categories = stats.get('categories', {})
        total = stats.get('total_queries', 1)
        
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            pct = 100 * count / total
            print(f"  {category:<30} {count:3d} ({pct:5.1f}%)")
    
    print("="*100)


def print_problem_queries(datasets_stats: Dict[str, Dict[str, Any]]):
    """Print problematic queries (zero precision without fallback)"""
    
    print("\n" + "="*100)
    print("PROBLEM QUERIES (Zero Precision, Non-Fallback)")
    print("="*100)
    
    has_problems = False
    
    for dataset_name, stats in datasets_stats.items():
        results = stats.get('results', [])
        problems = [r for r in results if r['precision'] == 0 and r['search_method'] != 'internet_fallback']
        
        if problems:
            has_problems = True
            print(f"\n{dataset_name}: {len(problems)} problem queries")
            print("-" * 100)
            
            for i, result in enumerate(problems[:10], 1):  # Show first 10
                print(f"  [{i}] {result['query_id']:10s} | {result['question']}")
                print(f"      Method: {result['search_method']} | Time: {result['retrieval_time_seconds']:.2f}s")
                if result['notes']:
                    print(f"      Notes: {result['notes']}")
    
    if not has_problems:
        print("\n✅ No problem queries found (all zero precision are from fallback)")
    
    print("="*100)


def main():
    parser = argparse.ArgumentParser(description='Analyze Multi-Dataset Retrieval Results')
    parser.add_argument(
        '--datasets',
        type=str,
        nargs='+',
        default=['NEW', 'OLD', 'COMBINED'],
        help='Datasets to analyze'
    )
    parser.add_argument(
        '--results-dir',
        type=str,
        default='evaluation',
        help='Directory containing results CSV files'
    )
    parser.add_argument(
        '--csv-files',
        type=str,
        nargs='+',
        default=None,
        help='Specific CSV files to analyze (if not provided, uses latest for each dataset)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*100)
    print("MULTI-DATASET RETRIEVAL TEST ANALYZER")
    print("="*100)
    
    datasets_stats = {}
    
    if args.csv_files:
        # Use provided CSV files
        for csv_file in args.csv_files:
            if os.path.exists(csv_file):
                dataset_name = os.path.basename(csv_file).split('_')[4] if '_' in os.path.basename(csv_file) else 'UNKNOWN'
                results, _ = parse_csv_results(csv_file)
                if results:
                    stats = calculate_statistics(results)
                    datasets_stats[dataset_name] = stats
    else:
        # Find latest for each dataset
        for dataset in args.datasets:
            print(f"\n🔍 Looking for latest results for {dataset}...")
            csv_file = find_latest_results(dataset, args.results_dir)
            
            if csv_file:
                results, _ = parse_csv_results(csv_file)
                if results:
                    stats = calculate_statistics(results)
                    datasets_stats[dataset] = stats
            else:
                print(f"⚠️  No results found for {dataset}")
    
    if not datasets_stats:
        print("❌ No datasets loaded")
        return
    
    # Print comparisons
    print_comparison_table(datasets_stats)
    print_search_methods_breakdown(datasets_stats)
    print_category_breakdown(datasets_stats)
    print_problem_queries(datasets_stats)
    
    # Save comparison summary
    summary_file = os.path.join(args.results_dir, f"comparison_summary_{len(datasets_stats)}_datasets.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        # Remove results before saving
        summary = {}
        for dataset, stats in datasets_stats.items():
            summary[dataset] = {k: v for k, v in stats.items() if k != 'results'}
        
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Summary saved: {summary_file}")


if __name__ == "__main__":
    main()
