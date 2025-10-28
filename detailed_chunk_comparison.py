"""
Detailed Comparison: Chunk Test vs Retrieval Test
=================================================
Compare chunk IDs found by each method for the same queries.
Identify if differences are due to different retrieval systems or different chunks.
Align by row position (same question, different ID format).
"""

import csv
import json

print("\n" + "="*90)
print("🔬 DETAILED CHUNK COMPARISON: Direct Supabase RPC vs RAG API Retrieval")
print("="*90)
print()

# Load both CSVs
chunk_rows = []
retrieval_rows = []

print("📂 Loading chunk test CSV...")
with open('evaluation/chunk_test_old_dataset_metrics.csv', 'r', encoding='utf-8') as f:
    chunk_rows = list(csv.DictReader(f))
print(f"✅ Loaded {len(chunk_rows)} chunk test results")
print()

print("📂 Loading retrieval test CSV...")
with open('evaluation/old_dataset_retrieval_test_template.csv', 'r', encoding='utf-8') as f:
    retrieval_rows = list(csv.DictReader(f))
print(f"✅ Loaded {len(retrieval_rows)} retrieval test results")
print()

# Align by row position (same questions, different ID formats)
if len(chunk_rows) != len(retrieval_rows):
    print(f"⚠️  WARNING: Different number of rows ({len(chunk_rows)} vs {len(retrieval_rows)})")
    total_rows = min(len(chunk_rows), len(retrieval_rows))
else:
    total_rows = len(chunk_rows)

# Compare
print("="*90)
print("📊 COMPARISON ANALYSIS (by row position)")
print("="*90)
print()

# Categories
same_chunks = []  # Found same chunks in both
different_chunks = []  # Found chunks but different ones
chunk_only = []  # Only chunk test found chunks
retrieval_only = []  # Only retrieval test found chunks
both_empty = []  # Neither found chunks

for i in range(total_rows):
    chunk_row = chunk_rows[i]
    ret_row = retrieval_rows[i]
    
    # Parse chunk IDs
    chunk_str = chunk_row.get('retrieved_chunks', '')
    chunk_ids = [c.strip() for c in chunk_str.split(',') if c.strip()] if chunk_str else []
    
    # Parse retrieval chunks
    ret_str = ret_row.get('generated_chunks', '')
    ret_ids = []
    if ret_str and ret_str.strip():
        try:
            if ret_str.startswith('['):
                ret_ids = json.loads(ret_str)
            else:
                ret_ids = [c.strip() for c in ret_str.split(',') if c.strip()]
        except:
            ret_ids = []
    
    chunk_set = set(chunk_ids)
    ret_set = set(ret_ids)
    
    qid_chunk = chunk_row['query_id']
    qid_ret = ret_row['query_id']
    question = chunk_row['question'][:60]
    
    if len(chunk_set) == 0 and len(ret_set) == 0:
        both_empty.append((qid_chunk, qid_ret, question))
    elif len(chunk_set) > 0 and len(ret_set) == 0:
        chunk_only.append((qid_chunk, qid_ret, question, chunk_ids))
    elif len(chunk_set) == 0 and len(ret_set) > 0:
        retrieval_only.append((qid_chunk, qid_ret, question, ret_ids))
    elif chunk_set == ret_set:
        same_chunks.append((qid_chunk, qid_ret, question, chunk_ids))
    else:
        different_chunks.append((qid_chunk, qid_ret, question, chunk_ids, ret_ids))

print(f"✅ SAME CHUNKS (both methods found identical chunks):")
print(f"   {len(same_chunks)}/{total_rows} queries ({len(same_chunks)/total_rows*100:.1f}%)")
if same_chunks:
    for qid_chunk, qid_ret, question, chunks in same_chunks[:5]:
        print(f"      {qid_chunk}/{qid_ret}: {', '.join(chunks)}")
    if len(same_chunks) > 5:
        print(f"      ... and {len(same_chunks)-5} more")
print()

print(f"❌ DIFFERENT CHUNKS (both found chunks but different ones):")
print(f"   {len(different_chunks)}/{total_rows} queries ({len(different_chunks)/total_rows*100:.1f}%)")
if different_chunks:
    for qid_chunk, qid_ret, question, chunk_ids, ret_ids in different_chunks[:3]:
        print(f"      {qid_chunk}/{qid_ret}:")
        print(f"         Chunk Test: {', '.join(chunk_ids)}")
        print(f"         Retrieval:  {', '.join(ret_ids[:5])}")
    if len(different_chunks) > 3:
        print(f"      ... and {len(different_chunks)-3} more")
print()

print(f"🔍 CHUNK TEST ONLY (only chunk test found chunks):")
print(f"   {len(chunk_only)}/{total_rows} queries ({len(chunk_only)/total_rows*100:.1f}%)")
if chunk_only:
    for qid_chunk, qid_ret, question, chunks in chunk_only[:5]:
        print(f"      {qid_chunk}/{qid_ret}: {', '.join(chunks)}")
    if len(chunk_only) > 5:
        print(f"      ... and {len(chunk_only)-5} more")
print()

print(f"🌐 RETRIEVAL ONLY (only retrieval test found chunks via fallback):")
print(f"   {len(retrieval_only)}/{total_rows} queries ({len(retrieval_only)/total_rows*100:.1f}%)")
if retrieval_only:
    for qid_chunk, qid_ret, question, ret_ids in retrieval_only[:5]:
        ret_row_data = retrieval_rows[retrieval_rows.index(next(r for r in retrieval_rows if r['query_id'] == qid_ret))]
        search_method = ret_row_data.get('search_method', 'unknown')
        print(f"      {qid_chunk}/{qid_ret} [{search_method}]: {', '.join(ret_ids[:3])}...")
    if len(retrieval_only) > 5:
        print(f"      ... and {len(retrieval_only)-5} more")
print()

print(f"⚪ BOTH EMPTY (neither method found chunks):")
print(f"   {len(both_empty)}/{total_rows} queries ({len(both_empty)/total_rows*100:.1f}%)")
print()

# Summary statistics
print("="*90)
print("📈 SUMMARY STATISTICS")
print("="*90)
print()

chunk_total = sum(len(r.get('retrieved_chunks', '').split(',')) for r in chunk_rows)
chunk_with = sum(1 for r in chunk_rows if r.get('retrieved_chunks', '').strip())

ret_total = 0
ret_with = 0
for r in retrieval_rows:
    ret_str = r.get('generated_chunks', '')
    if ret_str and ret_str.strip():
        ret_with += 1
        try:
            if ret_str.startswith('['):
                ret_total += len(json.loads(ret_str))
            else:
                ret_total += len([c for c in ret_str.split(',') if c.strip()])
        except:
            pass

print(f"Chunk Test Results (Direct Supabase RPC):")
print(f"  Queries with chunks: {chunk_with}/50 ({chunk_with/50*100:.1f}%)")
print(f"  Total chunks found: {chunk_total}")
print(f"  Average chunks/query: {chunk_total/chunk_with:.1f}" if chunk_with > 0 else "  N/A")
print()

print(f"Retrieval Test Results (RAG API + Fallback):")
print(f"  Queries with chunks: {ret_with}/50 ({ret_with/50*100:.1f}%)")
print(f"  Total chunks found: {ret_total}")
print(f"  Average chunks/query: {ret_total/ret_with:.1f}" if ret_with > 0 else "  N/A")
print()

# Timing comparison
chunk_times = [float(r['query_time_seconds']) for r in chunk_rows if r.get('query_time_seconds')]
ret_times = [float(r['retrieval_time_seconds']) for r in retrieval_rows if r.get('retrieval_time_seconds')]

avg_chunk_time = sum(chunk_times) / len(chunk_times) if chunk_times else 0
avg_ret_time = sum(ret_times) / len(ret_times) if ret_times else 0

print(f"Speed Comparison:")
print(f"  Chunk Test avg: {avg_chunk_time:.2f}s")
print(f"  Retrieval Test avg: {avg_ret_time:.2f}s")
print(f"  Retrieval is {avg_ret_time/avg_chunk_time:.1f}x slower")
print()

print("="*90)
print("🎯 KEY FINDINGS")
print("="*90)
print()
print(f"1. SYSTEM ALIGNMENT:")
print(f"   ✅ Same chunks found: {len(same_chunks)} queries ({len(same_chunks)/total_rows*100:.1f}%)")
print(f"   ⚠️  Different chunks: {len(different_chunks)} queries ({len(different_chunks)/total_rows*100:.1f}%)")
print()
print(f"2. COVERAGE DIFFERENCE:")
print(f"   - Chunk test ONLY: {len(chunk_only)} queries (direct vector search)")
print(f"   - Retrieval ONLY: {len(retrieval_only)} queries (internet fallback)")
print(f"   - Both empty: {len(both_empty)} queries")
print()
print(f"3. DATA QUALITY:")
if len(same_chunks) > 20:
    print(f"   ✅ HIGH ALIGNMENT - Both systems find same chunks when local search works")
    print(f"   ✅ Internet fallback adds coverage without breaking consistency")
elif len(different_chunks) > len(same_chunks):
    print(f"   ⚠️  POTENTIAL ISSUE - Different chunks retrieved in {len(different_chunks)} cases")
    print(f"      Check: vector similarity calculations, embedding consistency")
else:
    print(f"   ✅ ACCEPTABLE - Most aligned queries match, differences in new results")
print()
print(f"4. RECOMMENDATION:")
if len(same_chunks) / total_rows > 0.4:
    print(f"   ✅ Systems are compatible - differences due to internet fallback coverage")
else:
    print(f"   🔍 INVESTIGATE - More than 40% queries show different chunks")
print()

print("="*90)
