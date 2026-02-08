"""
Quick verification script to test chunk ID fix
"""
import requests
import json

def test_api_chunk_ids():
    """Test if API now returns chunk IDs"""
    
    url = "http://localhost:8001/chat"
    
    # Use a query from baseline that we know got Supabase results (Q002)
    test_query = {
        "messages": [
            {"role": "user", "content": "Apakah KSO atau JO Bisa Memiliki NIB?"}
        ]
    }
    
    print("[TEST] Testing API chunk ID fix...")
    print(f"Query: {test_query['messages'][0]['content']}")
    print("(Using Q002 from baseline which got Supabase results)\n")
    
    try:
        response = requests.post(url, json=test_query, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("[OK] API Response received")
            print(f"Answer preview: {result['message'][:200]}...\n")
            
            sources = result.get('sources', [])
            print(f" Sources returned: {len(sources)}")
            
            if sources:
                print("\n[SEARCH] First source structure:")
                first_source = sources[0]
                for key, value in first_source.items():
                    if key == 'content_preview':
                        print(f"  - {key}: {str(value)[:80]}...")
                    else:
                        print(f"  - {key}: {value}")
                
                # Check if chunk_id exists
                chunk_ids = [s.get('chunk_id') for s in sources if s.get('chunk_id') is not None]
                filenames = [s.get('filename') for s in sources if s.get('filename')]
                
                print(f"\n[STATS] Chunk IDs found: {len(chunk_ids)}")
                print(f"   Sample IDs: {chunk_ids[:3]}")
                print(f"\n Filenames found: {len(filenames)}")
                print(f"   Sample filenames: {filenames[:3]}")
                
                if chunk_ids:
                    print("\n[OK] SUCCESS! API now returns chunk IDs")
                    print(f"   Type check: {type(chunk_ids[0])}")
                else:
                    print("\n[FAIL] FAILED! No chunk IDs in response")
                    
            else:
                print("[WARN]  No sources in response")
                
        else:
            print(f"[FAIL] API Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("[FAIL] Cannot connect to API. Make sure it's running on http://localhost:8001")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

if __name__ == "__main__":
    test_api_chunk_ids()
