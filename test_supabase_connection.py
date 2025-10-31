#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

# Load .env file
load_dotenv()

supabase_url = os.getenv('SUPABASE_URL', '')
supabase_key = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

print(f'SUPABASE_URL exists: {bool(supabase_url)}')
print(f'SUPABASE_KEY exists: {bool(supabase_key)}')

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        pg_table = os.getenv('PG_TABLE', 'rag_chunks_jateng')
        print(f'PG_TABLE: {pg_table}')
        
        result = supabase.table(pg_table).select('content').eq('id', 8646).execute()
        print(f'Chunk 8646 found: {len(result.data) > 0}')
        if result.data:
            content = result.data[0].get('content', '')
            print(f'Content length: {len(content)} chars')
            print(f'Content preview: {content[:100]}...')
    except Exception as e:
        print(f'Error: {e}')
