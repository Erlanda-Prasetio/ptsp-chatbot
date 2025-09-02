import sys, os, json
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
    SupabaseVectorStore = None

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def extract_text_from_excel(file_path):
    """Extract text from Excel file"""
    try:
        # Read all sheets and combine
        excel_file = pd.ExcelFile(file_path)
        all_text = f"File: {file_path.name}\n\n"
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            all_text += f"Sheet: {sheet_name}\n"
            all_text += f"Columns: {', '.join(str(col) for col in df.columns)}\n"
            
            # Convert dataframe to text representation
            for index, row in df.head(100).iterrows():  # Limit to first 100 rows
                row_text = " | ".join(str(val) for val in row.values if pd.notna(val))
                if row_text.strip():
                    all_text += f"Row {index}: {row_text}\n"
            all_text += "\n"
            
        return all_text
    except Exception as e:
        print(f"Error reading Excel {file_path}: {e}")
        return ""

def extract_text_from_csv(file_path):
    """Extract text from CSV file"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
        all_text = f"File: {file_path.name}\n\n"
        all_text += f"Columns: {', '.join(str(col) for col in df.columns)}\n\n"
        
        # Convert dataframe to text representation
        for index, row in df.head(100).iterrows():  # Limit to first 100 rows
            row_text = " | ".join(str(val) for val in row.values if pd.notna(val))
            if row_text.strip():
                all_text += f"Row {index}: {row_text}\n"
                
        return all_text
    except Exception as e:
        print(f"Error reading CSV {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        import docx
        doc = docx.Document(file_path)
        text = f"File: {file_path.name}\n\n"
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def extract_text_from_file(file_path):
    """Extract text from various file formats"""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    if extension == '.txt':
        return file_path.read_text(encoding='utf-8', errors='ignore')
    elif extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif extension in ['.xlsx', '.xls']:
        return extract_text_from_excel(file_path)
    elif extension == '.csv':
        return extract_text_from_csv(file_path)
    elif extension == '.docx':
        return extract_text_from_docx(file_path)
    else:
        # Try to read as text file
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except:
            print(f"Unsupported file format: {extension}")
            return ""

def ingest_file_indonesia(file_path: Path, supa=None):
    """Ingest a single file into the vector store"""
    try:
        text = extract_text_from_file(file_path)
        if not text or len(text.strip()) < 10:
            print(f"Skipping {file_path}: insufficient content")
            return
            
        chunks = chunk_text(text)
        if VECTOR_BACKEND == 'supabase' and supa:
            supa.add_chunks(str(file_path), chunks)
        else:
            embeddings = embed_texts(chunks)
            metas = [{"source": str(file_path), "chunk_index": i} for i, _ in enumerate(chunks)]
            store.add(embeddings, chunks, metas)
            
        print(f"✓ Ingested {file_path.name} ({len(chunks)} chunks)")
    except Exception as e:
        print(f"✗ Error ingesting {file_path}: {e}")

def process_indonesia_dataset():
    """Process the entire Indonesian PTSP dataset"""
    dataset_path = Path("data/scraped_ptsp_indonesia")
    
    if not dataset_path.exists():
        print(f"Dataset path {dataset_path} does not exist")
        return
    
    # Initialize backend
    supa = None
    try:
        if VECTOR_BACKEND == 'supabase':
            supa = SupabaseVectorStore()
            print("✓ Connected to Supabase backend")
        else:
            store.load()
            print("✓ Using local vector store backend")
    except Exception as e:
        print(f"⚠ Error with Supabase backend: {e}")
        print("Falling back to local backend...")
        # Fall back to local
        store.load()
        supa = None
    
    # Get all files
    supported_extensions = {'.txt', '.pdf', '.xlsx', '.xls', '.csv', '.docx'}
    all_files = []
    
    for ext in supported_extensions:
        files = list(dataset_path.rglob(f'*{ext}'))
        all_files.extend(files)
    
    print(f"Found {len(all_files)} files to process")
    
    # Process files in batches to avoid memory issues
    batch_size = 50
    for i in tqdm(range(0, len(all_files), batch_size), desc="Processing batches"):
        batch = all_files[i:i + batch_size]
        for file_path in batch:
            ingest_file_indonesia(file_path, supa)
    
    # Save results
    try:
        if supa:
            supa.close()
            print("✓ Indonesian dataset processed (Supabase backend)")
        else:
            store.save()
            print("✓ Indonesian dataset processed (local backend)")
    except Exception as e:
        print(f"Error saving: {e}")
        # Always try to save locally as backup
        store.save()
        print("✓ Data saved to local backup")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--indonesia":
        process_indonesia_dataset()
    else:
        print("Usage: python src/ingest_indonesia.py --indonesia")
        print("This will process all files in data/scraped_ptsp_indonesia/")
