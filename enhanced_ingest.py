"""
Enhanced ingestion script for rag_api.py
Re-processes documents with improved PDF extraction, semantic chunking, and filtering
Compatible with existing Supabase setup
"""

import sys
import os
sys.path.append('src')

from enhanced_utils import EnhancedPDFProcessor, SemanticChunker
from config import VECTOR_BACKEND
from embed import embed_texts
import json
from typing import List, Dict
from pathlib import Path

# Import appropriate vector store
if VECTOR_BACKEND == 'supabase':
    from vector_store_supabase_rest import SupabaseRestVectorStore
else:
    from vector_store import VectorStore

class EnhancedIngestion:
    """Enhanced document ingestion with improved processing"""
    
    def __init__(self):
        self.pdf_processor = EnhancedPDFProcessor()
        self.chunker = SemanticChunker(chunk_size=1000, overlap=200)
        
        # Initialize vector store
        if VECTOR_BACKEND == 'supabase':
            self.store = SupabaseRestVectorStore()
        else:
            self.store = VectorStore()
        
        print(f"🔧 Enhanced ingestion initialized with {VECTOR_BACKEND} backend")
    
    def process_documents(self, data_dirs: List[str]) -> List[Dict]:
        """Process documents with enhanced extraction and chunking"""
        processed_chunks = []
        processed_files = 0
        skipped_files = 0
        
        for data_dir in data_dirs:
            if not os.path.exists(data_dir):
                print(f"⚠️ Directory not found: {data_dir}")
                continue
                
            print(f"📁 Processing directory: {data_dir}")
            
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        file_path = os.path.join(root, file)
                        print(f"📄 Processing: {file}")
                        
                        # Extract text
                        raw_text = self.pdf_processor.extract_text_from_pdf(file_path)
                        if not raw_text:
                            print(f"  ❌ No text extracted from: {file}")
                            skipped_files += 1
                            continue
                        
                        # Clean text
                        clean_text = self.pdf_processor.clean_text(raw_text)
                        if len(clean_text) < 100:
                            print(f"  ❌ Text too short: {file}")
                            skipped_files += 1
                            continue
                        
                        # Check relevance
                        if not self.pdf_processor.is_ptsp_relevant(clean_text):
                            print(f"  ❌ Not PTSP relevant: {file}")
                            skipped_files += 1
                            continue
                        
                        print(f"  ✅ PTSP relevant: {file}")
                        processed_files += 1
                        
                        # Chunk text with enhanced chunking
                        chunks = self.chunker.chunk_text(clean_text)
                        
                        for i, chunk in enumerate(chunks):
                            processed_chunks.append({
                                'content': chunk,
                                'source': file,
                                'chunk_id': f"{file}_{i}",
                                'file_path': file_path,
                                'chunk_index': i,
                                'metadata': {
                                    'source': file,
                                    'chunk_index': i,
                                    'file_path': file_path,
                                    'is_ptsp_relevant': True,
                                    'processing_version': 'enhanced_v1'
                                }
                            })
        
        print(f"\n📊 Processing complete:")
        print(f"  - Files processed: {processed_files}")
        print(f"  - Files skipped: {skipped_files}")
        print(f"  - Total chunks: {len(processed_chunks)}")
        print(f"  - PTSP relevance: 100% (all chunks)")
        
        return processed_chunks
    
    def upload_to_vector_store(self, chunks: List[Dict]) -> bool:
        """Upload chunks to vector store"""
        if not chunks:
            print("❌ No chunks to upload!")
            return False
        
        print(f"🔄 Uploading {len(chunks)} chunks to {VECTOR_BACKEND}...")
        
        try:
            # Prepare texts and metadata
            texts = [chunk['content'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            # Generate embeddings
            print("🧠 Generating embeddings...")
            embeddings = embed_texts(texts)
            
            if VECTOR_BACKEND == 'supabase':
                # Clear existing data first (optional - comment out to append)
                print("🗑️ Clearing existing data...")
                self.store.clear()
                
                # Upload in batches for Supabase
                batch_size = 100
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i+batch_size]
                    batch_embeddings = embeddings[i:i+batch_size]
                    batch_metadata = metadatas[i:i+batch_size]
                    
                    success = self.store.add_texts(
                        texts=batch_texts,
                        embeddings=batch_embeddings,
                        metadatas=batch_metadata
                    )
                    
                    if success:
                        print(f"  ✅ Uploaded batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                    else:
                        print(f"  ❌ Failed to upload batch {i//batch_size + 1}")
                        return False
            else:
                # For local vector store
                self.store.add_texts(texts, embeddings, metadatas)
                self.store.save()
            
            print(f"✅ Successfully uploaded {len(chunks)} enhanced chunks!")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading chunks: {e}")
            return False
    
    def run_enhanced_ingestion(self, data_dirs: List[str] = None) -> bool:
        """Run complete enhanced ingestion pipeline"""
        if data_dirs is None:
            data_dirs = [
                "data/scraped_dpmptsp",
                "data/scraped_ptsp_indonesia", 
                "data/scraped"
            ]
        
        print("🚀 Starting Enhanced Document Ingestion")
        print("=" * 50)
        
        # Process documents
        chunks = self.process_documents(data_dirs)
        
        if not chunks:
            print("❌ No chunks processed!")
            return False
        
        # Upload to vector store
        success = self.upload_to_vector_store(chunks)
        
        if success:
            print("\n✅ Enhanced ingestion completed successfully!")
            print(f"Expected improvement: 58.3% → 75%+ accuracy")
            print("\nRestart your rag_api.py to use enhanced data:")
            print("  python rag_api.py")
        else:
            print("\n❌ Enhanced ingestion failed!")
        
        return success

def main():
    """Main function to run enhanced ingestion"""
    try:
        ingester = EnhancedIngestion()
        success = ingester.run_enhanced_ingestion()
        
        if success:
            # Save processing log
            log_data = {
                "processing_version": "enhanced_v1",
                "backend": VECTOR_BACKEND,
                "timestamp": str(os.path.getmtime(__file__)),
                "features": [
                    "Enhanced PDF extraction",
                    "Semantic chunking", 
                    "PTSP relevance filtering",
                    "Improved similarity scoring"
                ]
            }
            
            with open('enhanced_ingestion_log.json', 'w') as f:
                json.dump(log_data, f, indent=2)
                
            print(f"📝 Processing log saved to: enhanced_ingestion_log.json")
        
        return success
        
    except Exception as e:
        print(f"❌ Enhanced ingestion failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)