#!/usr/bin/env python3
"""
Migrate existing local vector store to Supabase
"""

import os
import sys
import numpy as np
import json
from pathlib import Path
from tqdm import tqdm

def migrate_to_supabase():
    """Migrate local vector store to Supabase"""
    print("🔄 Migrating local vector store to Supabase...")
    
    # Check if local store exists
    local_store_path = Path("data/default_vector_store.npy")
    local_meta_path = Path("data/default_docs_meta.json")
    
    if not local_store_path.exists() or not local_meta_path.exists():
        print("❌ No local vector store found!")
        print("Please run ingestion first: python src/ingest_scraped.py data/scraped")
        return False
    
    try:
        # Load local data
        print("📂 Loading local vector store...")
        embeddings = np.load(local_store_path)
        with open(local_meta_path, 'r') as f:
            metadata = json.load(f)
        
        print(f"📊 Found {len(embeddings)} vectors to migrate")
        
        # Initialize Supabase store
        from src.vector_store_supabase_rest import SupabaseRestVectorStore
        supa_store = SupabaseRestVectorStore()
        
        # Get texts and metadata
        texts = metadata['texts']
        meta_list = metadata['meta']
        
        # Migrate data in batches
        batch_size = 50  # Smaller batches for REST API
        total_items = len(texts)
        
        print(f"🚀 Starting migration of {total_items} chunks...")
        
        for i in tqdm(range(0, total_items, batch_size), desc="Migrating batches"):
            batch_end = min(i + batch_size, total_items)
            
            # Prepare batch data
            batch_texts = texts[i:batch_end]
            batch_meta = meta_list[i:batch_end]
            batch_embeddings = embeddings[i:batch_end]
            
            # Convert to the format expected by REST API
            chunks = []
            for text, meta, embedding in zip(batch_texts, batch_meta, batch_embeddings):
                chunk = {
                    'content': text,
                    'metadata': meta,
                    'embedding': embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
                }
                chunks.append(chunk)
            
            # Insert batch into Supabase
            success = supa_store.add_chunks(chunks)
            
            if not success:
                print(f"❌ Failed to migrate batch {i//batch_size + 1}")
                return False
        
        print("✅ Migration completed successfully!")
        
        # Verify migration
        final_count = supa_store.get_count()
        print(f"📊 Verification: {final_count} chunks in Supabase")
        
        # Update .env to use Supabase backend
        env_file = Path(".env")
        content = env_file.read_text()
        content = content.replace("VECTOR_BACKEND = local", "VECTOR_BACKEND = supabase")
        env_file.write_text(content)
        
        print("✅ Updated configuration to use Supabase backend")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Local to Supabase Migration Tool")
    print("="*50)
    
    # Check if Supabase is configured
    try:
        from src.config import VECTOR_BACKEND, PG_HOST, PG_PASSWORD
        
        if "your_supabase" in PG_HOST or "your_supabase" in PG_PASSWORD:
            print("❌ Supabase not configured yet!")
            print("Please run: python setup_supabase.py first")
            sys.exit(1)
            
    except ImportError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Perform migration
    if migrate_to_supabase():
        print("\n🎉 Migration completed!")
        print("\nYour vector data is now stored in Supabase!")
        print("You can now run: python src/chatbot.py")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
