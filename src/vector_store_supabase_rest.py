"""
Supabase Vector Store using REST API (more reliable than direct PostgreSQL)
"""
import os
import json
import requests
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class SupabaseRestVectorStore:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY') 
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.table_name = os.getenv('PG_TABLE', 'rag_chunks_jateng')
        
        if not all([self.url, self.service_key]):
            raise ValueError("Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")
        
        self.headers = {
            'apikey': self.service_key,
            'Authorization': f'Bearer {self.service_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        print(f"🔗 Supabase REST API initialized: {self.url}")
        self._ensure_table()
    
    def _ensure_table(self):
        """Check if table exists, create manually if needed"""
        # First, try to check if table exists by querying it
        try:
            response = requests.get(
                f"{self.url}/rest/v1/{self.table_name}?select=id&limit=1",
                headers=self.headers
            )
            
            if response.status_code == 200:
                print(f"✅ Table {self.table_name} already exists")
                return
            elif response.status_code == 404:
                print(f"⚠️  Table {self.table_name} not found. Please create it manually.")
                print(f"📋 Go to your Supabase Dashboard → SQL Editor and run the SQL from setup_supabase_sql.sql")
                print(f"🔗 Or visit: {self.url.replace('https://', 'https://app.supabase.com/project/')}/sql")
                return
            else:
                print(f"⚠️  Table check response: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"⚠️  Could not verify table existence: {e}")
            print(f"📋 Please manually create the table using setup_supabase_sql.sql")
    
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """Add multiple chunks to the vector store"""
        try:
            # Prepare data for insertion
            records = []
            for chunk in chunks:
                record = {
                    'content': chunk['content'],
                    'metadata': chunk.get('metadata', {}),
                    'embedding': chunk['embedding'].tolist() if isinstance(chunk['embedding'], np.ndarray) else chunk['embedding']
                }
                records.append(record)
            
            # Insert in batches of 100
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                response = requests.post(
                    f"{self.url}/rest/v1/{self.table_name}",
                    headers=self.headers,
                    json=batch
                )
                
                if response.status_code in [201, 200]:
                    total_inserted += len(batch)
                    print(f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} chunks (Total: {total_inserted})")
                else:
                    print(f"❌ Failed to insert batch {i//batch_size + 1}: {response.status_code} - {response.text}")
                    return False
            
            print(f"🎉 Successfully inserted {total_inserted} chunks total")
            return True
            
        except Exception as e:
            print(f"❌ Error adding chunks: {e}")
            return False
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks using cosine similarity"""
        try:
            # Convert embedding to list for JSON serialization
            query_vector = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
            
            # Use RPC function for vector similarity search
            rpc_data = {
                "query_embedding": query_vector,
                "match_threshold": 0.1,
                "match_count": top_k
            }
            
            response = requests.post(
                f"{self.url}/rest/v1/rpc/match_chunks",
                headers=self.headers,
                json=rpc_data
            )
            
            if response.status_code == 200:
                results = response.json()
                return results
            else:
                # Fallback to manual similarity calculation
                print(f"⚠️  RPC search failed, using fallback method")
                return self._fallback_search(query_vector, top_k)
                
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def _fallback_search(self, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Fallback search method"""
        try:
            # Get all embeddings (not efficient for large datasets)
            response = requests.get(
                f"{self.url}/rest/v1/{self.table_name}?select=id,content,metadata,embedding",
                headers=self.headers
            )
            
            if response.status_code != 200:
                return []
            
            all_chunks = response.json()
            
            # Calculate similarities
            similarities = []
            query_np = np.array(query_vector)
            
            for chunk in all_chunks:
                if chunk.get('embedding'):
                    chunk_embedding = np.array(chunk['embedding'])
                    similarity = np.dot(query_np, chunk_embedding) / (
                        np.linalg.norm(query_np) * np.linalg.norm(chunk_embedding)
                    )
                    similarities.append((similarity, chunk))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [chunk for _, chunk in similarities[:top_k]]
            
        except Exception as e:
            print(f"❌ Fallback search error: {e}")
            return []
    
    def get_count(self) -> int:
        """Get the number of chunks in the store"""
        try:
            response = requests.get(
                f"{self.url}/rest/v1/{self.table_name}?select=count",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get('count', 0)
                # Fallback: try to get content-range header
                content_range = response.headers.get('Content-Range', '')
                if content_range and '/' in content_range:
                    total = content_range.split('/')[-1]
                    if total.isdigit():
                        return int(total)
            
            return 0
        except Exception as e:
            print(f"⚠️  Error getting count: {e}")
            return 0

def test_rest_connection():
    """Test the Supabase REST API connection"""
    try:
        store = SupabaseRestVectorStore()
        count = store.get_count()
        print(f"✅ Connection successful! Current chunks: {count}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_rest_connection()
