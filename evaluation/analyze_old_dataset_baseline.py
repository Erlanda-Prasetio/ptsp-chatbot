"""
Analyze OLD Dataset Retrieval Test Results
==========================================

Analyzes the retrieval test results from retrieval_test_result.csv
specifically for the OLD dataset and exports baseline metrics.

Usage:
    python evaluation/analyze_old_dataset_baseline.py
"""

import os
import sys
import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def analyze_old_dataset_baseline():
    """Analyze and export OLD dataset retrieval test baseline"""
    
    print("\n" + "="*70)
    print("OLD DATASET RETRIEVAL TEST BASELINE ANALYSIS")
    print("="*70 + "\n")
    
    # Load the retrieval test results
    csv_file = Path('evaluation') / 'retrieval_test_result.csv'
    
    if not csv_file.exists():
        print(f"[FAIL] ERROR: {csv_file} not found!")
        return False
    
    print(f" Loading retrieval test results from: {csv_file}")
    
    # Parse CSV
    old_results = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Only keep OLD dataset entries
                if row.get('dataset_source') == 'OLD':
                    old_results.append(row)
        
        print(f"   [OK] Loaded {len(old_results)} OLD dataset query results\n")
        
        if len(old_results) == 0:
            print("[FAIL] No OLD dataset results found in CSV!")
            return False
        
        # Analyze results
        print("[SEARCH] Analyzing results...\n")
        
        # Initialize tracking
        analysis_data = []
        metrics = {
            'total_queries': len(old_results),
            'by_category': defaultdict(list),
            'by_search_method': defaultdict(list),
            'precision_scores': [],
            'recall_scores': [],
            'f1_scores': [],
            'retrieval_times': [],
        }
        
        for idx, row in enumerate(old_results, 1):
            query_id = row.get('query_id', '')
            question = row.get('question', '')
            category = row.get('category', 'Unknown')
            retrieved_chunks = row.get('retrieved_chunks', '')
            search_method = row.get('search_method', 'unknown')
            retrieval_time = float(row.get('retrieval_time_seconds', 0) or 0)
            
            try:
                precision = float(row.get('precision', 0) or 0)
            except:
                precision = 0.0
            
            try:
                recall = float(row.get('recall', 0) or 0)
            except:
                recall = 0.0
            
            try:
                f1_score = float(row.get('f1_score', 0) or 0)
            except:
                f1_score = 0.0
            
            # Count retrieved chunks
            chunk_count = len([x for x in retrieved_chunks.split(',') if x.strip()])
            
            # Determine if result is good (F1 > 0.5)
            quality = 'Good' if f1_score >= 0.5 else 'Poor'
            
            analysis_data.append({
                'query_id': query_id,
                'question': question,
                'category': category,
                'retrieved_chunk_count': chunk_count,
                'search_method': search_method,
                'retrieval_time_seconds': round(retrieval_time, 2),
                'precision': round(precision, 3),
                'recall': round(recall, 3),
                'f1_score': round(f1_score, 3),
                'quality': quality,
            })
            
            # Track metrics
            metrics['by_category'][category].append(f1_score)
            metrics['by_search_method'][search_method].append(f1_score)
            metrics['precision_scores'].append(precision)
            metrics['recall_scores'].append(recall)
            metrics['f1_scores'].append(f1_score)
            metrics['retrieval_times'].append(retrieval_time)
        
        # Export to CSV
        csv_output = Path('evaluation') / 'old_dataset_baseline.csv'
        
        print(f" Exporting to {csv_output}...")
        
        with open(csv_output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'query_id', 'question', 'category', 'retrieved_chunk_count',
                'search_method', 'retrieval_time_seconds', 'precision', 'recall', 
                'f1_score', 'quality'
            ])
            writer.writeheader()
            writer.writerows(analysis_data)
        
        print(f"   [OK] Exported {len(analysis_data)} records\n")
        
        # Calculate summary statistics
        print("[METRIC] Summary Statistics:")
        print(f"   Total Queries: {metrics['total_queries']}")
        
        avg_precision = sum(metrics['precision_scores']) / len(metrics['precision_scores']) if metrics['precision_scores'] else 0
        avg_recall = sum(metrics['recall_scores']) / len(metrics['recall_scores']) if metrics['recall_scores'] else 0
        avg_f1 = sum(metrics['f1_scores']) / len(metrics['f1_scores']) if metrics['f1_scores'] else 0
        
        print(f"   Average Precision: {avg_precision:.3f}")
        print(f"   Average Recall: {avg_recall:.3f}")
        print(f"   Average F1 Score: {avg_f1:.3f}")
        
        avg_retrieval_time = sum(metrics['retrieval_times']) / len(metrics['retrieval_times']) if metrics['retrieval_times'] else 0
        print(f"   Average Retrieval Time: {avg_retrieval_time:.2f}s")
        
        good_quality = sum(1 for d in analysis_data if d['quality'] == 'Good')
        poor_quality = sum(1 for d in analysis_data if d['quality'] == 'Poor')
        print(f"   Good Quality Results: {good_quality}/{metrics['total_queries']} ({good_quality/metrics['total_queries']*100:.1f}%)")
        print(f"   Poor Quality Results: {poor_quality}/{metrics['total_queries']} ({poor_quality/metrics['total_queries']*100:.1f}%)")
        
        # By Category
        print(f"\n   By Category:")
        for category in sorted(metrics['by_category'].keys()):
            scores = metrics['by_category'][category]
            avg_score = sum(scores) / len(scores)
            print(f"      {category}: {len(scores)} queries, Avg F1: {avg_score:.3f}")
        
        # By Search Method
        print(f"\n   By Search Method:")
        for method in sorted(metrics['by_search_method'].keys()):
            scores = metrics['by_search_method'][method]
            avg_score = sum(scores) / len(scores)
            print(f"      {method}: {len(scores)} queries, Avg F1: {avg_score:.3f}")
        
        # Save summary
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'dataset': 'OLD',
            'total_queries': metrics['total_queries'],
            'average_precision': round(avg_precision, 3),
            'average_recall': round(avg_recall, 3),
            'average_f1': round(avg_f1, 3),
            'average_retrieval_time': round(avg_retrieval_time, 2),
            'good_quality_count': good_quality,
            'poor_quality_count': poor_quality,
            'good_quality_percentage': round(good_quality/metrics['total_queries']*100, 1),
            'by_category': {
                cat: {
                    'count': len(scores),
                    'avg_f1': round(sum(scores) / len(scores), 3)
                }
                for cat, scores in metrics['by_category'].items()
            },
            'by_search_method': {
                method: {
                    'count': len(scores),
                    'avg_f1': round(sum(scores) / len(scores), 3)
                }
                for method, scores in metrics['by_search_method'].items()
            },
        }
        
        summary_path = Path('evaluation') / 'old_dataset_baseline_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n Summary saved to: {summary_path}")
        print(f" CSV saved to: {csv_output}\n")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = analyze_old_dataset_baseline()
    
    if success:
        print("[OK] Analysis complete!\n")
    else:
        print("[FAIL] Analysis failed!\n")
        sys.exit(1)
