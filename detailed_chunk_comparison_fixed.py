"""
Detailed Comparison: Chunk Test vs Retrieval Test (FIXED)
==========================================================
Compare chunk IDs found by each method for the same queries.
Use correct columns: chunk_test uses 'retrieved_chunks', retrieval_test uses 'chunk1_id' through 'chunk5_id'
"""

import csv
import json

print("\n" + "="*90)
print(" DETAILED CHUNK COMPARISON: Direct Supabase RPC vs RAG API Retrieval")
print("="*90)
print()

# Load both CSVs
chunk_rows = []
retrieval_rows = []

print("[DIR] Loading chunk test CSV...")
with open('evaluation/chunk_test_old_dataset_metrics.csv', 'r', encoding='utf-8') as f:
    chunk_rows = list(csv.DictReader(f))
print(f"[OK] Loaded {len(chunk_rows)} chunk test results")
print()

print("[DIR] Loading retrieval test CSV...")
with open('evaluation/old_dataset_retrieval_test_template.csv', 'r', encoding='utf-8') as f:
    retrieval_rows = list(csv.DictReader(f))
print(f"[OK] Loaded {len(retrieval_rows)} retrieval test results")
print()

# Align by row position (same questions, different ID formats)
if len(chunk_rows) != len(retrieval_rows):
    print(f"[WARN]  WARNING: Different number of rows ({len(chunk_rows)} vs {len(retrieval_rows)})")
    total_rows = min(len(chunk_rows), len(retrieval_rows))
else:
    total_rows = len(chunk_rows)

# Compare
print("="*90)
print("[STATS] COMPARISON ANALYSIS (by row position)")
print("="*90)
print()

# Categories
same_chunks = []
different_chunks = []
chunk_only = []
retrieval_only = []
both_empty = []

for i in range(total_rows):
    chunk_row = chunk_rows[i]
    ret_row = retrieval_rows[i]
    
    # Parse chunk IDs from chunk test
    chunk_str = chunk_row.get('retrieved_chunks', '')
    chunk_ids = [c.strip() for c in chunk_str.split(',') if c.strip()] if chunk_str else []
    
    # Parse chunk IDs from retrieval test (use chunk1_id through chunk5_id columns)
    ret_ids = []
    for j in range(1, 6):
        col_name = f'chunk{j}_id'
        chunk_id = ret_row.get(col_name, '').strip()
        if chunk_id and chunk_id != 'chunk_1':  # Ignore placeholder
            ret_ids.append(chunk_id)
    
    chunk_set = set(chunk_ids)
    ret_set = set(ret_ids)
    
    qid_chunk = chunk_row['query_id']
    qid_ret = ret_row['query_id']
    question = chunk_row['question'][:60]
    search_method = ret_row.get('search_method', 'unknown')
    
    if len(chunk_set) == 0 and len(ret_set) == 0:
        both_empty.append((qid_chunk, qid_ret, question))
    elif len(chunk_set) > 0 and len(ret_set) == 0:
        chunk_only.append((qid_chunk, qid_ret, question, chunk_ids))
    elif len(chunk_set) == 0 and len(ret_set) > 0:
        retrieval_only.append((qid_chunk, qid_ret, question, ret_ids, search_method))
    elif chunk_set == ret_set:
        same_chunks.append((qid_chunk, qid_ret, question, chunk_ids))
    else:
        different_chunks.append((qid_chunk, qid_ret, question, chunk_ids, ret_ids))

print(f"[OK] SAME CHUNKS (both methods found identical chunks):")
print(f"   {len(same_chunks)}/{total_rows} queries ({len(same_chunks)/total_rows*100:.1f}%)")
if same_chunks:
    for qid_chunk, qid_ret, question, chunks in same_chunks[:5]:
        print(f"      {qid_chunk}/{qid_ret}: {', '.join(chunks)}")
    if len(same_chunks) > 5:
        print(f"      ... and {len(same_chunks)-5} more")
print()

print(f"[FAIL] DIFFERENT CHUNKS (both found chunks but different ones):")
print(f"   {len(different_chunks)}/{total_rows} queries ({len(different_chunks)/total_rows*100:.1f}%)")
if different_chunks:
    for qid_chunk, qid_ret, question, chunk_ids, ret_ids in different_chunks[:3]:
        print(f"      {qid_chunk}/{qid_ret}:")
        print(f"         Chunk Test: {', '.join(chunk_ids)}")
        print(f"         Retrieval:  {', '.join(ret_ids)}")
    if len(different_chunks) > 3:
        print(f"      ... and {len(different_chunks)-3} more")
print()

print(f"[SEARCH] CHUNK TEST ONLY (only chunk test found chunks):")
print(f"   {len(chunk_only)}/{total_rows} queries ({len(chunk_only)/total_rows*100:.1f}%)")
if chunk_only:
    for qid_chunk, qid_ret, question, chunks in chunk_only[:5]:
        print(f"      {qid_chunk}/{qid_ret}: {', '.join(chunks)}")
    if len(chunk_only) > 5:
        print(f"      ... and {len(chunk_only)-5} more")
print()

print(f" RETRIEVAL ONLY (only retrieval test found chunks via search):")
print(f"   {len(retrieval_only)}/{total_rows} queries ({len(retrieval_only)/total_rows*100:.1f}%)")
if retrieval_only:
    for qid_chunk, qid_ret, question, ret_ids, search_method in retrieval_only[:5]:
        print(f"      {qid_chunk}/{qid_ret} [{search_method}]: {', '.join(ret_ids[:3])}")
    if len(retrieval_only) > 5:
        print(f"      ... and {len(retrieval_only)-5} more")
print()

print(f" BOTH EMPTY (neither method found chunks):")
print(f"   {len(both_empty)}/{total_rows} queries ({len(both_empty)/total_rows*100:.1f}%)")
if both_empty:
    for qid_chunk, qid_ret, question in both_empty[:3]:
        print(f"      {qid_chunk}/{qid_ret}")
print()

# Summary statistics
print("="*90)
print("[METRIC] SUMMARY STATISTICS")
print("="*90)
print()

chunk_total = sum(len([c for c in chunk_row.get('retrieved_chunks', '').split(',') if c.strip()]) 
                  for chunk_row in chunk_rows)
chunk_with = sum(1 for chunk_row in chunk_rows 
                 if chunk_row.get('retrieved_chunks', '').strip())

ret_total = 0
ret_with = 0
for ret_row in retrieval_rows:
    ret_ids = []
    for j in range(1, 6):
        col_name = f'chunk{j}_id'
        chunk_id = ret_row.get(col_name, '').strip()
        if chunk_id and chunk_id != 'chunk_1':
            ret_ids.append(chunk_id)
    if ret_ids:
        ret_with += 1
        ret_total += len(ret_ids)

print(f"Chunk Test Results (Direct Supabase RPC):")
print(f"  Queries with chunks: {chunk_with}/{total_rows} ({chunk_with/total_rows*100:.1f}%)")
print(f"  Total chunks found: {chunk_total}")
print(f"  Average chunks/query: {chunk_total/chunk_with:.1f}" if chunk_with > 0 else "  N/A")
print()

print(f"Retrieval Test Results (RAG API):")
print(f"  Queries with chunks: {ret_with}/{total_rows} ({ret_with/total_rows*100:.1f}%)")
print(f"  Total chunks found: {ret_total}")
print(f"  Average chunks/query: {ret_total/ret_with:.1f}" if ret_with > 0 else "  N/A")
print()

# Timing comparison
chunk_times = [float(chunk_row['query_time_seconds']) for chunk_row in chunk_rows 
               if chunk_row.get('query_time_seconds')]
ret_times = [float(ret_row['retrieval_time_seconds']) for ret_row in retrieval_rows 
             if ret_row.get('retrieval_time_seconds')]

avg_chunk_time = sum(chunk_times) / len(chunk_times) if chunk_times else 0
avg_ret_time = sum(ret_times) / len(ret_times) if ret_times else 0

print(f"Speed Comparison:")
print(f"  Chunk Test avg: {avg_chunk_time:.2f}s")
print(f"  Retrieval Test avg: {avg_ret_time:.2f}s")
if avg_chunk_time > 0:
    print(f"  Retrieval is {avg_ret_time/avg_chunk_time:.1f}x slower")
print()

print("="*90)
print("[TARGET] KEY FINDINGS")
print("="*90)
print()
print(f"1. SYSTEM ALIGNMENT:")
print(f"   [OK] Same chunks found: {len(same_chunks)} queries ({len(same_chunks)/total_rows*100:.1f}%)")
print(f"   [WARN]  Different chunks: {len(different_chunks)} queries ({len(different_chunks)/total_rows*100:.1f}%)")
print()
print(f"2. COVERAGE DIFFERENCE:")
print(f"   - Chunk test ONLY: {len(chunk_only)} queries (direct vector search)")
print(f"   - Retrieval ONLY: {len(retrieval_only)} queries (possibly API fallback)")
print(f"   - Both empty: {len(both_empty)} queries (no match in either)")
print()
print(f"3. DATA QUALITY:")
if len(same_chunks) > 20:
    print(f"   [OK] HIGH ALIGNMENT - Both systems find same chunks when local search works")
    print(f"   [OK] Systems are consistent and compatible")
elif len(different_chunks) > len(same_chunks):
    print(f"   [WARN]  POTENTIAL ISSUE - Different chunks retrieved in {len(different_chunks)} cases")
    print(f"      Check: vector similarity calculations, embedding consistency")
else:
    print(f"   [OK] ACCEPTABLE - Most aligned queries match")
print()
print(f"4. RECOMMENDATION:")
if len(same_chunks) / total_rows > 0.4:
    print(f"   [OK] Systems are compatible - chunk test and retrieval test use consistent data")
elif len(different_chunks) / total_rows > 0.4:
    print(f"   [SEARCH] INVESTIGATE - High rate of different chunks across systems")
else:
    print(f"   [OK] No significant issues - proceed with confidence")
print()

print("="*90)
