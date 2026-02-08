import json
import numpy as np
from scipy import stats
import sys
import os

def load_scores(filepath):
    """Load F1 scores from a results JSON file."""
    if not os.path.exists(filepath):
        print(f"[Error] File not found: {filepath}")
        return None
        
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    scores = []
    # Check if 'results' key exists
    if 'results' not in data:
        print(f"[Error] 'results' key not found in {filepath}")
        return None
        
    for r in data['results']:
        # Try to find f1_score, default to 0 if not found (or handle as error)
        # Note: If the experiment wasn't scored, this might be None
        f1 = r.get('f1_score')
        if f1 is not None:
            scores.append(float(f1))
            
    return scores

def main():
    # Define paths based on your project structure
    baseline_path = 'evaluation/raw_results/baseline_old_dataset.json'
    maf_rag_path = 'evaluation/raw_results/experiment2_new_dataset.json' # Or the scored version
    
    print("Loading scores...")
    baseline_scores = load_scores(baseline_path)
    maf_scores = load_scores(maf_rag_path)
    
    if not baseline_scores or not maf_scores:
        print("\n[!] Could not load scores. Make sure you have run the evaluation and scoring scripts.")
        print("    If 'experiment2' is not scored, run: python evaluation/manual_scoring.py ...")
        return

    # Ensure we have the same number of samples for a paired t-test
    if len(baseline_scores) != len(maf_scores):
        print(f"\n[Warning] Sample sizes differ! Baseline: {len(baseline_scores)}, MAF-RAG: {len(maf_scores)}")
        print("Switching to Independent t-test (less powerful but valid for different sizes)...")
        t_stat, p_val = stats.ttest_ind(maf_scores, baseline_scores, equal_var=False)
        test_type = "Independent t-test"
    else:
        print(f"\n[Info] Sample sizes match ({len(baseline_scores)}). Running Paired t-test...")
        t_stat, p_val = stats.ttest_rel(maf_scores, baseline_scores)
        test_type = "Paired t-test"

    print("\n" + "="*40)
    print(f"RESULTS: {test_type}")
    print("="*40)
    print(f"Baseline Mean F1: {np.mean(baseline_scores):.4f} (SD: {np.std(baseline_scores):.4f})")
    print(f"MAF-RAG Mean F1:  {np.mean(maf_scores):.4f} (SD: {np.std(maf_scores):.4f})")
    print("-" * 40)
    print(f"t-statistic: {t_stat:.4f}")
    print(f"p-value:     {p_val:.4e}")
    print("-" * 40)
    
    if p_val < 0.05:
        print("✅ RESULT: Statistically Significant (p < 0.05)")
        print("   You can write in your paper: 'The improvement was statistically significant (p < 0.05).'")
    else:
        print("❌ RESULT: Not Statistically Significant (p >= 0.05)")
        print("   You should stick to reporting Mean and Standard Deviation.")

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("[Error] scipy is not installed. Run: pip install scipy")
