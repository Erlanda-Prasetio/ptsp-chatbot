"""
Populate chunk IDs in retrieval test CSV
=========================================
Extract chunk IDs from retrieved_chunks column and populate chunk1_id through chunk5_id
"""

import csv
import json

csv_path = 'evaluation/old_dataset_retrieval_test_template.csv'

print("Loading retrieval test CSV...")
rows = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Loaded {len(rows)} rows")
print()

# Check what needs to be populated
needs_population = 0
for i, row in enumerate(rows):
    # Check if chunk IDs already exist
    has_chunk_ids = False
    for j in range(1, 6):
        if row.get(f'chunk{j}_id', '').strip() and row.get(f'chunk{j}_id').strip() != 'chunk_1':
            has_chunk_ids = True
            break
    
    if not has_chunk_ids and row.get('retrieved_chunks', '').strip():
        needs_population += 1

print(f"Rows needing chunk ID population: {needs_population}/50")
print()

# Populate chunk IDs
populated = 0
for i, row in enumerate(rows):
    # Check if chunk IDs already exist
    has_chunk_ids = False
    for j in range(1, 6):
        if row.get(f'chunk{j}_id', '').strip() and row.get(f'chunk{j}_id').strip() != 'chunk_1':
            has_chunk_ids = True
            break
    
    # If no chunk IDs but retrieved_chunks exists, populate from it
    if not has_chunk_ids and row.get('retrieved_chunks', '').strip():
        chunks_str = row.get('retrieved_chunks', '')
        chunks = []
        
        # Parse chunks
        if chunks_str.startswith('['):
            try:
                chunks = json.loads(chunks_str)
            except:
                chunks = [c.strip() for c in chunks_str.split(',') if c.strip()]
        else:
            chunks = [c.strip() for c in chunks_str.split(',') if c.strip()]
        
        # Populate chunk ID columns
        for j, chunk_id in enumerate(chunks[:5], 1):
            row[f'chunk{j}_id'] = chunk_id
        
        populated += 1
        print(f"[{i+1:2d}] ✅ Populated {len(chunks)} chunks: {', '.join(chunks[:3])}")

print()
print(f"Populated {populated} rows")
print()

# Save updated CSV
with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    fieldnames = rows[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Saved updated CSV to {csv_path}")
print()
print("Now the retrieval test CSV has all chunk IDs populated and ready for use.")
