import sys
import os
import json
import pandas as pd
import PyPDF2
from pathlib import Path
from tqdm import tqdm
from chunk import chunk_text
from embed import embed_texts
from config import VECTOR_BACKEND
from vector_store import store
if VECTOR_BACKEND == 'supabase':
    from vector_store_supabase import SupabaseVectorStore
else:
    SupabaseVectorStore = None  # type: ignore

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def extract_text_from_excel(excel_path: Path) -> str:
    """Extract text from Excel/CSV files"""
    try:
        # Determine file type and read accordingly
        if excel_path.suffix.lower() == '.xlsx':
            df = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')  # Read all sheets
        elif excel_path.suffix.lower() == '.xls':
            df = pd.read_excel(excel_path, sheet_name=None, engine='xlrd')  # Read all sheets with xlrd
        elif excel_path.suffix.lower() == '.csv':
            # For CSV, create a dict with single sheet
            df_single = pd.read_csv(excel_path)
            df = {'Sheet1': df_single}
        else:
            return ""
        
        text = f"File: {excel_path.name}\n\n"
        
        for sheet_name, sheet_data in df.items():
            text += f"Sheet: {sheet_name}\n"
            text += sheet_data.to_string(index=False) + "\n\n"
            
        return text
    except Exception as e:
        print(f"Error reading {excel_path}: {e}")
        return ""

def ingest_file(path: Path):
    """Ingest a single file based on its type"""
    print(f"Processing: {path.name}")
    
    # Extract text based on file type
    if path.suffix.lower() == '.pdf':
        text = extract_text_from_pdf(path)
    elif path.suffix.lower() in ['.xlsx', '.xls', '.csv']:
        text = extract_text_from_excel(path)
    elif path.suffix.lower() == '.txt':
        text = path.read_text(encoding='utf-8', errors='ignore')
    else:
        print(f"Unsupported file type: {path.suffix}")
        return
    
    if not text.strip():
        print(f"No text extracted from {path.name}")
        return
    
    # Add file metadata to the text
    enhanced_text = f"Source: {path.name}\nFile Type: {path.suffix}\nPath: {path}\n\n{text}"
    
    # Chunk the text
    chunks = chunk_text(enhanced_text)
    
    if VECTOR_BACKEND == 'supabase':
        supa.add_chunks(str(path), chunks)
    else:
        embeddings = embed_texts(chunks)
        metas = [{"source": str(path), "filename": path.name, "chunk_index": i, "file_type": path.suffix} 
                for i, _ in enumerate(chunks)]
        store.add(embeddings, chunks, metas)

def ingest_directory(directory: Path, supported_extensions=None):
    """Ingest all supported files from a directory"""
    if supported_extensions is None:
        supported_extensions = {'.pdf', '.xlsx', '.xls', '.csv', '.txt'}
    
    files = []
    for ext in supported_extensions:
        files.extend(directory.rglob(f'*{ext}'))
    
    # Filter out very large files (>50MB) to avoid memory issues
    files = [f for f in files if f.stat().st_size < 50 * 1024 * 1024]
    
    print(f"Found {len(files)} supported files in {directory}")
    
    for file_path in tqdm(files, desc="Ingesting files"):
        try:
            ingest_file(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/ingest_scraped.py <data_directory> [file1 file2 ...]")
        print("Example: python src/ingest_scraped.py data/scraped")
        sys.exit(1)
    
    # Initialize vector store
    if VECTOR_BACKEND == 'supabase':
        supa = SupabaseVectorStore()
    else:
        store.load()
    
    # Process arguments
    paths = [Path(p) for p in sys.argv[1:]]
    
    for path in paths:
        if path.is_file():
            ingest_file(path)
        elif path.is_dir():
            ingest_directory(path)
        else:
            print(f"Path not found: {path}")
    
    # Save and cleanup
    if VECTOR_BACKEND == 'supabase':
        supa.close()
        print("Done (supabase backend)")
    else:
        store.save()
        print("Done (local backend)")
