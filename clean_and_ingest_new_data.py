"""
Clean guides data and ingest all new OSS data (FAQ, Investment, Guides) into Supabase
"""
import os
import re
from pathlib import Path
from typing import List, Dict
import json

def clean_guide_text(text: str) -> str:
    """
    Clean guide text by:
    1. Fixing missing spaces between concatenated words
    2. Removing duplicate step numbers
    3. Removing image section
    4. Normalizing step format
    """
    lines = text.split('\n')
    
    # Find where actual steps start (after metadata)
    step_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith(''):
            step_start = i + 1
            break
    
    # Find where images section starts
    image_start = len(lines)
    for i, line in enumerate(lines):
        if 'IMAGES' in line or line.strip().startswith('') and i > step_start + 5:
            image_start = i
            break
    
    # Extract metadata and steps
    metadata = '\n'.join(lines[:step_start]).strip()
    step_lines = lines[step_start:image_start]
    
    cleaned_steps = []
    for line in step_lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove duplicate step numbers like "1. 1." -> "1."
        line = re.sub(r'^(\d+)\.\s+\1\.\s+', r'\1. ', line)
        
        # Fix common concatenations (add space before capital letters and common words)
        line = re.sub(r'([a-z])([A-Z])', r'\1 \2', line)  # camelCase -> camel Case
        line = re.sub(r'(https?://[^\s,]+)(,)', r'\1 \2', line)  # URL,word -> URL, word
        line = re.sub(r'(\w)(klik)', r'\1 klik', line, flags=re.IGNORECASE)  # wordklik -> word klik
        line = re.sub(r'(klik)([A-Z])', r'\1 \2', line)  # klikWORD -> klik WORD
        line = re.sub(r'(\w)(menu)', r'\1 menu', line, flags=re.IGNORECASE)  # wordmenu -> word menu
        line = re.sub(r'(tombol)([A-Z])', r'\1 \2', line)  # tombolWORD -> tombol WORD
        
        # Fix specific patterns
        line = line.replace('Kunjungihttps', 'Kunjungi https')
        line = line.replace('klikMASUK', 'klik MASUK')
        line = line.replace('menuPENJADWALAN', 'menu PENJADWALAN')
        line = line.replace('tombolMASUK', 'tombol MASUK')
        line = line.replace('untukmelanjutkan', 'untuk melanjutkan')
        line = line.replace('untukuntuk', 'untuk')
        line = line.replace('dapatmelihat', 'dapat melihat')
        
        cleaned_steps.append(line)
    
    # Reconstruct document
    result = metadata + '\n\n' + '\n'.join(cleaned_steps)
    return result.strip()


def read_txt_file(file_path: Path) -> Dict[str, str]:
    """Read and parse a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata
        title = ""
        source = ""
        
        if "Title:" in content:
            title_match = re.search(r'Title:\s*(.+?)(?:\n|Source:)', content)
            if title_match:
                title = title_match.group(1).strip()
        
        if "Source:" in content or "SOURCE:" in content:
            source_match = re.search(r'[Ss][Oo][Uu][Rr][Cc][Ee]:\s*(.+?)(?:\n|$)', content)
            if source_match:
                source = source_match.group(1).strip()
        
        # Use filename as fallback title
        if not title:
            title = file_path.stem
        
        return {
            'filename': file_path.name,
            'title': title,
            'content': content,
            'source': source,
            'file_type': 'txt'
        }
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def process_folder(folder_path: Path, clean_guides: bool = False) -> List[Dict]:
    """Process all txt files in a folder"""
    documents = []
    txt_files = list(folder_path.rglob('*.txt'))
    
    print(f"\nProcessing {len(txt_files)} files from {folder_path.name}...")
    
    for i, file_path in enumerate(txt_files, 1):
        if i % 50 == 0:
            print(f"  Processed {i}/{len(txt_files)} files...")
        
        doc = read_txt_file(file_path)
        if doc:
            # Clean guides content
            if clean_guides and 'guides' in str(folder_path).lower():
                doc['content'] = clean_guide_text(doc['content'])
                doc['cleaned'] = True
            else:
                doc['cleaned'] = False
            
            documents.append(doc)
    
    print(f"[OK] Processed {len(documents)} documents from {folder_path.name}")
    return documents


def chunk_document(doc: Dict, chunk_size: int = 800, overlap: int = 100) -> List[Dict]:
    """
    Split document into semantic chunks
    For step-by-step guides, try to keep steps together
    """
    content = doc['content']
    chunks = []
    
    # For guides with numbered steps, split by steps
    if 'guides' in doc.get('filename', '').lower() or re.search(r'^\d+\.', content, re.MULTILINE):
        # Split by step numbers
        step_pattern = r'(?=\d+\.\s+)'
        steps = re.split(step_pattern, content)
        
        current_chunk = ""
        for step in steps:
            step = step.strip()
            if not step:
                continue
            
            # If adding this step exceeds chunk_size, save current chunk
            if len(current_chunk) + len(step) > chunk_size and current_chunk:
                chunks.append({
                    'content': current_chunk.strip(),
                    'metadata': {
                        'source': doc['filename'],
                        'title': doc.get('title', ''),
                        'url': doc.get('source', ''),
                        'type': 'guide_steps'
                    }
                })
                # Start new chunk with overlap (last part of previous chunk)
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + '\n\n' + step
            else:
                current_chunk += '\n\n' + step if current_chunk else step
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'metadata': {
                    'source': doc['filename'],
                    'title': doc.get('title', ''),
                    'url': doc.get('source', ''),
                    'type': 'guide_steps'
                }
            })
    else:
        # For FAQ and investment guides, use simple sliding window
        words = content.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1
            
            if current_size >= chunk_size:
                chunks.append({
                    'content': ' '.join(current_chunk),
                    'metadata': {
                        'source': doc['filename'],
                        'title': doc.get('title', ''),
                        'url': doc.get('source', ''),
                        'type': 'faq' if 'faq' in doc['filename'].lower() else 'investment'
                    }
                })
                # Overlap: keep last N words
                overlap_words = int(overlap / 5)  # Rough estimate
                current_chunk = current_chunk[-overlap_words:]
                current_size = sum(len(w) + 1 for w in current_chunk)
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'content': ' '.join(current_chunk),
                'metadata': {
                    'source': doc['filename'],
                    'title': doc.get('title', ''),
                    'url': doc.get('source', ''),
                    'type': 'faq' if 'faq' in doc['filename'].lower() else 'investment'
                }
            })
    
    return chunks


def main():
    """Main ingestion workflow"""
    print("="*80)
    print("[START] CLEANING AND INGESTING NEW OSS DATA")
    print("="*80)
    
    # Paths
    data_oss_path = Path('data/data_oss')
    faq_path = data_oss_path / 'faq'
    guides_path = data_oss_path / 'guides'
    investment_path = data_oss_path / 'investment_guides'
    
    # Step 1: Process all folders
    print("\n[DIR] Step 1: Reading documents...")
    
    faq_docs = process_folder(faq_path, clean_guides=False)
    investment_docs = process_folder(investment_path, clean_guides=False)
    guides_docs = process_folder(guides_path, clean_guides=True)
    
    all_docs = faq_docs + investment_docs + guides_docs
    print(f"\n[STATS] Total documents: {len(all_docs)}")
    print(f"   - FAQ: {len(faq_docs)}")
    print(f"   - Investment: {len(investment_docs)}")
    print(f"   - Guides (cleaned): {len(guides_docs)}")
    
    # Step 2: Chunk documents
    print("\n  Step 2: Chunking documents...")
    all_chunks = []
    for doc in all_docs:
        doc_chunks = chunk_document(doc, chunk_size=800, overlap=100)
        all_chunks.extend(doc_chunks)
    
    print(f"[OK] Created {len(all_chunks)} chunks")
    
    # Step 3: Save for review
    output_file = 'data/new_oss_chunks_preview.json'
    print(f"\n[SAVE] Step 3: Saving preview to {output_file}...")
    
    preview_data = {
        'total_documents': len(all_docs),
        'total_chunks': len(all_chunks),
        'breakdown': {
            'faq': len(faq_docs),
            'investment': len(investment_docs),
            'guides': len(guides_docs)
        },
        'sample_chunks': all_chunks[:10],  # First 10 chunks
        'chunk_size_stats': {
            'min': min(len(c['content']) for c in all_chunks),
            'max': max(len(c['content']) for c in all_chunks),
            'avg': sum(len(c['content']) for c in all_chunks) // len(all_chunks)
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(preview_data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Preview saved!")
    print(f"\nChunk size stats:")
    print(f"   Min: {preview_data['chunk_size_stats']['min']} chars")
    print(f"   Max: {preview_data['chunk_size_stats']['max']} chars")
    print(f"   Avg: {preview_data['chunk_size_stats']['avg']} chars")
    
    # Step 4: Embed and ingest to Supabase
    print("\n Step 4: Embedding and ingesting to Supabase...")
    print("This will take a while for 496 documents...")
    
    try:
        import sys
        sys.path.append('src')
        from embed import embed_texts
        from vector_store_supabase_rest import SupabaseRestVectorStore
        
        # Initialize store
        store = SupabaseRestVectorStore()
        
        # Prepare chunks for ingestion
        chunks_to_ingest = []
        batch_size = 50
        
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i+batch_size]
            print(f"  Processing batch {i//batch_size + 1}/{(len(all_chunks)-1)//batch_size + 1}...")
            
            # Extract texts
            texts = [chunk['content'] for chunk in batch]
            
            # Embed texts
            embeddings = embed_texts(texts)
            
            # Prepare for Supabase
            for chunk, embedding in zip(batch, embeddings):
                chunks_to_ingest.append({
                    'content': chunk['content'],
                    'metadata': chunk['metadata'],
                    'embedding': embedding
                })
            
            # Ingest batch
            if len(chunks_to_ingest) >= 100:
                print(f"    Ingesting {len(chunks_to_ingest)} chunks...")
                store.add_chunks(chunks_to_ingest)
                chunks_to_ingest = []
        
        # Ingest remaining
        if chunks_to_ingest:
            print(f"    Ingesting final {len(chunks_to_ingest)} chunks...")
            store.add_chunks(chunks_to_ingest)
        
        print("\n[OK] INGESTION COMPLETE!")
        print(f"   Total chunks ingested: {len(all_chunks)}")
        print(f"   Ready for Experiment 2 evaluation!")
        
    except Exception as e:
        print(f"\n[FAIL] Error during ingestion: {e}")
        print("Chunks are saved in preview file for manual inspection")
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    if success:
        print("\n" + "="*80)
        print(" NEW DATASET READY FOR EXPERIMENT 2!")
        print("="*80)
        print("\nNext steps:")
        print("1. Verify data in Supabase")
        print("2. Test a few queries with the API")
        print("3. Run Experiment 2 evaluation:")
        print("   python evaluation/run_balanced_evaluation.py --name experiment2_new_dataset")
