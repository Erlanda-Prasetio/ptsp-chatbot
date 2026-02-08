"""
Create Retrieval Test Template from sample_50_balanced_cleaned.json
==================================================================

Reads the 50 balanced questions from the JSON file and creates
a CSV template with columns for chunk IDs to be populated.

Usage:
    python evaluation/create_retrieval_template.py
"""

import json
import csv
from pathlib import Path

def create_template_from_json():
    """Create retrieval test template from JSON sample"""
    
    print("\n" + "="*70)
    print("CREATE RETRIEVAL TEST TEMPLATE FROM JSON")
    print("="*70 + "\n")
    
    # Load JSON file
    json_path = Path('evaluation') / 'sample_50_balanced_cleaned.json'
    
    if not json_path.exists():
        print(f"[FAIL] ERROR: {json_path} not found!")
        return False
    
    print(f"[DIR] Loading questions from: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    queries = data.get('queries', [])
    print(f"[OK] Loaded {len(queries)} questions\n")
    
    # Print metadata
    metadata = data.get('metadata', {})
    print("[STATS] Metadata:")
    print(f"   Old Dataset: {metadata.get('distribution', {}).get('old_questions')} questions")
    print(f"   New Dataset: {metadata.get('distribution', {}).get('new_questions')} questions")
    print(f"   Total: {len(queries)} questions\n")
    
    # Create CSV data
    csv_data = []
    
    for query in queries:
        query_id = query.get('id', '')
        question = query.get('query', '')
        category = query.get('category', 'Unknown')
        dataset_source = query.get('dataset_source', 'OLD')
        
        csv_data.append({
            'query_id': query_id,
            'question': question,
            'category': category,
            'dataset_source': dataset_source,
            'retrieved_chunks': '',  # Empty - will be filled by chunk test
            'chunk1_id': '',
            'chunk2_id': '',
            'chunk3_id': '',
            'chunk4_id': '',
            'chunk5_id': '',
            'generated_chunks': '',  # Empty - will be filled by retrieval test
            'search_method': '',     # Empty - will be filled by retrieval test
            'retrieval_time_seconds': '',  # Empty - will be filled by retrieval test
            'precision': '',         # Empty - will be filled by retrieval test
            'recall': '',            # Empty - will be filled by retrieval test
            'f1_score': '',          # Empty - will be filled by retrieval test
            'notes': '',             # Empty
        })
    
    # Save as CSV
    csv_path = Path('evaluation') / 'old_dataset_retrieval_test_template.csv'
    
    print(f" Creating CSV template: {csv_path}")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'query_id', 'question', 'category', 'dataset_source', 
            'retrieved_chunks', 'chunk1_id', 'chunk2_id', 'chunk3_id', 'chunk4_id', 'chunk5_id',
            'generated_chunks', 'search_method', 'retrieval_time_seconds',
            'precision', 'recall', 'f1_score', 'notes'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"[OK] Created template with {len(csv_data)} questions\n")
    
    # Verify
    old_count = sum(1 for q in csv_data if q['dataset_source'] == 'OLD')
    new_count = sum(1 for q in csv_data if q['dataset_source'] == 'NEW')
    
    print("[STATS] Template Summary:")
    print(f"   Total Questions: {len(csv_data)}")
    print(f"   OLD Dataset: {old_count}")
    print(f"   NEW Dataset: {new_count}")
    print(f"   Ready for: Chunk confidence test\n")
    
    return True


if __name__ == "__main__":
    success = create_template_from_json()
    
    if success:
        print("[OK] Template created successfully!\n")
        print("Next step: Run chunk confidence test")
        print("   python evaluation/chunk_confidence_test.py")
    else:
        print("[FAIL] Template creation failed!\n")
