"""
Analyze Retrieval Test Results
================================

Analyzes results from run_retrieval_test.py
Shows precision, recall, F1 score, search method distribution, and problem areas.

Usage:
    python evaluation/analyze_retrieval_test.py evaluation/raw_results/retrieval_baseline.json
    python evaluation/analyze_retrieval_test.py evaluation/retrieval_test_result.csv

Author: RAG Evaluation Framework
Date: October 2025
"""

import json
import csv
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List


def load_results(file_path: str) -> Dict:
    """Load retrieval test results from JSON or CSV file"""
    if file_path.endswith('.csv'):
        # Load from CSV
        results = []
        total_retrieval_time = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert precision/recall/f1 to float
                retrieval_time = 0
                if row.get('retrieval_time_seconds'):
                    try:
                        retrieval_time = float(row['retrieval_time_seconds'])
                        total_retrieval_time += retrieval_time
                    except ValueError:
                        retrieval_time = 0
                
                result = {
                    'query_id': row['query_id'],
                    'question': row['question'],
                    'dataset_source': row.get('dataset_source', 'unknown'),
                    'category': row.get('category', 'unknown'),
                    'search_method': row.get('search_method', 'unknown'),
                    'precision': float(row['precision']) if row.get('precision') else None,
                    'recall': float(row['recall']) if row.get('recall') else None,
                    'f1_score': float(row['f1_score']) if row.get('f1_score') else None,
                    'retrieval_time_seconds': retrieval_time,
                }
                results.append(result)
        
        return {
            'test_name': Path(file_path).stem,
            'results': results,
            'total_time_seconds': total_retrieval_time,
            'test_type': 'retrieval'
        }
    else:
        # Load from JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)



def analyze_retrieval_test(results_data: Dict):
    """Analyze and display retrieval test results"""
    
    test_name = results_data.get('test_name', 'Unknown')
    results = results_data.get('results', [])
    total_time = results_data.get('total_time_seconds', 0)
    
    if not results:
        print("❌ No results to analyze")
        return
    
    # Calculate aggregate metrics
    total_queries = len(results)
    successful = sum(1 for r in results if not r.get('error'))
    failed = total_queries - successful
    
    # Retrieval metrics (only for queries with ground truth)
    scorable_results = [r for r in results if r.get('precision') is not None]
    
    if scorable_results:
        avg_precision = sum(r['precision'] for r in scorable_results) / len(scorable_results)
        avg_recall = sum(r['recall'] for r in scorable_results) / len(scorable_results)
        avg_f1 = sum(r['f1_score'] for r in scorable_results) / len(scorable_results)
        
        min_precision = min(r['precision'] for r in scorable_results)
        max_precision = max(r['precision'] for r in scorable_results)
        min_recall = min(r['recall'] for r in scorable_results)
        max_recall = max(r['recall'] for r in scorable_results)
        min_f1 = min(r['f1_score'] for r in scorable_results)
        max_f1 = max(r['f1_score'] for r in scorable_results)
    else:
        avg_precision = avg_recall = avg_f1 = 0
        min_precision = max_precision = 0
        min_recall = max_recall = 0
        min_f1 = max_f1 = 0
    
    # Search method distribution
    search_methods = defaultdict(int)
    for r in results:
        method = r.get('search_method', 'unknown')
        if not method or method.strip() == '':
            method = 'unknown'
        search_methods[method] += 1
    
    # Dataset distribution
    dataset_counts = defaultdict(int)
    for r in results:
        dataset = r.get('dataset_source', 'unknown')
        dataset_counts[dataset] += 1
    
    # Category performance
    category_metrics = defaultdict(lambda: {'count': 0, 'f1_sum': 0, 'f1_scores': []})
    for r in scorable_results:
        cat = r.get('category', 'uncategorized')
        category_metrics[cat]['count'] += 1
        category_metrics[cat]['f1_sum'] += r['f1_score']
        category_metrics[cat]['f1_scores'].append(r['f1_score'])
    
    # Problem identification - exclude internet_fallback as it's expected to have 0 precision
    zero_precision_with_fallback = sum(1 for r in scorable_results if r['precision'] == 0)
    zero_recall_with_fallback = sum(1 for r in scorable_results if r['recall'] == 0)
    
    # Count zero precision/recall ONLY from non-internet_fallback queries
    zero_precision_actual_issue = sum(1 for r in scorable_results 
                                     if r['precision'] == 0 and r.get('search_method') != 'internet_fallback')
    zero_recall_actual_issue = sum(1 for r in scorable_results 
                                   if r['recall'] == 0 and r.get('search_method') != 'internet_fallback')
    
    internet_fallback = sum(1 for r in results if r.get('search_method') == 'internet_fallback')
    
    # Timing
    retrieval_times = [r.get('retrieval_time_seconds', 0) for r in results]
    avg_retrieval_time = sum(retrieval_times) / len(retrieval_times) if retrieval_times else 0
    max_retrieval_time = max(retrieval_times) if retrieval_times else 0
    min_retrieval_time = min(retrieval_times) if retrieval_times else 0
    
    # Print report
    print()
    print("=" * 70)
    print("RETRIEVAL TEST ANALYSIS")
    print("=" * 70)
    print()
    print(f" Overall Performance:")
    print(f"   Total Queries: {total_queries}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print()
    print(f"  Timing:")
    print(f"   Avg Retrieval Time: {avg_retrieval_time:.2f}s")
    print(f"   Max Retrieval Time: {max_retrieval_time:.2f}s")
    print(f"   Min Retrieval Time: {min_retrieval_time:.2f}s")
    print(f"   Total Test Time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print()
    
    if scorable_results:
        print(f" Retrieval Metrics (n={len(scorable_results)}):")
        print(f"   Precision: {avg_precision:.3f} (min={min_precision:.3f}, max={max_precision:.3f})")
        print(f"   Recall:    {avg_recall:.3f} (min={min_recall:.3f}, max={max_recall:.3f})")
        print(f"   F1-Score:  {avg_f1:.3f} (min={min_f1:.3f}, max={max_f1:.3f})")
        print()
    
    print(f" Query Distribution:")
    for dataset, count in sorted(dataset_counts.items()):
        print(f"   {dataset} Dataset: {count} questions")
    print()
    
    print(f" Search Method Distribution:")
    for method, count in sorted(search_methods.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_queries * 100) if total_queries > 0 else 0
        print(f"   {method:20s}: {count:3d} ({pct:5.1f}%)")
    print()
    
    if category_metrics:
        print(f" Performance by Category:")
        for cat, metrics in sorted(category_metrics.items(), key=lambda x: x[1]['f1_sum']/x[1]['count'], reverse=True):
            avg_f1_cat = metrics['f1_sum'] / metrics['count']
            print(f"   {cat:15s}: {metrics['count']:3d} questions, F1={avg_f1_cat:.3f}")
        print()
    
    print(f"  Issues Identified:")
    if scorable_results:
        # Report zero precision/recall ONLY if they come from non-internet_fallback queries
        if zero_precision_actual_issue > 0:
            zero_prec_pct = (zero_precision_actual_issue / len(scorable_results) * 100)
            print(f"   Zero Precision (non-fallback): {zero_precision_actual_issue}/{len(scorable_results)} ({zero_prec_pct:.1f}%)")
        
        if zero_recall_actual_issue > 0:
            zero_rec_pct = (zero_recall_actual_issue / len(scorable_results) * 100)
            print(f"   Zero Recall (non-fallback):    {zero_recall_actual_issue}/{len(scorable_results)} ({zero_rec_pct:.1f}%)")
        
        # Show total zero precision/recall for context (including fallback)
        total_zero_prec_pct = (zero_precision_with_fallback / len(scorable_results) * 100)
        total_zero_rec_pct = (zero_recall_with_fallback / len(scorable_results) * 100)
        print(f"   Zero Precision (all methods):  {zero_precision_with_fallback}/{len(scorable_results)} ({total_zero_prec_pct:.1f}%) [incl. fallback: {zero_precision_with_fallback - zero_precision_actual_issue}]")
        print(f"   Zero Recall (all methods):     {zero_recall_with_fallback}/{len(scorable_results)} ({total_zero_rec_pct:.1f}%) [incl. fallback: {zero_recall_with_fallback - zero_recall_actual_issue}]")
    
    fallback_pct = (internet_fallback / total_queries * 100) if total_queries > 0 else 0
    print(f"   Internet Fallback: {internet_fallback}/{total_queries} ({fallback_pct:.1f}%)")
    if fallback_pct > 30:
        print(f"   ℹ️  Note: Internet fallback returns non-local chunks, zero precision is expected")
    print()
    
    # Worst performing queries
    if scorable_results:
        print(" Worst Performing Queries (Bottom 5 by F1):")
        worst_queries = sorted(scorable_results, key=lambda x: x['f1_score'])[:5]
        for i, r in enumerate(worst_queries, 1):
            q_id = r.get('query_id', '?')
            question = r.get('question', '')[:50]
            f1 = r.get('f1_score', 0)
            method = r.get('search_method', '?')
            fallback_tag = " [🌐 FALLBACK]" if method == 'internet_fallback' else ""
            print(f"   {i}. [{q_id}] F1={f1:.3f} ({method}){fallback_tag}: {question}...")
        print()
        
        print(" Best Performing Queries (Top 5 by F1):")
        best_queries = sorted(scorable_results, key=lambda x: x['f1_score'], reverse=True)[:5]
        for i, r in enumerate(best_queries, 1):
            q_id = r.get('query_id', '?')
            question = r.get('question', '')[:50]
            f1 = r.get('f1_score', 0)
            method = r.get('search_method', '?')
            fallback_tag = " [🌐 FALLBACK]" if method == 'internet_fallback' else ""
            print(f"   {i}. [{q_id}] F1={f1:.3f} ({method}){fallback_tag}: {question}...")
        print()
    
    print("=" * 70)
    print(" Summary:")
    print("=" * 70)
    if scorable_results:
        print(f"Overall F1 Score: {avg_f1:.3f}")
        print(f"Precision: {avg_precision:.3f}")
        print(f"Recall: {avg_recall:.3f}")
    print(f"Internet Fallback Rate: {fallback_pct:.1f}%")
    print(f"Retrieval Timing:")
    print(f"  Average: {avg_retrieval_time:.2f}s")
    print(f"  Max: {max_retrieval_time:.2f}s")
    print(f"  Min: {min_retrieval_time:.2f}s")
    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_retrieval_test.py <results_file.json>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    
    if not Path(results_file).exists():
        print(f"❌ File not found: {results_file}")
        sys.exit(1)
    
    print(f"📁 Loaded results from: {results_file}")
    results_data = load_results(results_file)
    
    analyze_retrieval_test(results_data)


if __name__ == "__main__":
    main()
