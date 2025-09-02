#!/usr/bin/env python3
"""
Setup script for Supabase/PostgreSQL vector database
"""

import os
import sys
from pathlib import Path

def update_env_file():
    """Update .env file with Supabase credentials"""
    print("🔧 Supabase Vector Store Setup")
    print("="*50)
    
    # Get current .env content
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    print("Please provide your Supabase connection details:")
    print("(You can find these in your Supabase project settings)")
    
    # Get user input
    host = input("🌐 Supabase Host (e.g., xxxxx.supabase.co): ").strip()
    password = input("🔒 Database Password: ").strip()
    
    if not host or not password:
        print("❌ Host and password are required!")
        return False
    
    # Read current .env content
    content = env_file.read_text()
    
    # Update the placeholder values
    content = content.replace("your_supabase_host.supabase.co", host)
    content = content.replace("your_supabase_password", password)
    
    # Write back to .env
    env_file.write_text(content)
    
    print("✅ .env file updated successfully!")
    return True

def test_connection():
    """Test the Supabase connection"""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        from src.config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD
        import psycopg
        
        conn = psycopg.connect(
            host=PG_HOST, 
            port=PG_PORT, 
            dbname=PG_DB, 
            user=PG_USER, 
            password=PG_PASSWORD
        )
        
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def setup_vector_extension():
    """Set up pgvector extension and table"""
    print("\n🛠️ Setting up pgvector extension and table...")
    
    try:
        from src.vector_store_supabase import SupabaseVectorStore
        
        # This will automatically create the extension and table
        store = SupabaseVectorStore()
        store.close()
        
        print("✅ pgvector extension and table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure pgvector extension is available in your Supabase project")
        print("2. Check your connection credentials")
        print("3. Ensure your database user has necessary permissions")
        return False

def main():
    """Main setup function"""
    print("🚀 Welcome to Supabase Vector Store Setup!")
    print("This script will help you configure Supabase for your RAG system.\n")
    
    # Step 1: Update .env file
    if not update_env_file():
        sys.exit(1)
    
    # Step 2: Test connection
    if not test_connection():
        print("\n❌ Setup failed. Please check your credentials and try again.")
        sys.exit(1)
    
    # Step 3: Setup vector extension
    if not setup_vector_extension():
        sys.exit(1)
    
    print("\n🎉 Supabase setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python src/ingest_scraped.py data/scraped")
    print("2. Run: python src/chatbot.py")
    print("\nYour data will now be stored in Supabase for scalable vector search!")

if __name__ == "__main__":
    main()
