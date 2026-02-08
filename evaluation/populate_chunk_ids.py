"""
Populate Chunk IDs - Get actual chunks from RAG system
=====================================================

For each question in the CSV, query the RAG system to get the top 5
chunk IDs that it actually retrieves, and save them to the CSV.

Usage:
    python evaluation/populate_chunk_ids.py --csv evaluation/retrieval_test_25queries.csv
"""

import os
import sys
import csv
import json
import argparse
import requests
from pathlib import Path

# Configuration
API_URL = "http://localhost:8001"
TIMEOUT = 30

def query_rag_system(question: str, api_url: str = API_URL) -> dict:
    """
    Query the RAG system to get chunks for a question
    """
    try:
        payload = {
            "messages": [{"role": "user", "content": question}],
            "retrieve_only": True
        }
        
        response = requests.post(
            f"{api_url}/retrieve",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[FAIL] Error querying RAG: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Populate chunk IDs from RAG system")
    parser.add_argument("--csv", type=str, required=True, help="Path to CSV file")
    args = parser.parse_args()
    
    csv_file = args.csv
    
    if not os.path.exists(csv_file):
        print(f"[FAIL] CSV file not found: {csv_file}")
        sys.exit(1)
    
    # Check API health
    print(f"[CONNECT] Testing connection to {API_URL}...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] API is healthy")
        else:
            print(f"[WARN]  API returned status {response.status_code}")
    except Exception as e:
        print(f"[FAIL] API connection failed: {e}")
        sys.exit(1)
    
    # Read CSV
    print(f"[DIR] Loading CSV from: {csv_file}")
    rows = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        print(f"[OK] Loaded {len(rows)} queries")
    except Exception as e:
        print(f"[FAIL] Error reading CSV: {e}")
        sys.exit(1)
    
    # Query each question
    print("\n" + "="*80)
    print("[SEARCH] QUERYING RAG SYSTEM FOR CHUNKS")
    print("="*80 + "\n")
    
    updated_rows = []
    for idx, row in enumerate(rows, 1):
        query_id = row.get("query_id", f"Q{idx:03d}")
        question = row.get("question", "")
        
        if not question:
            print(f"[{idx}/{len(rows)}] {query_id}: [WARN]  No question text")
            updated_rows.append(row)
            continue
        
        print(f"[{idx}/{len(rows)}] {query_id}: {question[:60]}...")
        
        # Query RAG system
        result = query_rag_system(question)
        
        if result:
            # Parse sources from response
            sources = result.get('sources', [])
            chunk_ids = []
            
            for source in sources[:5]:
                if isinstance(source, dict):
                    # Try different possible ID field names
                    chunk_id = source.get('id') or source.get('chunk_id') or source.get('document_id')
                    if chunk_id:
                        chunk_ids.append(str(chunk_id))
                else:
                    chunk_ids.append(str(source))
            
            if chunk_ids:
                # Fill in the chunk IDs
                row["retrieved_chunks"] = ",".join(chunk_ids)
                for i, chunk_id in enumerate(chunk_ids, 1):
                    row[f"chunk{i}_id"] = chunk_id
                
                print(f"   [OK] Found {len(chunk_ids)} chunks: {','.join(chunk_ids)}")
            else:
                print(f"   [WARN]  No chunks found in response")
        else:
            print(f"   [WARN]  No response from RAG system")
        
        updated_rows.append(row)
    
    # Save updated CSV
    print("\n" + "="*80)
    print("[SAVE] SAVING RESULTS TO CSV")
    print("="*80 + "\n")
    
    try:
        # Get fieldnames from first row, preserving order
        fieldnames = list(rows[0].keys()) if rows else []
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        
        print(f"[OK] Results saved to: {csv_file}")
    except Exception as e:
        print(f"[FAIL] Error saving CSV: {e}")
        sys.exit(1)
    
    # Summary
    print("\n" + "="*80)
    print("[STATS] SUMMARY")
    print("="*80)
    print(f"Total Queries: {len(updated_rows)}")
    print(f"Queries with Chunks: {sum(1 for row in updated_rows if row.get('retrieved_chunks'))}")
    print(f"Queries without Chunks: {sum(1 for row in updated_rows if not row.get('retrieved_chunks'))}")
    print("="*80)

if __name__ == "__main__":
    main()
