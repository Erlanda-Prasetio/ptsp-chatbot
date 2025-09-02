"""
Batch ingest script with CUDA GPU acceleration for embeddings
Processes all files in data/scraped/ directory efficiently
"""
import os
import sys
import glob
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import torch

sys.path.append('src')

from vector_store_supabase_rest import SupabaseRestVectorStore
from chunk import chunk_text
from embed import embed_texts
import pandas as pd
import PyPDF2
import json

# Check CUDA availability
print(f"🔥 CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"🚀 GPU: {torch.cuda.get_device_name()}")
    print(f"📊 Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# Force GPU embeddings
os.environ['USE_LOCAL_EMBEDDINGS'] = 'true'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Use first GPU

class BatchIngestor:
    def __init__(self):
        self.store = SupabaseRestVectorStore()
        self.total_chunks = 0
        self.processed_files = 0
        self.failed_files = []
        
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
                # Convert DataFrame to readable text
                text_parts = []
                text_parts.append(f"Dataset: {Path(file_path).name}")
                text_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
                text_parts.append(f"Total Records: {len(df)}")
                text_parts.append("\nData Summary:")
                
                # Add first few rows as examples
                for idx, row in df.head(20).iterrows():
                    row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                    text_parts.append(f"Record {idx + 1}: {row_text}")
                
                # Add column statistics for numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    text_parts.append("\nStatistical Summary:")
                    for col in numeric_cols:
                        stats = df[col].describe()
                        text_parts.append(f"{col}: Min={stats['min']}, Max={stats['max']}, Mean={stats['mean']:.2f}")
                
                return "\n".join(text_parts)
                
            elif file_ext == '.pdf':
                text_parts = []
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text_parts.append(f"Document: {Path(file_path).name}")
                    text_parts.append(f"Total Pages: {len(reader.pages)}")
                    
                    for page_num, page in enumerate(reader.pages[:10]):  # First 10 pages
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_parts.append(f"\nPage {page_num + 1}:\n{page_text}")
                
                return "\n".join(text_parts)
                
            elif file_ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
                # Similar processing as CSV
                text_parts = []
                text_parts.append(f"Spreadsheet: {Path(file_path).name}")
                text_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
                text_parts.append(f"Total Records: {len(df)}")
                
                for idx, row in df.head(15).iterrows():
                    row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                    text_parts.append(f"Record {idx + 1}: {row_text}")
                
                return "\n".join(text_parts)
                
            elif file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return f"JSON Document: {Path(file_path).name}\n{json.dumps(data, indent=2, ensure_ascii=False)}"
                
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f"Text Document: {Path(file_path).name}\n{f.read()}"
                    
            else:
                print(f"⚠️  Unsupported file type: {file_ext}")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting from {file_path}: {e}")
            return None
    
    def process_file(self, file_path: str) -> int:
        """Process a single file and return number of chunks created"""
        try:
            print(f"📄 Processing: {Path(file_path).name}")
            
            # Extract text
            text = self.extract_text_from_file(file_path)
            if not text or len(text.strip()) < 50:
                print(f"⚠️  Skipping {file_path}: insufficient text content")
                return 0
            
            # Create chunks
            chunks = chunk_text(text)
            if not chunks:
                print(f"⚠️  No chunks created for {file_path}")
                return 0
            
            print(f"✂️  Created {len(chunks)} chunks from {Path(file_path).name}")
            
            # Prepare metadata
            metadata = {
                'source': str(file_path),
                'filename': Path(file_path).name,
                'file_type': Path(file_path).suffix.lower(),
                'chunk_count': len(chunks)
            }
            
            # Create embeddings in batches for GPU efficiency
            batch_size = 32  # Optimal for most GPUs
            all_chunk_data = []
            
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i + batch_size]
                print(f"🔮 Embedding batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1} ({len(batch_chunks)} chunks)")
                
                # Generate embeddings
                embeddings = embed_texts(batch_chunks)
                
                # Prepare chunk data
                for j, (chunk, embedding) in enumerate(zip(batch_chunks, embeddings)):
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_index'] = i + j
                    
                    all_chunk_data.append({
                        'content': chunk,
                        'embedding': embedding,
                        'metadata': chunk_metadata
                    })
            
            # Store all chunks for this file
            success = self.store.add_chunks(all_chunk_data)
            if success:
                print(f"✅ Stored {len(all_chunk_data)} chunks for {Path(file_path).name}")
                return len(all_chunk_data)
            else:
                print(f"❌ Failed to store chunks for {Path(file_path).name}")
                return 0
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            self.failed_files.append(file_path)
            return 0
    
    def ingest_directory(self, directory: str, max_workers: int = 2):
        """Ingest all supported files in directory"""
        print(f"🚀 Starting batch ingest from: {directory}")
        print(f"👥 Using {max_workers} parallel workers")
        
        # Find all supported files
        patterns = ['*.csv', '*.pdf', '*.xls', '*.xlsx', '*.json', '*.txt']
        files = []
        
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(directory, pattern)))
        
        if not files:
            print(f"❌ No supported files found in {directory}")
            return
        
        print(f"📁 Found {len(files)} files to process")
        
        start_time = time.time()
        
        # Process files with controlled parallelism (avoid GPU memory issues)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(self.process_file, file_path): file_path 
                            for file_path in files}
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    chunks_added = future.result()
                    self.total_chunks += chunks_added
                    self.processed_files += 1
                    
                    # Progress update
                    progress = (self.processed_files / len(files)) * 100
                    print(f"📊 Progress: {progress:.1f}% ({self.processed_files}/{len(files)} files, {self.total_chunks} total chunks)")
                    
                except Exception as e:
                    print(f"❌ Error processing {file_path}: {e}")
                    self.failed_files.append(file_path)
        
        elapsed = time.time() - start_time
        
        # Final summary
        print("\n" + "="*60)
        print("🎉 BATCH INGEST COMPLETE")
        print("="*60)
        print(f"⏱️  Total Time: {elapsed:.1f} seconds")
        print(f"📄 Files Processed: {self.processed_files}/{len(files)}")
        print(f"📦 Total Chunks Created: {self.total_chunks}")
        print(f"🚀 Average Speed: {self.total_chunks/elapsed:.1f} chunks/second")
        
        if self.failed_files:
            print(f"\n❌ Failed Files ({len(self.failed_files)}):")
            for failed_file in self.failed_files:
                print(f"  - {failed_file}")
        
        # Check final database count
        try:
            db_count = self.store.get_count()
            print(f"\n📊 Database now contains: {db_count} total chunks")
        except Exception as e:
            print(f"⚠️  Could not verify database count: {e}")

def main():
    print("🔥 GPU-Accelerated Batch Ingestor for Central Java RAG")
    print("="*60)
    
    # Check if data directory exists
    data_dir = "data/scraped"
    if not os.path.exists(data_dir):
        print(f"❌ Directory not found: {data_dir}")
        return
    
    # Initialize and run
    ingestor = BatchIngestor()
    
    # Use 2 workers to balance speed vs GPU memory
    max_workers = 2 if torch.cuda.is_available() else 1
    
    ingestor.ingest_directory(data_dir, max_workers=max_workers)
    
    print("\n🎯 Ready for enhanced RAG queries!")
    print("💡 Restart your rag_api.py to use the updated dataset")

if __name__ == "__main__":
    main()
