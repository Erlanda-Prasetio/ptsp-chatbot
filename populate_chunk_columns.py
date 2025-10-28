"""
Fix: Populate chunk1_id through chunk5_id from generated_chunks
================================================================
"""

import csv
import json

print("\n" + "="*90)
print("🔧 POPULATING chunk1_id - chunk5_id columns")
print("="*90)
print()

# Load CSV
rows = []
with open('evaluation/old_dataset_retrieval_test_template_updated.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Loaded {len(rows)} rows")
print()

# Populate chunk columns
populated = 0
for i, row in enumerate(rows):
    generated_str = row.get('generated_chunks', '')
    chunks = []
    
    # Parse generated_chunks
    if generated_str and generated_str.strip():
        if generated_str.startswith('['):
            try:
                chunks = [str(c) for c in json.loads(generated_str)]
            except:
                chunks = [c.strip() for c in generated_str.split(',') if c.strip()]
        else:
            chunks = [c.strip() for c in generated_str.split(',') if c.strip()]
    
    # Clear existing chunk columns
    for j in range(1, 6):
        row[f'chunk{j}_id'] = ''
    
    # Populate from chunks
    for j, chunk_id in enumerate(chunks[:5], 1):
        row[f'chunk{j}_id'] = chunk_id
    
    if chunks:
        populated += 1
        if i < 3 or i >= len(rows) - 1:
            print(f"[{i+1:2d}] Populated {len(chunks)} chunks: {chunks[:3]}")

print(f"\n✅ Populated {populated} rows")
print()

# Save
output_file = 'evaluation/old_dataset_retrieval_test_template_updated.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = rows[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Saved to: {output_file}")
print()
