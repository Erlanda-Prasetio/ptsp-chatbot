"""
Compare Retrieval vs Generated Chunks
======================================
Check if the chunks retrieved by the API match what was generated before.
"""

import csv

print("\n" + "="*90)
print("🔍 COMPARING RETRIEVAL vs GENERATED CHUNKS")
print("="*90)
print()

# Load the new results
print("Loading retrieval test results...")
new_rows = []
with open('evaluation/old_dataset_retrieval_test_template_run.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    new_rows = list(reader)

print(f"Loaded {len(new_rows)} results")
print()

# Analyze
matching = 0
different = 0
details = []

for i, row in enumerate(new_rows):
    query_id = row.get('query_id', '')
    question = row.get('question', '')[:60]
    
    # Get retrieved chunk IDs
    retrieved_str = row.get('retrieved_chunks', '')
    retrieved = set([c.strip() for c in retrieved_str.split(',') if c.strip()])
    
    # Get generated chunk IDs (these are in chunk1_id through chunk5_id)
    generated = set()
    for j in range(1, 6):
        col_name = f'chunk{j}_id'
        chunk_id = row.get(col_name, '').strip()
        if chunk_id and chunk_id != 'chunk_1':
            generated.add(chunk_id)
    
    # Compare
    if retrieved == generated:
        matching += 1
        status = "✅ MATCH"
    else:
        different += 1
        status = "❌ DIFFERENT"
        details.append({
            'query_id': query_id,
            'question': question,
            'retrieved': retrieved,
            'generated': generated
        })
    
    print(f"[{i+1:2d}] {query_id}: {status}")
    if retrieved != generated:
        print(f"     Retrieved: {retrieved if retrieved else 'NONE'}")
        print(f"     Generated: {generated if generated else 'NONE'}")

print()
print("="*90)
print("📊 SUMMARY")
print("="*90)
print()
print(f"✅ Matching:   {matching}/50 ({matching/50*100:.1f}%)")
print(f"❌ Different:  {different}/50 ({different/50*100:.1f}%)")
print()

if different > 0:
    print("❌ CHUNK MISMATCH DETAILS:")
    print()
    for i, detail in enumerate(details[:10], 1):
        print(f"{i}. {detail['query_id']}:")
        print(f"   Retrieval:  {detail['retrieved'] if detail['retrieved'] else 'NONE'}")
        print(f"   Generated:  {detail['generated'] if detail['generated'] else 'NONE'}")
    
    if len(details) > 10:
        print(f"   ... and {len(details)-10} more mismatches")
    print()
    print("⚠️  CONCLUSION: Chunks are NOT matching between retrieval and generated")
else:
    print("✅ CONCLUSION: All chunks match perfectly between retrieval and generated!")

print()
print("="*90)
