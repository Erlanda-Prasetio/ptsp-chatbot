# MADAM Retrieval Test with Delays - Implementation Summary

## Changes Made

### 1. Updated MADAM Hybrid System (`madam_hybrid_system.py`)

Added three types of delays to the `ask_with_fallback()` method:

- **60-second delay between questions**: Prevents rate limiting issues when processing multiple questions
- **10-second delays between phases**: 
  - After Vector phase (if not returning early)
  - After Enhanced phase (if not returning early)
  - After MADAM Debate phase (if not returning early)
  - Before Internet fallback phase

### 2. Configuration

**Delay Strategy:**
```
Question 1
├─ Wait 60 seconds (prevent rate limiting)
├─ Vector Phase
├─ Wait 10 seconds (if continuing)
├─ Enhanced Phase
├─ Wait 10 seconds (if continuing)
├─ MADAM Debate Phase
├─ Wait 10 seconds (if continuing)
└─ Internet Fallback Phase

Question 2
├─ Wait 60 seconds (prevent rate limiting)
├─ [repeat phases...]
```

### 3. Test Setup

Created `test_madam_retrieval_with_delays.py` to test:
- **2 CSV Files:**
  1. `evaluation/retrieval_test_result.csv` (MADAM system results)
  2. `evaluation/old_dataset_retrieval_test_template.csv` (baseline results)
  
- **Queries Per File:** 2 (for quick testing)

- **Expected Test Duration:**
  - File 1: 2 queries × 60s between + phase time = ~120s+ for processing
  - 60s gap between files
  - File 2: 2 queries × 60s between + phase time = ~120s+ for processing
  - **Total: ~5-6 minutes**

### 4. Test Execution

The test:
1. Loads 2 queries from each CSV file
2. For each query:
   - Calls MADAM system with delays
   - Records: query_id, question, category, search_method, time, sources, status
3. Generates results CSV files:
   - `test_madam_delays_file1_results.csv`
   - `test_madam_delays_file2_results.csv`

## Benefits of This Approach

✅ **Rate Limiting Protection:**
- 60s between questions prevents API rate limit errors
- 10s between phases gives service time to stabilize

✅ **Model Compatibility:**
- Works with new model API changes
- Provides consistent request pacing

✅ **Observability:**
- Tracks phase execution times
- Records search methods used
- Captures sources retrieved

## Monitoring Progress

The test provides real-time output:
```
📋 Query 1/2: query_id [Category]
Q: Question text...
⏳ Waiting 60 seconds between questions...
⏳ 10s gap between Vector and Enhanced phases...
⏳ 10s gap between Enhanced and MADAM Debate phases...
⏳ 10s gap between MADAM Debate and Internet phases...
✅ Query processed: search_method
   • Time: X.XXs
   • Sources: N
   • Answer: ...
```

## Verifying Results

After testing completes, check:

1. **Result Files Created:**
   ```
   test_madam_delays_file1_results.csv
   test_madam_delays_file2_results.csv
   ```

2. **Check Results:**
   - All queries should have `status: success`
   - `time_seconds` should reflect actual processing time
   - `search_method` should indicate which phase succeeded
   - `sources_retrieved` should be > 0 for successful queries

3. **Performance Analysis:**
   - Compare average times between files
   - Verify consistent method selection
   - Check source retrieval rates

## Next Steps

1. ✅ Monitor test execution (currently running)
2. ⏳ Wait for completion (~5-6 minutes from start)
3. ✅ Review generated CSV files
4. ✅ Verify delays are working (timestamps in output)
5. ✅ Compare results between the two dataset versions
6. ✅ Commit changes to repository

## Code Changes Summary

**File: `madam_hybrid_system.py`**
- Added 60s delay at start of `ask_with_fallback()`
- Added 10s delays between each phase transition
- Added console logging for delay information
- Delays only apply if not returning early (threshold met)

**File: `test_madam_retrieval_with_delays.py` (New)**
- Test harness for 2 CSV files
- Loads and processes queries sequentially
- Generates detailed result CSVs
- Tracks timing and method selection
- Provides comprehensive summary output
