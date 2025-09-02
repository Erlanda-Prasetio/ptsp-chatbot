import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        print("Testing Supabase connection...")
        print(f"Host: {os.getenv('PG_HOST')}")
        print(f"Port: {os.getenv('PG_PORT')}")
        print(f"Database: {os.getenv('PG_DB')}")
        print(f"User: {os.getenv('PG_USER')}")
        print(f"Password: {'*' * len(os.getenv('PG_PASSWORD', ''))}")
        
        conn = psycopg2.connect(
            host=os.getenv('PG_HOST'),
            port=int(os.getenv('PG_PORT', 5432)),
            database=os.getenv('PG_DB'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected successfully! PostgreSQL version: {version[0]}")
        
        # Check if pgvector is available
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        vector_ext = cursor.fetchone()
        if vector_ext:
            print("✅ pgvector extension is available")
        else:
            print("❌ pgvector extension not found")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
