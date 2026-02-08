#!/usr/bin/env python3
"""Compare all experiment runs."""
import json

def main():
    # Load results
    with open('evaluation/raw_results/baseline_old_dataset.json') as f:
        baseline = json.load(f)
    
    with open('evaluation/raw_results/experiment2_new_dataset.json') as f:
        exp2_combined = json.load(f)
    
    with open('evaluation/raw_results/experiment2_cleaned_dataset.json') as f:
        exp2_cleaned = json.load(f)
    
    print("\n" + "="*80)
    print("[STATS] COMPARISON: Baseline vs Combined vs Cleaned Dataset")
    print("="*80)
    
    # Count fallback rates
    datasets = {
        'Baseline (OLD only)': baseline,
        'Exp 2 Combined (OLD+NEW with separators)': exp2_combined,
        'Exp 2 Cleaned (NEW only, no separators)': exp2_cleaned
    }
    
    print(f"\n Internet Fallback Rate (Lower is Better):")
    print(f"{'Dataset':<45} {'Fallback':<15} {'Percentage'}")
    print("-" * 80)
    
    for name, data in datasets.items():
        fallback = sum(1 for r in data['results'] if r.get('search_method') == 'internet_fallback')
        total = len(data['results'])
        pct = fallback/total*100 if total > 0 else 0
        print(f"{name:<45} {fallback}/{total:<12} {pct:.1f}%")
    
    print(f"\n[TARGET] Vector-based (Supabase) - Higher is Better:")
    print(f"{'Dataset':<45} {'Vector':<15} {'Percentage'}")
    print("-" * 80)
    
    for name, data in datasets.items():
        vector = sum(1 for r in data['results'] if r.get('search_method') in ['vector_only', 'enhanced_vector'])
        total = len(data['results'])
        pct = vector/total*100 if total > 0 else 0
        print(f"{name:<45} {vector}/{total:<12} {pct:.1f}%")
    
    print(f"\n[METRIC] Average Confidence Score (Higher is Better):")
    print(f"{'Dataset':<45} {'Avg Confidence'}")
    print("-" * 80)
    
    for name, data in datasets.items():
        conf = data.get('metadata', {}).get('summary_statistics', {}).get('avg_confidence', 0)
        print(f"{name:<45} {conf:.3f}")
    
    print(f"\n[TIME]  Average Response Time:")
    print(f"{'Dataset':<45} {'Avg Time (s)'}")
    print("-" * 80)
    
    for name, data in datasets.items():
        time = data.get('metadata', {}).get('summary_statistics', {}).get('avg_response_time', 0)
        print(f"{name:<45} {time:.2f}s")
    
    print("\n" + "="*80)
    print("[OK] Key Findings:")
    print("="*80)
    
    b_fallback = sum(1 for r in baseline['results'] if r.get('search_method') == 'internet_fallback')
    c_fallback = sum(1 for r in exp2_combined['results'] if r.get('search_method') == 'internet_fallback')
    cl_fallback = sum(1 for r in exp2_cleaned['results'] if r.get('search_method') == 'internet_fallback')
    
    print(f"\n1. Combined Dataset (OLD+NEW): {b_fallback - c_fallback:+d} queries reduction in fallback")
    print(f"   - From {b_fallback/50*100:.1f}% to {c_fallback/50*100:.1f}% = {(c_fallback-b_fallback)/50*100:+.1f}% change")
    
    print(f"\n2. Cleaned Dataset (NEW only, no separators): {b_fallback - cl_fallback:+d} queries reduction")
    print(f"   - From {b_fallback/50*100:.1f}% to {cl_fallback/50*100:.1f}% = {(cl_fallback-b_fallback)/50*100:+.1f}% change")
    
    print(f"\n3. Cleaning Effect (Combined vs Cleaned): {cl_fallback - c_fallback:+d} queries difference")
    
    b_conf = baseline.get('metadata', {}).get('summary_statistics', {}).get('avg_confidence', 0)
    cl_conf = exp2_cleaned.get('metadata', {}).get('summary_statistics', {}).get('avg_confidence', 0)
    
    print(f"\n4. Confidence Improvement:")
    print(f"   - Baseline: {b_conf:.3f}")
    print(f"   - Cleaned:  {cl_conf:.3f} ({(cl_conf-b_conf)/b_conf*100:+.1f}%)")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
