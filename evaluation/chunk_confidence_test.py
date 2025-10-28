"""
Chunk Confidence Test - Retrieve Top 5 Chunks for Each Question
================================================================

For each question in the template, query Supabase to get the top 5
most relevant chunks using vector search, then save chunk IDs to CSV.

Usage:
    python evaluation/chunk_confidence_test.py
"""

import os
import sys
import csv
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append('src')
sys.path.append('.')

from dotenv import load_dotenv

load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY not found in .env")
    sys.exit(1)

from supabase import create_client
from src.embed import embed_texts


def get_top_chunks(supabase, table_name: str, query_text: str, limit: int = 5):
    """
    Query Supabase using vector search to get top chunks
    """
    try:
        # Embed the query
        query_embedding = embed_texts([query_text])[0]
        
        # Query using RPC function - it returns {data: [...], count: ...}
        if table_name == 'documents_old':
            result = supabase.rpc('match_documents_old', {
                'query_embedding': query_embedding,
                'match_count': limit
            }).execute()
        elif table_name == 'documents_new':
            result = supabase.rpc('match_documents_new', {
                'query_embedding': query_embedding,
                'match_count': limit
            }).execute()
        elif table_name == 'documents_combined':
            result = supabase.rpc('match_documents_combined', {
                'query_embedding': query_embedding,
                'match_count': limit
            }).execute()
        else:
            return []
        
        # Extract the data array from response
        # The RPC returns a response object with .data and .count attributes
        chunks = []
        try:
            # Try accessing as response object (supabase library returns this)
            if hasattr(result, 'data'):
                chunks = result.data if result.data else []
            # Try as dict
            elif isinstance(result, dict) and 'data' in result:
                chunks = result.get('data', [])
            # Try as list
            elif isinstance(result, list):
                chunks = result
        except Exception as e:
            print(f"      DEBUG: Error extracting chunks: {e}, result type: {type(result)}")
            chunks = []
        
        return chunks
        
    except Exception as e:
        print(f"   ❌ Error querying {table_name}: {e}")
        return []


def run_chunk_confidence_test():
    """Run chunk confidence test on template CSV"""
    
    print("\n" + "="*70)
    print("CHUNK CONFIDENCE TEST - RETRIEVE TOP 5 CHUNKS FOR EACH QUESTION")
    print("="*70 + "\n")
    
    # Connect to Supabase
    print("🔌 Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Load template CSV
    template_path = Path('evaluation') / 'old_dataset_retrieval_test_template.csv'
    
    if not template_path.exists():
        print(f"❌ ERROR: {template_path} not found!")
        return False
    
    print(f"📂 Loading template from: {template_path}\n")
    
    # Read CSV and process each question
    questions = []
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append(row)
        
        print(f"✅ Loaded {len(questions)} questions\n")
        
        # Process each question
        print("🔍 Running chunk confidence test...\n")
        
        for idx, question_row in enumerate(questions, 1):
            query_id = question_row.get('query_id', '')
            question_text = question_row.get('question', '')
            dataset_source = question_row.get('dataset_source', 'OLD')
            
            print(f"[{idx}/{len(questions)}] {query_id}: {question_text[:60]}...")
            
            # Determine which table to query
            if dataset_source == 'NEW':
                table_name = 'documents_new'
            elif dataset_source == 'COMBINED':
                table_name = 'documents_combined'
            else:
                table_name = 'documents_old'
            
            # Get top 5 chunks
            chunks = get_top_chunks(supabase, table_name, question_text, limit=5)
            
            if chunks:
                # Handle both dict and tuple responses from RPC
                chunk_ids = []
                for chunk in chunks:
                    if isinstance(chunk, dict):
                        chunk_id = chunk.get('id', '')
                        chunk_ids.append(str(chunk_id))
                    elif isinstance(chunk, (list, tuple)):
                        # First element of tuple is usually the ID
                        chunk_ids.append(str(chunk[0] if chunk else ''))
                
                # Filter out empty strings
                chunk_ids = [cid for cid in chunk_ids if cid and cid.strip()]
                
                if chunk_ids:
                    print(f"   ✅ Found {len(chunk_ids)} chunks: {', '.join(chunk_ids[:3])}...")
                
                # Update the row with chunk IDs
                question_row['retrieved_chunks'] = ','.join(chunk_ids)
                question_row['chunk1_id'] = chunk_ids[0] if len(chunk_ids) > 0 else ''
                question_row['chunk2_id'] = chunk_ids[1] if len(chunk_ids) > 1 else ''
                question_row['chunk3_id'] = chunk_ids[2] if len(chunk_ids) > 2 else ''
                question_row['chunk4_id'] = chunk_ids[3] if len(chunk_ids) > 3 else ''
                question_row['chunk5_id'] = chunk_ids[4] if len(chunk_ids) > 4 else ''
            else:
                print(f"   ⚠️  No chunks found for this question")
        
        # Save updated CSV
        output_path = Path('evaluation') / 'old_dataset_retrieval_test_template.csv'
        
        print(f"\n📝 Saving updated CSV to: {output_path}...")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if questions:
                fieldnames = questions[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(questions)
        
        print(f"   ✅ Saved {len(questions)} rows\n")
        
        # Print summary
        print("📊 Summary:")
        print(f"   Total Questions: {len(questions)}")
        old_questions = sum(1 for q in questions if q.get('dataset_source') == 'OLD')
        new_questions = sum(1 for q in questions if q.get('dataset_source') == 'NEW')
        print(f"   OLD Dataset: {old_questions}")
        print(f"   NEW Dataset: {new_questions}")
        
        with_chunks = sum(1 for q in questions if q.get('retrieved_chunks', '').strip())
        print(f"   With Chunks: {with_chunks}/{len(questions)} ({with_chunks/len(questions)*100:.1f}%)\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_chunk_confidence_test()
    
    if success:
        print("✅ Chunk confidence test complete!\n")
        print("Next step: Run retrieval test with populated CSV")
    else:
        print("❌ Chunk confidence test failed!\n")
        sys.exit(1)
