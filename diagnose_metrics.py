"""
Diagnose: Why are metrics 0?
============================
Compare the ground truth chunks (retrieved_chunks) vs what the API returned (generated_chunks)
"""

import csv

print("\n" + "="*90)
print("🔍 DIAGNOSTIC: Why are all metrics 0?")
print("="*90)
print()

# Load results
rows = []
with open('evaluation/old_dataset_retrieval_test_template_run.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total queries: {len(rows)}")
print()

# Find queries where ground truth exists
with_ground_truth = []
without_ground_truth = []
matching_chunks = []
different_chunks = []

for row in rows:
    query_id = row.get('query_id', '')
    question = row.get('question', '')[:50]
    
    # Ground truth (what SHOULD be retrieved)
    ground_truth_str = row.get('retrieved_chunks', '')
    ground_truth = set([c.strip() for c in ground_truth_str.split(',') if c.strip()])
    
    # What API actually returned
    generated_str = row.get('generated_chunks', '')
    generated = set()
    if generated_str.startswith('['):
        try:
            import json
            generated = set(str(c) for c in json.loads(generated_str))
        except:
            generated = set([c.strip() for c in generated_str.split(',') if c.strip()])
    else:
        generated = set([c.strip() for c in generated_str.split(',') if c.strip()])
    
    if ground_truth:
        with_ground_truth.append((query_id, question, ground_truth, generated))
        
        if ground_truth == generated:
            matching_chunks.append((query_id, question, ground_truth))
        else:
            different_chunks.append((query_id, question, ground_truth, generated))
    else:
        without_ground_truth.append((query_id, question, generated))

print(f"Queries WITH ground truth: {len(with_ground_truth)}")
print(f"Queries WITHOUT ground truth (empty retrieved_chunks): {len(without_ground_truth)}")
print()

print(f"Matching (ground truth == API result): {len(matching_chunks)}")
print(f"Different (ground truth != API result): {len(different_chunks)}")
print()

if different_chunks:
    print("="*90)
    print("❌ MISMATCHES (Ground Truth vs API Result)")
    print("="*90)
    print()
    
    for i, (qid, question, truth, generated) in enumerate(different_chunks[:5], 1):
        print(f"{i}. {qid}: {question}")
        print(f"   Ground truth (should find): {truth}")
        print(f"   API returned:              {generated}")
        print()
    
    if len(different_chunks) > 5:
        print(f"... and {len(different_chunks)-5} more mismatches")
    print()

if matching_chunks:
    print("="*90)
    print("✅ MATCHES (Ground Truth == API Result)")
    print("="*90)
    print()
    
    for i, (qid, question, truth) in enumerate(matching_chunks[:5], 1):
        print(f"{i}. {qid}: {question}")
        print(f"   Both found: {truth}")
        print()
    
    if len(matching_chunks) > 5:
        print(f"... and {len(matching_chunks)-5} more matches")
    print()

print("="*90)
print("🎯 ROOT CAUSE ANALYSIS")
print("="*90)
print()

if len(different_chunks) > len(matching_chunks):
    print("❌ PRIMARY ISSUE: API is returning DIFFERENT chunks than ground truth")
    print()
    print("Possible causes:")
    print("1. Ground truth was collected with different vector embeddings")
    print("2. Ground truth was collected with different search parameters")
    print("3. Database/chunks changed between ground truth collection and test run")
    print("4. Vector similarity calculations changed")
    print()
else:
    print("✅ Most chunks match correctly")
    print()
    print("The 0 metrics are likely due to the measurement logic, not system failure")

print()
