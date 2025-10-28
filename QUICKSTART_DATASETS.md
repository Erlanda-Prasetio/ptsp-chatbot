# Quick Start: Dataset-Specific RAG APIs

## 30-Second Setup

### 1. Start the API You Want
```bash
# For OLD dataset testing
python rag_api_old.py
# Now listening on http://localhost:8002

# OR for NEW dataset testing  
python rag_api_new.py
# Now listening on http://localhost:8003

# OR for COMBINED dataset testing
python rag_api_combined.py
# Now listening on http://localhost:8004
```

### 2. Test It Works
```bash
# Verify the API is responding
curl http://localhost:8002/health
```

### 3. Use with Retrieval Test
```bash
# Run the evaluation on the OLD dataset
python evaluation/run_retrieval_test.py \
  --csv evaluation/old_dataset_retrieval_test_template.csv \
  --api-url http://localhost:8002
```

## Which API to Use?

| Your Goal | Use This API | Port |
|-----------|--------------|------|
| Test OLD dataset only | `rag_api_old.py` | 8002 |
| Test NEW dataset only | `rag_api_new.py` | 8003 |
| Test COMBINED (both) | `rag_api_combined.py` | 8004 |
| General use (original) | `rag_api.py` | 8001 |

## Common Tasks

### Run Chunk Test on OLD Dataset
```bash
# Terminal 1: Start OLD dataset API
python rag_api_old.py

# Terminal 2: Run chunk test
python evaluation/chunk_confidence_test.py
```

### Run Full Evaluation on OLD Dataset
```bash
# Terminal 1: Start API
python rag_api_old.py

# Terminal 2: Run retrieval test
python evaluation/run_retrieval_test.py \
  --csv evaluation/old_dataset_retrieval_test_template.csv \
  --api-url http://localhost:8002

# Terminal 3: Analyze results
python evaluation/analyze_retrieval_test.py \
  evaluation/old_dataset_retrieval_test_template.csv
```

### Run Same Test on All Datasets
```bash
# Terminal 1: OLD dataset
python rag_api_old.py

# Terminal 2: NEW dataset  
python rag_api_new.py

# Terminal 3: COMBINED dataset
python rag_api_combined.py

# Terminal 4: Run tests
python evaluation/run_retrieval_test.py --csv evaluation/old_dataset_retrieval_test_template.csv --api-url http://localhost:8002
python evaluation/run_retrieval_test.py --csv evaluation/new_dataset_retrieval_test_template.csv --api-url http://localhost:8003
python evaluation/run_retrieval_test.py --csv evaluation/combined_dataset_retrieval_test_template.csv --api-url http://localhost:8004
```

## API Request Format

### Simple Query
```bash
curl -X POST http://localhost:8002/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "Apa itu NIB?"}'
```

### With Python
```python
import requests

response = requests.post(
    "http://localhost:8002/retrieve",
    json={"query": "Apa itu NIB?"}
)
print(response.json())
```

## Response Format

All APIs return the same format:

```json
{
  "query": "Your question",
  "sources": [
    {
      "id": 123,
      "content": "Relevant text...",
      "similarity": 0.95,
      "metadata": {}
    }
  ],
  "search_method": "vector_only",
  "count": 5,
  "dataset": "OLD"
}
```

## Troubleshooting

**Problem**: Port 8002 already in use
```bash
# Change port in rag_api_old.py:
# uvicorn.run(app, host="0.0.0.0", port=8002)
# Change 8002 to 9002
python rag_api_old.py  # Now on 9002
```

**Problem**: "Cannot connect to API"
```bash
# Make sure API is running in another terminal
ps aux | grep rag_api_old
# Should see the process running

# Or start it in background
python rag_api_old.py > rag_old.log 2>&1 &
```

**Problem**: "No data returned"
```bash
# Check table has data
curl http://localhost:8002/health
# Should show "status": "healthy"

# Check Supabase .env file
cat .env | grep SUPABASE
```

## Key Differences from Original API

| Feature | Original | Dataset-Specific |
|---------|----------|------------------|
| Dataset | COMBINED (mixed) | Pure (one only) |
| Consistency | May vary | Always same |
| Fallback | May use internet | Only uses table |
| Best for | General queries | Benchmarking |

## Files

- **APIs**: `rag_api_old.py`, `rag_api_new.py`, `rag_api_combined.py`
- **Classes**: `src/hybrid_rag_old.py`, `src/hybrid_rag_new.py`, `src/hybrid_rag_combined.py`
- **Docs**: `DATASET_API_README.md` (detailed), `IMPLEMENTATION_STATUS.md` (overview)

## Next Steps

1. ✅ Choose your dataset (OLD/NEW/COMBINED)
2. ✅ Start the corresponding API server
3. ✅ Verify with `/health` endpoint
4. ✅ Run your evaluation scripts
5. ✅ Analyze results

See `DATASET_API_README.md` for more details!
