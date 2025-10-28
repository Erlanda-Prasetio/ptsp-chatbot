import requests, os
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

print("Testing the exact query from fallback_search...")
resp = requests.get(
    f"{url}/rest/v1/documents_old?select=id,content,metadata,embedding&limit=1000",
    headers=headers
)
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text[:300]}')
