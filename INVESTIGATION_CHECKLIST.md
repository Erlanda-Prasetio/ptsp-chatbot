# 🔍 Generative Test Failure - Investigation Checklist

## Problem Summary
- ❌ **0 out of 25** queries produced valid AI-generated responses
- 92% empty responses
- 8% explicit timeouts
- System retrieved sources correctly but failed in the **generative phase**

## Investigation Steps

### Phase 1: Direct API Testing
```powershell
# Test 1: Simple health check
curl http://localhost:8001/health

# Test 2: Test a single query directly
$body = @{
    question = "Apa kode KBLI untuk laundry?"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8001/chat" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Check these things**:
- [ ] Does the API respond?
- [ ] Is the response JSON valid?
- [ ] Does the `answer` field have content?
- [ ] What's the response time?
- [ ] Are there any error messages in the API response?

### Phase 2: Check RAG API Logs
```powershell
# Look at rag_api.py console output while running the test
# Watch for:
# - Connection errors
# - Timeout messages
# - LLM API errors
# - Database connection issues
# - Empty generation results
```

**Look for**:
- [ ] "Error connecting to OpenRouter"
- [ ] "Database connection failed"
- [ ] "LLM generation returned empty"
- [ ] "Timeout in phase X"
- [ ] Any Python exceptions

### Phase 3: Verify Configuration
```powershell
# Check rag_api.py settings
# Look at:
# - API_URL (should be http://localhost:8001)
# - LLM provider (should be OpenRouter or similar)
# - API key validity
# - Model configuration
```

**Verify**:
- [ ] OpenRouter API key is set and valid
- [ ] API rate limit not exceeded
- [ ] Model name is correct
- [ ] Request timeout is > 30 seconds
- [ ] Retry logic is working

### Phase 4: Database Connectivity
```powershell
# Test Supabase connection
# In a Python script:
python -c "
from supabase import create_client
import os
url = 'YOUR_SUPABASE_URL'
key = 'YOUR_SUPABASE_KEY'
try:
    client = create_client(url, key)
    print('✅ Supabase connected')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

**Check**:
- [ ] Supabase project is accessible
- [ ] Vector DB has data
- [ ] Query performance is acceptable
- [ ] No connection timeouts

### Phase 5: LLM Provider Status
```powershell
# Test OpenRouter directly
$headers = @{
    "Authorization" = "Bearer YOUR_OPENROUTER_KEY"
    "Content-Type" = "application/json"
}

$body = @{
    model = "openrouter/auto"  # or specific model
    messages = @(
        @{
            role = "user"
            content = "Apa kode KBLI untuk laundry?"
        }
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://openrouter.ai/api/v1/chat/completions" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

**Check**:
- [ ] API key is valid
- [ ] No 429 (rate limit) errors
- [ ] No 401 (authentication) errors
- [ ] LLM is returning content
- [ ] Response format is correct

## Expected vs Actual Results

### Expected (Working System)
```json
{
  "answer": "Kode KBLI untuk usaha laundry adalah 96200, yang mencakup aktivitas penatu. Dengan kode ini, Anda dapat mendaftar usaha laundry Anda melalui sistem OSS...",
  "search_method": "vector_only",
  "sources_count": 5,
  "response_time_seconds": 5.2,
  "bertscore_f1": 0.82
}
```

### Actual (Current - Broken)
```json
{
  "answer": "",
  "search_method": "vector_only",
  "sources_count": 5,
  "response_time_seconds": 22.66,
  "error": null
}
```

**The difference**: Response time is HIGHER but answer is EMPTY
- This suggests the system is waiting/retrying but not getting LLM output

## Root Cause Hypotheses

### Hypothesis 1: LLM Provider Issue (Most Likely)
**Symptoms**:
- System retrieves sources (hence high response time)
- LLM call fails silently
- No error is logged

**Fix**: Check OpenRouter status, API key, quota

### Hypothesis 2: Generation Phase Not Implemented
**Symptoms**:
- Empty answer despite sources
- Response time is high (retrieval time)
- No mention of generation in logs

**Fix**: Verify `rag_api.py` has generative component

### Hypothesis 3: Response Parsing Error
**Symptoms**:
- LLM generates response but test framework doesn't capture it
- API returns valid response but `answer` field is missed

**Fix**: Check how `run_generative_test.py` extracts the `answer` field

### Hypothesis 4: Timeout in Generation
**Symptoms**:
- Partial response (2 queries timed out with messages)
- Most queries just empty
- No error message for most

**Fix**: Increase timeout, check LLM latency

## Test Configuration Review

Current test config:
```python
# From generative_test_rag_api.py
API_URL = "http://localhost:8001/chat"
REQUEST_TIMEOUT = 60  # seconds
DELAY_BETWEEN_QUERIES = 60  # seconds
```

**Questions**:
- [ ] Is REQUEST_TIMEOUT long enough?
- [ ] Is the API endpoint correct?
- [ ] Should timeout be per-phase or total?

## Comparison: Retrieval Tests vs Generative Tests

### What Worked: Retrieval Tests
- System correctly retrieved chunks
- Scored them with F1 metrics
- Handled delays properly

### What Failed: Generative Tests
- System retrieved chunks (verified by `sources_count`)
- But generation phase produced no output
- This is a **NEW failure point**, not a retrieval issue

**Implication**: The problem is in the **generation/LLM layer**, not the retrieval layer.

## Quick Fixes to Try (In Order)

1. **Restart rag_api.py** - May help if it crashed
   ```powershell
   # Kill old process, restart
   ```

2. **Test Direct LLM Call** - Verify OpenRouter is working
   ```powershell
   # Use Phase 5 test above
   ```

3. **Increase Timeout** - If LLM is just slow
   ```python
   # Change REQUEST_TIMEOUT to 120
   ```

4. **Check API Logs** - Enable verbose logging in rag_api.py
   ```python
   # Add: logging.basicConfig(level=logging.DEBUG)
   ```

5. **Test with Simple Query** - Isolate if it's query-specific
   ```bash
   # Try: "Apa itu OSS?"
   ```

## File Locations for Reference

| File | Purpose |
|------|---------|
| `rag_api.py` | Main RAG API - check logs here |
| `evaluation/run_generative_test.py` | Test runner - check response parsing |
| `evaluation/raw_results/generative_25_questions.json` | Raw results |
| `GENERATIVE_TEST_RESULTS.md` | This test's summary report |

## Next Testing Plan

Once root cause is identified:

1. **Fix the underlying issue**
2. **Rerun single test** - Verify 1 query works
3. **Rerun 3-5 queries** - Check consistency
4. **Full rerun** - All 25 questions with metrics
5. **Compare with retrieval tests** - Ensure no regression

---

**Last Updated**: 2025-10-29
**Status**: 🔴 Investigation Needed
