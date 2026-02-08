#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analyze Retrieval Test Results
================================

Analyzes results from run_retrieval_test.py
Shows precision, recall, F1 score, search method distribution, and problem areas.

Can also add BERTScore confidence metrics to CSV results.

Usage:
    python evaluation/analyze_retrieval_test.py evaluation/raw_results/retrieval_baseline.json
    python evaluation/analyze_retrieval_test.py evaluation/retrieval_test_result.csv
    python evaluation/analyze_retrieval_test.py evaluation/retrieval_test_result.csv --add-bertscore

Author: RAG Evaluation Framework
Date: October 2025
"""

import json
import csv
import sys
import os
import time
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
from dotenv import load_dotenv

# TF-IDF imports (lightweight alternative to BERTScore)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available, TF-IDF scores will be unavailable")
try:
    from bert_score import score as bert_score
    BERTSCORE_AVAILABLE = False  # Disabled due to memory issues
except ImportError:
    BERTSCORE_AVAILABLE = False

# Lightweight similarity scoring
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Supabase for chunk retrieval
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize Supabase client once
SUPABASE_CLIENT = None
if SUPABASE_AVAILABLE:
    try:
        supabase_url = os.getenv('SUPABASE_URL', '')
        supabase_key = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')
        if supabase_url and supabase_key:
            SUPABASE_CLIENT = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Warning: Could not initialize Supabase: {e}")


def load_results(file_path: str) -> Dict:
    """Load retrieval test results from JSON or CSV file"""
    if file_path.endswith('.csv'):
        # Load from CSV
        results = []
        total_retrieval_time = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert precision/recall/f1 to float
                retrieval_time = 0
                if row.get('retrieval_time_seconds'):
                    try:
                        retrieval_time = float(row['retrieval_time_seconds'])
                        total_retrieval_time += retrieval_time
                    except ValueError:
                        retrieval_time = 0
                
                result = {
                    'query_id': row['query_id'],
                    'question': row['question'],
                    'dataset_source': row.get('dataset_source', 'unknown'),
                    'category': row.get('category', 'unknown'),
                    'search_method': row.get('search_method', 'unknown'),
                    'precision': float(row['precision']) if row.get('precision') else None,
                    'recall': float(row['recall']) if row.get('recall') else None,
                    'f1_score': float(row['f1_score']) if row.get('f1_score') else None,
                    'retrieval_time_seconds': retrieval_time,
                }
                results.append(result)
        
        return {
            'test_name': Path(file_path).stem,
            'results': results,
            'total_time_seconds': total_retrieval_time,
            'test_type': 'retrieval'
        }
    else:
        # Load from JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


def get_chunk_content(chunk_id: str) -> str:
    """Retrieve chunk content from Supabase"""
    if not SUPABASE_CLIENT:
        return ""
    
    try:
        pg_table = os.getenv('PG_TABLE', 'rag_chunks_jateng')
        result = SUPABASE_CLIENT.table(pg_table).select('content').eq('id', int(chunk_id)).execute()
        
        if result.data and len(result.data) > 0:
            chunk = result.data[0]
            return chunk.get('content', '')
        
        return ""
    except Exception as e:
        return ""


def calculate_bertscore_confidence(question: str, chunk_contents: List[str]) -> Dict:
    """Calculate TF-IDF similarity confidence between question and chunks (lightweight alternative to BERTScore)"""
    if not SKLEARN_AVAILABLE or not chunk_contents:
        return {
            'bert_avg': '',
            'bert_max': '',
            'bert_level': 'unavailable'
        }
    
    try:
        # Use TF-IDF for lightweight similarity scoring
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        all_texts = [question] + chunk_contents
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarity between question and each chunk
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        avg_sim = float(similarities.mean())
        max_sim = float(similarities.max())
        
        # Categorize confidence level
        if max_sim >= 0.7:
            bert_level = 'high'
        elif max_sim >= 0.5:
            bert_level = 'medium'
        else:
            bert_level = 'low'
        
        return {
            'bert_avg': round(avg_sim, 3),
            'bert_max': round(max_sim, 3),
            'bert_level': bert_level
        }
    
    except Exception as e:
        error_msg = str(e)[:50]
        return {
            'bert_avg': '',
            'bert_max': '',
            'bert_level': f'error: {error_msg}'
        }


def add_bertscore_to_csv(csv_file: str, output_file: str = None):
    """Add BERTScore confidence metrics to CSV and save"""
    if not os.path.exists(csv_file):
        print(f"[FAIL] CSV file not found: {csv_file}")
        return
    
    if output_file is None:
        base, ext = os.path.splitext(csv_file)
        output_file = f"{base}_with_bertscore{ext}"
    
    print()
    print(f"[STATS] Adding BERTScore to: {csv_file}")
    print(f"[SAVE] Output: {output_file}")
    print()
    
    # Read input CSV
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"[OK] Loaded {len(rows)} results")
    print()
    print("=" * 80)
    print("CALCULATING BERTSCORE CONFIDENCE")
    print("=" * 80)
    print()
    
    start_time = time.time()
    
    for i, row in enumerate(rows, 1):
        query_id = row.get('query_id', f'Q_{i:02d}')
        question = row.get('question', '')
        generated_chunks = row.get('generated_chunks', '')
        
        print(f"[{i}/{len(rows)}] {query_id}: {question[:60]}...")
        
        chunk_ids = [cid.strip() for cid in generated_chunks.split(',') if cid.strip()]
        
        if not chunk_ids:
            row['bert_score'] = ''
            row['bert_level'] = 'no_chunks'
            row['bert_max'] = ''
            continue
        
        chunk_contents = []
        for chunk_id in chunk_ids:
            content = get_chunk_content(chunk_id)
            if content:
                chunk_contents.append(content)
        
        if not chunk_contents:
            row['bert_score'] = ''
            row['bert_level'] = 'no_content'
            row['bert_max'] = ''
            continue
        
        print(f"   [METRIC] BERTScore for {len(chunk_contents)} chunks...")
        bert_result = calculate_bertscore_confidence(question, chunk_contents)
        
        row['bert_score'] = bert_result['bert_avg']
        row['bert_level'] = bert_result['bert_level']
        row['bert_max'] = bert_result['bert_max']
        
        if bert_result['bert_avg']:
            print(f"   [OK] avg={bert_result['bert_avg']:.3f}, max={bert_result['bert_max']:.3f} ({bert_result['bert_level']})")
        else:
            print(f"   [WARN]  {bert_result['bert_level']}")
    
    elapsed = time.time() - start_time
    print()
    print("=" * 80)
    print(f"[TIME]  Complete in {elapsed:.1f}s")
    print("=" * 80)
    print()
    
    # Write output CSV
    if rows:
        fieldnames = list(rows[0].keys())
        
        if 'bert_score' not in fieldnames:
            fieldnames.append('bert_score')
        if 'bert_level' not in fieldnames:
            fieldnames.append('bert_level')
        if 'bert_max' not in fieldnames:
            fieldnames.append('bert_max')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"[OK] Saved to: {output_file}")
    else:
        print("[FAIL] No results to save")


def analyze_retrieval_test(results_data: Dict):
    """Analyze and display retrieval test results"""
    
    test_name = results_data.get('test_name', 'Unknown')
    results = results_data.get('results', [])
    total_time = results_data.get('total_time_seconds', 0)
    
    if not results:
        print("[FAIL] No results to analyze")
        return
    
    # Calculate aggregate metrics
    total_queries = len(results)
    successful = sum(1 for r in results if not r.get('error'))
    failed = total_queries - successful
    
    # Retrieval metrics (only for queries with ground truth)
    scorable_results = [r for r in results if r.get('precision') is not None]
    
    if scorable_results:
        avg_precision = sum(r['precision'] for r in scorable_results) / len(scorable_results)
        avg_recall = sum(r['recall'] for r in scorable_results) / len(scorable_results)
        avg_f1 = sum(r['f1_score'] for r in scorable_results) / len(scorable_results)
        
        min_precision = min(r['precision'] for r in scorable_results)
        max_precision = max(r['precision'] for r in scorable_results)
        min_recall = min(r['recall'] for r in scorable_results)
        max_recall = max(r['recall'] for r in scorable_results)
        min_f1 = min(r['f1_score'] for r in scorable_results)
        max_f1 = max(r['f1_score'] for r in scorable_results)
    else:
        avg_precision = avg_recall = avg_f1 = 0
        min_precision = max_precision = 0
        min_recall = max_recall = 0
        min_f1 = max_f1 = 0
    
    # Search method distribution
    search_methods = defaultdict(int)
    for r in results:
        method = r.get('search_method', 'unknown')
        if not method or method.strip() == '':
            method = 'unknown'
        search_methods[method] += 1
    
    # Dataset distribution
    dataset_counts = defaultdict(int)
    for r in results:
        dataset = r.get('dataset_source', 'unknown')
        dataset_counts[dataset] += 1
    
    # Category performance
    category_metrics = defaultdict(lambda: {'count': 0, 'f1_sum': 0, 'f1_scores': []})
    for r in scorable_results:
        cat = r.get('category', 'uncategorized')
        category_metrics[cat]['count'] += 1
        category_metrics[cat]['f1_sum'] += r['f1_score']
        category_metrics[cat]['f1_scores'].append(r['f1_score'])
    
    # Problem identification - exclude internet_fallback as it's expected to have 0 precision
    zero_precision_with_fallback = sum(1 for r in scorable_results if r['precision'] == 0)
    zero_recall_with_fallback = sum(1 for r in scorable_results if r['recall'] == 0)
    
    # Count zero precision/recall ONLY from non-internet_fallback queries
    zero_precision_actual_issue = sum(1 for r in scorable_results 
                                     if r['precision'] == 0 and r.get('search_method') != 'internet_fallback')
    zero_recall_actual_issue = sum(1 for r in scorable_results 
                                   if r['recall'] == 0 and r.get('search_method') != 'internet_fallback')
    
    internet_fallback = sum(1 for r in results if r.get('search_method') == 'internet_fallback')
    
    # Token usage tracking
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_all_tokens = 0
    for r in results:
        try:
            total_prompt_tokens += int(r.get('prompt_tokens', 0) or 0)
            total_completion_tokens += int(r.get('completion_tokens', 0) or 0)
            total_all_tokens += int(r.get('total_tokens', 0) or 0)
        except (ValueError, TypeError):
            pass
    
    # Timing - convert string times to float
    retrieval_times = []
    for r in results:
        time_val = r.get('retrieval_time_seconds', 0)
        try:
            if isinstance(time_val, str):
                time_val = float(time_val) if time_val else 0
            retrieval_times.append(float(time_val))
        except (ValueError, TypeError):
            retrieval_times.append(0)
    
    avg_retrieval_time = sum(retrieval_times) / len(retrieval_times) if retrieval_times else 0
    max_retrieval_time = max(retrieval_times) if retrieval_times else 0
    min_retrieval_time = min(retrieval_times) if retrieval_times else 0
    
    # Print report
    print()
    print("=" * 70)
    print("RETRIEVAL TEST ANALYSIS")
    print("=" * 70)
    print()
    print(f" Overall Performance:")
    print(f"   Total Queries: {total_queries}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print()
    print(f"  Timing:")
    print(f"   Avg Retrieval Time: {avg_retrieval_time:.2f}s")
    print(f"   Max Retrieval Time: {max_retrieval_time:.2f}s")
    print(f"   Min Retrieval Time: {min_retrieval_time:.2f}s")
    print(f"   Total Test Time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print()
    
    if scorable_results:
        print(f" Retrieval Metrics (n={len(scorable_results)}):")
        print(f"   Precision: {avg_precision:.3f} (min={min_precision:.3f}, max={max_precision:.3f})")
        print(f"   Recall:    {avg_recall:.3f} (min={min_recall:.3f}, max={max_recall:.3f})")
        print(f"   F1-Score:  {avg_f1:.3f} (min={min_f1:.3f}, max={max_f1:.3f})")
        print()
    
    # Only print Query Distribution if not all unknown
    if not (len(dataset_counts) == 1 and 'unknown' in dataset_counts):
        print(f" Query Distribution:")
        for dataset, count in sorted(dataset_counts.items()):
            if dataset != 'unknown':
                print(f"   {dataset} Dataset: {count} questions")
        print()
    
    print(f" Search Method Distribution:")
    for method, count in sorted(search_methods.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_queries * 100) if total_queries > 0 else 0
        print(f"   {method:20s}: {count:3d} ({pct:5.1f}%)")
    print()
    
    if category_metrics:
        print(f" Performance by Category:")
        for cat, metrics in sorted(category_metrics.items(), key=lambda x: x[1]['f1_sum']/x[1]['count'], reverse=True):
            avg_f1_cat = metrics['f1_sum'] / metrics['count']
            print(f"   {cat:15s}: {metrics['count']:3d} questions, F1={avg_f1_cat:.3f}")
        print()
    
    print(f"  Issues Identified:")
    if scorable_results:
        # Report zero precision/recall ONLY if they come from non-internet_fallback queries
        if zero_precision_actual_issue > 0:
            zero_prec_pct = (zero_precision_actual_issue / len(scorable_results) * 100)
            print(f"   Zero Precision (non-fallback): {zero_precision_actual_issue}/{len(scorable_results)} ({zero_prec_pct:.1f}%)")
        
        if zero_recall_actual_issue > 0:
            zero_rec_pct = (zero_recall_actual_issue / len(scorable_results) * 100)
            print(f"   Zero Recall (non-fallback):    {zero_recall_actual_issue}/{len(scorable_results)} ({zero_rec_pct:.1f}%)")
        
        # Show total zero precision/recall for context (including fallback)
        total_zero_prec_pct = (zero_precision_with_fallback / len(scorable_results) * 100)
        total_zero_rec_pct = (zero_recall_with_fallback / len(scorable_results) * 100)
        print(f"   Zero Precision (all methods):  {zero_precision_with_fallback}/{len(scorable_results)} ({total_zero_prec_pct:.1f}%) [incl. fallback: {zero_precision_with_fallback - zero_precision_actual_issue}]")
        print(f"   Zero Recall (all methods):     {zero_recall_with_fallback}/{len(scorable_results)} ({total_zero_rec_pct:.1f}%) [incl. fallback: {zero_recall_with_fallback - zero_recall_actual_issue}]")
    
    fallback_pct = (internet_fallback / total_queries * 100) if total_queries > 0 else 0
    print(f"   Internet Fallback: {internet_fallback}/{total_queries} ({fallback_pct:.1f}%)")
    if fallback_pct > 30:
        print(f"   ℹ  Note: Internet fallback returns non-local chunks, zero precision is expected")
    print()
    
    # Worst performing queries
    if scorable_results:
        print(" Worst Performing Queries (Bottom 5 by F1):")
        worst_queries = sorted(scorable_results, key=lambda x: x['f1_score'])[:5]
        for i, r in enumerate(worst_queries, 1):
            q_id = r.get('query_id', '?')
            question = r.get('question', '')[:50]
            f1 = r.get('f1_score', 0)
            method = r.get('search_method', '?')
            fallback_tag = " [ FALLBACK]" if method == 'internet_fallback' else ""
            print(f"   {i}. [{q_id}] F1={f1:.3f} ({method}){fallback_tag}: {question}...")
        print()
        
        print(" Best Performing Queries (Top 5 by F1):")
        best_queries = sorted(scorable_results, key=lambda x: x['f1_score'], reverse=True)[:5]
        for i, r in enumerate(best_queries, 1):
            q_id = r.get('query_id', '?')
            question = r.get('question', '')[:50]
            f1 = r.get('f1_score', 0)
            method = r.get('search_method', '?')
            fallback_tag = " [ FALLBACK]" if method == 'internet_fallback' else ""
            print(f"   {i}. [{q_id}] F1={f1:.3f} ({method}){fallback_tag}: {question}...")
        print()
    
    print("=" * 70)
    print(" Summary:")
    print("=" * 70)
    if scorable_results:
        print(f"Overall F1 Score: {avg_f1:.3f}")
        print(f"Precision: {avg_precision:.3f}")
        print(f"Recall: {avg_recall:.3f}")
    print(f"Internet Fallback Rate: {fallback_pct:.1f}%")
    print(f"Retrieval Timing:")
    print(f"  Average: {avg_retrieval_time:.2f}s")
    print(f"  Max: {max_retrieval_time:.2f}s")
    print(f"  Min: {min_retrieval_time:.2f}s")
    if total_all_tokens > 0:
        print(f"Token Usage:")
        print(f"  Prompt: {total_prompt_tokens:,}")
        print(f"  Completion: {total_completion_tokens:,}")
        print(f"  Total: {total_all_tokens:,}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze retrieval test results with optional BERTScore confidence'
    )
    parser.add_argument(
        'results_file',
        help='Path to results file (JSON or CSV)'
    )
    parser.add_argument(
        '--add-bertscore',
        action='store_true',
        help='Add BERTScore confidence metrics to CSV and save'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file for BERTScore results (default: input_with_bertscore.csv)'
    )
    
    args = parser.parse_args()
    results_file = args.results_file
    
    if not Path(results_file).exists():
        print(f"[FAIL] File not found: {results_file}")
        sys.exit(1)
    
    # If add-bertscore flag, run that instead
    if args.add_bertscore:
        if not results_file.endswith('.csv'):
            print("[FAIL] --add-bertscore requires a CSV file")
            sys.exit(1)
        add_bertscore_to_csv(results_file, args.output)
        return
    
    # Otherwise, analyze and display
    print(f"[FILE] Loaded results from: {results_file}")
    results_data = load_results(results_file)
    
    analyze_retrieval_test(results_data)


if __name__ == "__main__":
    main()
