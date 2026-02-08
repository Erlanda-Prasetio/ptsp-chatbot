"""Quick analysis of baseline evaluation results."""

import json
from pathlib import Path
from collections import Counter

def analyze_baseline():
    """Analyze baseline_old_dataset.json results."""
    
    results_file = Path('evaluation/raw_results/baseline_old_dataset.json')
    
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    meta = data['metadata']
    results = data['results']
    
    print("\n" + "="*70)
    print(" BASELINE EVALUATION RESULTS")
    print("="*70)
    
    # Overall stats
    print(f"\nOverall Performance:")
    print(f"   Total Queries: {meta['total_queries']}")
    print(f"   Successful: {meta['successful_queries']}")
    print(f"   Failed: {meta['failed_queries']}")
    
    stats = meta['summary_statistics']
    print(f"\n  Timing & Resources:")
    print(f"   Avg Response Time: {stats['avg_response_time']}s")
    print(f"   Avg Tokens: {stats['avg_tokens']:.0f}")
    print(f"   Total Evaluation Time: {stats['total_evaluation_time']:.1f}s ({stats['total_evaluation_time']/60:.1f} min)")
    
    print(f"\n Quality Metrics:")
    print(f"   Avg Confidence: {stats['avg_confidence']:.3f}")
    
    dist = meta['query_distribution']
    print(f"\n Query Distribution:")
    print(f"   OLD Dataset: {dist['old_dataset']} questions")
    print(f"   NEW Dataset: {dist['new_dataset']} questions")
    
    # Analyze retrieval metrics
    successful = [r for r in results if 'error' not in r]
    
    precisions = [r.get('precision') for r in successful if r.get('precision') is not None]
    recalls = [r.get('recall') for r in successful if r.get('recall') is not None]
    f1s = [r.get('f1_score') for r in successful if r.get('f1_score') is not None]
    
    if precisions:
        print(f"\n Retrieval Metrics (n={len(precisions)}):")
        print(f"   Precision: {sum(precisions)/len(precisions):.3f} (min={min(precisions):.3f}, max={max(precisions):.3f})")
    if recalls:
        print(f"   Recall:    {sum(recalls)/len(recalls):.3f} (min={min(recalls):.3f}, max={max(recalls):.3f})")
    if f1s:
        print(f"   F1-Score:  {sum(f1s)/len(f1s):.3f} (min={min(f1s):.3f}, max={max(f1s):.3f})")
    
    # Phase distribution
    methods = [r.get('search_method', 'unknown') for r in successful]
    method_counts = Counter(methods)
    
    print(f"\n Search Method Distribution:")
    for method, count in method_counts.most_common():
        pct = (count / len(successful)) * 100
        print(f"   {method:20s}: {count:2d} ({pct:5.1f}%)")
    
    # Category breakdown
    categories = {}
    for r in results:
        cat = r.get('category', 'Unknown')
        if cat not in categories:
            categories[cat] = {'total': 0, 'with_metrics': 0, 'avg_f1': []}
        categories[cat]['total'] += 1
        if r.get('f1_score') is not None:
            categories[cat]['with_metrics'] += 1
            categories[cat]['avg_f1'].append(r['f1_score'])
    
    print(f"\n Performance by Category:")
    for cat, stats in sorted(categories.items()):
        if stats['avg_f1']:
            avg_f1 = sum(stats['avg_f1']) / len(stats['avg_f1'])
            print(f"   {cat:15s}: {stats['total']:2d} questions, F1={avg_f1:.3f}")
        else:
            print(f"   {cat:15s}: {stats['total']:2d} questions, F1=N/A")
    
    # Issues identified
    zero_precision = sum(1 for p in precisions if p == 0.0)
    zero_recall = sum(1 for r in recalls if r == 0.0)
    
    print(f"\n Issues Identified:")
    print(f"   Zero Precision: {zero_precision}/{len(precisions)} ({zero_precision/len(precisions)*100:.1f}%)")
    print(f"   Zero Recall:    {zero_recall}/{len(recalls)} ({zero_recall/len(recalls)*100:.1f}%)")
    
    internet_fallback = method_counts.get('internet_fallback', 0)
    if internet_fallback > 0:
        print(f"   Internet Fallback: {internet_fallback}/{len(successful)} ({internet_fallback/len(successful)*100:.1f}%)")
        print(f"   [WARN]  High fallback rate indicates insufficient local chunks!")
    
    print("\n" + "="*70)
    print(" Next Steps:")
    print("="*70)
    print("1. Manual scoring: python evaluation/manual_scoring.py --file raw_results/baseline_old_dataset.json")
    print("2. Prepare new dataset for Experiment 2")
    print("3. Implement MADAM for Experiment 3")
    print("="*70 + "\n")
    
    return data

if __name__ == '__main__':
    analyze_baseline()
