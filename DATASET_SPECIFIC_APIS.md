# Dataset-Specific RAG APIs - Implementation Complete

## Summary

Created three separate RAG API servers for dataset isolation and testing:

### Files Created/Modified

#### 1. ✅ **rag_api_old.py** 
- **Table**: `documents_old` only
- **Port**: 8000
- **Purpose**: Test retrieval quality on OLD dataset
- **Usage**: `python rag_api_old.py`

#### 2. ✅ **rag_api_combined.py**
- **Table**: `documents_combined` only
- **Port**: 8003
- **Purpose**: Test retrieval quality on COMBINED (OLD + NEW) dataset
- **Usage**: `python rag_api_combined.py`

#### 3. ✅ **src/hybrid_rag_old.py**
- **Class**: `SmartEnhancedRAG_OLD`
- **Parent**: `SmartEnhancedRAG` from `src/smart_enhanced_rag.py`
- **Forces**: All queries to use `documents_old` table
- **Methods**: `__init__(table_name="documents_old")`

#### 4. ✅ **src/hybrid_rag_combined.py**
- **Class**: `SmartEnhancedRAG_COMBINED`
- **Parent**: `SmartEnhancedRAG` from `src/smart_enhanced_rag.py`
- **Forces**: All queries to use `documents_combined` table
- **Methods**: `__init__(table_name="documents_combined")`

#### 5. ✅ **Deleted**: `rag_api_new.py`
- Redundant with current `rag_api.py` (which already uses NEW dataset)

---

## API Endpoints

### OLD Dataset API (Port 8000)
```bash
# Health check
GET http://localhost:8000/health

# Full RAG pipeline
POST http://localhost:8000/chat
{
  "query": "Your question",
  "top_k": 5
}

# Retrieval only (no generation)
POST http://localhost:8000/retrieve
{
  "query": "Your question",
  "top_k": 5
}
```

### NEW Dataset API (Port 8001 - Current rag_api.py)
```bash
GET http://localhost:8001/health
POST http://localhost:8001/chat
POST http://localhost:8001/retrieve
```

### COMBINED Dataset API (Port 8003)
```bash
GET http://localhost:8003/health
POST http://localhost:8003/chat
POST http://localhost:8003/retrieve
```

---

## Running Multiple APIs Simultaneously

```bash
# Terminal 1 - OLD Dataset
python rag_api_old.py

# Terminal 2 - NEW Dataset (current)
python rag_api.py

# Terminal 3 - COMBINED Dataset
python rag_api_combined.py
```

---

## Chunk Test Results

From `evaluation/old_dataset_retrieval_test_template.csv`:
- **Total questions tested**: 50 (27 OLD, 23 NEW)
- **OLD questions with chunks found**: 20/27 (74%)
- **NEW questions with chunks found**: 0/23 (0%)
  - NEW dataset has no matching documents in Supabase
  - All NEW questions fall back to internet search

---

## Why Three APIs?

1. **rag_api_old.py** - Test quality on legacy OSS data
2. **rag_api.py** (NEW) - Test quality on new regulatory data
3. **rag_api_combined.py** - Test quality on both datasets merged

Each API is isolated to prevent cross-contamination during evaluation.

---

## Next Steps

Run retrieval tests on each API separately:
```bash
# Test OLD dataset retrieval
python evaluation/run_retrieval_test.py --csv evaluation/old_dataset_retrieval_test_template.csv

# Create and test NEW dataset template
python evaluation/create_retrieval_template.py --dataset new --output evaluation/new_dataset_retrieval_test_template.csv
python evaluation/chunk_confidence_test.py --dataset new --csv evaluation/new_dataset_retrieval_test_template.csv
python evaluation/run_retrieval_test.py --csv evaluation/new_dataset_retrieval_test_template.csv

# Test COMBINED dataset
python evaluation/create_retrieval_template.py --dataset combined --output evaluation/combined_dataset_retrieval_test_template.csv
python evaluation/chunk_confidence_test.py --dataset combined --csv evaluation/combined_dataset_retrieval_test_template.csv
python evaluation/run_retrieval_test.py --csv evaluation/combined_dataset_retrieval_test_template.csv
```

---

## Status: ✅ COMPLETE

All dataset-specific RAG APIs have been implemented and tested for syntax correctness.
