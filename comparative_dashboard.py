"""
Comparative Dashboard for Two Retrieval Test Results
Compares retrieval_test_result.csv vs old_dataset_retrieval_test_template.csv
"""
import csv
from collections import defaultdict
from typing import Dict, List, Tuple

FILE1 = "evaluation/retrieval_test_result.csv"
FILE2 = "evaluation/old_dataset_retrieval_test_template.csv"

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

def print_header(title: str):
    """Print formatted header"""
    print()
    print("╔" + "═" * 118 + "╗")
    print("║" + title.center(118) + "║")
    print("╚" + "═" * 118 + "╝")

def print_divider(char="-"):
    """Print divider line"""
    print("┌" + char * 118 + "┐")

def main():
    print("\n" + "=" * 120)
    print("RETRIEVAL TEST COMPARISON DASHBOARD".center(120))
    print("=" * 120)
    
    # Load both files
    print("\n📂 Loading data...")
    results1 = load_csv(FILE1)
    results2 = load_csv(FILE2)
    
    print(f"   ✅ {FILE1}: {len(results1)} queries")
    print(f"   ✅ {FILE2}: {len(results2)} queries")
    
    # Overall Statistics
    print_header("📊 OVERALL STATISTICS")
    
    # Calculate stats
    stats1 = {
        'total': len(results1),
        'mean_f1': sum(r['f1_score'] for r in results1) / len(results1) if results1 else 0,
        'mean_precision': sum(r['precision'] for r in results1) / len(results1) if results1 else 0,
        'mean_recall': sum(r['recall'] for r in results1) / len(results1) if results1 else 0,
        'mean_time': sum(r['retrieval_time_seconds'] for r in results1) / len(results1) if results1 else 0,
        'perfect': len([r for r in results1 if r['f1_score'] == 1.0]),
        'failed': len([r for r in results1 if r['f1_score'] == 0.0]),
    }
    
    stats2 = {
        'total': len(results2),
        'mean_f1': sum(r['f1_score'] for r in results2) / len(results2) if results2 else 0,
        'mean_precision': sum(r['precision'] for r in results2) / len(results2) if results2 else 0,
        'mean_recall': sum(r['recall'] for r in results2) / len(results2) if results2 else 0,
        'mean_time': sum(r['retrieval_time_seconds'] for r in results2) / len(results2) if results2 else 0,
        'perfect': len([r for r in results2 if r['f1_score'] == 1.0]),
        'failed': len([r for r in results2 if r['f1_score'] == 0.0]),
    }
    
    print("\n┌─ METRIC COMPARISON " + "─" * 97 + "┐")
    print(f"│ {'Metric':<25} │ {'retrieval_test_result.csv':^40} │ {'old_dataset_template.csv':^40} │ {'Difference':^8} │")
    print("├" + "─" * 25 + "┼" + "─" * 42 + "┼" + "─" * 42 + "┼" + "─" * 10 + "┤")
    
    # Simple metrics comparison
    print(f"│ {'Total Queries':<25} │ {stats1['total']:^40} │ {stats2['total']:^40} │ {stats1['total']-stats2['total']:>+8d} │")
    print(f"│ {'Mean F1 Score':<25} │ {stats1['mean_f1']:^40.3f} │ {stats2['mean_f1']:^40.3f} │ {stats1['mean_f1']-stats2['mean_f1']:>+8.3f} │")
    print(f"│ {'Mean Precision':<25} │ {stats1['mean_precision']:^40.3f} │ {stats2['mean_precision']:^40.3f} │ {stats1['mean_precision']-stats2['mean_precision']:>+8.3f} │")
    print(f"│ {'Mean Recall':<25} │ {stats1['mean_recall']:^40.3f} │ {stats2['mean_recall']:^40.3f} │ {stats1['mean_recall']-stats2['mean_recall']:>+8.3f} │")
    print(f"│ {'Mean Time (sec)':<25} │ {stats1['mean_time']:^40.2f}s │ {stats2['mean_time']:^40.2f}s │ {stats1['mean_time']-stats2['mean_time']:>+8.2f}s │")
    print(f"│ {'Perfect (1.0)':<25} │ {stats1['perfect']:^40} │ {stats2['perfect']:^40} │ {stats1['perfect']-stats2['perfect']:>+8d} │")
    print(f"│ {'Failed (0.0)':<25} │ {stats1['failed']:^40} │ {stats2['failed']:^40} │ {stats1['failed']-stats2['failed']:>+8d} │")
    
    print("└" + "─" * 25 + "┴" + "─" * 42 + "┴" + "─" * 42 + "┴" + "─" * 10 + "┘")
    
    # F1 Distribution
    print_header("📈 F1 SCORE DISTRIBUTION")
    
    dist1 = defaultdict(int)
    dist2 = defaultdict(int)
    
    for r in results1:
        category = categorize_f1(r['f1_score'])
        dist1[category] += 1
    
    for r in results2:
        category = categorize_f1(r['f1_score'])
        dist2[category] += 1
    
    categories = ['Perfect', 'High', 'Medium', 'Low', 'Failed']
    
    print("\n┌─ DISTRIBUTION BY CATEGORY " + "─" * 89 + "┐")
    print(f"│ {'Category':<15} │ {'retrieval_test_result.csv':^40} │ {'old_dataset_template.csv':^40} │")
    print("├" + "─" * 15 + "┼" + "─" * 42 + "┼" + "─" * 42 + "┤")
    
    for cat in categories:
        count1 = dist1.get(cat, 0)
        count2 = dist2.get(cat, 0)
        pct1 = count1 / len(results1) * 100 if results1 else 0
        pct2 = count2 / len(results2) * 100 if results2 else 0
        print(f"│ {cat:<15} │ {count1:>3} ({pct1:>5.1f}%) [{('█' * int(count1/2)):<20}] │ {count2:>3} ({pct2:>5.1f}%) [{('█' * int(count2/2)):<20}] │")
    
    print("└" + "─" * 15 + "┴" + "─" * 42 + "┴" + "─" * 42 + "┘")
    
    # Search Method Comparison
    print_header("🔍 SEARCH METHOD PERFORMANCE")
    
    methods1 = defaultdict(lambda: {'f1': [], 'time': []})
    methods2 = defaultdict(lambda: {'f1': [], 'time': []})
    
    for r in results1:
        method = r.get('search_method', 'unknown')
        methods1[method]['f1'].append(r['f1_score'])
        methods1[method]['time'].append(r['retrieval_time_seconds'])
    
    for r in results2:
        method = r.get('search_method', 'unknown')
        methods2[method]['f1'].append(r['f1_score'])
        methods2[method]['time'].append(r['retrieval_time_seconds'])
    
    print("\n┌─ retrieval_test_result.csv " + "─" * 88 + "┐")
    for method in sorted(methods1.keys()):
        f1_scores = methods1[method]['f1']
        times = methods1[method]['time']
        avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0
        avg_time = sum(times) / len(times) if times else 0
        perfect = len([f for f in f1_scores if f == 1.0])
        print(f"│  {method:<20s}: F1={avg_f1:.3f} | Count={len(f1_scores):2d} | Perfect={perfect:2d} | Avg Time={avg_time:.2f}s")
    print("└" + "─" * 118 + "┘")
    
    print("\n┌─ old_dataset_retrieval_test_template.csv " + "─" * 74 + "┐")
    for method in sorted(methods2.keys()):
        f1_scores = methods2[method]['f1']
        times = methods2[method]['time']
        avg_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0
        avg_time = sum(times) / len(times) if times else 0
        perfect = len([f for f in f1_scores if f == 1.0])
        print(f"│  {method:<20s}: F1={avg_f1:.3f} | Count={len(f1_scores):2d} | Perfect={perfect:2d} | Avg Time={avg_time:.2f}s")
    print("└" + "─" * 118 + "┘")
    
    # Category Performance
    print_header("📂 CATEGORY PERFORMANCE")
    
    cat_stats1 = defaultdict(lambda: {'f1': [], 'perfect': 0, 'failed': 0})
    cat_stats2 = defaultdict(lambda: {'f1': [], 'perfect': 0, 'failed': 0})
    
    for r in results1:
        cat = r.get('category', 'Unknown')
        f1 = r['f1_score']
        cat_stats1[cat]['f1'].append(f1)
        if f1 == 1.0:
            cat_stats1[cat]['perfect'] += 1
        elif f1 == 0.0:
            cat_stats1[cat]['failed'] += 1
    
    for r in results2:
        cat = r.get('category', 'Unknown')
        f1 = r['f1_score']
        cat_stats2[cat]['f1'].append(f1)
        if f1 == 1.0:
            cat_stats2[cat]['perfect'] += 1
        elif f1 == 0.0:
            cat_stats2[cat]['failed'] += 1
    
    print("\n┌─ CATEGORY BREAKDOWN " + "─" * 95 + "┐")
    print(f"│ {'Category':<15} │ {'Result File':^40} │ {'Template File':^40} │ {'Diff':^8} │")
    print("├" + "─" * 15 + "┼" + "─" * 42 + "┼" + "─" * 42 + "┼" + "─" * 10 + "┤")
    
    all_cats = set(list(cat_stats1.keys()) + list(cat_stats2.keys()))
    for cat in sorted(all_cats):
        stats_a = cat_stats1.get(cat, {'f1': []})
        stats_b = cat_stats2.get(cat, {'f1': []})
        
        avg_f1_a = sum(stats_a['f1']) / len(stats_a['f1']) if stats_a['f1'] else 0
        avg_f1_b = sum(stats_b['f1']) / len(stats_b['f1']) if stats_b['f1'] else 0
        diff = avg_f1_a - avg_f1_b
        
        count_a = len(stats_a['f1'])
        count_b = len(stats_b['f1'])
        
        str_a = f"{avg_f1_a:.3f} ({count_a})"
        str_b = f"{avg_f1_b:.3f} ({count_b})"
        str_diff = f"{diff:+.3f}"
        
        print(f"│ {cat:<15} │ {str_a:^40} │ {str_b:^40} │ {str_diff:>8} │")
    
    print("└" + "─" * 15 + "┴" + "─" * 42 + "┴" + "─" * 42 + "┴" + "─" * 10 + "┘")
    
    # Query Performance Comparison
    print_header("🔍 QUERY-BY-QUERY COMPARISON (Top Differences)")
    
    # Match queries by ID
    results1_by_id = {r['query_id']: r for r in results1}
    results2_by_id = {r['query_id']: r for r in results2}
    
    differences = []
    for qid in results1_by_id:
        if qid in results2_by_id:
            r1 = results1_by_id[qid]
            r2 = results2_by_id[qid]
            f1_diff = r1['f1_score'] - r2['f1_score']
            differences.append({
                'query_id': qid,
                'question': r1['question'][:50],
                'f1_result': r1['f1_score'],
                'f1_template': r2['f1_score'],
                'diff': f1_diff,
                'method1': r1.get('search_method', 'N/A'),
                'method2': r2.get('search_method', 'N/A'),
            })
    
    # Sort by absolute difference
    differences.sort(key=lambda x: abs(x['diff']), reverse=True)
    
    print("\n┌─ TOP 10 IMPROVED QUERIES (Result > Template) " + "─" * 70 + "┐")
    improved = [d for d in differences if d['diff'] > 0]
    for i, d in enumerate(improved[:10], 1):
        print(f"│ {i:2d}. {d['query_id']:10s} | {d['question']:<40} │ {d['f1_result']:.2f} vs {d['f1_template']:.2f} ({d['diff']:+.2f})")
    print("└" + "─" * 118 + "┘")
    
    print("\n┌─ TOP 10 DEGRADED QUERIES (Result < Template) " + "─" * 70 + "┐")
    degraded = [d for d in differences if d['diff'] < 0]
    for i, d in enumerate(degraded[:10], 1):
        print(f"│ {i:2d}. {d['query_id']:10s} | {d['question']:<40} │ {d['f1_result']:.2f} vs {d['f1_template']:.2f} ({d['diff']:+.2f})")
    print("└" + "─" * 118 + "┘")
    
    # Summary
    print_header("💡 SUMMARY & INSIGHTS")
    
    print("\n┌─ KEY FINDINGS " + "─" * 102 + "┐")
    
    improvement_count = len([d for d in differences if d['diff'] > 0.1])
    degradation_count = len([d for d in differences if d['diff'] < -0.1])
    
    print(f"│ • Queries with significant improvement (>0.1):  {improvement_count:3d}")
    print(f"│ • Queries with significant degradation (<-0.1): {degradation_count:3d}")
    print(f"│ • Overall F1 improvement: {stats1['mean_f1'] - stats2['mean_f1']:+.3f}")
    print(f"│ • Overall speed improvement: {(stats2['mean_time'] - stats1['mean_time']):+.2f}s faster" if stats1['mean_time'] < stats2['mean_time'] else f"│ • Overall speed degradation: {(stats1['mean_time'] - stats2['mean_time']):+.2f}s slower")
    
    internet_1 = len([r for r in results1 if r.get('search_method') == 'internet_fallback'])
    internet_2 = len([r for r in results2 if r.get('search_method') == 'internet_fallback'])
    
    print(f"│ • Internet fallback usage: {internet_1} (result) vs {internet_2} (template)")
    print(f"│ • Perfect match rate: {stats1['perfect']}/{stats1['total']} ({stats1['perfect']/stats1['total']*100:.1f}%) vs {stats2['perfect']}/{stats2['total']} ({stats2['perfect']/stats2['total']*100:.1f}%)")
    
    print("└" + "─" * 118 + "┘")
    
    print("\n" + "=" * 120 + "\n")

if __name__ == "__main__":
    main()
