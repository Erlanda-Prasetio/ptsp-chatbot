#!/usr/bin/env python3
"""Compare baseline vs Experiment 2 results."""
import json

def main():
    # Load results
    with open('evaluation/raw_results/baseline_old_dataset.json') as f:
        baseline = json.load(f)
    
    with open('evaluation/raw_results/experiment2_new_dataset.json') as f:
        exp2 = json.load(f)
    
    print("\n" + "="*70)
    print("📊 BASELINE (OLD Dataset) vs EXPERIMENT 2 (NEW Dataset)")
    print("="*70)
    
    # Count fallback rates (field name is 'search_method')
    b_fallback = sum(1 for r in baseline['results'] if r.get('search_method') == 'internet_fallback')
    e2_fallback = sum(1 for r in exp2['results'] if r.get('search_method') == 'internet_fallback')
    
    b_vector = sum(1 for r in baseline['results'] if r.get('search_method') in ['vector_only', 'enhanced_vector'])
    e2_vector = sum(1 for r in exp2['results'] if r.get('search_method') in ['vector_only', 'enhanced_vector'])
    
    total = len(baseline['results'])
    
    print(f"\n🌐 Internet Fallback (Lower is Better):")
    print(f"   Baseline: {b_fallback}/{total} = {b_fallback/total*100:.1f}%")
    print(f"   Exp 2:    {e2_fallback}/{total} = {e2_fallback/total*100:.1f}%")
    print(f"   Change:   {(e2_fallback-b_fallback)/total*100:+.1f}% ({e2_fallback-b_fallback:+d} queries)")
    
    print(f"\n🎯 Vector-based (Supabase) - Higher is Better:")
    print(f"   Baseline: {b_vector}/{total} = {b_vector/total*100:.1f}%")
    print(f"   Exp 2:    {e2_vector}/{total} = {e2_vector/total*100:.1f}%")
    print(f"   Change:   {(e2_vector-b_vector)/total*100:+.1f}% ({e2_vector-b_vector:+d} queries)")
    
    # Response time
    b_time = baseline.get('metadata', {}).get('summary_statistics', {}).get('avg_response_time', 0)
    e2_time = exp2.get('metadata', {}).get('summary_statistics', {}).get('avg_response_time', 0)
    
    print(f"\n⏱️  Average Response Time:")
    print(f"   Baseline: {b_time:.2f}s")
    print(f"   Exp 2:    {e2_time:.2f}s")
    if b_time > 0:
        print(f"   Change:   {(e2_time-b_time):+.2f}s ({(e2_time-b_time)/b_time*100:+.1f}%)")
    
    # Baseline has scored metrics (might be in results)
    b_results_with_f1 = [r for r in baseline['results'] if r.get('f1_score') is not None]
    if b_results_with_f1:
        avg_prec = sum(r.get('precision', 0) for r in b_results_with_f1) / len(b_results_with_f1)
        avg_rec = sum(r.get('recall', 0) for r in b_results_with_f1) / len(b_results_with_f1)
        avg_f1 = sum(r.get('f1_score', 0) for r in b_results_with_f1) / len(b_results_with_f1)
        
        print(f"\n📈 Baseline Metrics (from {len(b_results_with_f1)} scored results):")
        print(f"   Precision: {avg_prec:.3f}")
        print(f"   Recall:    {avg_rec:.3f}")
        print(f"   F1 Score:  {avg_f1:.3f}")
        print(f"\n⚠️  Exp 2 needs manual scoring for metrics!")
    
    print("\n" + "="*70)
    print("✅ Comparison complete!")
    print("="*70)
    
    print(f"\n📝 Next: Score Experiment 2 to get retrieval metrics")
    print(f"   python evaluation/manual_scoring.py --file evaluation/raw_results/experiment2_new_dataset.json")

if __name__ == '__main__':
    main()
