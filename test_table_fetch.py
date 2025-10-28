#!/usr/bin/env python3
"""
Test if we can fetch data from documents_old table directly
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json'
}

print("Testing direct fetch from documents_old table...")
print("="*70)

# Test 1: Simple count
print("\n1. Testing count...")
resp = requests.get(f'{url}/rest/v1/documents_old?select=count', headers=headers)
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text}")

# Test 2: Get one row
print("\n2. Testing single row fetch...")
resp = requests.get(f'{url}/rest/v1/documents_old?select=id,title&limit=1', headers=headers)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"   Response: {resp.json()}")
else:
    print(f"   Response: {resp.text[:200]}")

# Test 3: Get 10 rows with embedding
print("\n3. Testing 10 rows with embedding (limited fields)...")
resp = requests.get(
    f'{url}/rest/v1/documents_old?select=id,content,embedding&limit=10',
    headers=headers
)
print(f"   Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"   Got {len(data)} rows")
    if data:
        print(f"   First row has embedding: {'embedding' in data[0]}")
        print(f"   Embedding type: {type(data[0].get('embedding'))}")
else:
    print(f"   Response: {resp.text[:200]}")

print("\n" + "="*70)
