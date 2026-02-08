#!/usr/bin/env python3
"""
Enhanced cleaning and ingestion script - removes separators and metadata.
Only keeps actual text content (questions and answers).
"""
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

sys.path.append('src')
from vector_store_supabase_rest import SupabaseRestVectorStore
from embed import embed_texts

def clean_text_content(text):
    """
    Remove all separators, metadata, and formatting lines.
    Keep only actual question and answer text.
    """
    # Remove separator lines (================)
    text = re.sub(r'^=+$', '', text, flags=re.MULTILINE)
    
    # Remove metadata lines
    text = re.sub(r'^Title:.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^Source:.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^Scraped:.*$', '', text, flags=re.MULTILINE)
    
    # Remove label lines (QUESTION:, ANSWER:)
    text = re.sub(r'^QUESTION:\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^ANSWER:\s*$', '', text, flags=re.MULTILINE)
    
    # Remove image URL sections
    text = re.sub(r'Image URLs?:.*?(?=\n\n|\Z)', '', text, flags=re.DOTALL)
    
    # Remove multiple blank lines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def clean_guide_text(text):
    """Clean guide-specific formatting issues."""
    # Fix duplicate step numbers (e.g., "1. 1." -> "1.")
    text = re.sub(r'^(\d+)\.\s+\1\.\s+', r'\1. ', text, flags=re.MULTILINE)
    
    # Fix missing spaces in camelCase (e.g., "klikMASUK" -> "klik MASUK")
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Fix specific common concatenations
    text = text.replace('Kunjungihttps', 'Kunjungi https')
    text = text.replace('Masukke', 'Masuk ke')
    
    return text

def extract_title_from_file(filepath):
    """Extract title from file content or filename."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Try to extract from Title: line
            title_match = re.search(r'^Title:\s*(.+)$', content, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip()
    except:
        pass
    
    # Fallback to filename
    return Path(filepath).stem

def extract_url_from_file(filepath):
    """Extract source URL from file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            url_match = re.search(r'^Source:\s*(.+)$', content, re.MULTILINE)
            if url_match:
                return url_match.group(1).strip()
    except:
        pass
    return None

def chunk_document(text, doc_type, chunk_size=800, overlap=100):
    """Split document into chunks."""
    if doc_type == "guides":
        # For guides, try to split by steps
        step_pattern = r'\n(?=\d+\.\s+)'
        steps = re.split(step_pattern, text)
        
        chunks = []
        current_chunk = ""
        
        for step in steps:
            step = step.strip()
            if not step:
                continue
            
            if len(current_chunk) + len(step) < chunk_size:
                current_chunk += "\n\n" + step if current_chunk else step
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = step
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]
    
    else:
        # For FAQ and investment, use sliding window
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks if chunks else [text]

def process_folder(folder_path, folder_name):
    """Process all .txt files in a folder."""
    documents = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"[WARN]  Folder not found: {folder_path}")
        return documents
    
    txt_files = list(folder.glob('**/*.txt'))
    print(f"\n[FILE] Processing {folder_name}...")
    
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # Extract metadata before cleaning
            title = extract_title_from_file(file_path)
            url = extract_url_from_file(file_path)
            
            # Clean the content
            cleaned_content = clean_text_content(raw_content)
            
            # Apply guide-specific cleaning if needed
            if folder_name == "guides":
                cleaned_content = clean_guide_text(cleaned_content)
            
            if not cleaned_content.strip():
                print(f"[WARN]  Empty after cleaning: {file_path.name}")
                continue
            
            documents.append({
                'content': cleaned_content,
                'filename': file_path.name,
                'title': title,
                'url': url,
                'type': folder_name
            })
            
        except Exception as e:
            print(f"[FAIL] Error processing {file_path.name}: {e}")
    
    print(f"[OK] Processed {len(documents)} documents from {folder_name}")
    return documents

def main():
    print("\n" + "="*70)
    print(" ENHANCED DATA CLEANING & INGESTION")
    print("="*70)
    
    # Step 1: Read documents from all folders
    print("\n Step 1: Reading documents...")
    
    base_path = Path('data/data_oss')
    
    all_documents = []
    all_documents.extend(process_folder(base_path / 'faq', 'faq'))
    all_documents.extend(process_folder(base_path / 'investment_guides', 'investment'))
    all_documents.extend(process_folder(base_path / 'guides', 'guides'))
    
    print(f"\n[STATS] Total documents: {len(all_documents)}")
    
    if not all_documents:
        print("[FAIL] No documents to process!")
        return
    
    # Step 2: Chunk documents
    print("\n Step 2: Chunking documents...")
    
    all_chunks = []
    for doc in all_documents:
        chunks = chunk_document(doc['content'], doc['type'])
        
        for chunk in chunks:
            all_chunks.append({
                'content': chunk,
                'metadata': {
                    'source': doc['filename'],
                    'title': doc['title'],
                    'url': doc['url'],
                    'type': doc['type']
                }
            })
    
    print(f" Created {len(all_chunks)} chunks")
    
    # Calculate statistics
    chunk_sizes = [len(chunk['content']) for chunk in all_chunks]
    print(f"Chunk size stats: Min: {min(chunk_sizes)} chars, Max: {max(chunk_sizes)} chars, Avg: {sum(chunk_sizes)//len(chunk_sizes)} chars")
    
    # Step 3: Save preview
    print("\n Step 3: Saving preview...")
    
    preview = {
        'total_documents': len(all_documents),
        'total_chunks': len(all_chunks),
        'breakdown': {
            'faq': len([d for d in all_documents if d['type'] == 'faq']),
            'investment': len([d for d in all_documents if d['type'] == 'investment']),
            'guides': len([d for d in all_documents if d['type'] == 'guides'])
        },
        'chunk_stats': {
            'min': min(chunk_sizes),
            'max': max(chunk_sizes),
            'avg': sum(chunk_sizes)//len(chunk_sizes)
        },
        'sample_chunks': [
            {
                'content': chunk['content'][:300] + '...' if len(chunk['content']) > 300 else chunk['content'],
                'metadata': chunk['metadata']
            }
            for chunk in all_chunks[:10]
        ]
    }
    
    with open('data/cleaned_chunks_preview.json', 'w', encoding='utf-8') as f:
        json.dump(preview, f, indent=2, ensure_ascii=False)
    
    print("[SAVE] Preview saved to: data/cleaned_chunks_preview.json")
    
    # Step 4: Embed and ingest to Supabase
    print("\n Step 4: Embedding and ingesting to Supabase...")
    
    store = SupabaseRestVectorStore()
    
    # Process in batches
    batch_size = 50
    total_batches = (len(all_chunks) + batch_size - 1) // batch_size
    
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        batch_num = i // batch_size + 1
        
        print(f" Processing batch {batch_num}/{total_batches}...")
        
        # Extract content for embedding
        texts = [chunk['content'] for chunk in batch]
        
        # Generate embeddings
        embeddings = embed_texts(texts)
        
        # Prepare chunks for storage
        chunks_to_store = [
            {
                'content': chunk['content'],
                'embedding': emb if isinstance(emb, list) else emb.tolist(),
                'metadata': chunk['metadata']
            }
            for chunk, emb in zip(batch, embeddings)
        ]
        
        # Store in Supabase
        store.add_chunks(chunks_to_store)
    
    print(f"\n[OK] Successfully ingested {len(all_chunks)} chunks to Supabase!")
    print("="*70)

if __name__ == '__main__':
    main()
