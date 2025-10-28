"""
Final: Update CSV with recalculated metrics and save
====================================================
"""

import csv
import json

print("\n" + "="*90)
print("📝 FINAL UPDATE: Recalculate and update all metrics in CSV")
print("="*90)
print()

# Load CSV
rows = []
with open('evaluation/old_dataset_retrieval_test_template.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Loaded {len(rows)} rows")
print()

# Recalculate all metrics
perfect_match = 0
partial_match = 0
no_match = 0
fallback_queries = 0

for i, row in enumerate(rows):
    query_id = row.get('query_id', '')
    search_method = row.get('search_method', '')
    
    # Parse ground truth (retrieved_chunks)
    ground_truth_str = row.get('retrieved_chunks', '')
    ground_truth = set()
    if ground_truth_str and ground_truth_str.strip():
        if ground_truth_str.startswith('['):
            try:
                ground_truth = set(str(c) for c in json.loads(ground_truth_str))
            except:
                ground_truth = set([c.strip() for c in ground_truth_str.split(',') if c.strip()])
        else:
            ground_truth = set([c.strip() for c in ground_truth_str.split(',') if c.strip()])
    
    # Parse retrieved (chunk1_id - chunk5_id)
    retrieved = set()
    for j in range(1, 6):
        col_name = f'chunk{j}_id'
        chunk_id = row.get(col_name, '').strip()
        if chunk_id and chunk_id != 'chunk_1':
            retrieved.add(chunk_id)
    
    # Calculate metrics
    if len(ground_truth) == 0 or len(retrieved) == 0:
        precision = 0.0
        recall = 0.0
        f1_score = 0.0
        if len(retrieved) == 0:
            no_match += 1
    else:
        relevant_retrieved = len(retrieved & ground_truth)
        precision = relevant_retrieved / len(retrieved) if len(retrieved) > 0 else 0.0
        recall = relevant_retrieved / len(ground_truth) if len(ground_truth) > 0 else 0.0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        if f1_score == 1.0:
            perfect_match += 1
        elif f1_score > 0:
            partial_match += 1
        else:
            no_match += 1
    
    # Handle fallback
    if search_method == 'internet_fallback':
        fallback_queries += 1
        f1_score = 0.0  # Fallback doesn't match local chunks by definition
    
    # Update CSV
    row['precision'] = f"{precision:.3f}"
    row['recall'] = f"{recall:.3f}"
    row['f1_score'] = f"{f1_score:.3f}"

print(f"✅ Perfect matches: {perfect_match}")
print(f"✅ Partial matches: {partial_match}")
print(f"❌ No matches: {no_match}")
print(f"🌐 Internet fallback: {fallback_queries}")
print()

# Save
with open('evaluation/old_dataset_retrieval_test_template.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = rows[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Updated CSV saved")
print()
