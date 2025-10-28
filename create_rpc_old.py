#!/usr/bin/env python3
"""
Setup RPC functions in Supabase for match_documents_old
This is a direct approach using PostgreSQL connection
"""

import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Extract connection details from Supabase URL
# Format: https://xxxx.supabase.co
project_ref = SUPABASE_URL.replace('https://', '').split('.')[0]

print("="*70)
print("🔧 RPC Function Setup for OLD Dataset")
print("="*70)
print(f"\nProject Reference: {project_ref}")
print(f"Supabase URL: {SUPABASE_URL}")

# The SQL function definition
CREATE_RPC_SQL = '''
CREATE OR REPLACE FUNCTION match_documents_old(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.1,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    title text,
    content text,
    source text,
    similarity float
)
LANGUAGE sql
STABLE
AS $$
SELECT 
    documents_old.id,
    documents_old.title,
    documents_old.content,
    documents_old.source,
    1 - (documents_old.embedding <=> query_embedding) AS similarity
FROM documents_old
WHERE 1 - (documents_old.embedding <=> query_embedding) > match_threshold
ORDER BY documents_old.embedding <=> query_embedding
LIMIT match_count;
$$;
'''

print("\n" + "="*70)
print("📋 SQL TO EXECUTE IN SUPABASE SQL EDITOR:")
print("="*70)
print(CREATE_RPC_SQL)

print("\n" + "="*70)
print("🔗 STEPS TO CREATE THE RPC FUNCTION:")
print("="*70)
print("\n1. Go to: https://app.supabase.com/projects")
print(f"2. Open your project (Project ref: {project_ref})")
print("3. Click 'SQL Editor' (left sidebar)")
print("4. Click '+ New Query'")
print("5. Paste the SQL above")
print("6. Click 'RUN'")
print("\n7. After creation, verify by running:")
print("   python test_rpc_functions.py")
print("\n" + "="*70)
