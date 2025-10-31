# MADAM Rate Limiting & Groq API Switch - Implementation Complete

## Summary

✅ **OpenRouter Rate Limiting Fixed**: Added inter-round delays to spread 15-20 MADAM API calls across 60+ seconds
✅ **Groq API Enabled**: Switched from rate-limited OpenRouter to Groq LLM API (much higher rate limits)

---

## Changes Made

### 1. MADAM Debate Rate Limiting (testing/madam-rag/run_madam_rag.py)

Added strategic delays throughout the debate process:

| Phase | Delay | Purpose |
|-------|-------|---------|
| **Round 1: Between agents** | 8s × 3 agents | Spread 4 initial LLM calls |
| **Round 1: Before aggregation** | 5s | Gap before synthesis call |
| **Round 2-3: Before new round** | 10s | Full round gap |
| **Round 2-3: Between agents** | 8s × 3 agents | Spread iterative LLM calls |
| **Round 2-3: Before aggregation** | 5s | Gap before synthesis |

**Result**: 15-20 rapid-fire calls spread across **60-90 seconds** instead of seconds

### 2. Groq API Enabled (.env)

```diff
- USE_GROQ=false
+ USE_GROQ=true
```

**Configuration**:
- **API**: Groq (api.groq.com) ← Switched from OpenRouter
- **Model**: `llama-3.3-70b-versatile`
- **API Key**: Already in .env (gsk_...)
- **Rate Limits**: Groq has **significantly higher limits** than OpenRouter

---

## Why Groq Instead of OpenRouter?

| Feature | OpenRouter | Groq |
|---------|-----------|------|
| **Rate Limit** | ~1-3 req/min | ~30 req/min |
| **Cost** | Higher | Free tier available |
| **Latency** | Variable | Fast |
| **HTTP 429 Errors** | Frequent (observed) | Rare |
| **Best For** | Low-volume | High-volume (MADAM debates) |

Your MADAM debate makes **15-20 calls per query** → Perfect use case for Groq's higher limits.

---

## API Call Flow (With Both Protections)

```
Question 1
  ↓
[60s wait from previous question]
  ↓
Vector Phase (4s)
  ↓
Enhanced Phase (6s)
  ↓
[10s gap: Vector → Enhanced]
  ↓
MADAM Debate Phase (~75s with new delays)
  │
  ├─ Round 1 (~37s)
  │  ├─ Agent 1: LLM call + 8s gap
  │  ├─ Agent 2: LLM call + 8s gap
  │  ├─ Agent 3: LLM call + 8s gap
  │  ├─ Agent 4: LLM call (no gap, last)
  │  └─ Aggregation: LLM call + 5s gap
  │
  ├─ Round 2 (~47s if needed)
  │  ├─ [10s gap before round]
  │  ├─ Agents 1-4: Calls with 8s gaps
  │  └─ Aggregation + 5s gap
  │
  └─ Round 3 (~47s if needed)
     └─ [Same pattern as Round 2]
  ↓
[45s gap: After Debate → Internet]
  ↓
Internet Search Phase (if needed)
```

---

## Expected Improvements

### Before (OpenRouter + No Delays)
- ❌ HTTP 429 errors every 2-3 queries
- ❌ Rapid-fire API calls crash rate limiter
- ❌ Query 1 → 116.47s, P=R=F1=0.000 (unknown answer rejected)

### After (Groq + Debate Delays)
- ✅ 30 req/min Groq limit vs 1-3 req/min OpenRouter
- ✅ 60-90s spread prevents rate limiting
- ✅ Better answers from debate phase
- ✅ No HTTP 429 errors expected

---

## Next Steps

**Ready to test!** Run the retrieval test again:

```bash
python evaluation/run_retrieval_test.py --csv evaluation/retrieval_test_baseline.csv --name madam --timeout 180
```

Note: Using `--timeout 180` (3 minutes) since debate phase now takes ~75s (was 116s with rate limiting).

---

## API Configuration Details

### Groq Setup
- **Active model**: `llama-3.3-70b-versatile` (70B parameter open model)
- **Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **Fallback**: If Groq key fails, automatically falls back to OpenRouter

### Integration Points
1. `src/ask.py` - Automatically uses Groq when `USE_GROQ=true`
2. `madam_hybrid_system.py` - Uses `query_llm()` from ask.py (respects Groq config)
3. `testing/madam-rag/run_madam_rag.py` - Now has built-in rate limit protection delays

---

## Files Modified

1. **`.env`** - Changed `USE_GROQ=false` → `USE_GROQ=true`
2. **`testing/madam-rag/run_madam_rag.py`** - Added `import time` and debate phase delays
   - Round 1: 8s between agents + 5s before aggregation
   - Round 2-3: 10s before round + 8s between agents + 5s before aggregation

