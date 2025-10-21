# Evaluation Framework Setup Complete ✅

## 📊 What Was Created

### 1. Core Logging System
- **`evaluation/metrics_logger.py`** (400+ lines)
  - Captures all 8 metrics: Accuracy, Precision, Recall, F1, Confident Wrong, Response Time, Token Usage, Model Name
  - JSONL format for easy analysis
  - Supports MADAM-RAG specific metrics (debate rounds, convergence)

### 2. Test Dataset
- **`evaluation/test_dataset.json`** 
  - 10 initial queries with ground truth answers
  - Categories: perizinan_dasar, syarat_dokumen, prosedur, jenis_izin, peraturan
  - Difficulty levels: easy, medium, hard
  - **TODO**: Expand to 50-100 queries and add `relevant_chunk_ids`

### 3. Evaluation Runner
- **`evaluation/run_evaluation.py`**
  - Automated evaluation script
  - Supports all 4 systems: baseline, baseline_updated, madam_old, madam_new
  - Manual verification for correctness (y/n/skip)

### 4. Analysis Notebook
- **`evaluation/analyze_results.ipynb`**
  - Load logs from all experiments
  - Calculate aggregate metrics
  - Generate comparison charts (accuracy, precision, recall, F1, time, tokens)
  - Statistical significance testing (t-test)
  - Export to CSV and LaTeX tables for research paper

### 5. Documentation
- **`evaluation/README.md`** - Complete usage guide

---

## 🎯 Metrics Captured

| Metric | How It's Logged | When Calculated |
|--------|----------------|-----------------|
| **Accuracy** | `is_correct=True/False` in `log_response()` | Per query (manual) → Aggregate in notebook |
| **Precision** | Auto-calculated in `log_retrieval()` | Per query (if `relevant_chunk_ids` provided) |
| **Recall** | Auto-calculated in `log_retrieval()` | Per query (if `relevant_chunk_ids` provided) |
| **F1 Score** | Auto-calculated in `log_retrieval()` | Per query (if `relevant_chunk_ids` provided) |
| **Confident Wrong** | Auto-calculated in `log_response()` | Per query (if `confidence_score` >0.8 and wrong) |
| **Response Time** | Auto-tracked from `start_query()` to `log_response()` | Per query (automatic) |
| **Token Usage** | `token_usage` dict in `log_response()` | Per query (from LLM API response) |
| **Model Name** | `model_name` string in `log_response()` | Per query (from config) |

---

## 🚀 How to Use

### Step 1: Prepare Test Dataset

```bash
# Already generated with 10 queries
# View the file:
cat evaluation/test_dataset.json
```

**Next Actions**:
1. Add 40-90 more queries to reach 50-100 total
2. For each query, identify relevant chunk IDs from your database:
   ```python
   # Example: Query your Supabase to find relevant chunks
   from src.vector_store_supabase import SupabaseVectorStore
   vs = SupabaseVectorStore()
   results = vs.search("Apa syarat izin usaha?", k=20)
   # Manually review which chunks contain correct info
   # Add their IDs to test_dataset.json
   ```

### Step 2: Run Baseline Evaluation

```bash
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Run evaluation
python evaluation/run_evaluation.py --system baseline
```

**What happens**:
- System queries each test query
- Logs retrieval results (chunks, similarity scores)
- Shows you the generated answer
- Asks: "Is this answer correct? (y/n/skip)"
- Saves to `evaluation/logs/baseline.jsonl`

### Step 3: Analyze Results (Jupyter Notebook)

```bash
# Install Jupyter if needed
pip install jupyter matplotlib seaborn scipy

# Start Jupyter
jupyter notebook evaluation/analyze_results.ipynb
```

**Notebook cells**:
1. Load logs from all experiments
2. Calculate aggregate metrics (Accuracy, Precision, Recall, F1, etc.)
3. Generate bar charts comparing all 4 systems
4. Perform statistical significance testing
5. Export results to CSV and LaTeX

### Step 4: Repeat for All Systems

```bash
# After updating dataset
python evaluation/run_evaluation.py --system baseline_updated

# After implementing MADAM-RAG
python evaluation/run_evaluation.py --system madam_old
python evaluation/run_evaluation.py --system madam_new
```

---

## 📊 Log File Format (JSONL)

Each line in `evaluation/logs/*.jsonl` is a JSON object:

```json
{
  "query_id": "Q001",
  "query_text": "Apa syarat izin usaha UMKM?",
  "ground_truth": "Syarat izin usaha UMKM meliputi...",
  "timestamp": "2025-10-21T10:30:45",
  "experiment_name": "baseline",
  
  "retrieval": {
    "retrieved_chunk_ids": ["chunk_123", "chunk_456", "chunk_789"],
    "num_retrieved": 3,
    "relevant_chunk_ids": ["chunk_123", "chunk_456"],
    "precision": 0.667,
    "recall": 1.0,
    "f1_score": 0.800,
    "chunks": [
      {"chunk_id": "chunk_123", "similarity": 0.89, "text_preview": "..."},
      {"chunk_id": "chunk_456", "similarity": 0.85, "text_preview": "..."}
    ]
  },
  
  "response": {
    "text": "Untuk membuat izin usaha UMKM...",
    "model_name": "mistralai/mistral-small-3.2-24b-instruct",
    "confidence_score": 0.92,
    "is_correct": true,
    "confident_wrong": false,
    "response_time_seconds": 8.45,
    "token_usage": {
      "prompt_tokens": 850,
      "completion_tokens": 120,
      "total_tokens": 970
    }
  },
  
  "madam_debate": {
    "num_rounds": 3,
    "converged": true,
    "num_agents": 4,
    "agent_responses": [...],
    "aggregated_response": "..."
  }
}
```

---

## 🔍 Important: Recall & F1 Calculation

**For Recall and F1, you NEED `relevant_chunk_ids`**:

1. **Manual Approach** (Recommended for small datasets):
   ```python
   # For each query in test_dataset.json:
   # 1. Manually search your database
   # 2. Read the chunks
   # 3. Identify which ones contain correct information
   # 4. Add their IDs to "relevant_chunk_ids": ["chunk_X", "chunk_Y"]
   ```

2. **Semi-automated Approach**:
   ```python
   # Use your RAG system to retrieve top 20 chunks
   # Manually review and label which are relevant
   # Add to test_dataset.json
   ```

3. **LLM-as-Judge Approach** (For large datasets):
   ```python
   # Use GPT-4/Claude to evaluate if chunk is relevant
   # Ask: "Does this chunk contain information to answer: [query]?"
   # Automatically label chunks
   ```

**Without `relevant_chunk_ids`**:
- Precision: ✅ Can calculate (from retrieved chunks)
- Recall: ❌ Cannot calculate (need ground truth)
- F1: ❌ Cannot calculate (needs Recall)

---

## 📈 Expected Timeline

| Week | Task | Output |
|------|------|--------|
| **Week 1** | Expand test dataset to 50-100 queries | `test_dataset.json` |
| **Week 1** | Add `relevant_chunk_ids` for all queries | Updated `test_dataset.json` |
| **Week 1** | Run baseline evaluation | `logs/baseline.jsonl` |
| **Week 2** | Clean dataset + scrape fresh data | New Supabase data |
| **Week 2** | Run baseline_updated evaluation | `logs/baseline_updated.jsonl` |
| **Week 3** | Implement MADAM-RAG | `src/madam_rag_system.py` |
| **Week 3** | Run MADAM evaluations (old + new) | `logs/madam_*.jsonl` |
| **Week 4** | Analyze results in notebook | Charts, tables, stats |
| **Week 5-6** | Write research paper | Paper draft |

---

## 🎓 For Your Research Paper

The notebook generates publication-ready outputs:

1. **Tables**:
   - `aggregate_metrics.csv` - All metrics across 4 systems
   - LaTeX table code (copy-paste into paper)

2. **Charts** (300 DPI PNG):
   - `accuracy_comparison.png` - Bar chart of accuracy
   - `retrieval_metrics_comparison.png` - Precision, Recall, F1
   - `efficiency_comparison.png` - Response time, token usage
   - `confident_wrong_comparison.png` - False confidence rate

3. **Statistics**:
   - T-test results (p-values)
   - Statistical significance statements

---

## 🔧 Integration with Your RAG System

To integrate logging into `src/smart_enhanced_rag.py`:

```python
# Add to your RAG system's query method
def query(self, query_text: str, logger: MetricsLogger = None):
    # Your existing code...
    
    if logger:
        # Log retrieval
        logger.log_retrieval(
            retrieved_chunks=self.retrieved_chunks,
            relevant_chunk_ids=None  # Provided by test dataset
        )
    
    # Generate response...
    
    if logger:
        # Log response
        logger.log_response(
            response_text=answer,
            model_name=config.model_name,
            token_usage=token_usage,
            confidence_score=confidence,
            is_correct=None  # Evaluated later
        )
    
    return result
```

---

## ✅ What You Have Now

1. **Metrics logging infrastructure** - Complete
2. **Test dataset** - 10 queries (expand to 50-100)
3. **Evaluation runner** - Ready to use
4. **Analysis notebook** - Ready to use
5. **Documentation** - Complete

## ⏳ What's Next

1. **Expand test dataset** to 50-100 queries
2. **Add `relevant_chunk_ids`** for Recall/F1 calculation
3. **Run baseline evaluation** to establish 40% accuracy
4. **Clean dataset** (remove duplicates, add fresh data)
5. **Re-evaluate baseline** with new data
6. **Implement MADAM-RAG** system
7. **Run full 4-way comparison**
8. **Analyze results** and write paper

---

## 💡 Pro Tips

1. **Start small**: Evaluate with 10 queries first to test the system
2. **Manual verification**: For research, manually verify correctness (don't rush)
3. **Ground truth quality**: Spend time on good ground truth answers
4. **Chunk IDs**: This is tedious but critical for Recall/F1
5. **Token tracking**: Make sure your LLM API returns token counts
6. **Consistent queries**: Use EXACT same queries for all 4 experiments

---

Good luck with your research! 🚀
