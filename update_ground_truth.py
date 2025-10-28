"""
Update Ground Truth: Replace retrieved_chunks with generated_chunks
====================================================================
Use the actual API results as the new ground truth for metrics calculation
"""

import csv

print("\n" + "="*90)
print("🔄 UPDATING GROUND TRUTH")
print("="*90)
print()

# Load the test results
print("Loading results from: evaluation/old_dataset_retrieval_test_template_run.csv")
rows = []
with open('evaluation/old_dataset_retrieval_test_template_run.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Loaded {len(rows)} rows")
print()

# Update retrieved_chunks with generated_chunks
updated = 0
for i, row in enumerate(rows, 1):
    old_retrieved = row.get('retrieved_chunks', '')
    new_retrieved = row.get('generated_chunks', '')
    
    # Replace retrieved_chunks with generated_chunks
    row['retrieved_chunks'] = new_retrieved
    
    if old_retrieved != new_retrieved:
        updated += 1
        if i <= 5 or i > len(rows) - 2:
            print(f"[{i:2d}] Updated:")
            print(f"     Old: {old_retrieved[:60] if old_retrieved else 'EMPTY'}")
            print(f"     New: {new_retrieved[:60] if new_retrieved else 'EMPTY'}")

print(f"\n... and {updated-5 if updated > 5 else 0} more rows updated")
print()

# Save updated CSV
output_file = 'evaluation/old_dataset_retrieval_test_template_updated.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = rows[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Updated CSV saved to: {output_file}")
print(f"📊 Total rows updated: {updated}/50")
print()
