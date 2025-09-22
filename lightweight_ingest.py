"""
Lightweight enhanced ingestion for existing rag_api.py
Uses current processing but adds better filtering and chunk quality
"""

import sys
import os
sys.path.append('src')

from config import VECTOR_BACKEND
from embed import embed_texts
import json
import re
from typing import List, Dict

# Import appropriate vector store
if VECTOR_BACKEND == 'supabase':
    from vector_store_supabase_rest import SupabaseRestVectorStore
else:
    from vector_store import VectorStore

class LightweightEnhancedIngestion:
    """Lightweight document re-processing with better filtering"""
    
    def __init__(self):
        # Initialize vector store
        if VECTOR_BACKEND == 'supabase':
            self.store = SupabaseRestVectorStore()
        else:
            self.store = VectorStore()
        
        # PTSP relevance keywords
        self.ptsp_keywords = [
            'izin', 'perizinan', 'ptsp', 'investasi', 'usaha', 'modal', 
            'dpmptsp', 'pelayanan terpadu', 'satu pintu', 'oss',
            'permohonan', 'persyaratan', 'prosedur', 'syarat',
            'penanaman modal', 'bisnis', 'komersial', 'jawa tengah'
        ]
        
        print(f"🔧 Lightweight enhanced ingestion initialized with {VECTOR_BACKEND} backend")
    
    def is_ptsp_relevant(self, text: str) -> bool:
        """Check if text is relevant to PTSP services"""
        text_lower = text.lower()
        
        # Count keyword matches
        keyword_count = sum(1 for keyword in self.ptsp_keywords if keyword in text_lower)
        
        # Check for specific patterns
        has_license_content = any(pattern in text_lower for pattern in [
            'permohonan izin', 'syarat izin', 'prosedur izin',
            'pelayanan terpadu', 'satu pintu', 'investasi',
            'penanaman modal', 'oss'
        ])
        
        # Exclude irrelevant content
        is_irrelevant = any(pattern in text_lower for pattern in [
            'kelahiran', 'kematian', 'nikah', 'cerai',
            'kesehatan', 'rumah sakit', 'puskesmas',
            'neraca', 'laporan keuangan', 'anggaran'
        ])
        
        return (keyword_count >= 2 or has_license_content) and not is_irrelevant
    
    def clean_chunk_text(self, text: str) -> str:
        """Clean chunk text for better quality"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove page numbers and headers
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        
        # Remove table artifacts
        text = re.sub(r'Unnamed:\s*\d+.*?NaN', '', text)
        text = re.sub(r'\.{3,}', '...', text)
        
        # Fix common OCR issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'(\d+)([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'([A-Za-z])(\d+)', r'\1 \2', text)
        
        return text.strip()
    
    def get_existing_chunks(self) -> List[Dict]:
        """Get existing chunks from vector store"""
        print("📥 Retrieving existing chunks from vector store...")
        
        try:
            if VECTOR_BACKEND == 'supabase':
                # For Supabase, we'll do a broad search to get many chunks
                dummy_embedding = embed_texts(["sample query"])[0]
                all_chunks = self.store.search(dummy_embedding, top_k=10000)  # Get many chunks
                
                # Convert to standard format
                chunks = []
                for i, chunk in enumerate(all_chunks):
                    chunks.append({
                        'content': chunk.get('content', ''),
                        'metadata': chunk.get('metadata', {}),
                        'source': chunk.get('metadata', {}).get('source', f'chunk_{i}'),
                        'similarity': chunk.get('similarity', 0)
                    })
                
                print(f"📊 Retrieved {len(chunks)} chunks from Supabase")
                return chunks
            else:
                # For local store
                if hasattr(self.store, 'texts') and self.store.texts:
                    chunks = []
                    for i, text in enumerate(self.store.texts):
                        chunks.append({
                            'content': text,
                            'metadata': self.store.metadatas[i] if hasattr(self.store, 'metadatas') else {},
                            'source': f'chunk_{i}'
                        })
                    print(f"📊 Retrieved {len(chunks)} chunks from local store")
                    return chunks
                else:
                    print("❌ No chunks found in local store")
                    return []
                    
        except Exception as e:
            print(f"❌ Error retrieving chunks: {e}")
            return []
    
    def filter_and_enhance_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Filter existing chunks for PTSP relevance and enhance quality"""
        enhanced_chunks = []
        relevant_count = 0
        cleaned_count = 0
        
        print("🔍 Filtering and enhancing chunks...")
        
        for i, chunk in enumerate(chunks):
            content = chunk.get('content', '')
            
            if len(content) < 50:  # Skip very short chunks
                continue
            
            # Check PTSP relevance
            if not self.is_ptsp_relevant(content):
                continue
            
            relevant_count += 1
            
            # Clean the content
            cleaned_content = self.clean_chunk_text(content)
            
            if len(cleaned_content) < 100:  # Skip chunks that become too short
                continue
            
            cleaned_count += 1
            
            # Create enhanced chunk
            enhanced_chunk = {
                'content': cleaned_content,
                'metadata': {
                    **chunk.get('metadata', {}),
                    'is_ptsp_relevant': True,
                    'processing_version': 'lightweight_enhanced_v1',
                    'quality_score': len(cleaned_content) / len(content),  # Measure of cleaning effect
                    'original_source': chunk.get('source', f'chunk_{i}')
                }
            }
            
            enhanced_chunks.append(enhanced_chunk)
        
        print(f"📊 Enhancement results:")
        print(f"  - Original chunks: {len(chunks)}")
        print(f"  - PTSP relevant: {relevant_count}")
        print(f"  - High quality after cleaning: {cleaned_count}")
        print(f"  - Improvement ratio: {(cleaned_count/len(chunks)*100):.1f}%")
        
        return enhanced_chunks
    
    def upload_enhanced_chunks(self, chunks: List[Dict]) -> bool:
        """Upload enhanced chunks back to vector store"""
        if not chunks:
            print("❌ No enhanced chunks to upload!")
            return False
        
        print(f"🔄 Uploading {len(chunks)} enhanced chunks...")
        
        try:
            # Prepare texts and metadata
            texts = [chunk['content'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            
            # Generate embeddings
            print("🧠 Generating embeddings for enhanced chunks...")
            embeddings = embed_texts(texts)
            
            if VECTOR_BACKEND == 'supabase':
                # Clear existing data first
                print("🗑️ Clearing existing data...")
                self.store.clear()
                
                # Upload in batches
                batch_size = 100
                total_batches = (len(texts) + batch_size - 1) // batch_size
                
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i+batch_size]
                    batch_embeddings = embeddings[i:i+batch_size]
                    batch_metadata = metadatas[i:i+batch_size]
                    
                    success = self.store.add_texts(
                        texts=batch_texts,
                        embeddings=batch_embeddings,
                        metadatas=batch_metadata
                    )
                    
                    batch_num = i//batch_size + 1
                    if success:
                        print(f"  ✅ Uploaded batch {batch_num}/{total_batches}")
                    else:
                        print(f"  ❌ Failed to upload batch {batch_num}")
                        return False
            else:
                # For local vector store
                self.store.add_texts(texts, embeddings, metadatas)
                self.store.save()
            
            print(f"✅ Successfully uploaded {len(chunks)} enhanced chunks!")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading enhanced chunks: {e}")
            return False
    
    def run_lightweight_enhancement(self) -> bool:
        """Run complete lightweight enhancement pipeline"""
        print("🚀 Starting Lightweight Enhanced Ingestion")
        print("=" * 50)
        
        # Get existing chunks
        existing_chunks = self.get_existing_chunks()
        
        if not existing_chunks:
            print("❌ No existing chunks found!")
            return False
        
        # Filter and enhance
        enhanced_chunks = self.filter_and_enhance_chunks(existing_chunks)
        
        if not enhanced_chunks:
            print("❌ No chunks passed enhancement filters!")
            return False
        
        # Upload enhanced chunks
        success = self.upload_enhanced_chunks(enhanced_chunks)
        
        if success:
            print("\n✅ Lightweight enhancement completed successfully!")
            print(f"Quality improvement: Better filtering + text cleaning")
            print(f"PTSP relevance: 100% (all chunks now relevant)")
            print("\nYour rag_api.py will now use enhanced data!")
        else:
            print("\n❌ Lightweight enhancement failed!")
        
        return success

def main():
    """Main function to run lightweight enhancement"""
    try:
        ingester = LightweightEnhancedIngestion()
        success = ingester.run_lightweight_enhancement()
        
        if success:
            # Save processing log
            log_data = {
                "processing_version": "lightweight_enhanced_v1",
                "backend": VECTOR_BACKEND,
                "features": [
                    "PTSP relevance filtering",
                    "Text cleaning and OCR fixes",
                    "Quality-based chunk filtering",
                    "Enhanced metadata"
                ],
                "expected_improvement": "Better chunk quality and 100% PTSP relevance"
            }
            
            with open('lightweight_enhancement_log.json', 'w') as f:
                json.dump(log_data, f, indent=2)
                
            print(f"📝 Enhancement log saved to: lightweight_enhancement_log.json")
        
        return success
        
    except Exception as e:
        print(f"❌ Lightweight enhancement failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)