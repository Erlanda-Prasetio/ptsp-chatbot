import requests
import json

# Test the API directly
response = requests.post('http://localhost:8001/chat', 
    json={'messages': [{'role': 'user', 'content': 'Apa itu DPMPTSP?'}]})

print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Enhanced features: {data["enhanced_features"]}')
    print(f'Answer preview: {data["message"][:100]}...')
    print(f'Sources: {len(data["sources"])}')
else:
    print(f'Error: {response.text}')
