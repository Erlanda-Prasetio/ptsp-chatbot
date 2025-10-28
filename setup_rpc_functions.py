#!/usr/bin/env python3
"""
Setup RPC functions for dataset-specific matching in Supabase
This creates the match_documents_old, match_documents_new, and match_documents_combined RPC functions
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")
    exit(1)

def execute_sql(sql_query):
    """Execute SQL query via Supabase REST API"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # The REST API doesn't directly execute arbitrary SQL
    # We need to use the SQL endpoint directly (if available)
    # Or call a stored procedure
    # For now, let's check if we can call the functions to see if they exist
    
    print(f"Query: {sql_query[:100]}...")
    return True

# SQL for creating the RPC functions
CREATE_FUNCTIONS_SQL = """
-- Create matching function for OLD dataset
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

-- Create matching function for NEW dataset
CREATE OR REPLACE FUNCTION match_documents_new(
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
    documents_new.id,
    documents_new.title,
    documents_new.content,
    documents_new.source,
    1 - (documents_new.embedding <=> query_embedding) AS similarity
FROM documents_new
WHERE 1 - (documents_new.embedding <=> query_embedding) > match_threshold
ORDER BY documents_new.embedding <=> query_embedding
LIMIT match_count;
$$;

-- Create matching function for COMBINED dataset
CREATE OR REPLACE FUNCTION match_documents_combined(
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
    documents_combined.id,
    documents_combined.title,
    documents_combined.content,
    documents_combined.source,
    1 - (documents_combined.embedding <=> query_embedding) AS similarity
FROM documents_combined
WHERE 1 - (documents_combined.embedding <=> query_embedding) > match_threshold
ORDER BY documents_combined.embedding <=> query_embedding
LIMIT match_count;
$$;
"""

print("\n" + "="*70)
print("🚀 RPC Function Setup for Supabase")
print("="*70)
print("\n⚠️  IMPORTANT: The Supabase REST API doesn't support direct SQL execution")
print("You need to run this SQL manually in your Supabase SQL Editor:")
print("\n1. Go to: https://app.supabase.com")
print("2. Open your project")
print("3. Go to: SQL Editor → New Query")
print("4. Copy and paste the SQL below")
print("5. Click 'Run'")
print("\n" + "="*70)
print("\nSQL to execute:")
print("="*70 + "\n")
print(CREATE_FUNCTIONS_SQL)
print("\n" + "="*70)
print("After executing the SQL, test with:")
print("python test_rpc_functions.py")
print("="*70 + "\n")
