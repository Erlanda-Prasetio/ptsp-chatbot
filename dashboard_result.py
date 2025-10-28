"""
Dashboard for retrieval_test_result.csv
Individual analysis of retrieval test results
"""
import csv
from collections import defaultdict
from typing import Dict, List

CSV_FILE = "evaluation/retrieval_test_result.csv"

def load_csv(filepath: str) -> List[Dict]:
    """Load CSV file"""
    results = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['f1_score'] = float(row.get('f1_score', 0))
            row['precision'] = float(row.get('precision', 0))
            row['recall'] = float(row.get('recall', 0))
            row['retrieval_time_seconds'] = float(row.get('retrieval_time_seconds', 0))
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
    print("RETRIEVAL TEST RESULT - DETAILED DASHBOARD".center(120))
    print("=" * 120)
    
    # Overall Statistics
    print("\n╔" + "═" * 118 + "╗")
    print("║" + "📊 OVERALL STATISTICS".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    
    total = len(results)
    mean_f1 = sum(r['f1_score'] for r in results) / total if results else 0
    mean_precision = sum(r['precision'] for r in results) / total if results else 0
    mean_recall = sum(r['recall'] for r in results) / total if results else 0
    mean_time = sum(r['retrieval_time_seconds'] for r in results) / total if results else 0
    
    perfect = len([r for r in results if r['f1_score'] == 1.0])
    high = len([r for r in results if 0.7 < r['f1_score'] < 1.0])
    medium = len([r for r in results if 0.3 <= r['f1_score'] <= 0.7])
    low = len([r for r in results if 0 < r['f1_score'] < 0.3])
    failed = len([r for r in results if r['f1_score'] == 0.0])
    
    min_time = min(r['retrieval_time_seconds'] for r in results) if results else 0
    max_time = max(r['retrieval_time_seconds'] for r in results) if results else 0
    
    print(f"\n│ Total Queries:        {total:3d}")
    print(f"│ Mean F1 Score:        {mean_f1:.3f}")
    print(f"│ Mean Precision:       {mean_precision:.3f}")
    print(f"│ Mean Recall:          {mean_recall:.3f}")
    print(f"│ Mean Time:            {mean_time:.2f}s")
    print(f"│ Min/Max Time:         {min_time:.2f}s / {max_time:.2f}s")
    
    print(f"\n│ Perfect (1.0):        {perfect:3d} ({perfect/total*100:5.1f}%)")
    print(f"│ High (0.7-1.0):       {high:3d} ({high/total*100:5.1f}%)")
    print(f"│ Medium (0.3-0.7):     {medium:3d} ({medium/total*100:5.1f}%)")
    print(f"│ Low (0-0.3):          {low:3d} ({low/total*100:5.1f}%)")
    print(f"│ Failed (0.0):         {failed:3d} ({failed/total*100:5.1f}%)")
    
    # F1 Distribution Visual
    print("\n╔" + "═" * 118 + "╗")
    print("║" + "📈 F1 SCORE DISTRIBUTION".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    
    categories = ['Perfect', 'High', 'Medium', 'Low', 'Failed']
    counts = [perfect, high, medium, low, failed]
    
    print()
    for cat, count in zip(categories, counts):
        pct = count / total * 100
        bar = "█" * int(count / 2)
        print(f"│ {cat:<10s} │ {count:>3d} ({pct:>5.1f}%) │ {bar:<25s}")
    
    # Search Method Performance
    print("\n╔" + "═" * 118 + "╗")
    print("║" + "🔍 SEARCH METHOD PERFORMANCE".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    
    methods = defaultdict(lambda: {'f1': [], 'time': [], 'count': 0})
    
    for r in results:
        method = r.get('search_method', 'unknown')
        methods[method]['f1'].append(r['f1_score'])
        methods[method]['time'].append(r['retrieval_time_seconds'])
        methods[method]['count'] += 1
    
    print()
    for method in sorted(methods.keys()):
        stats = methods[method]
        avg_f1 = sum(stats['f1']) / len(stats['f1']) if stats['f1'] else 0
        avg_time = sum(stats['time']) / len(stats['time']) if stats['time'] else 0
        min_t = min(stats['time']) if stats['time'] else 0
        max_t = max(stats['time']) if stats['time'] else 0
        perfect_m = len([f for f in stats['f1'] if f == 1.0])
        failed_m = len([f for f in stats['f1'] if f == 0.0])
        
        print(f"│ {method:20s}")
        print(f"│   Count:       {stats['count']:3d}")
        print(f"│   Avg F1:      {avg_f1:.3f}")
        print(f"│   Avg Time:    {avg_time:.2f}s (min: {min_t:.2f}s, max: {max_t:.2f}s)")
        print(f"│   Perfect:     {perfect_m:3d}")
        print(f"│   Failed:      {failed_m:3d}")
        print()
    
    # Category Performance
    print("╔" + "═" * 118 + "╗")
    print("║" + "📂 CATEGORY PERFORMANCE".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    
    cat_stats = defaultdict(lambda: {'f1': [], 'perfect': 0, 'failed': 0, 'count': 0})
    
    for r in results:
        cat = r.get('category', 'Unknown')
        f1 = r['f1_score']
        cat_stats[cat]['f1'].append(f1)
        cat_stats[cat]['count'] += 1
        if f1 == 1.0:
            cat_stats[cat]['perfect'] += 1
        elif f1 == 0.0:
            cat_stats[cat]['failed'] += 1
    
    print()
    print(f"{'Category':<15} │ {'Count':>5} │ {'Avg F1':>7} │ {'Perfect':>7} │ {'Failed':>7} │ {'Distribution':<30}")
    print("─" * 100)
    
    for cat in sorted(cat_stats.keys()):
        stats = cat_stats[cat]
        avg_f1 = sum(stats['f1']) / len(stats['f1']) if stats['f1'] else 0
        dist = "█" * int(stats['perfect'] / 2) + "░" * int(stats['failed'] / 2)
        print(f"{cat:<15} │ {stats['count']:>5} │ {avg_f1:>7.3f} │ {stats['perfect']:>7} │ {stats['failed']:>7} │ {dist:<30}")
    
    # Dataset Source
    print("\n╔" + "═" * 118 + "╗")
    print("║" + "🗂️  DATASET SOURCE PERFORMANCE".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    
    dataset_stats = defaultdict(lambda: {'f1': [], 'count': 0})
    
    for r in results:
        ds = r.get('dataset_source', 'Unknown')
        dataset_stats[ds]['f1'].append(r['f1_score'])
        dataset_stats[ds]['count'] += 1
    
    print()
    for ds in sorted(dataset_stats.keys()):
        stats = dataset_stats[ds]
        avg_f1 = sum(stats['f1']) / len(stats['f1']) if stats['f1'] else 0
        perfect_ds = len([f for f in stats['f1'] if f == 1.0])
        failed_ds = len([f for f in stats['f1'] if f == 0.0])
        
        print(f"│ {ds:10s}: Count={stats['count']:2d} | Avg F1={avg_f1:.3f} | Perfect={perfect_ds:2d} | Failed={failed_ds:2d}")
    
    # Top Performers
    print("\n╔" + "═" * 118 + "╗")
    print("║" + "✅ TOP 10 BEST PERFORMING QUERIES (F1=1.0)".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    
    perfect_queries = [r for r in results if r['f1_score'] == 1.0]
    perfect_queries.sort(key=lambda x: x['retrieval_time_seconds'])
    
    print()
    for i, r in enumerate(perfect_queries[:10], 1):
        print(f"{i:2d}. {r['query_id']:10s} [{r['category']:12s}] {r['search_method']:20s} {r['retrieval_time_seconds']:6.2f}s")
        print(f"    Q: {r['question'][:80]}")
    
    # Worst Performers
    print("\n╔" + "═" * 118 + "╗")
    print("║" + "❌ BOTTOM 10 WORST PERFORMING QUERIES (F1=0.0)".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    
    failed_queries = [r for r in results if r['f1_score'] == 0.0]
    failed_queries.sort(key=lambda x: x['retrieval_time_seconds'], reverse=True)
    
    print()
    for i, r in enumerate(failed_queries[:10], 1):
        print(f"{i:2d}. {r['query_id']:10s} [{r['category']:12s}] {r['search_method']:20s} {r['retrieval_time_seconds']:6.2f}s")
        print(f"    Q: {r['question'][:80]}")
    
    # Slowest Queries
    print("\n╔" + "═" * 118 + "╗")
    print("║" + "⏱️  TOP 10 SLOWEST QUERIES".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    
    sorted_by_time = sorted(results, key=lambda x: x['retrieval_time_seconds'], reverse=True)
    
    print()
    for i, r in enumerate(sorted_by_time[:10], 1):
        print(f"{i:2d}. {r['query_id']:10s} [{r['category']:12s}] {r['search_method']:20s} {r['retrieval_time_seconds']:6.2f}s (F1={r['f1_score']:.2f})")
        print(f"    Q: {r['question'][:80]}")
    
    # Fastest Queries
    print("\n╔" + "═" * 118 + "╗")
    print("║" + "⚡ TOP 10 FASTEST QUERIES".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    
    sorted_by_time = sorted(results, key=lambda x: x['retrieval_time_seconds'])
    
    print()
    for i, r in enumerate(sorted_by_time[:10], 1):
        print(f"{i:2d}. {r['query_id']:10s} [{r['category']:12s}] {r['search_method']:20s} {r['retrieval_time_seconds']:6.2f}s (F1={r['f1_score']:.2f})")
        print(f"    Q: {r['question'][:80]}")
    
    # Summary Statistics
    print("\n╔" + "═" * 118 + "╗")
    print("║" + "💡 INSIGHTS & RECOMMENDATIONS".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    
    print()
    print("│ ✅ STRENGTHS:")
    print(f"│    • {perfect} queries ({perfect/total*100:.1f}%) achieve perfect retrieval (F1=1.0)")
    print(f"│    • Average retrieval time: {mean_time:.2f}s (fast and efficient)")
    print(f"│    • Enhanced vector method: F1={sum(methods['enhanced_vector']['f1'])/len(methods['enhanced_vector']['f1']):.3f}")
    
    print()
    print("│ ❌ WEAKNESSES:")
    print(f"│    • {failed} queries ({failed/total*100:.1f}%) have complete failures (F1=0.0)")
    print(f"│    • Internet fallback method: F1={sum(methods['internet_fallback']['f1'])/len(methods['internet_fallback']['f1']):.3f} (poor performance)")
    print(f"│    • Internet queries average {sum(methods['internet_fallback']['time'])/len(methods['internet_fallback']['time']):.2f}s (slow)")
    
    weakest_cat = min(cat_stats.items(), key=lambda x: sum(x[1]['f1'])/len(x[1]['f1']) if x[1]['f1'] else 0)[0]
    weakest_f1 = sum(cat_stats[weakest_cat]['f1'])/len(cat_stats[weakest_cat]['f1']) if cat_stats[weakest_cat]['f1'] else 0
    print(f"│    • Weakest category: {weakest_cat} (F1={weakest_f1:.3f})")
    
    print()
    print("│ 🎯 RECOMMENDATIONS:")
    print("│    1. Focus on improving internet fallback queries (currently F1=0.0)")
    print("│    2. Investigate failed queries in Licensing category")
    print("│    3. Optimize Procedure category performance (many low scores)")
    print("│    4. Vector-based methods are more reliable - use as default")
    print()
    print("═" * 120 + "\n")

if __name__ == "__main__":
    main()
