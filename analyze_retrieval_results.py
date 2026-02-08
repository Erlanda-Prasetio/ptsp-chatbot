"""
Detailed Retrieval Test Analysis
Analyzes results by search method, category, and dataset
"""
import csv
import json
from collections import defaultdict
from typing import Dict, List

RESULTS_FILE = "evaluation/retrieval_test_madam_results.csv"

def analyze_results():
    """Analyze retrieval test results"""
    
    # Read results
    results = []
    with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        results = list(reader)
    
    # Parse metrics
    for r in results:
        r['precision'] = float(r['precision'])
        r['recall'] = float(r['recall'])
        r['f1'] = float(r['f1'])
        r['retrieved_count'] = int(r['retrieved_count'])
        r['relevant_count'] = int(r['relevant_count'])
    
    print("=" * 90)
    print("[STATS] RETRIEVAL TEST DETAILED ANALYSIS")
    print("=" * 90)
    print()
    
    # 1. BY SEARCH METHOD
    print("1⃣  PERFORMANCE BY SEARCH METHOD")
    print("-" * 90)
    method_stats = defaultdict(lambda: {"f1": [], "precision": [], "recall": [], "count": 0})
    
    for r in results:
        method = r['search_method']
        method_stats[method]['f1'].append(r['f1'])
        method_stats[method]['precision'].append(r['precision'])
        method_stats[method]['recall'].append(r['recall'])
        method_stats[method]['count'] += 1
    
    for method in sorted(method_stats.keys()):
        stats = method_stats[method]
        avg_f1 = sum(stats['f1']) / len(stats['f1'])
        avg_prec = sum(stats['precision']) / len(stats['precision'])
        avg_rec = sum(stats['recall']) / len(stats['recall'])
        high = sum(1 for f in stats['f1'] if f > 0.7)
        mid = sum(1 for f in stats['f1'] if 0.3 < f <= 0.7)
        low = sum(1 for f in stats['f1'] if 0 < f <= 0.3)
        
        print(f"  {method:20s}")
        print(f"    Count:        {stats['count']:2d} queries")
        print(f"    Avg F1:       {avg_f1:.3f}")
        print(f"    Avg Precision: {avg_prec:.3f}")
        print(f"    Avg Recall:   {avg_rec:.3f}")
        print(f"    High (>0.7):  {high} | Mid (0.3-0.7): {mid} | Low (<0.3): {low}")
        print()
    
    # 2. BY CATEGORY
    print("2⃣  PERFORMANCE BY QUESTION CATEGORY")
    print("-" * 90)
    cat_stats = defaultdict(lambda: {"f1": [], "count": 0})
    
    for r in results:
        cat = r['category']
        cat_stats[cat]['f1'].append(r['f1'])
        cat_stats[cat]['count'] += 1
    
    for cat in sorted(cat_stats.keys()):
        stats = cat_stats[cat]
        avg_f1 = sum(stats['f1']) / len(stats['f1'])
        high = sum(1 for f in stats['f1'] if f > 0.7)
        perfect = sum(1 for f in stats['f1'] if f == 1.0)
        
        print(f"  {cat:15s}: Avg F1={avg_f1:.3f} | Count={stats['count']:2d} | Perfect={perfect} | High={high}")
    print()
    
    # 3. BY DATASET
    print("3⃣  PERFORMANCE BY DATASET (OLD vs NEW)")
    print("-" * 90)
    dataset_stats = defaultdict(lambda: {"f1": [], "count": 0})
    
    for r in results:
        dataset = "OLD" if r['query_id'].startswith('old_') else "NEW"
        dataset_stats[dataset]['f1'].append(r['f1'])
        dataset_stats[dataset]['count'] += 1
    
    for ds in ["OLD", "NEW"]:
        if ds in dataset_stats:
            stats = dataset_stats[ds]
            avg_f1 = sum(stats['f1']) / len(stats['f1'])
            high = sum(1 for f in stats['f1'] if f > 0.7)
            perfect = sum(1 for f in stats['f1'] if f == 1.0)
            
            print(f"  {ds} Dataset: Avg F1={avg_f1:.3f} | Count={stats['count']:2d} | Perfect={perfect} | High={high}")
    print()
    
    # 4. WORST PERFORMERS
    print("4⃣  LOWEST PERFORMING QUERIES (F1 = 0.0)")
    print("-" * 90)
    worst = sorted([r for r in results if r['f1'] == 0.0], key=lambda x: x['query_id'])
    for r in worst[:10]:
        print(f"  {r['query_id']:10s} [{r['category']:12s}] {r['question'][:50]}...")
        print(f"             Method: {r['search_method']:15s} | Relevant: {r['relevant_count']}, Retrieved: {r['retrieved_count']}")
    print(f"  Total: {len(worst)} queries with F1=0.0")
    print()
    
    # 5. BEST PERFORMERS
    print("5⃣  HIGHEST PERFORMING QUERIES (F1 = 1.0)")
    print("-" * 90)
    best = sorted([r for r in results if r['f1'] == 1.0], key=lambda x: x['query_id'])
    print(f"  Perfect Match: {len(best)} queries")
    for method in sorted(set(r['search_method'] for r in best)):
        count = sum(1 for r in best if r['search_method'] == method)
        print(f"    {method:15s}: {count} queries")
    print()
    
    # 6. STATISTICS SUMMARY
    print("6⃣  OVERALL STATISTICS")
    print("-" * 90)
    all_f1 = [r['f1'] for r in results]
    all_prec = [r['precision'] for r in results]
    all_rec = [r['recall'] for r in results]
    
    print(f"  Total Queries:      {len(results)}")
    print(f"  Perfect (F1=1.0):   {sum(1 for f in all_f1 if f == 1.0)} queries")
    print(f"  High (F1>0.7):      {sum(1 for f in all_f1 if 0.7 < f < 1.0)} queries")
    print(f"  Medium (0.3-0.7):   {sum(1 for f in all_f1 if 0.3 <= f <= 0.7)} queries")
    print(f"  Low (0<F1<0.3):     {sum(1 for f in all_f1 if 0 < f < 0.3)} queries")
    print(f"  Zero (F1=0.0):      {sum(1 for f in all_f1 if f == 0.0)} queries")
    print()
    print(f"  Mean F1:            {sum(all_f1) / len(all_f1):.3f}")
    print(f"  Mean Precision:     {sum(all_prec) / len(all_prec):.3f}")
    print(f"  Mean Recall:        {sum(all_rec) / len(all_rec):.3f}")
    print()
    
    # 7. CATEGORY BREAKDOWN
    print("7⃣  DETAILED CATEGORY BREAKDOWN")
    print("-" * 90)
    for cat in sorted(cat_stats.keys()):
        queries = [r for r in results if r['category'] == cat]
        f1_scores = [r['f1'] for r in queries]
        perfect = sum(1 for f in f1_scores if f == 1.0)
        high = sum(1 for f in f1_scores if 0.7 < f < 1.0)
        mid = sum(1 for f in f1_scores if 0.3 <= f <= 0.7)
        low = sum(1 for f in f1_scores if 0 < f < 0.3)
        zero = sum(1 for f in f1_scores if f == 0.0)
        
        print(f"  {cat:12s}: Perfect={perfect:2d} | High={high:2d} | Mid={mid:2d} | Low={low:2d} | Zero={zero:2d}")
    
    print()
    print("=" * 90)

if __name__ == "__main__":
    analyze_results()
