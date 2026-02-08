import pandas as pd
from scipy import stats
import sys

def calculate_significance():
    print("Loading results...")
    
    # Load MAF-RAG results
    try:
        madam_df = pd.read_csv('evaluation/retrieval_test_madam_results.csv')
        print(f"Loaded MAF-RAG results: {len(madam_df)} rows")
    except FileNotFoundError:
        print("Error: evaluation/retrieval_test_madam_results.csv not found")
        return

    # Load Baseline results
    try:
        baseline_df = pd.read_csv('evaluation/retrieval_test_result.csv')
        print(f"Loaded Baseline results: {len(baseline_df)} rows")
    except FileNotFoundError:
        print("Error: evaluation/retrieval_test_result.csv not found")
        return

    # Merge on query_id to ensure we are comparing the same queries
    # MAF-RAG uses 'f1', Baseline uses 'f1_score'
    merged_df = pd.merge(
        madam_df[['query_id', 'f1']], 
        baseline_df[['query_id', 'f1_score']], 
        on='query_id', 
        suffixes=('_madam', '_baseline')
    )
    
    print(f"Aligned queries for comparison: {len(merged_df)}")
    
    if len(merged_df) < 2:
        print("Not enough aligned data points for t-test")
        return

    # Extract scores
    madam_scores = merged_df['f1']
    baseline_scores = merged_df['f1_score']
    
    # Calculate means
    mean_madam = madam_scores.mean()
    mean_baseline = baseline_scores.mean()
    
    print(f"\nMean F1 (MAF-RAG): {mean_madam:.4f}")
    print(f"Mean F1 (Baseline): {mean_baseline:.4f}")
    print(f"Improvement: {mean_madam - mean_baseline:.4f} ({(mean_madam - mean_baseline)/mean_baseline*100:.1f}%)")

    # Perform Paired T-Test
    t_stat, p_value = stats.ttest_rel(madam_scores, baseline_scores)
    
    print("\n" + "="*40)
    print("STATISTICAL SIGNIFICANCE TEST (Paired t-test)")
    print("="*40)
    print(f"T-Statistic: {t_stat:.4f}")
    print(f"P-Value:     {p_value:.5f}")
    
    if p_value < 0.05:
        print("\n✅ RESULT: Statistically Significant (p < 0.05)")
    else:
        print("\n❌ RESULT: Not Statistically Significant (p >= 0.05)")
    print("="*40)

if __name__ == "__main__":
    calculate_significance()
