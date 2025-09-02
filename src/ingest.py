import sys, os, json
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

# Usage: python src/ingest.py data\sample.txt [more files...]

def ingest_file(path: Path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)
    metas = [{"source": str(path), "chunk_index": i} for i,_ in enumerate(chunks)]
    store.add(embeddings, chunks, metas)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Provide at least one file path")
        sys.exit(1)
    if VECTOR_BACKEND == 'supabase':
        supa = SupabaseVectorStore()
    else:
        store.load()
    files = [Path(p) for p in sys.argv[1:]]
    for f in tqdm(files, desc="Ingesting"):
        if f.is_file():
            if VECTOR_BACKEND == 'supabase':
                text = f.read_text(encoding='utf-8', errors='ignore')
                chunks = chunk_text(text)
                supa.add_chunks(str(f), chunks)
            else:
                ingest_file(f)
        else:
            # directory: ingest all *.txt
            for txt in f.rglob('*.txt'):
                if VECTOR_BACKEND == 'supabase':
                    text = txt.read_text(encoding='utf-8', errors='ignore')
                    chunks = chunk_text(text)
                    supa.add_chunks(str(txt), chunks)
                else:
                    ingest_file(txt)
    if VECTOR_BACKEND == 'supabase':
        supa.close()
        print("Done (supabase backend)")
    else:
        store.save()
        print("Done. Total documents:", len(store.texts))
