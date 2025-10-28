import requests, os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

resp = requests.get(f'{url}/rest/v1/documents_old?select=id,content,embedding&limit=220', headers=headers)
print(f'Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'Got {len(data)} rows')
else:
    print(f'Error: {resp.text[:200]}')
