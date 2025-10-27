#!/usr/bin/env python3
"""
Analyze Experiment 2 Cleaned Dataset Results
Similar to analyze_baseline.py but for the cleaned NEW dataset
"""
import json
from collections import defaultdict, Counter
from pathlib import Path

def load_results(filepath):
    """Load evaluation results from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_search_methods(results):
    """Analyze distribution of search methods."""
    methods = Counter(r.get('search_method', 'unknown') for r in results['results'] if 'search_method' in r or True)
    total = len(results['results'])
    
    print("\n" + "="*80)
    print("🔍 SEARCH METHOD DISTRIBUTION")
    print("="*80)
    
    for method, count in methods.most_common():
        pct = count/total*100
        print(f"{method:25} {count:3}/{total} = {pct:5.1f}%")
    
    return methods

def analyze_by_dataset_source(results):
    """Analyze performance by dataset source (OLD vs NEW questions)."""
    old_queries = [r for r in results['results'] if r.get('dataset_source') == 'OLD']
    new_queries = [r for r in results['results'] if r.get('dataset_source') == 'NEW']
    
    print("\n" + "="*80)
    print("📊 PERFORMANCE BY QUESTION SOURCE")
    print("="*80)
    
    for name, queries in [("OLD Questions", old_queries), ("NEW Questions", new_queries)]:
        if not queries:
            continue
            
        total = len(queries)
        fallback = sum(1 for q in queries if q.get('search_method') == 'internet_fallback')
        vector = sum(1 for q in queries if q.get('search_method') in ['vector_only', 'enhanced_vector'])
        avg_conf = sum(q.get('confidence_score', 0) for q in queries) / total if total > 0 else 0
        
        print(f"\n{name} ({total} queries):")
        print(f"  Internet Fallback: {fallback}/{total} = {fallback/total*100:.1f}%")
        print(f"  Vector-based:      {vector}/{total} = {vector/total*100:.1f}%")
        print(f"  Avg Confidence:    {avg_conf:.3f}")

def analyze_by_category(results):
    """Analyze performance by question category."""
    by_category = defaultdict(list)
    
    for r in results['results']:
        category = r.get('category', 'Unknown')
        by_category[category].append(r)
    
    print("\n" + "="*80)
    print("📂 PERFORMANCE BY CATEGORY")
    print("="*80)
    
    print(f"\n{'Category':<15} {'Total':<8} {'Fallback':<12} {'Vector':<12} {'Avg Conf'}")
    print("-" * 80)
    
    for category in sorted(by_category.keys()):
        queries = by_category[category]
        total = len(queries)
        fallback = sum(1 for q in queries if q.get('search_method') == 'internet_fallback')
        vector = sum(1 for q in queries if q.get('search_method') in ['vector_only', 'enhanced_vector'])
        avg_conf = sum(q.get('confidence_score', 0) for q in queries) / total if total > 0 else 0
        
        print(f"{category:<15} {total:<8} {fallback}/{total} ({fallback/total*100:4.0f}%)  {vector}/{total} ({vector/total*100:4.0f}%)  {avg_conf:.3f}")

def analyze_confidence_distribution(results):
    """Analyze confidence score distribution."""
    print("\n" + "="*80)
    print("📈 CONFIDENCE SCORE DISTRIBUTION")
    print("="*80)
    
    # Separate by search method
    fallback_conf = [r['confidence_score'] for r in results['results'] 
                     if r.get('search_method') == 'internet_fallback']
    vector_conf = [r['confidence_score'] for r in results['results'] 
                   if r.get('search_method') in ['vector_only', 'enhanced_vector']]
    
    print(f"\nInternet Fallback queries ({len(fallback_conf)}):")
    if fallback_conf:
        print(f"  Min: {min(fallback_conf):.3f}, Max: {max(fallback_conf):.3f}, Avg: {sum(fallback_conf)/len(fallback_conf):.3f}")
    
    print(f"\nVector-based queries ({len(vector_conf)}):")
    if vector_conf:
        print(f"  Min: {min(vector_conf):.3f}, Max: {max(vector_conf):.3f}, Avg: {sum(vector_conf)/len(vector_conf):.3f}")
        
        # Distribution bins
        bins = {
            '0.90-1.00': sum(1 for c in vector_conf if c >= 0.90),
            '0.80-0.89': sum(1 for c in vector_conf if 0.80 <= c < 0.90),
            '0.70-0.79': sum(1 for c in vector_conf if 0.70 <= c < 0.80),
            '0.60-0.69': sum(1 for c in vector_conf if 0.60 <= c < 0.70),
            '< 0.60':    sum(1 for c in vector_conf if c < 0.60),
        }
        
        print("\n  Distribution:")
        for bin_range, count in bins.items():
            pct = count/len(vector_conf)*100 if vector_conf else 0
            bar = '█' * int(pct / 2)
            print(f"    {bin_range}: {count:2} queries ({pct:4.1f}%) {bar}")

def analyze_fallback_queries(results):
    """List queries that fell back to internet."""
    fallback_queries = [r for r in results['results'] 
                        if r.get('search_method') == 'internet_fallback']
    
    print("\n" + "="*80)
    print(f"🌐 INTERNET FALLBACK QUERIES ({len(fallback_queries)} queries)")
    print("="*80)
    
    for r in fallback_queries:
        eval_id = r.get('eval_id', 'N/A')
        source = r.get('dataset_source', 'N/A')
        category = r.get('category', 'N/A')
        query = r.get('query_text', 'N/A')[:60]
        
        print(f"\n{eval_id} ({source} / {category}):")
        print(f"  Q: {query}...")

def analyze_high_confidence_matches(results):
    """Analyze high confidence vector matches."""
    vector_queries = [r for r in results['results'] 
                      if r.get('search_method') in ['vector_only', 'enhanced_vector']]
    
    high_conf = [r for r in vector_queries if r.get('confidence_score', 0) >= 0.80]
    
    print("\n" + "="*80)
    print(f"⭐ HIGH CONFIDENCE MATCHES (≥0.80) - {len(high_conf)} queries")
    print("="*80)
    
    for r in sorted(high_conf, key=lambda x: x.get('confidence_score', 0), reverse=True):
        eval_id = r.get('eval_id', 'N/A')
        method = r.get('search_method', 'N/A')
        conf = r.get('confidence_score', 0)
        query = r.get('query_text', 'N/A')[:60]
        
        print(f"\n{eval_id} ({method}, conf={conf:.3f}):")
        print(f"  Q: {query}...")

def compare_with_baseline(cleaned_results, baseline_path='evaluation/raw_results/baseline_old_dataset.json'):
    """Compare with baseline results."""
    try:
        baseline = load_results(baseline_path)
    except FileNotFoundError:
        print("\n⚠️  Baseline file not found, skipping comparison")
        return
    
    print("\n" + "="*80)
    print("📊 COMPARISON WITH BASELINE")
    print("="*80)
    
    # Match queries by eval_id
    baseline_map = {r.get('eval_id'): r for r in baseline['results'] if 'eval_id' in r}
    cleaned_map = {r.get('eval_id'): r for r in cleaned_results['results'] if 'eval_id' in r}
    
    improvements = []
    regressions = []
    
    for eval_id in baseline_map:
        if eval_id not in cleaned_map:
            continue
            
        b_method = baseline_map[eval_id].get('search_method')
        c_method = cleaned_map[eval_id].get('search_method')
        
        # Improvement: Fallback -> Vector
        if b_method == 'internet_fallback' and c_method in ['vector_only', 'enhanced_vector']:
            improvements.append({
                'eval_id': eval_id,
                'query': cleaned_map[eval_id].get('query_text', ''),
                'old': b_method,
                'new': c_method,
                'conf': cleaned_map[eval_id].get('confidence_score', 0)
            })
        
        # Regression: Vector -> Fallback
        elif b_method in ['vector_only', 'enhanced_vector'] and c_method == 'internet_fallback':
            regressions.append({
                'eval_id': eval_id,
                'query': cleaned_map[eval_id].get('query_text', ''),
                'old': b_method,
                'new': c_method
            })
    
    print(f"\n✅ Improvements (Fallback → Vector): {len(improvements)} queries")
    for imp in improvements:
        print(f"  {imp['eval_id']}: {imp['query'][:50]}... (conf={imp['conf']:.3f})")
    
    print(f"\n❌ Regressions (Vector → Fallback): {len(regressions)} queries")
    for reg in regressions:
        print(f"  {reg['eval_id']}: {reg['query'][:50]}...")
    
    # Overall stats
    b_fallback = sum(1 for r in baseline['results'] if r.get('search_method') == 'internet_fallback')
    c_fallback = sum(1 for r in cleaned_results['results'] if r.get('search_method') == 'internet_fallback')
    
    print(f"\n📈 Overall Change:")
    print(f"  Baseline Fallback:  {b_fallback}/50 = {b_fallback/50*100:.1f}%")
    print(f"  Cleaned Fallback:   {c_fallback}/49 = {c_fallback/49*100:.1f}%")
    print(f"  Net Improvement:    {b_fallback - c_fallback:+d} queries ({(c_fallback-b_fallback)/50*100:+.1f}%)")

def main():
    print("\n" + "="*80)
    print("📊 EXPERIMENT 2 - CLEANED DATASET ANALYSIS")
    print("="*80)
    
    # Load results
    results_path = 'evaluation/raw_results/experiment2_cleaned_dataset.json'
    results = load_results(results_path)
    
    metadata = results.get('metadata', {})
    stats = metadata.get('summary_statistics', {})
    
    print(f"\n📝 Experiment: {metadata.get('experiment_name', 'N/A')}")
    print(f"📅 Date: {metadata.get('evaluation_date', 'N/A')}")
    print(f"✅ Successful: {metadata.get('successful_queries', 0)}/{metadata.get('total_queries', 0)}")
    print(f"❌ Failed: {metadata.get('failed_queries', 0)}")
    print(f"⏱️  Avg Response Time: {stats.get('avg_response_time', 0):.2f}s")
    print(f"🎯 Avg Confidence: {stats.get('avg_confidence', 0):.3f}")
    
    # Run analyses
    analyze_search_methods(results)
    analyze_by_dataset_source(results)
    analyze_by_category(results)
    analyze_confidence_distribution(results)
    analyze_high_confidence_matches(results)
    analyze_fallback_queries(results)
    compare_with_baseline(results)
    
    print("\n" + "="*80)
    print("✅ Analysis Complete!")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
