"""
Quick Analysis Demo - Calculate Accuracy, Precision, Recall, F1 with Graphs
Run this after demo_manual_scoring.py to see visualizations
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)

def analyze_results(csv_file='evaluation/demo_scored_results.csv'):
    """Analyze scored results and create visualizations"""
    
    # Load data
    df = pd.read_csv(csv_file)
    print(f"\n📊 Loaded {len(df)} scored results\n")
    
    # ============================================================================
    # 1. ACCURACY CALCULATION
    # ============================================================================
    print("="*70)
    print("📈 ACCURACY METRICS")
    print("="*70)
    print("NOTE: Dataset (vector store) is OLD. Questions are mixed (OLD-related + NEW-related)")
    print("      This is BASELINE testing to show what's missing in OLD dataset.")
    print()
    
    accuracy = df['is_correct'].mean()
    total = len(df)
    correct = df['is_correct'].sum()
    
    print(f"Total Questions: {total}")
    print(f"Correct Answers: {correct}")
    print(f"Overall Accuracy: {accuracy:.2%}")
    print()
    
    # Accuracy by question type (not dataset version)
    accuracy_by_source = df.groupby('dataset_source').agg({
        'is_correct': ['count', 'sum', 'mean']
    })
    accuracy_by_source.columns = ['Total', 'Correct', 'Accuracy']
    
    print("Accuracy by Question Type:")
    print("  (OLD = questions answerable with old dataset)")
    print("  (NEW = questions requiring new dataset content)")
    for source in accuracy_by_source.index:
        total_src = accuracy_by_source.loc[source, 'Total']
        correct_src = accuracy_by_source.loc[source, 'Correct']
        acc_src = accuracy_by_source.loc[source, 'Accuracy']
        print(f"  {source} questions: {acc_src:.2%} ({int(correct_src)}/{int(total_src)})")
    
    # ============================================================================
    # 2. PRECISION, RECALL, F1 ESTIMATION
    # ============================================================================
    print("\n" + "="*70)
    print("📊 PRECISION, RECALL, F1 (Estimated)")
    print("="*70)
    print("Note: Without ground_truth chunks, we estimate based on system metrics")
    print()
    
    # Estimate precision from confidence
    df['estimated_precision'] = df['confidence_score']
    
    # Estimate recall from num_sources (5 sources = ideal)
    df['estimated_recall'] = df['num_sources'].apply(lambda x: min(x / 5, 1.0))
    
    # Calculate F1
    df['estimated_f1'] = 2 * (df['estimated_precision'] * df['estimated_recall']) / \
                         (df['estimated_precision'] + df['estimated_recall'] + 0.0001)
    
    print(f"Avg Precision (est): {df['estimated_precision'].mean():.4f}")
    print(f"Avg Recall (est):    {df['estimated_recall'].mean():.4f}")
    print(f"Avg F1 Score (est):  {df['estimated_f1'].mean():.4f}")
    
    # ============================================================================
    # 3. PERFORMANCE SUMMARY
    # ============================================================================
    print("\n" + "="*70)
    print("⚡ PERFORMANCE SUMMARY")
    print("="*70)
    
    metrics_summary = df.groupby('dataset_source').agg({
        'is_correct': 'mean',
        'confidence_score': 'mean',
        'response_time_seconds': 'mean',
        'total_tokens': 'mean',
        'num_sources': 'mean',
        'estimated_precision': 'mean',
        'estimated_recall': 'mean',
        'estimated_f1': 'mean'
    }).round(4)
    
    print(metrics_summary)
    
    # ============================================================================
    # 4. CONFIDENT WRONG ANALYSIS
    # ============================================================================
    print("\n" + "="*70)
    print("⚠️  CONFIDENT WRONG ANALYSIS")
    print("="*70)
    
    df['confident_wrong'] = (df['confidence_score'] > 0.6) & (df['is_correct'] == 0)
    confident_wrong_count = df['confident_wrong'].sum()
    confident_wrong_rate = confident_wrong_count / len(df)
    
    print(f"Confident Wrong Cases: {confident_wrong_count}")
    print(f"Confident Wrong Rate: {confident_wrong_rate:.2%}")
    
    if confident_wrong_count > 0:
        print("\nCases where system was confident (>0.6) but WRONG:")
        print(df[df['confident_wrong']][['eval_id', 'query', 'confidence_score']])
    
    # ============================================================================
    # 5. CREATE GRAPHS
    # ============================================================================
    print("\n" + "="*70)
    print("📊 GENERATING GRAPHS...")
    print("="*70)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 10))
    
    # Graph 1: Overall Accuracy (Top Left)
    ax1 = plt.subplot(2, 3, 1)
    bars1 = ax1.bar(['Overall'], [accuracy * 100], color='#2ecc71', alpha=0.7, edgecolor='black', width=0.5)
    ax1.set_ylabel('Accuracy (%)', fontweight='bold')
    ax1.set_title(f'Overall Accuracy\n(n={total} questions)', fontweight='bold', fontsize=11)
    ax1.set_ylim(0, 110)
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%\n({correct}/{total})', ha='center', va='bottom', fontweight='bold')
    
    # Graph 2: Precision, Recall, F1 (Top Middle)
    ax2 = plt.subplot(2, 3, 2)
    metrics_values = [df['estimated_precision'].mean(), df['estimated_recall'].mean(), df['estimated_f1'].mean()]
    metrics_labels = ['Precision', 'Recall', 'F1']
    bars2 = ax2.bar(metrics_labels, metrics_values, color=['#e74c3c', '#3498db', '#2ecc71'], alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Score', fontweight='bold')
    ax2.set_title('Avg Metrics (Estimated)', fontweight='bold', fontsize=12)
    ax2.set_ylim(0, 1.0)
    for bar, val in zip(bars2, metrics_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Graph 3: Response Time (Top Right)
    ax3 = plt.subplot(2, 3, 3)
    avg_time = df['response_time_seconds'].mean()
    bars3 = ax3.bar(['Avg Time'], [avg_time], color='#9b59b6', alpha=0.7, edgecolor='black', width=0.5)
    ax3.set_ylabel('Time (seconds)', fontweight='bold')
    ax3.set_title('Avg Response Time', fontweight='bold', fontsize=12)
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}s', ha='center', va='bottom', fontweight='bold')
    
    # Graph 4: Token Usage (Bottom Left)
    ax4 = plt.subplot(2, 3, 4)
    avg_tokens = df['total_tokens'].mean()
    bars4 = ax4.bar(['Avg Tokens'], [avg_tokens], color='#1abc9c', alpha=0.7, edgecolor='black', width=0.5)
    ax4.set_ylabel('Token Count', fontweight='bold')
    ax4.set_title('Avg Token Usage', fontweight='bold', fontsize=12)
    for bar in bars4:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # Graph 5: Confidence vs Correctness (Bottom Middle)
    ax5 = plt.subplot(2, 3, 5)
    correct_df = df[df['is_correct'] == 1]
    incorrect_df = df[df['is_correct'] == 0]
    ax5.scatter(correct_df.index, correct_df['confidence_score'], 
               c='green', label='Correct', s=100, alpha=0.6, edgecolors='black')
    ax5.scatter(incorrect_df.index, incorrect_df['confidence_score'], 
               c='red', label='Incorrect', s=100, alpha=0.6, edgecolors='black')
    ax5.axhline(y=0.6, color='orange', linestyle='--', label='High Conf', alpha=0.7)
    ax5.set_ylabel('Confidence', fontweight='bold')
    ax5.set_xlabel('Question Index', fontweight='bold')
    ax5.set_title('Confidence vs Correctness', fontweight='bold', fontsize=12)
    ax5.legend(fontsize=9)
    ax5.set_ylim(0, 1.0)
    
    # Graph 6: Sources Retrieved (Bottom Right)
    ax6 = plt.subplot(2, 3, 6)
    avg_sources = df['num_sources'].mean()
    bars6 = ax6.bar(['Avg Sources'], [avg_sources], color='#34495e', alpha=0.7, edgecolor='black', width=0.5)
    ax6.set_ylabel('Source Count', fontweight='bold')
    ax6.set_title('Avg Sources Retrieved', fontweight='bold', fontsize=12)
    ax6.axhline(y=5, color='green', linestyle='--', label='Ideal (5)', alpha=0.5)
    ax6.legend(fontsize=9)
    for bar in bars6:
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('evaluation/demo_analysis_graphs.png', dpi=150, bbox_inches='tight')
    print("\n✅ Graphs saved to: evaluation/demo_analysis_graphs.png")
    plt.show()
    
    # ============================================================================
    # 6. FINAL SUMMARY
    # ============================================================================
    print("\n" + "="*70)
    print("📋 FINAL SUMMARY")
    print("="*70)
    print(f"Overall Accuracy: {accuracy:.2%}")
    print(f"Avg Confidence: {df['confidence_score'].mean():.4f}")
    print(f"Avg Response Time: {df['response_time_seconds'].mean():.2f}s")
    print(f"Avg Tokens: {df['total_tokens'].mean():.0f}")
    print(f"Avg F1 Score: {df['estimated_f1'].mean():.4f}")
    print(f"Confident Wrong Rate: {confident_wrong_rate:.2%}")
    print("="*70)
    
    return df, metrics_summary


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎯 RAG EVALUATION ANALYSIS - BASELINE (OLD DATASET)")
    print("="*70)
    print("BASELINE: Testing OLD dataset with mixed questions")
    print("  - OLD questions: Should work (answerable with old docs)")
    print("  - NEW questions: Will likely fail (need 2024/2025 data)")
    print("="*70)
    
    df, metrics = analyze_results()
    
    print("\n✅ Analysis complete! Check the graphs above.")
    print("\n💡 After updating to NEW dataset, run again to compare:")
    print("   python evaluation/demo_analysis.py")
    print("   (Update csv_file path to new scored results)")
