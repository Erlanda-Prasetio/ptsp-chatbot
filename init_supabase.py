#!/usr/bin/env python3
"""
Simple Supabase initialization script
"""

import sys
sys.path.append('src')

from vector_store_supabase import SupabaseVectorStore

def main():
    try:
        print("🔄 Initializing Supabase vector store...")
        
        # This will create the extension and table
        store = SupabaseVectorStore()
        print("✅ Supabase vector store initialized successfully!")
        
        store.close()
        
        print("\n🎉 Ready to ingest data!")
        print("Run: python src/ingest_scraped.py data/scraped")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your Supabase credentials in .env file")
        print("2. Ensure pgvector extension is enabled in your Supabase project")
        print("3. Verify network connectivity to Supabase")

if __name__ == "__main__":
    main()
