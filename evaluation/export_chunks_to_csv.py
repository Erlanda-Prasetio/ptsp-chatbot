"""
Export Chunk Confidence Results to CSV for Retrieval Test

This script converts the chunk_confidence_log.json to a CSV format
for the retrieval test, showing all retrieved chunks per question
with columns for generated chunks and evaluation metrics.

Usage:
    python evaluation/export_chunks_to_csv.py --input evaluation/chunk_confidence_log.json --output evaluation/retrieval_test_baseline.csv
"""

import json
import csv
import argparse
from pathlib import Path
from typing import List, Dict


def export_to_csv(input_file: str, output_file: str, format_type: str = 'horizontal'):
    """
    Export chunk confidence results to CSV
    
    Args:
        input_file: Path to chunk_confidence_log.json
        output_file: Path to output CSV file
        format_type: 'horizontal' (1 row per question, 5 chunk columns) or 
                    'vertical' (5 rows per question, 1 chunk per row)
    """
    print(f"[DIR] Loading chunk confidence data from: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data['results']
    total_queries = len(results)
    
    print(f"    Found {total_queries} queries with chunk data")
    print(f" Exporting to CSV format: {format_type}")
    
    if format_type == 'horizontal':
        export_horizontal(results, output_file)
    else:
        export_vertical(results, output_file)
    
    print(f"[OK] Successfully exported to: {output_file}")
    print()


def export_horizontal(results: List[Dict], output_file: str):
    """
    Export in horizontal format: 1 row per question, 5 chunk ID columns
    
    CSV columns for RETRIEVAL TEST:
    - query_id
    - question
    - category
    - dataset_source
    - retrieved_chunks (chunk IDs from confidence test, comma-separated)
    - chunk1_id
    - chunk2_id
    - chunk3_id
    - chunk4_id
    - chunk5_id
    - generated_chunks (empty - to be filled by retrieval test)
    - precision (empty - calculated by retrieval test)
    - recall (empty - calculated by retrieval test)
    - f1_score (empty - calculated by retrieval test)
    - notes (empty - for manual notes)
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        # Define all columns for retrieval test
        base_columns = [
            'query_id', 'question', 'category', 'dataset_source',
            'retrieved_chunks'  # comma-separated chunk IDs
        ]
        
        chunk_columns = [f'chunk{i}_id' for i in range(1, 6)]  # Only IDs, no text
        
        eval_columns = [
            'generated_chunks',  # To be filled by retrieval test
            'search_method',     # Search phase used
            'retrieval_time_seconds',  # NEW: Time taken for this query
            'precision',
            'recall', 
            'f1_score',
            'notes'
        ]
        
        all_columns = base_columns + chunk_columns + eval_columns
        
        writer = csv.DictWriter(f, fieldnames=all_columns)
        writer.writeheader()
        
        for result in results:
            # Get chunk IDs for retrieved_chunks column
            top_chunks = result.get('top_chunks', [])
            chunk_ids = [str(chunk['chunk_id']) for chunk in top_chunks]  # Convert to string
            
            row = {
                'query_id': result['query_id'],
                'question': result['question'],
                'category': result['category'],
                'dataset_source': result['dataset_source'],
                'retrieved_chunks': ','.join(chunk_ids)  # comma-separated
            }
            
            # Add chunk data (up to 5 chunks) - only IDs
            for i in range(1, 6):
                if i - 1 < len(top_chunks):
                    chunk = top_chunks[i - 1]
                    row[f'chunk{i}_id'] = chunk['chunk_id']
                else:
                    row[f'chunk{i}_id'] = ''
            
            # Empty columns for retrieval test to fill
            row['generated_chunks'] = ''
            row['search_method'] = ''
            row['retrieval_time_seconds'] = ''
            row['precision'] = ''
            row['recall'] = ''
            row['f1_score'] = ''
            row['notes'] = ''
            
            writer.writerow(row)
    
    print(f"   [STATS] Format: 1 row per question, {len(all_columns)} columns")
    print(f"    Retrieval test columns: generated_chunks, precision, recall, f1_score")



def export_vertical(results: List[Dict], output_file: str):
    """
    Export in vertical format: 5 rows per question (1 row per chunk)
    
    CSV columns:
    - query_id
    - question
    - category
    - dataset_source
    - confidence_level
    - top_score
    - chunk_rank
    - chunk_id
    - chunk_score
    - chunk_text
    - is_relevant (empty - for user to fill)
    - notes (empty - for user to fill)
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        columns = [
            'query_id', 'question', 'category', 'dataset_source',
            'confidence_level', 'top_score',
            'chunk_rank', 'chunk_id', 'chunk_score', 'chunk_text',
            'is_relevant', 'notes'
        ]
        
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        
        for result in results:
            top_chunks = result.get('top_chunks', [])
            
            for chunk in top_chunks:
                row = {
                    'query_id': result['query_id'],
                    'question': result['question'],
                    'category': result['category'],
                    'dataset_source': result['dataset_source'],
                    'confidence_level': result['confidence_level'],
                    'top_score': result['top_similarity_score'],
                    'chunk_rank': chunk['rank'],
                    'chunk_id': chunk['chunk_id'],
                    'chunk_score': chunk['score'],
                    'chunk_text': chunk['text_preview'],
                    'is_relevant': '',  # For manual scoring
                    'notes': ''
                }
                writer.writerow(row)
    
    print(f"   [STATS] Format: {len(results) * 5} rows (5 rows per question)")
    print(f"    Manual evaluation columns added: is_relevant, notes")


def main():
    parser = argparse.ArgumentParser(
        description='Export chunk confidence results to CSV for evaluation'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input JSON file (e.g., evaluation/chunk_confidence_log.json)'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output CSV file (e.g., evaluation/chunk_evaluation.csv)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['horizontal', 'vertical'],
        default='horizontal',
        help='CSV format: horizontal (1 row/question) or vertical (5 rows/question)'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[FAIL] Error: Input file not found: {args.input}")
        return
    
    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print()
    print("=" * 70)
    print(" EXPORTING CHUNKS TO CSV FOR RETRIEVAL TEST")
    print("=" * 70)
    print()
    
    export_to_csv(args.input, args.output, args.format)
    
    print("=" * 70)
    print("[OK] EXPORT COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print(f"1. This CSV serves as the baseline for retrieval test")
    print(f"2. Retrieved chunks column: shows chunks from confidence analysis")
    print("3. Generated chunks column: will be filled by retrieval test")
    print("4. Precision/Recall/F1: will be calculated by retrieval test")
    print(f"5. Use this file: {args.output}")
    print()


if __name__ == "__main__":
    main()
