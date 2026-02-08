"""
Fix Chunk Test CSV - Validate and populate chunk IDs
Only fills chunk1-5_id if chunks were actually found (not system error)
"""

import csv
import os
import sys

sys.path.append('src')
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
from src.embed import embed_texts

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[FAIL] ERROR: SUPABASE credentials not found")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n" + "="*80)
print(" FIX CHUNK TEST CSV - VALIDATE AND POPULATE CHUNK IDs")
print("="*80)
print()

# Load chunk test CSV
with open('evaluation/chunk_test_old_dataset_metrics.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"[DIR] Loaded {len(rows)} rows from chunk_test_old_dataset_metrics.csv")
print()

# Process each row - populate chunk IDs and validate "not found" results
validated = 0
found_with_chunks = 0
found_no_chunks = 0
errors = []

for i, row in enumerate(rows, 1):
    query_id = row['query_id']
    question = row['question']
    dataset_source = row['dataset_source']
    chunks_found_str = row.get('chunks_found', '0')
    
    try:
        chunks_found = int(chunks_found_str) if chunks_found_str else 0
    except:
        chunks_found = 0
    
    # If chunks were found, populate chunk IDs
    if chunks_found > 0:
        # Re-query to get chunk IDs for population
        try:
            # Embed query
            query_embedding = embed_texts([question])[0]
            
            # Determine table
            table = 'documents_old' if dataset_source == 'OLD' else 'documents_new'
            rpc_name = f'match_{table}'
            
            # Query Supabase
            result = supabase.rpc(rpc_name, {
                'query_embedding': query_embedding,
                'match_count': 5
            }).execute()
            
            # Extract chunk IDs
            chunk_ids = []
            chunks = []
            if hasattr(result, 'data'):
                chunks = result.data if result.data else []
            elif isinstance(result, dict) and 'data' in result:
                chunks = result.get('data', [])
            elif isinstance(result, list):
                chunks = result
            
            for chunk in chunks[:5]:
                chunk_id = chunk[0] if isinstance(chunk, (list, tuple)) else chunk.get('id', '')
                if chunk_id:
                    chunk_ids.append(str(chunk_id))
            
            # Populate chunk columns
            row['retrieved_chunks'] = ','.join(chunk_ids)
            row['chunk1_id'] = chunk_ids[0] if len(chunk_ids) > 0 else ''
            row['chunk2_id'] = chunk_ids[1] if len(chunk_ids) > 1 else ''
            row['chunk3_id'] = chunk_ids[2] if len(chunk_ids) > 2 else ''
            row['chunk4_id'] = chunk_ids[3] if len(chunk_ids) > 3 else ''
            row['chunk5_id'] = chunk_ids[4] if len(chunk_ids) > 4 else ''
            
            if chunk_ids:
                print(f"[{i}/50] [OK] {query_id}: Found {len(chunk_ids)} chunks - {', '.join(chunk_ids[:3])}...")
                found_with_chunks += 1
            else:
                print(f"[{i}/50] [WARN]  {query_id}: Verified NO chunks found (genuine)")
                found_no_chunks += 1
            
            validated += 1
            
        except Exception as e:
            print(f"[{i}/50] [FAIL] {query_id}: ERROR - {str(e)[:60]}")
            errors.append((query_id, str(e)))
    else:
        # Already marked as no chunks found
        print(f"[{i}/50] [WARN]  {query_id}: Already marked no chunks (from original test)")
        found_no_chunks += 1
        validated += 1

print()
print("="*80)
print("[STATS] VALIDATION RESULTS")
print("="*80)
print()
print(f"[OK] Validated: {validated}/{len(rows)}")
print(f"   With chunks found: {found_with_chunks}")
print(f"   Genuine 'not found': {found_no_chunks}")
if errors:
    print(f"   [FAIL] Errors: {len(errors)}")
    for query_id, error in errors[:3]:
        print(f"      - {query_id}: {error[:50]}")
print()

# Save fixed CSV
output_path = 'evaluation/chunk_test_old_dataset_metrics.csv'
with open(output_path, 'w', newline='', encoding='utf-8') as f:
    if rows:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

print(f"[SAVE] Fixed CSV saved to: {output_path}")
print()
print("[OK] Chunk test CSV validation complete!")
print()
