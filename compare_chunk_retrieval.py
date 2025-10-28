import csv
from collections import defaultdict

# Load both CSV files
def load_csv(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

retrieval = load_csv('evaluation/old_dataset_retrieval_test_template.csv')
chunk = load_csv('evaluation/chunk_test_old_dataset_metrics.csv')

print("\n" + "="*80)
print("🔍 CHUNK TEST vs RETRIEVAL TEST COMPARISON")
print("="*80)
print()

# Basic stats
print(f"📊 BASIC STATISTICS:")
print(f"  Queries Analyzed: {len(retrieval)}")
print()

print(f"⏱️  TIMING COMPARISON:")
ret_times = [float(r['retrieval_time_seconds']) for r in retrieval if r['retrieval_time_seconds']]
chunk_times = [float(c['query_time_seconds']) for c in chunk if c['query_time_seconds']]

print(f"  Retrieval Test (using RAG API):")
print(f"    Average: {sum(ret_times)/len(ret_times):.2f}s")
print(f"    Min: {min(ret_times):.2f}s, Max: {max(ret_times):.2f}s")
print(f"    Total: {sum(ret_times):.1f}s ({sum(ret_times)/60:.1f} min)")
print()
print(f"  Chunk Test (direct Supabase RPC):")
print(f"    Average: {sum(chunk_times)/len(chunk_times):.2f}s")
print(f"    Min: {min(chunk_times):.2f}s, Max: {max(chunk_times):.2f}s")
print(f"    Total: {sum(chunk_times):.1f}s ({sum(chunk_times)/60:.1f} min)")
print()
print(f"  ⚡ Retrieval test is {sum(ret_times)/sum(chunk_times):.1f}x SLOWER than chunk test")
print()

# Search method distribution
print(f"🔎 SEARCH METHOD DISTRIBUTION:")
ret_methods = defaultdict(int)
for r in retrieval:
    method = r['search_method'] if r['search_method'].strip() else 'unknown'
    ret_methods[method] += 1

print(f"  Retrieval Test Methods:")
for method, count in sorted(ret_methods.items(), key=lambda x: x[1], reverse=True):
    pct = count / len(retrieval) * 100
    print(f"    {method:20s}: {count:2d} ({pct:5.1f}%)")
print()

chunk_methods = defaultdict(int)
for c in chunk:
    method = c['search_method'] if c['search_method'].strip() else 'unknown'
    chunk_methods[method] += 1

print(f"  Chunk Test Methods:")
for method, count in sorted(chunk_methods.items(), key=lambda x: x[1], reverse=True):
    pct = count / len(chunk) * 100
    print(f"    {method:20s}: {count:2d} ({pct:5.1f}%)")
print()

# Chunks found
ret_with_chunks = sum(1 for r in retrieval if r['generated_chunks'] and r['generated_chunks'].strip())
chunk_with_chunks = sum(1 for c in chunk if c['chunks_found'] and int(c['chunks_found']) > 0)

print(f"✅ CHUNKS FOUND:")
print(f"  Retrieval Test: {ret_with_chunks}/50 ({ret_with_chunks/50*100:.1f}%) queries found chunks")
print(f"  Chunk Test:     {chunk_with_chunks}/50 ({chunk_with_chunks/50*100:.1f}%) queries found chunks")
print()

# Success rate
ret_success = sum(1 for r in retrieval if r.get('status', '') != 'error')
chunk_success = sum(1 for c in chunk if c['status'] == 'success')

print(f"✨ SUCCESS RATE:")
print(f"  Retrieval Test: {ret_success}/{len(retrieval)} ({ret_success/len(retrieval)*100:.1f}%) successful")
print(f"  Chunk Test:     {chunk_success}/{len(chunk)} ({chunk_success/len(chunk)*100:.1f}%) successful")
print()

print(f"🎯 KEY INSIGHTS:")
print(f"  • Chunk test is much FASTER (direct Supabase vs API overhead)")
print(f"  • Retrieval test finds chunks in {ret_with_chunks}/50 queries via internet_fallback")
print(f"  • Chunk test finds chunks in {chunk_with_chunks}/50 queries via direct vector search")
print(f"  • {abs(ret_with_chunks - chunk_with_chunks)} queries differ between methods")
print()

print("="*80)
