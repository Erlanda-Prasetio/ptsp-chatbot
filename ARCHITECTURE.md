# Architecture: Dataset-Specific RAG APIs

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Evaluation Layer                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │ Chunk Confidence │  │ Retrieval Test   │  │ Analysis Script  │      │
│  │ Test             │  │ Script           │  │                  │      │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘      │
│           │                     │                      │                │
└───────────┼─────────────────────┼──────────────────────┼────────────────┘
            │                     │                      │
            ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API Selection Layer                             │
│  Choose ONE of these three:                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │ rag_api_old.py   │  │ rag_api_new.py   │  │ rag_api_combined │      │
│  │ Port: 8002       │  │ Port: 8003       │  │ Port: 8004       │      │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘      │
│           │                     │                      │                │
└───────────┼─────────────────────┼──────────────────────┼────────────────┘
            │                     │                      │
            ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      RAG Wrapper Classes                                │
│  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐   │
│  │SmartEnhancedRAG   │  │SmartEnhancedRAG   │  │SmartEnhancedRAG   │   │
│  │_OLD               │  │_NEW               │  │_COMBINED          │   │
│  │table="documents   │  │table="documents   │  │table="documents   │   │
│  │_old"              │  │_new"              │  │_combined"         │   │
│  └────────┬──────────┘  └────────┬──────────┘  └────────┬──────────┘   │
│           │                     │                      │                │
└───────────┼─────────────────────┼──────────────────────┼────────────────┘
            │                     │                      │
            ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SmartEnhancedRAG Base Class                          │
│  - Vector Search                                                        │
│  - Query Expansion                                                      │
│  - Domain Detection                                                     │
│  - LLM Generation                                                       │
│  - Result Formatting                                                    │
└────────────┬─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Supabase Vector Database                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │documents_old     │  │documents_new     │  │documents_combined│      │
│  │(OLD dataset)     │  │(NEW dataset)     │  │(BOTH datasets)   │      │
│  │~27 documents    │  │~23 documents    │  │~50 documents    │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow: Query Processing

```
┌─────────────────┐
│ User Query      │
│ "Apa itu NIB?"  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ Endpoint Selection                              │
│ - /chat (full RAG)                              │
│ - /retrieve (vectors only)                      │
│ - /health (status check)                        │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ Table Enforcement                               │
│ table_name = "documents_old"  ← FORCED!         │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ Vector Embedding                                │
│ query_embedding = embed("Apa itu NIB?")         │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ Vector Search                                   │
│ SELECT * FROM documents_old                     │
│ WHERE similarity(embedding, query) > threshold  │
│ ORDER BY similarity DESC                        │
│ LIMIT 5                                         │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│ Results Retrieved                               │
│ - chunk_id: 123                                 │
│ - content: "NIB adalah..."                      │
│ - similarity: 0.95                              │
│ (Repeat for top 5)                              │
└────────┬────────────────────────────────────────┘
         │
         ├─ If /retrieve endpoint ──────────┐
         │                                  │
         ▼                                  ▼
    ┌─────────────┐              ┌──────────────────────┐
    │ Return JSON │              │ LLM Generation       │
    │ (vectors)   │              │ Generate answer      │
    └─────────────┘              │ using retrieved text │
                                 └──────┬───────────────┘
                                        │
                                        ▼
                                 ┌──────────────────────┐
                                 │ Return JSON          │
                                 │ (answer + sources)   │
                                 └──────────────────────┘
```

## Table Enforcement Mechanism

```python
class SmartEnhancedRAG_OLD(SmartEnhancedRAG):
    """
    All methods force table_name = "documents_old"
    """
    
    def retrieve(self, query, top_k=5):
        # Before calling parent:
        original_table = self.table_name
        self.table_name = "documents_old"  # ← FORCE
        
        # Call parent with forced table
        try:
            result = super().retrieve(query, top_k)
            return result
        finally:
            # Restore original (not used, but good practice)
            self.table_name = original_table
```

## Comparison: API Behaviors

```
Query: "Apa itu NIB?"

Original API (rag_api.py, port 8001):
├─ Search in: documents_combined
├─ Fallback: May use enhanced_vector or internet_fallback
├─ Result: Mix of OLD and NEW chunks
└─ Dataset: COMBINED

OLD API (rag_api_old.py, port 8002):
├─ Search in: documents_old ONLY
├─ Fallback: NO - only use documents_old
├─ Result: Pure OLD chunks only
└─ Dataset: OLD

NEW API (rag_api_new.py, port 8003):
├─ Search in: documents_new ONLY
├─ Fallback: NO - only use documents_new
├─ Result: Pure NEW chunks only
└─ Dataset: NEW

COMBINED API (rag_api_combined.py, port 8004):
├─ Search in: documents_combined
├─ Fallback: May use enhanced_vector
├─ Result: Mix of OLD and NEW chunks
└─ Dataset: COMBINED
```

## Evaluation Pipeline with Dataset-Specific APIs

```
┌──────────────────────────────────────────────────┐
│ Step 1: Create Question Templates                │
│ Input: sample_50_balanced_cleaned.json            │
│ Output: CSV with 50 questions (27 OLD, 23 NEW)   │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│ Step 2: Chunk Confidence Test                    │
│ Start: python rag_api_old.py (port 8002)        │
│ Run: python evaluation/chunk_confidence_test.py  │
│ Output: CSV with chunk IDs populated             │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│ Step 3: Retrieval Test                           │
│ Run: python evaluation/run_retrieval_test.py    │
│     --csv evaluation/old_dataset_retrieval...csv │
│     --api-url http://localhost:8002              │
│ Output: CSV with retrieval results               │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│ Step 4: Analysis                                 │
│ Run: python evaluation/analyze_retrieval_test.py │
│ Input: Same CSV from Step 3                      │
│ Output: Metrics, statistics, visualizations      │
└──────────────────────────────────────────────────┘
```

## Port Assignments

```
8000 → Available (custom use)
8001 → rag_api.py (ORIGINAL - COMBINED dataset)
8002 → rag_api_old.py (NEW - OLD dataset)
8003 → rag_api_new.py (NEW - NEW dataset)
8004 → rag_api_combined.py (NEW - COMBINED dataset)
8005+ → Available for other services
```

## Component Isolation

```
Each API is completely isolated:

rag_api_old.py  ←─────────────────→ documents_old table
                        ↓
           (No access to documents_new)
           (No internet fallback option)
           (Pure OLD dataset results)

rag_api_new.py  ←─────────────────→ documents_new table
                        ↓
           (No access to documents_old)
           (No internet fallback option)
           (Pure NEW dataset results)

rag_api_combined.py ←──────────────→ documents_combined table
                        ↓
           (May use both OLD and NEW)
           (May use internet fallback)
           (Mixed dataset results)
```

## How It Solves the Problem

**Problem**: Retrieval test finds different chunks than chunk confidence test
- Chunk test queries: documents_old (via RPC)
- Retrieval test queries: documents_combined (via RAG API)
- ❌ Different tables = different results

**Solution**: Use dataset-specific APIs
- Chunk test queries: documents_old (via RPC)
- Retrieval test queries: documents_old (via rag_api_old.py)
- ✅ Same table = same results = consistency
