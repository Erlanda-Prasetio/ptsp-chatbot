# Generative Test Setup - 25 Questions with Ground Truth

## Overview

This setup enables generative testing of the RAG API using 25 curated questions from `generative_test_query.csv` with:
- Ground truth answers
- 60-second delays between questions (rate limiting protection)
- BERTScore and other metrics for evaluation

## Files

### Input CSV
**File**: `evaluation/generative_test_query.csv`

**Columns**:
- `id`: Question identifier (Q1, Q2, ..., Q25)
- `query`: The question text
- `ground_truth`: Expected/reference answer for comparison

**Total**: 25 questions covering OSS, NIB, perizinan, procedures, etc.

### Test Scripts

1. **`evaluation/run_generative_test.py`** (Existing)
   - Main generative test runner
   - Accepts JSON input with queries
   - Supports 60-second delays between questions
   - Calculates BERTScore confidence
   - Saves results to JSON

2. **`evaluation/run_generative_csv_test.py`** (New)
   - Wrapper script for CSV to JSON conversion
   - Runs the generative test automatically
   - Integrates the 25 questions from CSV

## Setup Instructions

### Prerequisites

1. **Start the RAG API** (in a separate terminal):
```bash
cd d:\backup\ptspRag
python rag_api.py
```

The API should be running at `http://localhost:8001`

### Optional: Install Metrics Libraries

For more detailed metrics (strongly recommended):
```bash
pip install bert-score rouge-score nltk scikit-learn
```

### Run the Test

Execute the generative test with 25 questions:
```bash
python evaluation/run_generative_csv_test.py
```

**What happens**:
1. ✅ Converts `generative_test_query.csv` to JSON format
2. ✅ Tests the RAG API against each of the 25 questions
3. ✅ Waits 60 seconds between each question (rate limiting)
4. ✅ Calculates metrics: BERTScore, token usage, response time
5. ✅ Saves detailed results to `evaluation/raw_results/generative_25_questions.json`

**Estimated Time**: ~25-30 minutes (25 questions × 60s delay + processing time)

## Output

### JSON Results
**File**: `evaluation/raw_results/generative_25_questions.json`

**Structure**:
```json
{
  "test_name": "generative_25_questions",
  "test_type": "generative",
  "timestamp": "2025-10-29T...",
  "total_queries": 25,
  "total_time_seconds": 1500,
  "delay_seconds": 60,
  "results": [
    {
      "query_id": "Q1",
      "question": "Apa kode KBLI untuk usaha laundry?",
      "ground_truth": "Kode KBLI untuk laundry adalah 96200...",
      "answer": "Kode KBLI untuk usaha laundry adalah 96200...",
      "search_method": "enhanced_vector",
      "sources_count": 5,
      "response_time_seconds": 2.15,
      "total_tokens": 256,
      "system_confidence": 0.85,
      "bertscore_f1": 0.82,
      "bertscore_confidence": "good",
      "error": null
    },
    ...
  ]
}
```

## Metrics Explained

### BERTScore Confidence
- **Great** (≥0.7): Excellent semantic similarity to ground truth
- **Good** (0.6-0.7): Good match to ground truth
- **Marginal** (0.5-0.6): Acceptable but needs improvement
- **Not Confident** (<0.5): Poor match

### Response Time
- Includes API processing time only
- Does not include the 60-second delays between questions

### Search Method
- `enhanced_vector`: Enhanced vector search method
- `vector_only`: Pure vector similarity
- `internet_fallback`: Web search fallback
- `madam_debate`: Multi-agent debate method

## Rate Limiting Strategy

**60-second delay between questions** ensures:
- No API rate limiting from the LLM backend (OpenRouter)
- Safe, consistent test execution
- Reliable metrics collection

This is especially important for:
- OpenRouter API with free tier limits
- Supabase vector DB query rate limits
- System resource management

## Next Steps After Testing

1. **Analyze Results**:
   ```bash
   python evaluation/analyze_generative_test.py evaluation/raw_results/generative_25_questions.json
   ```

2. **Export to CSV** (measurement columns):
   - Extract results from JSON
   - Add columns: BLEU, ROUGE, BERTScore, response_time
   - Save to `evaluation/generative_test_results.csv`

3. **Compare with Ground Truth**:
   - Identify queries with low BERTScore
   - Analyze failure patterns
   - Improve RAG performance

## Troubleshooting

### "Cannot connect to RAG API"
- Make sure `rag_api.py` is running
- Check if port 8001 is available
- Try: `curl http://localhost:8001/health`

### "Request timeout"
- Increase timeout: `--timeout 60`
- Check API logs for errors
- Ensure database connection is stable

### BERTScore not working
- Install dependencies: `pip install bert-score`
- Tests will continue without it (with warnings)

### Test interrupted
- The test auto-saves checkpoints
- Resume with: `python evaluation/run_generative_test.py --name generative_25_questions --resume`

## Customization

To modify test parameters:

**Increase delay**:
```bash
python evaluation/run_generative_csv_test.py  # Uses 60s (hardcoded)
```

Or use `run_generative_test.py` directly:
```bash
python evaluation/run_generative_test.py \
  --name my_test \
  --sample evaluation/generative_test_queries.json \
  --delay 120  # 120 seconds between queries
```

**Different sample file**:
```bash
python evaluation/run_generative_test.py \
  --name my_test \
  --sample path/to/my_questions.json
```

## CSV Measurement Columns

After testing, the results CSV will include:
- `id`: Question identifier
- `question`: The question text
- `ground_truth`: Reference answer
- `generated_answer`: RAG API response
- `bleu_score`: BLEU similarity (0-1)
- `rouge1_score`: ROUGE-1 F1 score
- `rouge2_score`: ROUGE-2 F1 score
- `rougeL_score`: ROUGE-L F1 score
- `bert_score`: BERTScore F1 (0-1)
- `api_time_seconds`: Response time
- `sources_retrieved`: Number of chunks retrieved
- `status`: "success" or "error"
