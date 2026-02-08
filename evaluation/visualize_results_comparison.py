#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Results and Discussion: Comparative Visualization of Retrieval Performance
===========================================================================

Compares three experimental conditions:
1. Baseline Enhanced Dataset (retrieval_test_result.csv)
2. Baseline Legacy Dataset (old_dataset_retrieval_test_template.csv)
3. MAF-RAG System (retrieval_test_madam_results.csv)

Generates visualizations for:
- Overall F1-Score comparison
- Performance by search method
- Performance by query category
- Performance distribution (histogram)
- Method usage distribution
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10

# File paths
ENHANCED_BASELINE = "evaluation/retrieval_test_result.csv"
LEGACY_BASELINE = "evaluation/old_dataset_retrieval_test_template.csv"
MAFRAG_RESULTS = "evaluation/retrieval_test_madam_results.csv"

def load_and_prepare_data():
    """Load all three datasets and prepare for comparison"""
    
    # Load datasets
    enhanced = pd.read_csv(ENHANCED_BASELINE)
    legacy = pd.read_csv(LEGACY_BASELINE)
    mafrag = pd.read_csv(MAFRAG_RESULTS)
    
    # Add system identifier
    enhanced['system'] = 'Baseline Enhanced'
    legacy['system'] = 'Baseline Legacy'
    mafrag['system'] = 'MAF-RAG'
    
    # Standardize column names (use 'f1' for MAF-RAG, 'f1_score' for baselines)
    if 'f1' in mafrag.columns and 'f1_score' not in mafrag.columns:
        mafrag['f1_score'] = mafrag['f1']
    
    # Ensure all have required columns
    for df in [enhanced, legacy, mafrag]:
        if 'precision' not in df.columns:
            df['precision'] = 0.0
        if 'recall' not in df.columns:
            df['recall'] = 0.0
        if 'f1_score' not in df.columns:
            df['f1_score'] = 0.0
    
    # Combine all datasets
    all_data = pd.concat([enhanced, legacy, mafrag], ignore_index=True)
    
    return enhanced, legacy, mafrag, all_data

def calculate_summary_statistics(df, system_name):
    """Calculate summary statistics for a dataset"""
    stats = {
        'System': system_name,
        'Total Queries': len(df),
        'Mean F1': df['f1_score'].mean(),
        'Std F1': df['f1_score'].std(),
        'Mean Precision': df['precision'].mean(),
        'Mean Recall': df['recall'].mean(),
        'Perfect (F1=1.0)': (df['f1_score'] == 1.0).sum(),
        'High (F1≥0.7)': (df['f1_score'] >= 0.7).sum(),
        'Medium (0.4≤F1<0.7)': ((df['f1_score'] >= 0.4) & (df['f1_score'] < 0.7)).sum(),
        'Low (0<F1<0.4)': ((df['f1_score'] > 0.0) & (df['f1_score'] < 0.4)).sum(),
        'Failed (F1=0.0)': (df['f1_score'] == 0.0).sum(),
    }
    return stats

def plot_overall_comparison(enhanced, legacy, mafrag):
    """Plot 1: Overall performance comparison across systems"""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Prepare data
    systems = ['Baseline\nEnhanced', 'Baseline\nLegacy', 'MAF-RAG']
    f1_means = [enhanced['f1_score'].mean(), legacy['f1_score'].mean(), mafrag['f1_score'].mean()]
    precision_means = [enhanced['precision'].mean(), legacy['precision'].mean(), mafrag['precision'].mean()]
    recall_means = [enhanced['recall'].mean(), legacy['recall'].mean(), mafrag['recall'].mean()]
    
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    # Plot 1: Mean F1-Score
    ax1 = axes[0, 0]
    bars1 = ax1.bar(systems, f1_means, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Mean F1-Score', fontweight='bold')
    ax1.set_title('Overall F1-Score Comparison', fontweight='bold', fontsize=12)
    ax1.set_ylim([0, 1.0])
    ax1.axhline(y=0.7, color='green', linestyle='--', alpha=0.5, label='High Quality (0.7)')
    ax1.axhline(y=0.4, color='orange', linestyle='--', alpha=0.5, label='Medium Quality (0.4)')
    for i, (bar, val) in enumerate(zip(bars1, f1_means)):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.02, f'{val:.3f}', 
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(axis='y', alpha=0.3)
    
    # Plot 2: Precision vs Recall
    ax2 = axes[0, 1]
    x = np.arange(len(systems))
    width = 0.35
    bars2_1 = ax2.bar(x - width/2, precision_means, width, label='Precision', 
                      color='#3498db', alpha=0.7, edgecolor='black')
    bars2_2 = ax2.bar(x + width/2, recall_means, width, label='Recall', 
                      color='#e74c3c', alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Score', fontweight='bold')
    ax2.set_title('Precision vs Recall Comparison', fontweight='bold', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(systems)
    ax2.set_ylim([0, 1.0])
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', alpha=0.3)
    
    # Plot 3: Performance Distribution
    ax3 = axes[1, 0]
    categories = ['Perfect\n(1.0)', 'High\n(≥0.7)', 'Medium\n(0.4-0.7)', 'Low\n(<0.4)', 'Failed\n(0.0)']
    enhanced_dist = [
        (enhanced['f1_score'] == 1.0).sum(),
        ((enhanced['f1_score'] >= 0.7) & (enhanced['f1_score'] < 1.0)).sum(),
        ((enhanced['f1_score'] >= 0.4) & (enhanced['f1_score'] < 0.7)).sum(),
        ((enhanced['f1_score'] > 0.0) & (enhanced['f1_score'] < 0.4)).sum(),
        (enhanced['f1_score'] == 0.0).sum(),
    ]
    legacy_dist = [
        (legacy['f1_score'] == 1.0).sum(),
        ((legacy['f1_score'] >= 0.7) & (legacy['f1_score'] < 1.0)).sum(),
        ((legacy['f1_score'] >= 0.4) & (legacy['f1_score'] < 0.7)).sum(),
        ((legacy['f1_score'] > 0.0) & (legacy['f1_score'] < 0.4)).sum(),
        (legacy['f1_score'] == 0.0).sum(),
    ]
    mafrag_dist = [
        (mafrag['f1_score'] == 1.0).sum(),
        ((mafrag['f1_score'] >= 0.7) & (mafrag['f1_score'] < 1.0)).sum(),
        ((mafrag['f1_score'] >= 0.4) & (mafrag['f1_score'] < 0.7)).sum(),
        ((mafrag['f1_score'] > 0.0) & (mafrag['f1_score'] < 0.4)).sum(),
        (mafrag['f1_score'] == 0.0).sum(),
    ]
    
    x = np.arange(len(categories))
    width = 0.25
    ax3.bar(x - width, enhanced_dist, width, label='Baseline Enhanced', 
            color='#3498db', alpha=0.7, edgecolor='black')
    ax3.bar(x, legacy_dist, width, label='Baseline Legacy', 
            color='#e74c3c', alpha=0.7, edgecolor='black')
    ax3.bar(x + width, mafrag_dist, width, label='MAF-RAG', 
            color='#2ecc71', alpha=0.7, edgecolor='black')
    ax3.set_ylabel('Number of Queries', fontweight='bold')
    ax3.set_title('Performance Distribution by Quality Tier', fontweight='bold', fontsize=12)
    ax3.set_xticks(x)
    ax3.set_xticklabels(categories, fontsize=9)
    ax3.legend(fontsize=8)
    ax3.grid(axis='y', alpha=0.3)
    
    # Plot 4: Box plot comparison
    ax4 = axes[1, 1]
    data_for_box = [enhanced['f1_score'], legacy['f1_score'], mafrag['f1_score']]
    bp = ax4.boxplot(data_for_box, labels=systems, patch_artist=True,
                     medianprops=dict(color='red', linewidth=2),
                     boxprops=dict(facecolor='lightblue', alpha=0.7))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax4.set_ylabel('F1-Score', fontweight='bold')
    ax4.set_title('F1-Score Distribution (Box Plot)', fontweight='bold', fontsize=12)
    ax4.set_ylim([0, 1.0])
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('evaluation/visualization_overall_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: evaluation/visualization_overall_comparison.png")
    plt.close()

def plot_category_comparison(enhanced, legacy, mafrag):
    """Plot 2: Performance by query category"""
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Get unique categories
    all_categories = sorted(set(list(enhanced['category'].unique()) + 
                               list(legacy['category'].unique()) + 
                               list(mafrag['category'].unique())))
    
    # Calculate mean F1 by category for each system
    enhanced_by_cat = enhanced.groupby('category')['f1_score'].mean()
    legacy_by_cat = legacy.groupby('category')['f1_score'].mean()
    mafrag_by_cat = mafrag.groupby('category')['f1_score'].mean()
    
    # Ensure all categories present (fill missing with 0)
    enhanced_vals = [enhanced_by_cat.get(cat, 0) for cat in all_categories]
    legacy_vals = [legacy_by_cat.get(cat, 0) for cat in all_categories]
    mafrag_vals = [mafrag_by_cat.get(cat, 0) for cat in all_categories]
    
    # Plot 1: Grouped bar chart
    ax1 = axes[0]
    x = np.arange(len(all_categories))
    width = 0.25
    ax1.bar(x - width, enhanced_vals, width, label='Baseline Enhanced', 
            color='#3498db', alpha=0.7, edgecolor='black')
    ax1.bar(x, legacy_vals, width, label='Baseline Legacy', 
            color='#e74c3c', alpha=0.7, edgecolor='black')
    ax1.bar(x + width, mafrag_vals, width, label='MAF-RAG', 
            color='#2ecc71', alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Mean F1-Score', fontweight='bold')
    ax1.set_title('Performance by Query Category', fontweight='bold', fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(all_categories, rotation=45, ha='right')
    ax1.set_ylim([0, 1.0])
    ax1.axhline(y=0.7, color='green', linestyle='--', alpha=0.3)
    ax1.axhline(y=0.4, color='orange', linestyle='--', alpha=0.3)
    ax1.legend(fontsize=9)
    ax1.grid(axis='y', alpha=0.3)
    
    # Plot 2: Count by category
    ax2 = axes[1]
    enhanced_counts = enhanced['category'].value_counts()
    legacy_counts = legacy['category'].value_counts()
    mafrag_counts = mafrag['category'].value_counts()
    
    enhanced_count_vals = [enhanced_counts.get(cat, 0) for cat in all_categories]
    legacy_count_vals = [legacy_counts.get(cat, 0) for cat in all_categories]
    mafrag_count_vals = [mafrag_counts.get(cat, 0) for cat in all_categories]
    
    ax2.bar(x - width, enhanced_count_vals, width, label='Baseline Enhanced', 
            color='#3498db', alpha=0.7, edgecolor='black')
    ax2.bar(x, legacy_count_vals, width, label='Baseline Legacy', 
            color='#e74c3c', alpha=0.7, edgecolor='black')
    ax2.bar(x + width, mafrag_count_vals, width, label='MAF-RAG', 
            color='#2ecc71', alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Number of Queries', fontweight='bold')
    ax2.set_title('Query Distribution by Category', fontweight='bold', fontsize=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(all_categories, rotation=45, ha='right')
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('evaluation/visualization_category_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: evaluation/visualization_category_comparison.png")
    plt.close()

def plot_method_comparison(enhanced, legacy, mafrag):
    """Plot 3: Performance by search method"""
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: F1-Score by method for MAF-RAG (has multiple methods)
    ax1 = axes[0]
    if 'search_method' in mafrag.columns:
        method_performance = mafrag.groupby('search_method')['f1_score'].agg(['mean', 'count'])
        method_performance = method_performance.sort_values('mean', ascending=False)
        
        bars = ax1.bar(range(len(method_performance)), method_performance['mean'], 
                      color=['#2ecc71', '#3498db', '#e74c3c'][:len(method_performance)], 
                      alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Mean F1-Score', fontweight='bold')
        ax1.set_title('MAF-RAG: Performance by Search Method', fontweight='bold', fontsize=12)
        ax1.set_xticks(range(len(method_performance)))
        ax1.set_xticklabels(method_performance.index, rotation=45, ha='right')
        ax1.set_ylim([0, 1.0])
        ax1.axhline(y=0.7, color='green', linestyle='--', alpha=0.3)
        ax1.axhline(y=0.4, color='orange', linestyle='--', alpha=0.3)
        
        # Add count labels
        for i, (bar, count) in enumerate(zip(bars, method_performance['count'])):
            ax1.text(bar.get_x() + bar.get_width()/2, 0.05, f'n={int(count)}', 
                    ha='center', va='bottom', fontsize=9, color='black', fontweight='bold')
        
        ax1.grid(axis='y', alpha=0.3)
    
    # Plot 2: Method distribution
    ax2 = axes[1]
    if 'search_method' in mafrag.columns:
        method_counts = mafrag['search_method'].value_counts()
        colors_pie = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6'][:len(method_counts)]
        
        wedges, texts, autotexts = ax2.pie(method_counts.values, labels=method_counts.index, 
                                           autopct='%1.1f%%', startangle=90,
                                           colors=colors_pie, textprops={'fontweight': 'bold'})
        ax2.set_title('MAF-RAG: Search Method Distribution', fontweight='bold', fontsize=12)
        
        # Add count to labels
        for i, (text, count) in enumerate(zip(texts, method_counts.values)):
            text.set_text(f'{text.get_text()}\n(n={count})')
    
    plt.tight_layout()
    plt.savefig('evaluation/visualization_method_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: evaluation/visualization_method_comparison.png")
    plt.close()

def plot_f1_histograms(enhanced, legacy, mafrag):
    """Plot 4: F1-Score distribution histograms"""
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    datasets = [
        (enhanced, 'Baseline Enhanced', '#3498db', axes[0]),
        (legacy, 'Baseline Legacy', '#e74c3c', axes[1]),
        (mafrag, 'MAF-RAG', '#2ecc71', axes[2])
    ]
    
    for df, title, color, ax in datasets:
        ax.hist(df['f1_score'], bins=20, color=color, alpha=0.7, edgecolor='black')
        ax.axvline(df['f1_score'].mean(), color='red', linestyle='--', linewidth=2, 
                  label=f'Mean: {df["f1_score"].mean():.3f}')
        ax.axvline(df['f1_score'].median(), color='blue', linestyle='--', linewidth=2, 
                  label=f'Median: {df["f1_score"].median():.3f}')
        ax.set_xlabel('F1-Score', fontweight='bold')
        ax.set_ylabel('Frequency', fontweight='bold')
        ax.set_title(f'{title}\n(n={len(df)})', fontweight='bold', fontsize=11)
        ax.set_xlim([0, 1.0])
        ax.legend(fontsize=8)
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('evaluation/visualization_f1_histograms.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: evaluation/visualization_f1_histograms.png")
    plt.close()

def generate_summary_table(enhanced, legacy, mafrag):
    """Generate comprehensive summary statistics table"""
    
    stats_list = [
        calculate_summary_statistics(enhanced, 'Baseline Enhanced'),
        calculate_summary_statistics(legacy, 'Baseline Legacy'),
        calculate_summary_statistics(mafrag, 'MAF-RAG')
    ]
    
    df_stats = pd.DataFrame(stats_list)
    
    # Calculate percentages
    df_stats['Perfect %'] = (df_stats['Perfect (F1=1.0)'] / df_stats['Total Queries'] * 100).round(1)
    df_stats['High %'] = (df_stats['High (F1≥0.7)'] / df_stats['Total Queries'] * 100).round(1)
    df_stats['Failed %'] = (df_stats['Failed (F1=0.0)'] / df_stats['Total Queries'] * 100).round(1)
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(df_stats.to_string(index=False))
    print("="*80 + "\n")
    
    # Save to CSV
    df_stats.to_csv('evaluation/summary_statistics.csv', index=False)
    print("✅ Saved: evaluation/summary_statistics.csv\n")
    
    return df_stats

def main():
    """Main execution function"""
    
    print("\n" + "="*80)
    print("RESULTS AND DISCUSSION: COMPARATIVE VISUALIZATION")
    print("="*80 + "\n")
    
    # Load data
    print("[1/6] Loading datasets...")
    enhanced, legacy, mafrag, all_data = load_and_prepare_data()
    print(f"   - Baseline Enhanced: {len(enhanced)} queries")
    print(f"   - Baseline Legacy: {len(legacy)} queries")
    print(f"   - MAF-RAG: {len(mafrag)} queries\n")
    
    # Generate summary statistics
    print("[2/6] Generating summary statistics...")
    df_stats = generate_summary_table(enhanced, legacy, mafrag)
    
    # Generate visualizations
    print("[3/6] Creating overall comparison plots...")
    plot_overall_comparison(enhanced, legacy, mafrag)
    
    print("[4/6] Creating category comparison plots...")
    plot_category_comparison(enhanced, legacy, mafrag)
    
    print("[5/6] Creating method comparison plots...")
    plot_method_comparison(enhanced, legacy, mafrag)
    
    print("[6/6] Creating F1-score histograms...")
    plot_f1_histograms(enhanced, legacy, mafrag)
    
    print("\n" + "="*80)
    print("✅ VISUALIZATION COMPLETE!")
    print("="*80)
    print("\nGenerated files:")
    print("  📊 evaluation/visualization_overall_comparison.png")
    print("  📊 evaluation/visualization_category_comparison.png")
    print("  📊 evaluation/visualization_method_comparison.png")
    print("  📊 evaluation/visualization_f1_histograms.png")
    print("  📄 evaluation/summary_statistics.csv")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
