#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL', '')
supabase_key = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
pg_table = os.getenv('PG_TABLE', 'rag_chunks_jateng')

print(f'Testing chunk retrieval...')
print(f'Table: {pg_table}')

supabase = create_client(supabase_url, supabase_key)

# Test with chunk from CSV: 8918
chunk_id = 8918
try:
    result = supabase.table(pg_table).select('id, content').eq('id', chunk_id).execute()
    print(f'Chunk {chunk_id} - Found: {len(result.data) > 0}')
    if result.data:
        content = result.data[0].get('content', '')
        print(f'Content length: {len(content)}')
        print(f'Content preview: {content[:100]}...')
    else:
        print(f'Query returned 0 results')
except Exception as e:
    print(f'Error: {e}')
