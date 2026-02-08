#!/usr/bin/env python3
"""
Analyze retrieval test results with BERTScore confidence calculation.
This script takes a retrieval test CSV and adds BERTScore confidence metrics
by comparing questions against the retrieved chunks.

BERTScore runs after retrieval is complete, avoiding memory issues during real-time testing.
"""

import sys
import csv
import os
import argparse
from typing import Dict, List, Tuple
import time

# BERTScore imports
try:
    from bert_score import score as bert_score
    BERTSCORE_AVAILABLE = True
except ImportError:
    BERTSCORE_AVAILABLE = False

# Supabase for chunk retrieval
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Load environment variables
from dotenv import load_dotenv
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


def get_chunk_content(chunk_id: str) -> str:
    """
    Retrieve chunk content from Supabase by chunk_id
    Uses pre-initialized SUPABASE_CLIENT for efficiency
    """
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
    """
    Calculate BERTScore confidence between question and retrieved chunks.
    
    Args:
        question: The query/question
        chunk_contents: List of retrieved chunk texts
    
    Returns:
        dict with bert_avg, bert_max, bert_level
    """
    if not BERTSCORE_AVAILABLE or not chunk_contents:
        return {
            'bert_avg': '',
            'bert_max': '',
            'bert_level': 'unavailable'
        }
    
    try:
        # Create list of questions (same for all chunks)
        questions = [question] * len(chunk_contents)
        
        # Calculate BERTScore F1 between question and each chunk
        P, R, F1 = bert_score(chunk_contents, questions, lang='en', verbose=False)
        
        # Get average and max F1 scores
        f1_list = F1.tolist() if hasattr(F1, 'tolist') else F1
        avg_f1 = sum(f1_list) / len(f1_list)
        max_f1 = max(f1_list)
        
        # Categorize confidence level
        if max_f1 >= 0.7:
            bert_level = 'high'
        elif max_f1 >= 0.5:
            bert_level = 'medium'
        else:
            bert_level = 'low'
        
        return {
            'bert_avg': round(avg_f1, 3),
            'bert_max': round(max_f1, 3),
            'bert_level': bert_level
        }
    
    except Exception as e:
        print(f"   [WARN]  BERTScore error: {str(e)[:50]}")
        return {
            'bert_avg': '',
            'bert_max': '',
            'bert_level': 'error'
        }


def analyze_retrieval_csv(csv_file: str, output_file: str = None):
    """
    Analyze retrieval test CSV and add BERTScore confidence metrics.
    
    Args:
        csv_file: Path to retrieval test CSV
        output_file: Output CSV file (default: input_file_with_bertscore.csv)
    """
    if not os.path.exists(csv_file):
        print(f"[FAIL] CSV file not found: {csv_file}")
        return
    
    if output_file is None:
        base, ext = os.path.splitext(csv_file)
        output_file = f"{base}_with_bertscore{ext}"
    
    print(f"[STATS] Analyzing retrieval results: {csv_file}")
    print(f"[SAVE] Output will be saved to: {output_file}")
    print()
    
    # Read input CSV
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"[OK] Loaded {len(rows)} retrieval results")
    print()
    
    # Process each row
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
        
        # Get chunk IDs
        chunk_ids = [cid.strip() for cid in generated_chunks.split(',') if cid.strip()]
        
        if not chunk_ids:
            print(f"   [WARN]  No chunks retrieved")
            row['bert_score'] = ''
            row['bert_level'] = 'no_chunks'
            row['bert_max'] = ''
            continue
        
        # Retrieve chunk contents from Supabase
        chunk_contents = []
        for chunk_id in chunk_ids:
            content = get_chunk_content(chunk_id)
            if content:
                chunk_contents.append(content)
        
        if not chunk_contents:
            print(f"   [WARN]  Could not retrieve chunk contents from Supabase")
            row['bert_score'] = ''
            row['bert_level'] = 'no_content'
            row['bert_max'] = ''
            continue
        
        # Calculate BERTScore
        print(f"   [METRIC] Calculating BERTScore for {len(chunk_contents)} chunks...")
        bert_result = calculate_bertscore_confidence(question, chunk_contents)
        
        # Add to row
        row['bert_score'] = bert_result['bert_avg']
        row['bert_level'] = bert_result['bert_level']
        row['bert_max'] = bert_result['bert_max']
        
        if bert_result['bert_avg']:
            print(f"   [OK] BERTScore: avg={bert_result['bert_avg']:.3f}, max={bert_result['bert_max']:.3f} ({bert_result['bert_level']})")
        else:
            print(f"   [WARN]  BERTScore calculation failed: {bert_result['bert_level']}")
    
    elapsed = time.time() - start_time
    print()
    print("=" * 80)
    print(f"[TIME]  Analysis complete in {elapsed:.1f}s")
    print("=" * 80)
    print()
    
    # Write output CSV
    if rows:
        fieldnames = list(rows[0].keys())
        
        # Add BERTScore columns if not present
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
        
        print(f"[OK] Results saved to: {output_file}")
    else:
        print("[FAIL] No results to save")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze retrieval test results with BERTScore confidence'
    )
    parser.add_argument(
        '--csv',
        required=True,
        help='Path to retrieval test CSV file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output CSV file (default: input_file_with_bertscore.csv)'
    )
    
    args = parser.parse_args()
    
    analyze_retrieval_csv(args.csv, args.output)


if __name__ == '__main__':
    main()
