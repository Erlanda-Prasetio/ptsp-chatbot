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
            
            # Always use fallback method for reliability
            return self._fallback_search(query_vector, top_k)
                
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def _fallback_search(self, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Fallback search method"""
        try:
            # Get all embeddings (not efficient for large datasets)
            response = requests.get(
                f"{self.url}/rest/v1/{self.table_name}?select=id,content,metadata,embedding&limit=1000",
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch data: {response.status_code}")
                return []
            
            all_chunks = response.json()
            print(f"🔍 Comparing against {len(all_chunks)} chunks")
            
            # Calculate similarities
            similarities = []
            query_np = np.array(query_vector)
            
            for chunk in all_chunks:
                if chunk.get('embedding'):
                    try:
                        # Handle different embedding formats
                        embedding_data = chunk['embedding']
                        if isinstance(embedding_data, str):
                            # Parse string representation of list
                            embedding_data = embedding_data.strip('[]').split(',')
                            chunk_embedding = np.array([float(x.strip()) for x in embedding_data])
                        elif isinstance(embedding_data, list):
                            chunk_embedding = np.array(embedding_data)
                        else:
                            continue
                            
                        similarity = np.dot(query_np, chunk_embedding) / (
                            np.linalg.norm(query_np) * np.linalg.norm(chunk_embedding)
                        )
                        
                        # Add similarity score to the result
                        result_chunk = {
                            'id': chunk.get('id'),  # Include the chunk ID
                            'content': chunk['content'],
                            'metadata': chunk.get('metadata', {}),
                            'similarity': float(similarity)
                        }
                        similarities.append((similarity, result_chunk))
                    except Exception as e:
                        print(f"⚠️  Error processing chunk {chunk.get('id')}: {e}")
                        continue
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[0], reverse=True)
            results = [chunk for _, chunk in similarities[:top_k]]
            
            if results:
                sim_scores = [r["similarity"] for r in results[:3]]
                print(f"🎯 Top {len(results)} similarities: {sim_scores}")
            return results
            
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
    
    def clear(self):
        """Clear all data from the vector store"""
        try:
            print(f"🗑️ Clearing all data from {self.table_name}...")
            # For Supabase, we need to use a WHERE clause like "id.gte.0" to delete all rows
            response = requests.delete(
                f"{self.url}/rest/v1/{self.table_name}?id=gte.0",
                headers=self.headers
            )
            
            if response.status_code in [200, 204]:
                print("✅ Data cleared successfully")
                return True
            else:
                print(f"⚠️  Clear response: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            return False
    
    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]] = None, embeddings: List[List[float]] = None) -> List[str]:
        """Add texts with embeddings to the store"""
        try:
            if not embeddings:
                raise ValueError("Embeddings are required for add_texts")
            
            if metadatas is None:
                metadatas = [{}] * len(texts)
            
            chunks_to_insert = []
            for i, (text, metadata, embedding) in enumerate(zip(texts, metadatas, embeddings)):
                chunk = {
                    'content': text,
                    'metadata': metadata,
                    'embedding': embedding
                }
                chunks_to_insert.append(chunk)
            
            # Batch insert using REST API
            response = requests.post(
                f"{self.url}/rest/v1/{self.table_name}",
                headers=self.headers,
                json=chunks_to_insert
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Successfully uploaded {len(chunks_to_insert)} chunks")
                return [str(i) for i in range(len(texts))]  # Return IDs
            else:
                print(f"❌ Error uploading chunks: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error in add_texts: {e}")
            return []

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
