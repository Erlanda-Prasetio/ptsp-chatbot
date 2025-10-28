# Dataset-Specific RAG APIs

This document describes the three dataset-specific RAG API servers.

## Overview

Three separate FastAPI servers are available, each constrained to a specific dataset:

| API | Port | Dataset | Table | Purpose |
|-----|------|---------|-------|---------|
| `rag_api.py` | 8001 | COMBINED | documents_combined | Original/default API |
| `rag_api_old.py` | 8002 | OLD | documents_old | OLD dataset only |
| `rag_api_new.py` | 8003 | documents_new | documents_new | NEW dataset only |
| `rag_api_combined.py` | 8004 | COMBINED | documents_combined | COMBINED dataset only |

## Starting the Servers

### OLD Dataset API
```bash
python rag_api_old.py
# Runs on http://localhost:8002
```

### NEW Dataset API
```bash
python rag_api_new.py
# Runs on http://localhost:8003
```

### COMBINED Dataset API
```bash
python rag_api_combined.py
# Runs on http://localhost:8004
```

## API Endpoints

All servers have the same endpoints:

### `/health` - GET
Health check endpoint
```bash
curl http://localhost:8002/health
```

Response:
```json
{
  "status": "healthy",
  "dataset": "OLD",
  "table": "documents_old",
  "timestamp": "2025-10-28T00:30:00"
}
```

### `/retrieve` - POST
Retrieve chunks only (no LLM generation)

Request:
```bash
curl -X POST http://localhost:8002/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "Apa itu NIB?"}'
```

Response:
```json
{
  "query": "Apa itu NIB?",
  "sources": [
    {
      "id": 123,
      "content": "NIB adalah...",
      "similarity": 0.95,
      "metadata": {}
    }
  ],
  "search_method": "vector_only",
  "count": 5,
  "dataset": "OLD"
}
```

### `/chat` - POST
Full RAG pipeline (retrieval + LLM generation)

Request:
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Apa itu NIB?"}'
```

Response:
```json
{
  "message": "NIB adalah Nomor Induk Berusaha...",
  "sources": [
    {
      "id": 123,
      "content": "...",
      "similarity": 0.95
    }
  ],
  "search_method": "vector_only",
  "dataset": "OLD"
}
```

## Implementation Details

### SmartEnhancedRAG_OLD
- **File**: `src/hybrid_rag_old.py`
- **Behavior**: Wrapper around `SmartEnhancedRAG` that forces `table_name = "documents_old"`
- **Features**:
  - All queries constrained to OLD dataset only
  - Never falls back to NEW dataset
  - Consistent results for OLD dataset evaluation

### SmartEnhancedRAG_NEW
- **File**: `src/hybrid_rag_new.py`
- **Behavior**: Wrapper around `SmartEnhancedRAG` that forces `table_name = "documents_new"`
- **Features**:
  - All queries constrained to NEW dataset only
  - Never falls back to OLD dataset
  - Consistent results for NEW dataset evaluation

### SmartEnhancedRAG_COMBINED
- **File**: `src/hybrid_rag_combined.py`
- **Behavior**: Wrapper around `SmartEnhancedRAG` that forces `table_name = "documents_combined"`
- **Features**:
  - Uses the merged COMBINED table
  - Includes both OLD and NEW datasets
  - Best performance when both datasets available

## Usage with Evaluation Scripts

### Run Retrieval Test on OLD Dataset
```bash
# Start OLD dataset API
python rag_api_old.py &

# Run retrieval test against it
python evaluation/run_retrieval_test.py \
  --csv evaluation/old_dataset_retrieval_test_template.csv \
  --api-url http://localhost:8002
```

### Run Retrieval Test on NEW Dataset
```bash
# Start NEW dataset API
python rag_api_new.py &

# Run retrieval test
python evaluation/run_retrieval_test.py \
  --csv evaluation/new_dataset_retrieval_test_template.csv \
  --api-url http://localhost:8003
```

## Architecture

Each API server:
1. **Loads** the appropriate hybrid RAG class (OLD/NEW/COMBINED)
2. **Constrains** all operations to the target table
3. **Wraps** the parent `SmartEnhancedRAG` to enforce table selection
4. **Provides** standard `/chat` and `/retrieve` endpoints
5. **Reports** dataset in all responses

## Key Differences from Original API

| Aspect | Original `rag_api.py` | Dataset-Specific APIs |
|--------|---|---|
| Table | documents_combined | Constrained to one table |
| Dataset | Mixed (both OLD/NEW) | Pure (only one dataset) |
| Consistency | May vary | Consistent per dataset |
| Fallback | May use internet | Uses only specified table |
| Use Case | General queries | Controlled evaluation |

## Troubleshooting

### Port Already in Use
If a port is already in use, modify the port number in the script:
```python
# In rag_api_old.py, change:
uvicorn.run(app, host="0.0.0.0", port=8002)
# To:
uvicorn.run(app, host="0.0.0.0", port=9002)
```

### Connection Refused
Ensure Supabase environment variables are set:
```bash
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_KEY
```

### No Results
Check that the target table has data:
```bash
# For OLD dataset
python -c "from src.vector_store_supabase_rest import SupabaseRestVectorStore; print(SupabaseRestVectorStore().get_count())"
```

## See Also
- `rag_api.py` - Original combined API
- `src/hybrid_rag.py` - Base SmartEnhancedRAG class
- `src/hybrid_rag_old.py` - OLD dataset wrapper
- `src/hybrid_rag_new.py` - NEW dataset wrapper
- `src/hybrid_rag_combined.py` - COMBINED dataset wrapper
