import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

print("Testing which RPC functions exist...")
test_vec = [0.1]*384

for func_name in ['match_documents', 'match_documents_old', 'match_documents_new', 'match_documents_combined']:
    resp = requests.post(
        f'{url}/rest/v1/rpc/{func_name}',
        json={'query_embedding': test_vec, 'match_count': 5, 'filter': {}},
        headers=headers
    )
    print(f"\n{func_name}:")
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.text[:150]}")
