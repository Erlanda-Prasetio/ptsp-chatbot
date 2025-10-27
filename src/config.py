import os
from dotenv import load_dotenv

load_dotenv()

# Try Groq first, fallback to OpenRouter
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Determine which API to use - check env variable explicitly
_use_groq_env = os.getenv("USE_GROQ", "").lower()
USE_GROQ = _use_groq_env == "true" if _use_groq_env else bool(GROQ_API_KEY)

if not GROQ_API_KEY and not OPENROUTER_API_KEY:
    raise RuntimeError("Missing API key: Set either GROQ_API_KEY or OPENROUTER_API_KEY in .env")

# Model selection - use MODEL from .env for Groq, GEN_MODEL for OpenRouter
if USE_GROQ:
    GEN_MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")
    print(f"✅ Using Groq API with model: {GEN_MODEL}")
else:
    GEN_MODEL = os.getenv("GEN_MODEL", "mistral-7b-instruct")
    print(f"✅ Using OpenRouter API with model: {GEN_MODEL}")
EMB_MODEL = os.getenv("EMB_MODEL", "nomic-embed-text")
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "1600"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Dataset namespace (lets you keep multiple corpora: dev, staging, prod)
DATASET_NAME = os.getenv("DATASET_NAME", "default").strip().replace(" ", "_")

_store_path_env = os.getenv("STORE_PATH")
_docs_index_env = os.getenv("DOCS_INDEX_PATH")
if _store_path_env:
    STORE_PATH = _store_path_env
else:
    STORE_PATH = f"data/{DATASET_NAME}_vector_store.npy"
if _docs_index_env:
    DOCS_INDEX_PATH = _docs_index_env
else:
    DOCS_INDEX_PATH = f"data/{DATASET_NAME}_docs_meta.json"

# Backend: "local" or "supabase"
VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "local").lower()

# Supabase / Postgres connection (for pgvector)
PG_HOST = os.getenv("PG_HOST")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
_pg_table_env = os.getenv("PG_TABLE")
if _pg_table_env:
    PG_TABLE = _pg_table_env
else:
    PG_TABLE = f"rag_chunks_{DATASET_NAME}"
