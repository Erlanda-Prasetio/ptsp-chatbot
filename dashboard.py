"""
Dashboard for MADAM Hybrid System - Formatted consistently with other dashboards
Individual analysis of MADAM retrieval test results
"""
import csv
from collections import defaultdict
from typing import Dict, List

CSV_FILE = "evaluation/retrieval_test_madam_results.csv"

def load_csv(filepath: str) -> List[Dict]:
    """Load CSV file"""
    results = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['f1'] = float(row.get('f1', 0))
            row['precision'] = float(row.get('precision', 0))
            row['recall'] = float(row.get('recall', 0))
            row['retrieval_time'] = float(row.get('retrieval_time', 0))
            results.append(row)
    return results

def categorize_f1(f1: float) -> str:
    """Categorize F1 score"""
    if f1 == 1.0:
        return "Perfect"
    elif f1 > 0.7:
        return "High"
    elif f1 > 0.3:
        return "Medium"
    elif f1 > 0.0:
        return "Low"
    else:
        return "Failed"

def main():
    results = load_csv(CSV_FILE)
    
    print("\n" + "=" * 120)
    print("MADAM HYBRID RAG SYSTEM - RETRIEVAL TEST DASHBOARD".center(120))
    print("=" * 120)
    
    # Overall Statistics
    print("\n" + "" * 118 + "")
    print("" + "[STATS] OVERALL STATISTICS".center(118) + "")
    print("" + "" * 118 + "")
    
    total = len(results)
    mean_f1 = sum(r['f1'] for r in results) / total if results else 0
    mean_precision = sum(r['precision'] for r in results) / total if results else 0
    mean_recall = sum(r['recall'] for r in results) / total if results else 0
    mean_time = sum(r['retrieval_time'] for r in results) / total if results else 0
    
    perfect = len([r for r in results if r['f1'] == 1.0])
    high = len([r for r in results if 0.7 < r['f1'] < 1.0])
    medium = len([r for r in results if 0.3 <= r['f1'] <= 0.7])
    low = len([r for r in results if 0 < r['f1'] < 0.3])
    failed = len([r for r in results if r['f1'] == 0.0])
    
    min_time = min(r['retrieval_time'] for r in results) if results else 0
    max_time = max(r['retrieval_time'] for r in results) if results else 0
    
    print(f"\n Total Queries:        {total:3d}")
    print(f" Mean F1 Score:        {mean_f1:.3f}")
    print(f" Mean Precision:       {mean_precision:.3f}")
    print(f" Mean Recall:          {mean_recall:.3f}")
    print(f" Mean Time:            {mean_time:.2f}s")
    print(f" Min/Max Time:         {min_time:.2f}s / {max_time:.2f}s")
    
    print(f"\n Perfect (1.0):        {perfect:3d} ({perfect/total*100:5.1f}%)")
    print(f" High (0.7-1.0):       {high:3d} ({high/total*100:5.1f}%)")
    print(f" Medium (0.3-0.7):     {medium:3d} ({medium/total*100:5.1f}%)")
    print(f" Low (0-0.3):          {low:3d} ({low/total*100:5.1f}%)")
    print(f" Failed (0.0):         {failed:3d} ({failed/total*100:5.1f}%)")
    
    # F1 Distribution Visual
    print("\n" + "" * 118 + "")
    print("" + " F1 SCORE DISTRIBUTION".center(118) + "")
    print("" + "" * 118 + "")
    
    print(f"\n Perfect      {perfect:2d} ({perfect/total*100:5.1f}%)  {'' * int(perfect/total*40):<40}")
    print(f" High         {high:2d} ({high/total*100:5.1f}%)  {'' * int(high/total*40):<40}")
    print(f" Medium       {medium:2d} ({medium/total*100:5.1f}%)  {'' * int(medium/total*40):<40}")
    print(f" Low          {low:2d} ({low/total*100:5.1f}%)  {'' * int(low/total*40):<40}")
    print(f" Failed       {failed:2d} ({failed/total*100:5.1f}%)  {'' * int(failed/total*40):<40}")
    
    # Search Method Performance
    print("\n" + "" * 118 + "")
    print("" + " SEARCH METHOD PERFORMANCE".center(118) + "")
    print("" + "" * 118 + "")
    
    method_stats = defaultdict(list)
    for r in results:
        method_stats[r['search_method']].append(r['f1'])
    
    method_ranks = sorted(method_stats.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)
    
    for method, f1_scores in method_ranks:
        avg_f1 = sum(f1_scores) / len(f1_scores)
        avg_time = sum(r['retrieval_time'] for r in results if r['search_method'] == method) / len(f1_scores)
        min_tm = min(r['retrieval_time'] for r in results if r['search_method'] == method)
        max_tm = max(r['retrieval_time'] for r in results if r['search_method'] == method)
        perfect_m = len([f for f in f1_scores if f == 1.0])
        failed_m = len([f for f in f1_scores if f == 0.0])
        
        print(f"\n {method}")
        print(f"   Count:        {len(f1_scores)}")
        print(f"   Avg F1:       {avg_f1:.3f}")
        print(f"   Avg Time:     {avg_time:.2f}s (min: {min_tm:.2f}s, max: {max_tm:.2f}s)")
        print(f"   Perfect:      {perfect_m}")
        print(f"   Failed:       {failed_m}")
    
    # Category Performance
    print("\n" + "" * 118 + "")
    print("" + " CATEGORY PERFORMANCE".center(118) + "")
    print("" + "" * 118 + "")
    
    cat_stats = defaultdict(list)
    for r in results:
        cat_stats[r['category']].append(r['f1'])
    
    cat_ranks = sorted(cat_stats.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)
    
    print(f"\n{'Category':<15}  {'Count':<5}  {'Avg F1':<7}  {'Perfect':<7}  {'Failed':<7}  {'Distribution':<40}")
    print("" * 100)
    
    for cat, f1_scores in cat_ranks:
        avg_f1 = sum(f1_scores) / len(f1_scores)
        perfect_c = len([f for f in f1_scores if f == 1.0])
        failed_c = len([f for f in f1_scores if f == 0.0])
        bar_width = int(len(f1_scores) / total * 40)
        bar = '' * int(perfect_c / len(f1_scores) * bar_width) + '' * (bar_width - int(perfect_c / len(f1_scores) * bar_width))
        
        print(f"{cat:<15}  {len(f1_scores):<5}  {avg_f1:<7.3f}  {perfect_c:<7}  {failed_c:<7}  {bar:<40}")
    
    # Dataset Source Performance
    print("\n" + "" * 118 + "")
    print("" + "  DATASET SOURCE PERFORMANCE".center(118) + "")
    print("" + "" * 118 + "")
    
    dataset_stats = defaultdict(list)
    for r in results:
        dataset_stats[r.get('dataset_source', 'N/A')].append(r['f1'])
    
    for dataset, f1_scores in sorted(dataset_stats.items()):
        avg_f1 = sum(f1_scores) / len(f1_scores)
        perfect_d = len([f for f in f1_scores if f == 1.0])
        failed_d = len([f for f in f1_scores if f == 0.0])
        print(f" {dataset:<10}: Count={len(f1_scores):2d} | Avg F1={avg_f1:.3f} | Perfect={perfect_d:2d} | Failed={failed_d:2d}")
    
    # Top Performers
    print("\n" + "" * 118 + "")
    print("" + "[OK] TOP 10 BEST PERFORMING QUERIES (F1=1.0)".center(118) + "")
    print("" + "" * 118 + "")
    
    top_queries = sorted([r for r in results if r['f1'] == 1.0], 
                        key=lambda x: float(x.get('retrieval_time', 0)))[:10]
    
    for idx, r in enumerate(top_queries, 1):
        print(f"\n{idx:2d}. {r.get('query_id', 'N/A'):10s} [{r.get('category', 'N/A'):12s}] {r.get('search_method', 'N/A'):20s} {float(r.get('retrieval_time', 0)):6.2f}s")
        print(f"    Q: {r.get('question', 'N/A')[:80]}")
    
    # Worst Performers
    print("\n" + "" * 118 + "")
    print("" + "[FAIL] BOTTOM 10 WORST PERFORMING QUERIES (F1=0.0)".center(118) + "")
    print("" + "" * 118 + "")
    
    bottom_queries = sorted([r for r in results if r['f1'] == 0.0], 
                           key=lambda x: float(x.get('retrieval_time', 0)), reverse=True)[:10]
    
    for idx, r in enumerate(bottom_queries, 1):
        print(f"\n{idx:2d}. {r.get('query_id', 'N/A'):10s} [{r.get('category', 'N/A'):12s}] {r.get('search_method', 'N/A'):20s} {float(r.get('retrieval_time', 0)):6.2f}s")
        print(f"    Q: {r.get('question', 'N/A')[:80]}")
    
    # Slowest Queries
    print("\n" + "" * 118 + "")
    print("" + "[TIME]  TOP 10 SLOWEST QUERIES".center(118) + "")
    print("" + "" * 118 + "")
    
    slowest = sorted(results, key=lambda x: float(x.get('retrieval_time', 0)), reverse=True)[:10]
    
    for idx, r in enumerate(slowest, 1):
        f1 = float(r.get('f1', 0))
        print(f"\n{idx:2d}. {r.get('query_id', 'N/A'):10s} [{r.get('category', 'N/A'):12s}] {r.get('search_method', 'N/A'):20s} {float(r.get('retrieval_time', 0)):6.2f}s (F1={f1:.2f})")
        print(f"    Q: {r.get('question', 'N/A')[:80]}")
    
    # Fastest Queries
    print("\n" + "" * 118 + "")
    print("" + " TOP 10 FASTEST QUERIES".center(118) + "")
    print("" + "" * 118 + "")
    
    fastest = sorted(results, key=lambda x: float(x.get('retrieval_time', 0)))[:10]
    
    for idx, r in enumerate(fastest, 1):
        f1 = float(r.get('f1', 0))
        print(f"\n{idx:2d}. {r.get('query_id', 'N/A'):10s} [{r.get('category', 'N/A'):12s}] {r.get('search_method', 'N/A'):20s} {float(r.get('retrieval_time', 0)):6.2f}s (F1={f1:.2f})")
        print(f"    Q: {r.get('question', 'N/A')[:80]}")
    
    # Insights & Recommendations
    print("\n" + "" * 118 + "")
    print("" + "[INFO] INSIGHTS & RECOMMENDATIONS".center(118) + "")
    print("" + "" * 118 + "")
    
    print(f"\n [OK] STRENGTHS:")
    print(f"    • {perfect} queries ({perfect/total*100:.1f}%) achieve perfect retrieval (F1=1.0)")
    print(f"    • Average retrieval time: {mean_time:.2f}s")
    best_method = max(method_ranks, key=lambda x: sum(x[1])/len(x[1]))
    best_method_f1 = sum(best_method[1]) / len(best_method[1])
    print(f"    • Best method: {best_method[0]} with F1={best_method_f1:.3f}")
    best_cat = max(cat_ranks, key=lambda x: sum(x[1])/len(x[1]))
    best_cat_f1 = sum(best_cat[1]) / len(best_cat[1])
    print(f"    • Best category: {best_cat[0]} with F1={best_cat_f1:.3f}")
    
    print(f"\n [FAIL] WEAKNESSES:")
    print(f"    • {failed} queries ({failed/total*100:.1f}%) have complete failures (F1=0.0)")
    worst_method = min(method_ranks, key=lambda x: sum(x[1])/len(x[1]))
    worst_method_f1 = sum(worst_method[1]) / len(worst_method[1])
    print(f"    • Weakest method: {worst_method[0]} with F1={worst_method_f1:.3f}")
    worst_cat = min(cat_ranks, key=lambda x: sum(x[1])/len(x[1]))
    worst_cat_f1 = sum(worst_cat[1]) / len(worst_cat[1])
    print(f"    • Weakest category: {worst_cat[0]} with F1={worst_cat_f1:.3f}")
    print(f"    • Slowest method average: {max(method_ranks, key=lambda x: sum(float(r['retrieval_time']) for r in results if r['search_method'] == x[0])/len(x[1]))[0]}")
    
    print(f"\n [TARGET] RECOMMENDATIONS:")
    print(f"    1. Focus on improving {worst_cat[0]} category performance")
    print(f"    2. Investigate why {worst_method[0]} underperforms")
    print(f"    3. Optimize retrieval time for slow queries")
    print(f"    4. Leverage strengths in {best_method[0]} method for more queries")
    
    print("\n" + "=" * 120 + "\n")

if __name__ == "__main__":
    main()
