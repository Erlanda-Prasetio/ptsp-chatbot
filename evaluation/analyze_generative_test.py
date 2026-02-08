"""
Analyze Generative Test Results
=================================

Analyzes results from run_generative_test.py
Shows response time, token usage, BERTScore confidence, and manual scoring stats.

Usage:
    python evaluation/analyze_generative_test.py evaluation/raw_results/generative_test1.json

Author: RAG Evaluation Framework
Date: October 2025
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List


def load_results(file_path: str) -> Dict:
    """Load generative test results from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_generative_test(results_data: Dict):
    """Analyze and display generative test results"""
    
    test_name = results_data.get('test_name', 'Unknown')
    results = results_data.get('results', [])
    total_time = results_data.get('total_time_seconds', 0)
    delay_seconds = results_data.get('delay_seconds', 0)
    
    if not results:
        print("[FAIL] No results to analyze")
        return
    
    # Calculate aggregate metrics
    total_queries = len(results)
    successful = sum(1 for r in results if not r.get('error'))
    failed = total_queries - successful
    
    # Response time statistics
    response_times = [r.get('response_time_seconds', 0) for r in results]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    max_response_time = max(response_times) if response_times else 0
    
    # Token usage statistics
    token_counts = [r.get('total_tokens', 0) for r in results]
    avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0
    total_tokens = sum(token_counts)
    
    # BERTScore confidence distribution
    bertscore_available = sum(1 for r in results if r.get('bertscore_f1') is not None)
    if bertscore_available > 0:
        bert_scores = [r['bertscore_f1'] for r in results if r.get('bertscore_f1') is not None]
        avg_bertscore = sum(bert_scores) / len(bert_scores)
        
        confidence_dist = defaultdict(int)
        for r in results:
            conf = r.get('bertscore_confidence', 'unavailable')
            if conf != 'unavailable':
                confidence_dist[conf] += 1
    else:
        avg_bertscore = 0
        confidence_dist = {}
    
    # Manual scoring statistics
    manually_scored = [r for r in results if r.get('manual_score') is not None]
    if manually_scored:
        correct_answers = sum(1 for r in manually_scored if r.get('manual_score') == 'correct')
        accuracy = (correct_answers / len(manually_scored)) * 100
    else:
        accuracy = None
    
    # Search method distribution
    search_methods = defaultdict(int)
    for r in results:
        method = r.get('search_method', 'unknown')
        search_methods[method] += 1
    
    # Category performance
    category_metrics = defaultdict(lambda: {
        'count': 0, 
        'response_times': [], 
        'tokens': [],
        'bert_scores': []
    })
    
    for r in results:
        cat = r.get('category', 'uncategorized')
        category_metrics[cat]['count'] += 1
        category_metrics[cat]['response_times'].append(r.get('response_time_seconds', 0))
        category_metrics[cat]['tokens'].append(r.get('total_tokens', 0))
        if r.get('bertscore_f1'):
            category_metrics[cat]['bert_scores'].append(r['bertscore_f1'])
    
    # Print report
    print()
    print("=" * 70)
    print("GENERATIVE TEST ANALYSIS")
    print("=" * 70)
    print()
    print(f" Overall Performance:")
    print(f"   Total Queries: {total_queries}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print()
    print(f"  Timing & Resources:")
    print(f"   Avg Response Time: {avg_response_time:.2f}s (min={min_response_time:.2f}s, max={max_response_time:.2f}s)")
    print(f"   Delay Between Queries: {delay_seconds:.0f}s")
    print(f"   Total Test Time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print()
    print(f"   Avg Tokens per Query: {avg_tokens:.0f}")
    print(f"   Total Tokens Used: {total_tokens}")
    print()
    
    # BERTScore analysis
    if bertscore_available > 0:
        print(f" BERTScore Confidence Analysis:")
        print(f"   Queries with BERTScore: {bertscore_available}/{total_queries}")
        print(f"   Average BERTScore F1: {avg_bertscore:.3f}")
        print()
        print(f"   Confidence Distribution:")
        for level in ['great', 'good', 'marginal', 'not_confident']:
            count = confidence_dist.get(level, 0)
            pct = (count / bertscore_available * 100) if bertscore_available > 0 else 0
            emoji = "🟢" if level == "great" else "🟡" if level == "good" else "🟠" if level == "marginal" else ""
            threshold = "≥0.7" if level == "great" else "0.6-0.7" if level == "good" else "0.5-0.6" if level == "marginal" else "<0.5"
            print(f"      {emoji} {level:15s} ({threshold:8s}): {count:3d} ({pct:5.1f}%)")
        print()
    else:
        print(f"  BERTScore: Not available")
        print(f"   Install with: pip install bert-score")
        print()
    
    # Manual scoring
    if manually_scored:
        print(f"  Manual Scoring:")
        print(f"   Scored: {len(manually_scored)}/{total_queries}")
        print(f"   Accuracy: {accuracy:.1f}%")
        print()
    else:
        print(f" Manual Scoring: Not yet completed")
        print(f"   Run: python evaluation/manual_scoring.py --file {results_data.get('test_name', 'test')}.json")
        print()
    
    print(f" Search Method Distribution:")
    for method, count in sorted(search_methods.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_queries * 100) if total_queries > 0 else 0
        print(f"   {method:20s}: {count:3d} ({pct:5.1f}%)")
    print()
    
    if category_metrics:
        print(f" Performance by Category:")
        for cat, metrics in sorted(category_metrics.items(), key=lambda x: x[1]['count'], reverse=True):
            avg_time = sum(metrics['response_times']) / len(metrics['response_times'])
            avg_tok = sum(metrics['tokens']) / len(metrics['tokens'])
            avg_bert = sum(metrics['bert_scores']) / len(metrics['bert_scores']) if metrics['bert_scores'] else None
            
            print(f"   {cat:15s}: {metrics['count']:3d} queries, "
                  f"time={avg_time:.2f}s, tokens={avg_tok:.0f}", end="")
            if avg_bert:
                print(f", bert={avg_bert:.3f}")
            else:
                print()
        print()
    
    # Slowest queries
    print(" Slowest Queries (Top 5):")
    slowest = sorted(results, key=lambda x: x.get('response_time_seconds', 0), reverse=True)[:5]
    for i, r in enumerate(slowest, 1):
        q_id = r.get('query_id', '?')
        question = r.get('question', '')[:50]
        time_s = r.get('response_time_seconds', 0)
        method = r.get('search_method', '?')
        print(f"   {i}. [{q_id}] {time_s:.2f}s ({method}): {question}...")
    print()
    
    # Fastest queries
    print(" Fastest Queries (Top 5):")
    fastest = sorted(results, key=lambda x: x.get('response_time_seconds', 0))[:5]
    for i, r in enumerate(fastest, 1):
        q_id = r.get('query_id', '?')
        question = r.get('question', '')[:50]
        time_s = r.get('response_time_seconds', 0)
        method = r.get('search_method', '?')
        print(f"   {i}. [{q_id}] {time_s:.2f}s ({method}): {question}...")
    print()
    
    # Best BERTScore
    if bertscore_available > 0:
        print(" Highest BERTScore (Top 5):")
        best_bert = sorted([r for r in results if r.get('bertscore_f1')], 
                          key=lambda x: x['bertscore_f1'], reverse=True)[:5]
        for i, r in enumerate(best_bert, 1):
            q_id = r.get('query_id', '?')
            question = r.get('question', '')[:50]
            bert = r.get('bertscore_f1', 0)
            conf = r.get('bertscore_confidence', '?')
            print(f"   {i}. [{q_id}] {bert:.3f} ({conf}): {question}...")
        print()
    
    print("=" * 70)
    print(" Summary:")
    print("=" * 70)
    print(f"Total Queries: {total_queries}")
    print(f"Average Response Time: {avg_response_time:.2f}s")
    print(f"Average Tokens: {avg_tokens:.0f}")
    if bertscore_available > 0:
        print(f"Average BERTScore: {avg_bertscore:.3f}")
    if manually_scored:
        print(f"Manual Accuracy: {accuracy:.1f}%")
    else:
        print(f"Manual Scoring: Pending")
    print("=" * 70)
    print()
    print(" Next Steps:")
    if not manually_scored:
        print(f"   1. Run manual scoring: python evaluation/manual_scoring.py --file raw_results/{results_data.get('test_name', 'test')}.json")
    print(f"   2. Review answers in: evaluation/raw_results/{results_data.get('test_name', 'test')}.json")
    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_generative_test.py <results_file.json>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    
    if not Path(results_file).exists():
        print(f"[FAIL] File not found: {results_file}")
        sys.exit(1)
    
    print(f"[FILE] Loaded results from: {results_file}")
    results_data = load_results(results_file)
    
    analyze_generative_test(results_data)


if __name__ == "__main__":
    main()
