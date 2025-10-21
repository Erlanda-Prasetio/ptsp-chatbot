# 2-Phase Evaluation Workflow

## Overview

The evaluation is split into **2 phases** to separate automated metrics from manual verification:

### ⚡ Phase 1: Automated Evaluation
- Runs ALL queries through the system
- Logs response time, tokens, precision, recall, F1
- **NO manual verification** (response time = pure system performance)
- Saves results to JSON

### 👤 Phase 2: Manual Scoring
- Read saved results
- Score each answer as correct/incorrect (y/n)
- **Does NOT affect response time**
- Exports to CSV for analysis

---

## Workflow

### Step 1: Sample Queries (One-time)

```bash
# If you have 310 queries in evaluation/full_dataset_310.json
python evaluation/sample_queries.py

# This creates:
# - evaluation/sample_30_quick.json (quick test)
# - evaluation/sample_50_standard.json
# - evaluation/sample_100_paper.json (RECOMMENDED)
# - evaluation/sample_200_extended.json
```

---

### Step 2: Phase 1 - Automated Evaluation

```bash
# Run for each system (4 times total)

# 1. Baseline (old dataset)
python evaluation/run_evaluation.py --system baseline --sample evaluation/sample_100_paper.json --delay 1.0

# 2. Baseline (updated dataset) - after cleaning data
python evaluation/run_evaluation.py --system baseline_updated --sample evaluation/sample_100_paper.json --delay 1.0

# 3. MADAM-RAG (old dataset) - after implementing MADAM-RAG
python evaluation/run_evaluation.py --system madam_old --sample evaluation/sample_100_paper.json --delay 1.0

# 4. MADAM-RAG (updated dataset)
python evaluation/run_evaluation.py --system madam_new --sample evaluation/sample_100_paper.json --delay 1.0
```

**Output**: `evaluation/raw_results/{system}_{timestamp}.json`

**Time**: ~15-30 minutes per system (100 queries @ 10-20s each)

---

### Step 3: Phase 2 - Manual Scoring

```bash
# Score the results from Phase 1
python evaluation/manual_scoring.py --file evaluation/raw_results/baseline_20251021_143022.json

# Interactive prompts:
# [1/100] Q001 - perizinan (easy)
# ❓ QUESTION: Apa itu OSS?
# 💡 GROUND TRUTH: OSS adalah sistem perizinan...
# 🤖 SYSTEM ANSWER: OSS (Online Single Submission) adalah...
# Is this answer CORRECT? (y/n/s/q/?): y
# ✅ Marked as CORRECT
```

**Commands**:
- `y` = Correct answer
- `n` = Incorrect answer
- `s` = Skip (leave unscored)
- `q` = Quit (saves progress, can resume later)
- `?` = Show full ground truth and answer

**Output**: 
- Updates JSON with `is_correct` field
- Exports to CSV: `evaluation/raw_results/{system}_{timestamp}.csv`

**Time**: ~30-60 minutes per 100 queries (depends on reading speed)

---

### Step 4: Analyze Results (Jupyter Notebook)

```bash
jupyter notebook evaluation/analyze_results.ipynb
```

The notebook will:
1. Load all 4 CSV files
2. Calculate aggregate metrics
3. Generate comparison charts
4. Run statistical significance tests
5. Export tables for research paper

---

## File Structure

```
evaluation/
├── sample_queries.py              # Generate query samples
├── run_evaluation.py              # Phase 1: Automated evaluation
├── manual_scoring.py              # Phase 2: Manual scoring
├── analyze_results.ipynb          # Analysis & visualization
├── full_dataset_310.json          # Your 310 queries
├── sample_100_paper.json          # Sampled 100 queries (seed=42)
├── raw_results/                   # Phase 1 output
│   ├── baseline_20251021_143022.json
│   ├── baseline_20251021_143022.csv     # After Phase 2
│   ├── baseline_updated_20251021_153045.json
│   ├── baseline_updated_20251021_153045.csv
│   ├── madam_old_20251022_091234.json
│   ├── madam_old_20251022_091234.csv
│   ├── madam_new_20251022_103456.json
│   └── madam_new_20251022_103456.csv
└── results/                       # Final analysis output
    ├── aggregate_metrics.csv
    ├── accuracy_comparison.png
    └── ...
```

---

## CSV Format

After Phase 2, each CSV contains:

| Column | Description | Example |
|--------|-------------|---------|
| `query_id` | Unique query identifier | Q001 |
| `query_text` | The question asked | "Apa syarat izin usaha?" |
| `category` | Query category | perizinan |
| `difficulty` | Query difficulty | medium |
| `answer` | System's answer | "Untuk mengurus izin..." |
| `ground_truth` | Expected answer | "Syarat izin usaha: KTP..." |
| `is_correct` | Manual verification | True/False |
| `confident_wrong` | False positive (conf>0.8) | True/False |
| `response_time_seconds` | Pure system time | 8.45 |
| `model_name` | LLM used | mistralai/mistral-small |
| `prompt_tokens` | Input tokens | 850 |
| `completion_tokens` | Output tokens | 120 |
| `total_tokens` | Total tokens | 970 |
| `num_retrieved` | Chunks retrieved | 8 |
| `precision` | Retrieval precision | 0.667 |
| `recall` | Retrieval recall | 1.0 |
| `f1_score` | F1 score | 0.800 |
| `confidence_score` | System confidence | 0.92 |
| `system_name` | System evaluated | baseline |

---

## Benefits of 2-Phase Approach

### ✅ Advantages:

1. **Accurate Response Time**
   - No human delay in timing measurements
   - Response time = pure system performance
   
2. **Flexible Scoring**
   - Score at your own pace (no pressure)
   - Can quit and resume anytime (progress saved)
   - Re-score if needed

3. **Batch Processing**
   - Run Phase 1 for all systems overnight
   - Do Phase 2 scoring later when you have time

4. **Data Preservation**
   - Raw results saved (answer, sources, metrics)
   - Can re-analyze without re-running system
   - Easy to share results with collaborators

---

## Tips

### For Fast Evaluation:

1. **Phase 1**: Run all 4 systems in sequence
   ```bash
   python evaluation/run_evaluation.py --system baseline --delay 1.0
   python evaluation/run_evaluation.py --system baseline_updated --delay 1.0
   python evaluation/run_evaluation.py --system madam_old --delay 1.0
   python evaluation/run_evaluation.py --system madam_new --delay 1.0
   ```

2. **Phase 2**: Score in batches
   - Score 20-30 queries per session
   - Use `q` to quit and save progress
   - Resume with same command later

### For Consistent Scoring:

- Read ground truth first
- Check if answer covers key points
- Be consistent with your criteria
- When in doubt, mark as incorrect (strict evaluation)

### For API Rate Limiting:

- Use `--delay 1.0` (1 second between queries)
- If hitting limits, increase to `--delay 2.0` or `--delay 3.0`
- OpenRouter free tier: ~60 requests/minute

---

## Example Session

```bash
# 1. Sample queries (one-time)
python evaluation/sample_queries.py
# Output: sample_100_paper.json created

# 2. Phase 1: Automated evaluation
python evaluation/run_evaluation.py --system baseline --sample evaluation/sample_100_paper.json
# Output: raw_results/baseline_20251021_143022.json
# Time: ~15 minutes (100 queries)

# 3. Phase 2: Manual scoring
python evaluation/manual_scoring.py --file evaluation/raw_results/baseline_20251021_143022.json
# Interactive scoring session
# Output: baseline_20251021_143022.csv
# Time: ~45 minutes

# 4. Repeat for other systems
python evaluation/run_evaluation.py --system baseline_updated
python evaluation/manual_scoring.py --file evaluation/raw_results/baseline_updated_*.json

# 5. Analyze all results
jupyter notebook evaluation/analyze_results.ipynb
```

---

## Troubleshooting

### "File not found" error in Phase 2
- Check the exact filename from Phase 1 output
- Use tab completion: `python evaluation/manual_scoring.py --file evaluation/raw_results/base<TAB>`

### Phase 1 taking too long
- Reduce sample size: use `sample_30_quick.json` for testing
- Increase `--delay` if API rate limiting

### Want to re-score
- Phase 2 asks if you want to re-score when it detects existing scores
- Or delete the JSON and CSV, re-run Phase 2

### System crashed during Phase 1
- Results are saved after each query
- Check `raw_results/` for partial JSON
- Can manually score what was completed

---

## Next Steps

1. ✅ Create `evaluation/full_dataset_310.json` with your 310 queries
2. ⏳ Run `sample_queries.py` to generate samples
3. ⏳ Run Phase 1 for baseline system
4. ⏳ Run Phase 2 to score results
5. ⏳ Repeat for all 4 systems
6. ⏳ Analyze with Jupyter notebook
7. ⏳ Export charts and tables for paper

Good luck! 🚀
