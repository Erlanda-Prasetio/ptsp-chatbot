"""
Import ground truth from CSV template back into sample_50_balanced.json
"""

import csv
import json
import os

def import_ground_truth_from_csv():
    """Import ground truth and relevant_chunk_ids from CSV into JSON"""
    
    csv_file = 'evaluation/ground_truth_template_fixed.csv'
    json_file = 'evaluation/sample_50_balanced.json'
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return False
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return False
    
    print(f"\n{'='*80}")
    print(f"📥 IMPORTING GROUND TRUTH FROM CSV")
    print(f"{'='*80}\n")
    
    # Load JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Loaded JSON: {len(data['queries'])} questions")
    
    # Load CSV
    ground_truth_map = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            eval_id = row['eval_id']
            ground_truth = row['ground_truth'].strip()
            chunk_ids_str = row['relevant_chunk_ids'].strip()
            
            # Parse chunk IDs
            if chunk_ids_str:
                # Remove any extra quotes and split by comma
                chunk_ids_str = chunk_ids_str.replace('"', '').replace("'", "")
                chunk_ids = [int(cid.strip()) for cid in chunk_ids_str.split(',') if cid.strip().isdigit()]
            else:
                chunk_ids = []
            
            ground_truth_map[eval_id] = {
                'ground_truth': ground_truth,
                'relevant_chunk_ids': chunk_ids
            }
    
    print(f"✅ Loaded CSV: {len(ground_truth_map)} ground truth entries")
    
    # Update JSON
    updated_count = 0
    missing_count = 0
    
    for query in data['queries']:
        eval_id = query.get('eval_id', '')
        
        if eval_id in ground_truth_map:
            query['ground_truth'] = ground_truth_map[eval_id]['ground_truth']
            query['relevant_chunk_ids'] = ground_truth_map[eval_id]['relevant_chunk_ids']
            updated_count += 1
            
            if updated_count <= 3:  # Show first 3 for verification
                print(f"\n✅ Updated {eval_id}:")
                print(f"   Query: {query['query'][:60]}...")
                print(f"   Ground Truth: {query['ground_truth'][:80]}...")
                print(f"   Chunk IDs ({len(query['relevant_chunk_ids'])}): {query['relevant_chunk_ids']}")
        else:
            print(f"⚠️  No ground truth found for: {eval_id}")
            missing_count += 1
    
    # Save updated JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"📊 IMPORT SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Updated: {updated_count} questions")
    print(f"⚠️  Missing: {missing_count} questions")
    print(f"✅ Saved to: {json_file}")
    
    if updated_count == 50 and missing_count == 0:
        print(f"\n🎉 SUCCESS! All 50 questions imported successfully!")
        print(f"\n📋 NEXT STEP:")
        print(f"   Run evaluation:")
        print(f"   python evaluation/run_balanced_evaluation.py --name baseline_old_dataset")
        return True
    else:
        print(f"\n⚠️  Warning: Some questions were not updated")
        return False

if __name__ == '__main__':
    import_ground_truth_from_csv()
