"""
Advanced RAG Upgrade Path
Upgrade to better embedding models and hybrid search
"""
import os
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()

class AdvancedRAGUpgrade:
    """Tools for upgrading to better embeddings and hybrid search"""
    
    def __init__(self):
        self.current_dimensions = 384
        self.upgrade_options = {
            'bge-large-en-v1.5': {
                'dimensions': 1024,
                'model_name': 'BAAI/bge-large-en-v1.5',
                'description': 'Excellent for English + multilingual, state-of-the-art performance',
                'performance': '⭐⭐⭐⭐⭐'
            },
            'e5-large-v2': {
                'dimensions': 1024,
                'model_name': 'intfloat/e5-large-v2',
                'description': 'Strong general-purpose model, excellent retrieval',
                'performance': '⭐⭐⭐⭐⭐'
            },
            'multilingual-e5-large': {
                'dimensions': 1024,
                'model_name': 'intfloat/multilingual-e5-large',
                'description': 'Specialized for multilingual tasks (Indonesian + English)',
                'performance': '⭐⭐⭐⭐⭐'
            },
            'all-mpnet-base-v2': {
                'dimensions': 768,
                'model_name': 'sentence-transformers/all-mpnet-base-v2',
                'description': 'Good balance of performance and speed',
                'performance': '⭐⭐⭐⭐'
            }
        }
    
    def show_upgrade_options(self):
        """Display available embedding model upgrades"""
        print("🚀 **Advanced RAG Upgrade Options**")
        print("=" * 50)
        print(f"Current model: sentence-transformers/all-MiniLM-L6-v2 ({self.current_dimensions} dimensions)")
        print("\n📈 **Recommended Upgrades:**\n")
        
        for key, info in self.upgrade_options.items():
            print(f"**{key}**")
            print(f"  • Performance: {info['performance']}")
            print(f"  • Dimensions: {info['dimensions']}")
            print(f"  • Model: {info['model_name']}")
            print(f"  • Description: {info['description']}")
            print()
    
    def create_upgrade_script(self, model_choice: str):
        """Create upgrade script for chosen model"""
        if model_choice not in self.upgrade_options:
            print(f"❌ Unknown model: {model_choice}")
            return
        
        model_info = self.upgrade_options[model_choice]
        
        upgrade_script = f'''"""
Upgrade script for {model_choice}
This will upgrade your embeddings to {model_info['dimensions']} dimensions
"""
import os
import sys
import numpy as np
import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from pathlib import Path

sys.path.append('src')
from vector_store_supabase_rest import SupabaseRestVectorStore

def upgrade_embeddings():
    """Upgrade to {model_choice} embeddings"""
    print("🚀 Upgrading to {model_choice}")
    print("=" * 50)
    
    # Load the new model
    print("📥 Loading new embedding model...")
    model = SentenceTransformer('{model_info['model_name']}')
    print(f"✅ Loaded {model_choice} ({model_info['dimensions']} dimensions)")
    
    # Load existing text data
    metadata_file = "data/default_docs_meta.json"
    if not os.path.exists(metadata_file):
        print("❌ No existing data found. Please run ingestion first.")
        return False
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    texts = metadata['texts']
    meta_list = metadata['meta']
    
    print(f"📊 Found {{len(texts)}} texts to re-embed")
    
    # Generate new embeddings
    print("🔄 Generating new embeddings...")
    new_embeddings = []
    batch_size = 32
    
    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts[i:i + batch_size]
        batch_embeddings = model.encode(batch_texts, convert_to_numpy=True)
        new_embeddings.extend(batch_embeddings)
    
    new_embeddings = np.array(new_embeddings)
    print(f"✅ Generated {{len(new_embeddings)}} embeddings with {{new_embeddings.shape[1]}} dimensions")
    
    return new_embeddings, texts, meta_list

def update_supabase_schema():
    """Update Supabase table for new dimensions"""
    print("🔧 Updating Supabase schema...")
    
    # Create new table with updated dimensions
    create_table_sql = f"""
    -- Drop existing table (CAREFUL: This deletes all data!)
    DROP TABLE IF EXISTS rag_chunks_jateng_backup;
    ALTER TABLE rag_chunks_jateng RENAME TO rag_chunks_jateng_backup;
    
    -- Create new table with {model_info['dimensions']} dimensions
    CREATE TABLE rag_chunks_jateng (
        id BIGSERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        metadata JSONB DEFAULT '{{}}',
        embedding vector({model_info['dimensions']}),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Set up RLS and policies
    ALTER TABLE rag_chunks_jateng ENABLE ROW LEVEL SECURITY;
    CREATE POLICY "Allow all access" ON rag_chunks_jateng FOR ALL USING (true);
    
    -- Create index
    CREATE INDEX rag_chunks_jateng_embedding_idx 
    ON rag_chunks_jateng USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
    
    -- Update search function
    CREATE OR REPLACE FUNCTION match_chunks(
        query_embedding vector({model_info['dimensions']}),
        match_threshold float DEFAULT 0.1,
        match_count int DEFAULT 5
    )
    RETURNS TABLE (
        id bigint,
        content text,
        metadata jsonb,
        similarity float
    )
    LANGUAGE sql STABLE AS $$
    SELECT 
        rag_chunks_jateng.id,
        rag_chunks_jateng.content,
        rag_chunks_jateng.metadata,
        1 - (rag_chunks_jateng.embedding <=> query_embedding) AS similarity
    FROM rag_chunks_jateng
    WHERE 1 - (rag_chunks_jateng.embedding <=> query_embedding) > match_threshold
    ORDER BY rag_chunks_jateng.embedding <=> query_embedding
    LIMIT match_count;
    $$;
    """
    
    print("📋 SQL commands to run in Supabase:")
    print("=" * 40)
    print(create_table_sql)
    print("=" * 40)
    print("⚠️  IMPORTANT: Run this SQL in your Supabase SQL Editor BEFORE proceeding!")
    
    return create_table_sql

def migrate_upgraded_data():
    """Migrate data with new embeddings to Supabase"""
    print("🔄 Migrating upgraded data to Supabase...")
    
    # Generate new embeddings
    new_embeddings, texts, meta_list = upgrade_embeddings()
    
    if new_embeddings is None:
        return False
    
    # Initialize Supabase store
    store = SupabaseRestVectorStore()
    
    # Prepare chunks
    chunks = []
    for text, meta, embedding in zip(texts, meta_list, new_embeddings):
        chunk = {{
            'content': text,
            'metadata': meta,
            'embedding': embedding.tolist()
        }}
        chunks.append(chunk)
    
    # Upload in batches
    batch_size = 50
    total_uploaded = 0
    
    for i in tqdm(range(0, len(chunks), batch_size), desc="Uploading batches"):
        batch = chunks[i:i + batch_size]
        success = store.add_chunks(batch)
        
        if success:
            total_uploaded += len(batch)
        else:
            print(f"❌ Failed to upload batch {{i//batch_size + 1}}")
            return False
    
    print(f"✅ Successfully migrated {{total_uploaded}} chunks with {model_choice} embeddings!")
    return True

def update_config():
    """Update configuration to use new model"""
    env_file = ".env"
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Update embedding model
        content = content.replace(
            'EMB_MODEL = sentence-transformers/all-MiniLM-L6-v2',
            'EMB_MODEL = {model_info['model_name']}'
        )
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Updated .env configuration")
        
    except Exception as e:
        print(f"❌ Error updating config: {{e}}")

if __name__ == "__main__":
    print("🚀 {model_choice} Upgrade Process")
    print("=" * 50)
    
    print("Step 1: Update Supabase schema")
    sql_commands = update_supabase_schema()
    
    input("\\nPress Enter after running the SQL commands in Supabase...")
    
    print("\\nStep 2: Migrate data with new embeddings")
    success = migrate_upgraded_data()
    
    if success:
        print("\\nStep 3: Update configuration")
        update_config()
        
        print("\\n🎉 Upgrade complete!")
        print(f"Your RAG system now uses {model_choice} with {model_info['dimensions']} dimensions!")
        print("\\nTo test: python enhanced_rag.py \\"Your question here\\"")
    else:
        print("\\n❌ Upgrade failed. Check errors above.")
'''
        
        filename = f"upgrade_to_{model_choice.replace('-', '_')}.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(upgrade_script)
        
        print(f"✅ Created upgrade script: {filename}")
        print(f"📋 Run: python {filename}")

def main():
    upgrade_tool = AdvancedRAGUpgrade()
    
    print("🔍 **RAG Accuracy Improvement Options**")
    print("=" * 50)
    
    print("✅ **Immediate Improvements** (Already implemented):")
    print("  • Enhanced prompting and context formatting")
    print("  • Query expansion and preprocessing") 
    print("  • Cross-encoder reranking")
    print("  • Better metadata usage")
    print("  • Improved similarity filtering")
    print()
    
    print("🚀 **Advanced Upgrades** (Optional):")
    upgrade_tool.show_upgrade_options()
    
    print("💡 **Recommendation:**")
    print("For Indonesian government data, 'multilingual-e5-large' would be ideal")
    print("as it handles both Indonesian and English text excellently.")
    print()
    
    choice = input("Enter model name to create upgrade script (or 'skip'): ").strip()
    
    if choice.lower() != 'skip' and choice in upgrade_tool.upgrade_options:
        upgrade_tool.create_upgrade_script(choice)
        print()
        print("📋 **Upgrade Steps:**")
        print("1. Run the generated upgrade script")
        print("2. Execute SQL commands in Supabase SQL Editor")
        print("3. Let script migrate your data")
        print("4. Test with enhanced_rag.py")
    elif choice.lower() != 'skip':
        print("❌ Invalid choice. Run again to try different model.")

if __name__ == "__main__":
    main()
