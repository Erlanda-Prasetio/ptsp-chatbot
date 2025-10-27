#!/usr/bin/env python3
"""Clear all chunks from Supabase before re-ingesting cleaned data."""
import sys
import os
import requests
from dotenv import load_dotenv

sys.path.append('src')
load_dotenv()

def clear_supabase_table():
    """Delete all rows from rag_chunks_jateng table."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables!")
        return False
    
    table_url = f"{supabase_url}/rest/v1/rag_chunks_jateng"
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    print("\n" + "="*70)
    print("🗑️  CLEARING SUPABASE TABLE")
    print("="*70)
    
    # First, count current rows
    count_response = requests.get(
        table_url,
        headers={**headers, 'Prefer': 'count=exact'},
        params={'select': 'id', 'limit': 1}
    )
    
    if count_response.ok:
        count = count_response.headers.get('Content-Range', '0-0/0').split('/')[-1]
        print(f"\n📊 Current rows in table: {count}")
    
    # Delete all rows (using a condition that matches all rows)
    print("\n🗑️  Deleting all rows...")
    delete_response = requests.delete(
        table_url,
        headers=headers,
        params={'id': 'gte.0'}  # Delete where id >= 0 (all rows)
    )
    
    if delete_response.status_code in [200, 204]:
        print("✅ Table cleared successfully!")
        print("="*70 + "\n")
        return True
    else:
        print(f"❌ Failed to clear table: {delete_response.status_code}")
        print(f"Response: {delete_response.text}")
        return False

if __name__ == '__main__':
    success = clear_supabase_table()
    sys.exit(0 if success else 1)
