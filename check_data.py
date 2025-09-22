#!/usr/bin/env python3
"""
Check the uploaded data in Supabase
"""
import requests
from src.vector_store_supabase_rest import SupabaseRestVectorStore

def main():
    vs = SupabaseRestVectorStore()
    
    # Check count
    response = requests.get(
        f"{vs.url}/rest/v1/{vs.table_name}?select=count",
        headers={
            'apikey': vs.service_key,
            'Authorization': f'Bearer {vs.service_key}',
            'Content-Type': 'application/json',
            'Prefer': 'count=exact'
        }
    )
    
    content_range = response.headers.get("content-range", "unknown")
    print(f"Total vectors: {content_range}")
    
    # Sample a few records
    response = requests.get(
        f"{vs.url}/rest/v1/{vs.table_name}?select=id,content,source&limit=3",
        headers={
            'apikey': vs.service_key,
            'Authorization': f'Bearer {vs.service_key}',
            'Content-Type': 'application/json'
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSample records ({len(data)} shown):")
        for i, record in enumerate(data):
            print(f"  {i+1}. ID: {record.get('id')}")
            print(f"     Source: {record.get('source', 'unknown')}")
            print(f"     Content: {record.get('content', '')[:100]}...")
            print()
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()