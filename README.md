# ptspRag

Prototype Retrieval-Augmented Generation setup using Mistral 7B via OpenRouter.

## Structure
- `src/` source code
- `data/` raw & processed documents
- `.env` holds `OPENROUTER_API_KEY`

## Quick start
1. Create and fill `.env`:
```
OPENROUTER_API_KEY=sk-...
```
2. Install deps (Windows PowerShell):
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
3. Ingest sample docs:
```
python src\ingest.py data\sample.txt
```
4. Ask a question:
```
python src\ask.py "What does Mistral Small offer?"
```

## Next steps
- Add dataset chunker logic in `ingest.py`.
- Optionally add re-ranking and caching.
 - Switch to Supabase Postgres (pgvector) backend.

## Supabase / pgvector backend
Set env vars in `.env`:
```
VECTOR_BACKEND=supabase
PG_HOST=your_host
PG_PORT=5432
PG_DB=your_db
PG_USER=your_user
PG_PASSWORD=your_password
PG_TABLE=rag_chunks
```
Ensure the database has the pgvector extension (the code attempts `CREATE EXTENSION IF NOT EXISTS vector;`).
Embedding dimension in `vector_store_supabase.py` must match your embedding model (default 1536 for `nomic-embed-text`). Adjust if needed.

## Multiple datasets / namespaces
Use `DATASET_NAME` in `.env` to isolate indexes.
Examples:
```
DATASET_NAME=dev
```
Creates local files: `data/dev_vector_store.npy`, `data/dev_docs_meta.json` and (if pgvector) table `rag_chunks_dev`.

Switch to production corpus later with:
```
DATASET_NAME=prod
```
Then ingest again; existing dev artifacts remain untouched.

## Web / Page Dataset Scraper
You can scrape a webpage (optionally crawling same-origin links) and automatically download dataset-style files (xlsx, pdf, docx, csv) into an output folder. A `manifest.json` with metadata will be created.

Example (single page):
```
python src\scrape.py https://example.com/datasets/ data\scraped
```

Example (crawl up to 2 link levels deep, max 50 pages, also save HTML pages):
```
python src\scrape.py https://example.com/datasets/ data\scraped --max-depth 2 --max-pages 50 --collect-html
```

Output structure:
```
data\scraped\<files...>
data\scraped\manifest.json
data\scraped\pages\*.html (if --collect-html specified)
```

Each manifest `files` entry contains: url, filename, size_bytes, content_type, retrieved_at.
Errors (if any) are listed under `stats.errors`.

After downloading, you can ingest text-extractable files by converting them to `.txt` (not automated yet). Future enhancement: add automatic PDF / DOCX -> text extraction & ingest pipeline.
