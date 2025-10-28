import requests, os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

resp = requests.get(f'{url}/rest/v1/documents_old?select=*&limit=1', headers=headers)
if resp.status_code == 200:
    row = resp.json()[0]
    print("Columns in documents_old table:")
    for col in row.keys():
        print(f"  - {col}: {type(row[col]).__name__}")
else:
    print(f"Error: {resp.text}")
