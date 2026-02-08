#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Test: replicate what the analyze script does
supabase_url = os.getenv('SUPABASE_URL', '')
supabase_key = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
pg_table = os.getenv('PG_TABLE', 'rag_chunks_jateng')

print(f'Supabase URL: {bool(supabase_url)}')
print(f'Supabase Key: {bool(supabase_key)}')
print(f'Table: {pg_table}')

SUPABASE_CLIENT = None
try:
    if supabase_url and supabase_key:
        SUPABASE_CLIENT = create_client(supabase_url, supabase_key)
        print('[OK] Client initialized')
except Exception as e:
    print(f'[FAIL] Error: {e}')

def get_chunk_content(chunk_id):
    if not SUPABASE_CLIENT:
        print(f'  No client available')
        return ""
    
    try:
        print(f'  Querying chunk {chunk_id}...')
        result = SUPABASE_CLIENT.table(pg_table).select('content, text').eq('id', int(chunk_id)).execute()
        print(f'  Query complete, data: {len(result.data)} rows')
        
        if result.data and len(result.data) > 0:
            chunk = result.data[0]
            content = chunk.get('content') or chunk.get('text', '')
            print(f'  Got {len(content)} chars')
            return content
        
        return ""
    except Exception as e:
        print(f'  Exception: {e}')
        return ""

# Test with chunk from CSV
test_chunk_id = '8646'
print(f'\nTesting chunk {test_chunk_id}:')
content = get_chunk_content(test_chunk_id)
print(f'Content: {len(content)} chars, preview: {content[:50]}...')
