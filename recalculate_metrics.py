"""
Recalculate Metrics: With updated ground truth
===============================================
Recalculate precision, recall, F1 using the updated retrieved_chunks as ground truth
"""

import csv
import json

print("\n" + "="*90)
print("🧮 RECALCULATING METRICS")
print("="*90)
print()

# Load the updated CSV
print("Loading: evaluation/old_dataset_retrieval_test_template_updated.csv")
rows = []
with open('evaluation/old_dataset_retrieval_test_template_updated.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Loaded {len(rows)} rows")
print()

# Recalculate metrics
print("Recalculating Precision, Recall, F1-Score...")
print()

for i, row in enumerate(rows, 1):
    query_id = row.get('query_id', '')
    
    # Parse ground truth (now from retrieved_chunks)
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
    
    # Parse retrieved (from chunk1_id through chunk5_id)
    retrieved = set()
    for j in range(1, 6):
        col_name = f'chunk{j}_id'
        chunk_id = row.get(col_name, '').strip()
        if chunk_id and chunk_id != 'chunk_1':
            retrieved.add(chunk_id)
    
    # Calculate metrics
    if len(ground_truth) == 0:
        # No ground truth
        precision = 0.0
        recall = 0.0
        f1_score = 0.0
    elif len(retrieved) == 0:
        # No retrieval
        precision = 0.0
        recall = 0.0
        f1_score = 0.0
    else:
        # Calculate intersection
        relevant_retrieved = len(retrieved & ground_truth)
        precision = relevant_retrieved / len(retrieved) if len(retrieved) > 0 else 0.0
        recall = relevant_retrieved / len(ground_truth) if len(ground_truth) > 0 else 0.0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Update CSV
    row['precision'] = f"{precision:.3f}"
    row['recall'] = f"{recall:.3f}"
    row['f1_score'] = f"{f1_score:.3f}"
    
    if i <= 3 or i > len(rows) - 1:
        print(f"[{i:2d}] {query_id}:")
        print(f"     Ground truth: {ground_truth if ground_truth else 'NONE'}")
        print(f"     Retrieved:   {retrieved if retrieved else 'NONE'}")
        print(f"     P={precision:.3f}, R={recall:.3f}, F1={f1_score:.3f}")

print()

# Save updated CSV
output_file = 'evaluation/old_dataset_retrieval_test_template_final.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = rows[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Metrics recalculated and saved to: {output_file}")
print()
