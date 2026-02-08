#!/usr/bin/env python3
"""
Analyze generative test results and create summary report with CSV export.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def analyze_results(results_file):
    """Analyze the generative test results."""
    
    # Read results
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data['results']
    total_queries = len(results)
    
    # Initialize counters
    stats = {
        'total': total_queries,
        'success': 0,
        'timeout': 0,
        'empty_response': 0,
        'no_sources': 0,
        'search_methods': defaultdict(int),
        'response_times': [],
        'bertscore_scores': [],
        'sources_counts': [],
        'errors': defaultdict(int)
    }
    
    csv_rows = []
    
    # Analyze each result
    for result in results:
        query_id = result['query_id']
        question = result['question']
        ground_truth = result['ground_truth']
        answer = result['answer']
        search_method = result['search_method']
        sources_count = result['sources_count']
        response_time = result['response_time_seconds']
        bertscore = result['bertscore_f1']
        error = result['error']
        
        # Count errors
        if error:
            stats['errors'][error] += 1
            if 'timeout' in error.lower():
                stats['timeout'] += 1
        elif not answer or answer.strip() == '':
            stats['empty_response'] += 1
        else:
            stats['success'] += 1
        
        # Count search methods
        stats['search_methods'][search_method] += 1
        
        # Collect metrics
        if response_time:
            stats['response_times'].append(response_time)
        if sources_count:
            stats['sources_counts'].append(sources_count)
        if bertscore is not None:
            stats['bertscore_scores'].append(bertscore)
        
        # Track no sources
        if sources_count == 0:
            stats['no_sources'] += 1
        
        # Create CSV row
        csv_rows.append({
            'id': query_id,
            'question': question[:100],  # First 100 chars
            'ground_truth_preview': ground_truth[:100],
            'answer_preview': answer[:100] if answer else '',
            'search_method': search_method,
            'sources_retrieved': sources_count,
            'response_time_seconds': response_time,
            'bertscore_f1': bertscore if bertscore is not None else '',
            'bertscore_confidence': result.get('bertscore_confidence', ''),
            'error': error if error else 'success'
        })
    
    return stats, csv_rows, results

def print_analysis(stats, csv_rows, results_file, results=None):
    """Print formatted analysis report."""
    
    print("\n" + "="*80)
    print("[STATS] GENERATIVE TEST RESULTS ANALYSIS")
    print("="*80)
    
    print(f"\n[FILE] File: {results_file}")
    print(f" Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary Stats
    print(f"\n[METRIC] OVERALL STATISTICS")
    print("-" * 80)
    print(f"  Total Queries:        {stats['total']}")
    print(f"  [OK] Successful:        {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"  [TIME]  Timeout:           {stats['timeout']} ({stats['timeout']/stats['total']*100:.1f}%)")
    print(f"   Empty Response:    {stats['empty_response']} ({stats['empty_response']/stats['total']*100:.1f}%)")
    print(f"  [SEARCH] No Sources Found:  {stats['no_sources']} ({stats['no_sources']/stats['total']*100:.1f}%)")
    
    # Error breakdown
    print(f"\n[FAIL] ERRORS")
    print("-" * 80)
    for error_type, count in sorted(stats['errors'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {error_type}: {count}")
    
    # Search methods
    print(f"\n SEARCH METHODS USED")
    print("-" * 80)
    for method, count in sorted(stats['search_methods'].items(), key=lambda x: x[1], reverse=True):
        pct = count / stats['total'] * 100
        print(f"  {method:20s}: {count:3d} ({pct:5.1f}%)")
    
    # Performance metrics
    print(f"\n PERFORMANCE METRICS")
    print("-" * 80)
    
    if stats['response_times']:
        avg_time = sum(stats['response_times']) / len(stats['response_times'])
        min_time = min(stats['response_times'])
        max_time = max(stats['response_times'])
        print(f"  Response Time (seconds):")
        print(f"    Average:  {avg_time:.2f}s")
        print(f"    Minimum:  {min_time:.2f}s")
        print(f"    Maximum:  {max_time:.2f}s")
    
    if stats['sources_counts']:
        avg_sources = sum(stats['sources_counts']) / len(stats['sources_counts'])
        min_sources = min(stats['sources_counts'])
        max_sources = max(stats['sources_counts'])
        print(f"  Sources Retrieved:")
        print(f"    Average:  {avg_sources:.2f}")
        print(f"    Minimum:  {min_sources}")
        print(f"    Maximum:  {max_sources}")
    
    # BERTScore analysis
    print(f"\n[TARGET] BERTSCORE ANALYSIS")
    print("-" * 80)
    
    if stats['bertscore_scores']:
        avg_bert = sum(stats['bertscore_scores']) / len(stats['bertscore_scores'])
        min_bert = min(stats['bertscore_scores'])
        max_bert = max(stats['bertscore_scores'])
        
        # Count confidence levels
        great = len([s for s in stats['bertscore_scores'] if s >= 0.7])
        good = len([s for s in stats['bertscore_scores'] if 0.6 <= s < 0.7])
        marginal = len([s for s in stats['bertscore_scores'] if 0.5 <= s < 0.6])
        not_confident = len([s for s in stats['bertscore_scores'] if s < 0.5])
        
        print(f"  Average BERTScore:    {avg_bert:.3f}")
        print(f"  Minimum BERTScore:    {min_bert:.3f}")
        print(f"  Maximum BERTScore:    {max_bert:.3f}")
        print(f"\n  Confidence Distribution:")
        print(f"    🟢 Great (≥0.7):      {great} ({great/len(stats['bertscore_scores'])*100:.1f}%)")
        print(f"    🟡 Good (0.6-0.7):    {good} ({good/len(stats['bertscore_scores'])*100:.1f}%)")
        print(f"    🟠 Marginal (0.5-0.6): {marginal} ({marginal/len(stats['bertscore_scores'])*100:.1f}%)")
        print(f"     Not Confident (<0.5): {not_confident} ({not_confident/len(stats['bertscore_scores'])*100:.1f}%)")
    else:
        print(f"  [WARN]  No BERTScore data available")
    
    # Bottom performers
    print(f"\n[WARN]  QUERIES WITH ISSUES")
    print("-" * 80)
    if results:
        problem_queries = [r for r in results if r['error'] or not r['answer']]
        print(f"  Total problematic queries: {len(problem_queries)}")
        
        for i, result in enumerate(problem_queries[:5], 1):
            print(f"\n  [{i}] {result['query_id']}: {result['question'][:60]}...")
            print(f"      Error: {result['error'] if result['error'] else 'Empty response'}")
            print(f"      Response Time: {result['response_time_seconds']:.2f}s")
        
        if len(problem_queries) > 5:
            print(f"\n  ... and {len(problem_queries)-5} more problematic queries")
    
    print("\n" + "="*80)

def export_to_csv(csv_rows, output_file):
    """Export analysis to CSV."""
    if not csv_rows:
        print(f"[FAIL] No data to export")
        return
    
    # Create output directory if needed
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write CSV
    fieldnames = csv_rows[0].keys()
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
    
    print(f"\n[OK] Results exported to: {output_file}")

def main():
    results_file = Path('d:/backup/ptspRag/evaluation/raw_results/generative_25_questions.json')
    
    if not results_file.exists():
        print(f"[FAIL] Results file not found: {results_file}")
        return
    
    # Analyze
    stats, csv_rows, results = analyze_results(results_file)
    
    # Print report
    print_analysis(stats, csv_rows, results_file, results)
    
    # Export to CSV
    csv_file = results_file.parent / 'generative_25_questions_analysis.csv'
    export_to_csv(csv_rows, csv_file)
    
    print("\n[OK] Analysis complete!")

if __name__ == '__main__':
    main()
