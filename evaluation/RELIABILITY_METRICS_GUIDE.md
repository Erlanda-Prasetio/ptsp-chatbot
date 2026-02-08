# System Reliability Metrics - Thesis Documentation

## Overview
In addition to retrieval performance metrics (Precision, Recall, F1-Score), this study employs **system reliability metrics** to provide insight into real-world performance.

## Metrics Covered

### 1. **Success and Failure Rates**
Measures how often the system successfully retrieves relevant documents vs complete failure.

**Calculation:**
- **Success Rate** = (Total Queries - Failed Queries) / Total Queries × 100%
- **Failure Rate** = Failed Queries / Total Queries × 100%
- **Perfect Retrieval Rate** = Queries with F1=1.0 / Total Queries × 100%

**Performance Tiers:**
- **Failed**: F1 = 0.0 (no relevant documents retrieved)
- **Low**: 0.0 < F1 < 0.5
- **Medium**: 0.5 ≤ F1 < 0.7
- **High**: F1 ≥ 0.7

---

### 2. **Phase Utilization** (MAF-RAG only)
Tracks which retrieval phase was used for each query, demonstrating the adaptive fallback mechanism.

**Three Phases:**
1. **VOR (Vector-Only Retrieval)** - `search_method='vector_only'`
   - First attempt using standard vector search
   - Fastest, most efficient

2. **EVR (Enhanced Vector Retrieval)** - `search_method='enhanced_vector'`
   - Second attempt with query enhancement
   - Moderate complexity

3. **MADAM (Multi-Agent Debate)** - `search_method='madam_debate'`
   - Final fallback with multi-agent debate
   - Highest complexity, most thorough

**Analysis includes:**
- Percentage of queries handled by each phase
- Success rate per phase
- Performance (mean F1-Score) per phase

---

### 3. **Category Performance** ✅
Already covered in main analysis - F1-Score broken down by query category.

---

### 4. **Response Time**
⚠️ **Note**: Response time data is available in `demo_scored_results.csv` but NOT in the retrieval test CSVs used for thesis evaluation.

**If response time data is available**, it includes:
- Mean response time per model
- Response time distribution
- Correlation between response time and retrieval quality

---

## Where to Find These Metrics

### In the Notebook (`thesis_results_final.ipynb`):
- **Section 8**: System Reliability Metrics
  - Cell 15: Success/Failure Rates calculation
  - Cell 16: Phase Utilization analysis
- **Section 9**: Reliability Metrics Visualization
  - Cell 17: Dual chart (Success Rates + Phase Utilization pie chart)
- **Section 10**: Updated comprehensive summary

### Data Sources:
- **Success/Failure Rates**: Calculated from `F1_Score` column in all CSVs
- **Phase Utilization**: From `search_method` column in `retrieval_test_madam_results.csv`
- **Category Performance**: From `category` column in all CSVs

---

## Expected Results Structure

### Success/Failure Rates Table:
```
Model                      | Success Rate | Failure Rate | Perfect Rate | High Quality Rate
---------------------------|--------------|--------------|--------------|------------------
MAF-RAG                    |     XX%      |     XX%      |     XX%      |       XX%
Baseline Enhanced Dataset  |     XX%      |     XX%      |     XX%      |       XX%
Baseline Legacy Dataset    |     XX%      |     XX%      |     XX%      |       XX%
```

### Phase Utilization (MAF-RAG only):
```
Phase                           | Queries | Percentage | Mean F1 | Success Rate
--------------------------------|---------|------------|---------|-------------
VOR (Vector-Only)               |   XX    |   XX%      |  X.XXX  |    XX%
EVR (Enhanced Vector)           |   XX    |   XX%      |  X.XXX  |    XX%
MADAM (Multi-Agent Debate)      |   XX    |   XX%      |  X.XXX  |    XX%
```

---

## Thesis Integration

**For Results & Discussion section, include:**

1. **Table**: Success/Failure rates comparison across three models
2. **Figure**: Dual visualization
   - Left: Stacked bar chart of Success vs Failure
   - Right: Pie chart of MAF-RAG phase utilization
3. **Text analysis**:
   - "MAF-RAG achieved XX% success rate vs Enhanced (YY%) and Legacy (ZZ%)"
   - "Phase distribution shows XX% handled by VOR, YY% required EVR, and ZZ% needed MADAM fallback"
   - "This demonstrates the system's ability to adapt complexity based on query difficulty"

---

## Running the Analysis

### Option 1: Jupyter Notebook (Recommended)
```python
# Use Python 3.10 kernel
# Run cells 1-18 in thesis_results_final.ipynb
```

### Option 2: Command Line
```bash
py -3.10 evaluation/generate_thesis_results.py
```

---

## Files Generated
- `evaluation/thesis_overall_performance.png` - Overall F1 comparison
- `evaluation/thesis_category_comparison.png` - Category-wise F1 comparison
- `evaluation/thesis_reliability_metrics.png` - Success rates + Phase utilization (new)

---

## Notes

✅ **Available metrics**: Precision, Recall, F1-Score, Success Rate, Failure Rate, Phase Utilization, Category Performance

⚠️ **Not available in current data**: Response Time (only in demo_scored_results.csv, not in retrieval test data)

💡 **Recommendation**: Focus on the 4 available metrics that directly demonstrate MAF-RAG's superiority and adaptive behavior.
