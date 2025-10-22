"""
Fix CSV formatting issue where entire rows are wrapped in quotes.
Pattern: "Q001,...,...,...,ground_truth_text,""chunk1, chunk2, chunk3"","
"""

import csv
import re

def fix_csv_format():
    input_file = 'evaluation/ground_truth_template.csv'
    output_file = 'evaluation/ground_truth_template_fixed.csv'
    backup_file = 'evaluation/ground_truth_template_backup.csv'
    
    # Backup original file
    import shutil
    shutil.copy(input_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    rows = []
    
    # Read the file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    # First line is header (correct format)
    header_line = lines[0].strip()
    print(f"Header: {header_line}")
    
    # Process each data line
    for i, line in enumerate(lines[1:], start=2):
        line = line.strip()
        if not line:
            continue
        
        # Pattern: "Q001,query text,OLD,Category,ground truth text,""chunk_ids"","
        # Remove outer quotes
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        elif line.startswith('"') and line.endswith(',"'):
            line = line[1:-2]
        
        # Now we have: Q001,query text,OLD,Category,ground truth text,""chunk_ids""
        # or: Q001,query text,OLD,Category,ground truth text,""chunk_ids"",...
        
        # Find the chunk_ids pattern: ""7294, 7168, 7241""
        # This is at the end or near end
        chunk_pattern = re.search(r',""([0-9, ]+)""', line)
        
        if not chunk_pattern:
            print(f"Warning line {i}: Could not find chunk pattern")
            print(f"  Line: {line[:100]}...")
            continue
        
        chunk_ids_str = chunk_pattern.group(1).strip()
        chunk_start_pos = chunk_pattern.start()
        
        # Everything before chunk_ids
        before_chunks = line[:chunk_start_pos]
        
        # Everything after chunk_ids (notes field)
        after_chunks = line[chunk_pattern.end():]
        if after_chunks.startswith(','):
            after_chunks = after_chunks[1:]
        notes = after_chunks.strip()
        
        # Now parse before_chunks: Q001,query,OLD,Category,ground_truth
        # Split by comma, but need to find OLD/NEW and Category
        parts = before_chunks.split(',')
        
        if len(parts) < 4:
            print(f"Warning line {i}: Not enough parts before chunks: {len(parts)}")
            continue
        
        eval_id = parts[0]
        
        # Find OLD or NEW
        dataset_idx = None
        for idx, part in enumerate(parts[1:], start=1):
            if part in ['OLD', 'NEW']:
                dataset_idx = idx
                break
        
        if dataset_idx is None:
            print(f"Warning line {i}: Could not find OLD/NEW")
            continue
        
        # Query is from parts[1] to parts[dataset_idx-1]
        query = ','.join(parts[1:dataset_idx])
        dataset_source = parts[dataset_idx]
        
        # Category is parts[dataset_idx+1]
        category = parts[dataset_idx + 1]
        
        # Ground truth is everything from parts[dataset_idx+2] onwards
        ground_truth = ','.join(parts[dataset_idx + 2:])
        
        rows.append({
            'eval_id': eval_id,
            'query': query,
            'dataset_source': dataset_source,
            'category': category,
            'ground_truth': ground_truth,
            'relevant_chunk_ids': chunk_ids_str,
            'notes': notes
        })
        
        if i <= 4:  # Debug first few
            print(f"\nLine {i}:")
            print(f"  eval_id: {eval_id}")
            print(f"  query: {query[:40]}...")
            print(f"  dataset: {dataset_source}")
            print(f"  category: {category}")
            print(f"  ground_truth: {ground_truth[:60]}...")
            print(f"  chunks: {chunk_ids_str}")
            print(f"  notes: {notes[:30] if notes else '(empty)'}")
    
    print(f"\n✅ Parsed {len(rows)} data rows")
    
    # Write properly formatted CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['eval_id', 'query', 'dataset_source', 'category', 'ground_truth', 'relevant_chunk_ids', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Fixed CSV written to: {output_file}")
    
    # Verify
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        verified_rows = list(reader)
    
    print(f"✅ Verified: {len(verified_rows)} rows in output file")
    
    # Show sample
    if verified_rows:
        print(f"\nSample row (Q001):")
        print(f"  eval_id: {verified_rows[0]['eval_id']}")
        print(f"  query: {verified_rows[0]['query']}")
        print(f"  ground_truth: {verified_rows[0]['ground_truth'][:80]}...")
        print(f"  chunk_ids: {verified_rows[0]['relevant_chunk_ids']}")
    
    return len(verified_rows)

if __name__ == '__main__':
    count = fix_csv_format()
    if count == 50:
        print(f"\n🎉 SUCCESS! All 50 questions successfully reformatted")
    else:
        print(f"\n⚠️  Warning: Expected 50 rows, got {count}")
