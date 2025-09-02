#!/usr/bin/env python3
"""
Ingest data directly to Supabase with proper error handling
"""

import sys
import os
sys.path.append('src')

from pathlib import Path
from tqdm import tqdm
from chunk import chunk_text
from embed import embed_texts

def ingest_to_supabase():
    """Ingest files to Supabase with connection retry"""
    
    print("🔄 Starting Supabase ingestion...")
    
    # Switch to Supabase backend
    os.environ['VECTOR_BACKEND'] = 'supabase'
    
    try:
        from vector_store_supabase import SupabaseVectorStore
        
        # Initialize with retry
        print("🔗 Connecting to Supabase...")
        store = SupabaseVectorStore()
        print("✅ Connected to Supabase successfully!")
        
        # Get files to ingest
        scraped_dir = Path("data/scraped")
        csv_files = list(scraped_dir.glob("*.csv"))[:10]  # Start with first 10 CSV files
        
        print(f"📂 Found {len(csv_files)} CSV files to ingest")
        
        for file_path in tqdm(csv_files, desc="Ingesting files"):
            try:
                # Read and process file
                text = file_path.read_text(encoding='utf-8', errors='ignore')
                enhanced_text = f"Source: {file_path.name}\nFile Type: {file_path.suffix}\nPath: {file_path}\n\n{text}"
                
                # Chunk the text
                chunks = chunk_text(enhanced_text)
                
                if chunks:
                    # Add to Supabase
                    store.add_chunks(str(file_path), chunks)
                    print(f"✅ Ingested: {file_path.name} ({len(chunks)} chunks)")
                
            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")
                continue
        
        store.close()
        print("🎉 Supabase ingestion completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        
        # Provide helpful troubleshooting
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file has correct Supabase credentials")
        print("2. Ensure pgvector extension is enabled in Supabase:")
        print("   - Go to SQL Editor in Supabase Dashboard")
        print("   - Run: CREATE EXTENSION IF NOT EXISTS vector;")
        print("3. Check network connectivity")
        print("4. Verify database permissions")
        
        return False

if __name__ == "__main__":
    success = ingest_to_supabase()
    if success:
        print("\n✅ Ready to test chatbot with Supabase!")
        print("Run: python src/chatbot.py")
    else:
        print("\n❌ Ingestion failed. Please check the troubleshooting steps above.")
