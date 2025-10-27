# Two-Test Evaluation Framework

This framework provides two distinct testing approaches to evaluate your RAG system comprehensively.

## 📊 Test 1: Retrieval Test

**Purpose:** Measure vector search quality WITHOUT LLM generation

**What it tests:**
- Vector search precision, recall, F1-score
- Search method distribution (vector_only, enhanced_vector, internet_fallback)
- Which questions trigger internet fallback
- Retrieval speed

**Advantages:**
- ✅ Fast (no LLM delays)
- ✅ Cheap (no API costs)
- ✅ Repeatable (deterministic)
- ✅ Dataset-focused (tests your chunks directly)

**Usage:**
```bash
# Run retrieval test with 50 balanced questions
python evaluation/run_retrieval_test.py --name retrieval_baseline --sample evaluation/sample_50_balanced.json

# Test after changing dataset
python evaluation/run_retrieval_test.py --name retrieval_experiment2 --sample evaluation/sample_50_balanced.json

# Analysis runs automatically, or manually:
python evaluation/analyze_retrieval_test.py evaluation/raw_results/retrieval_baseline.json
```

**Output Metrics:**
- Average Precision, Recall, F1-Score
- Search method distribution
- Performance by category
- Queries with zero precision/recall
- Internet fallback rate

---

## 🤖 Test 2: Generative Test

**Purpose:** Measure LLM answer quality with full RAG pipeline

**What it tests:**
- LLM-generated answer quality
- Response time (end-to-end)
- Token usage
- BERTScore confidence (automatic)
  - ≥0.7 = Great 🟢
  - 0.6-0.7 = Good 🟡
  - 0.5-0.6 = Marginal 🟠
  - <0.5 = Not Confident 🔴
- Manual accuracy scoring

**Advantages:**
- ✅ Tests full user experience
- ✅ Measures answer correctness
- ✅ Includes LLM generation quality
- ✅ BERTScore provides automatic confidence
- ✅ Manual scoring validates accuracy

**Usage:**
```bash
# Run generative test with YOUR 25 custom questions (60s delay default)
python evaluation/run_generative_test.py \
  --name generative_test1 \
  --sample my_25_questions.json \
  --delay 60

# Resume if interrupted
python evaluation/run_generative_test.py \
  --name generative_test1 \
  --sample my_25_questions.json \
  --resume

# Analysis runs automatically, or manually:
python evaluation/analyze_generative_test.py evaluation/raw_results/generative_test1.json

# Then do manual scoring
python evaluation/manual_scoring.py --file evaluation/raw_results/generative_test1.json
```

**Output Metrics:**
- Average response time
- Total token usage
- BERTScore F1 (if ground truth provided)
- Confidence level distribution
- Manual accuracy (after scoring)
- Performance by category

---

## 📋 Question Format

Both tests use JSON files with this format:

```json
[
  {
    "id": "Q001",
    "question": "Your question here",
    "category": "General|Licensing|NIB|Procedure|Technical|Support",
    "dataset_source": "OLD|NEW",
    "ground_truth": "Expected answer (for generative test BERTScore)",
    "relevant_chunk_ids": ["chunk_123", "chunk_456"]
  }
]
```

**For Retrieval Test:**
- Needs `question`, `relevant_chunk_ids` (for P/R/F1 calculation)

**For Generative Test:**
- Needs `question`, `ground_truth` (for BERTScore)
- `relevant_chunk_ids` optional

---

## 🔄 Workflow

### Option A: Dataset Comparison
1. **Run Retrieval Test** on OLD dataset (baseline)
2. **Change dataset** (ingest new chunks)
3. **Run Retrieval Test** on NEW dataset
4. **Compare F1 scores** - did retrieval improve?

### Option B: Full System Evaluation
1. **Run Generative Test** with your 25 questions
2. **Wait ~30-40 minutes** (25 queries × 60s delay + response time)
3. **Review automatic analysis** (BERTScore confidence)
4. **Do manual scoring** to validate answers
5. **Get final accuracy percentage**

### Option C: Both Tests (Recommended)
1. **Retrieval Test** - Quick check of vector search quality
2. **Generative Test** - Deep dive into answer quality
3. **Compare metrics** - Are good retrievals producing good answers?

---

## 📊 Output Files

Both tests save results to `evaluation/raw_results/`:

**Retrieval Test:**
- `<name>.json` - Full results with P/R/F1 per query
- Analyzed by `analyze_retrieval_test.py`

**Generative Test:**
- `<name>.json` - Full results with answers, BERTScore, manual scores
- `<name>_checkpoint.json` - Resume point (deleted when complete)
- Analyzed by `analyze_generative_test.py`

---

## 🛠️ Setup

**Install BERTScore (optional but recommended for generative test):**
```bash
pip install bert-score
```

**Make sure RAG API is running:**
```bash
python rag_api.py
```

**Prepare your question files:**
- Use `evaluation/sample_50_balanced.json` for retrieval test
- Create your own 25-question JSON for generative test

---

## 💡 Tips

**Retrieval Test:**
- Run this FIRST to identify coverage gaps
- Use 50 questions for statistical significance
- Zero precision/recall = missing chunks
- High fallback rate = insufficient local data

**Generative Test:**
- Use 25 carefully chosen questions (saves API costs)
- 60-second delay prevents rate limits
- BERTScore works best with good ground truth
- Manual scoring is essential for accuracy

**When to use which:**
- 🔍 **Retrieval only** = Testing dataset changes, chunk quality
- 🤖 **Generative only** = Testing answer quality, user experience
- 📊 **Both** = Complete evaluation (recommended for research)

---

## 🎯 Key Differences

| Aspect | Retrieval Test | Generative Test |
|--------|---------------|-----------------|
| **Speed** | Fast (~5 min) | Slow (~30-40 min) |
| **Cost** | Free | API tokens |
| **Questions** | 50 (balanced) | 25 (your choice) |
| **Metrics** | P/R/F1 | Time/Tokens/BERTScore/Accuracy |
| **Focus** | Chunks | Answers |
| **Repeatable** | Yes | Yes (with seed) |
| **Rate Limit** | No | Yes (60s delay) |

---

## 📖 Example Workflow

```bash
# 1. Test baseline retrieval (OLD dataset)
python evaluation/run_retrieval_test.py --name retrieval_old --sample evaluation/sample_50_balanced.json

# 2. Change dataset
python ingest_supabase.py  # or your ingestion script

# 3. Test new retrieval
python evaluation/run_retrieval_test.py --name retrieval_new --sample evaluation/sample_50_balanced.json

# 4. Run generative test with your questions
python evaluation/run_generative_test.py --name gen_test1 --sample my_25_questions.json

# 5. Manual scoring
python evaluation/manual_scoring.py --file evaluation/raw_results/gen_test1.json

# 6. Compare all results
python evaluation/compare_all_experiments.py
```

---

## 📝 Notes

- Both tests auto-run analysis when complete
- Use `--no-analyze` flag to skip auto-analysis
- Checkpoint files allow resuming interrupted tests
- Results are saved even if tests fail mid-way

---

**Questions? Check:**
- `run_retrieval_test.py --help`
- `run_generative_test.py --help`
