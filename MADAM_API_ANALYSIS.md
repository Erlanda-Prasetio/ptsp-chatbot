# MADAM Debate Phase Analysis: API Call Patterns & Rate Limiting

## Issue Summary
Query `old_51` (Perbedaan izin usaha kecil dan besar?) ran for **116.47 seconds** but returned **P=0.000, R=0.000, F1=0.000** (no correct chunks matched).

The logs show repeated OpenRouter API calls with rate limiting errors (HTTP 429) during the debate phase.

---

## Root Cause Analysis

### 1. **MADAM Debate Computational Complexity**

The MADAM debate runs **3 rounds** by default with **4 agents** (debate_top_k=4):

#### Round 1: Initial Agent Responses
- **4 LLM calls** (1 per agent answering the question independently)
- 1 **aggregation call** to synthesize responses
- **Total: 5 API calls**

#### Rounds 2-3: Iterative Debate (if convergence not reached)
- **4 LLM calls per round** (each agent sees other agents' responses)
- 1 **aggregation call** per round
- **Total per round: 5 API calls × 2 rounds = 10 API calls**

#### **Total API Calls Per Query**
- **Best case** (convergence in Round 1): **5 calls**
- **Worst case** (all 3 rounds): **15-20 calls** ✅ *This matches your observation*

### 2. **Why P=R=F1=0.000 Despite 116.47 seconds?**

The debate phase has a **quality check** that returns `None` if the aggregation contains "unknown":

```python
# Lines 228-233 in madam_hybrid_system.py
final_aggregation = records.get("final_aggregation", "") if isinstance(records, dict) else ""
if not final_aggregation or "unknown" in final_aggregation.lower():
    print("⚠️  MADAM debate produced unknown answer")
    phase_log.append({...})
    return None  # ❌ No result returned!
```

**Result**: The debate phase took 116.47s but returned `None`, so the system fell back to internet search (Phase 4) which also returned empty results → **P=R=F1=0.000**

### 3. **OpenRouter Rate Limiting (HTTP 429)**

Your logs show:
```
❌ HTTP error 0: 429 Client Error: Too Many Requests
⏱️  Rate limit throttle: waiting 0.7s...
```

This indicates:
- **Rate limit exceeded** during the 15-20 debate phase API calls
- The system **retries with exponential backoff** (0.7s → 0.3s → 1.2s)
- After multiple retries, the call may **fail silently or return partial results**

---

## Current Rate Limiting Strategy

| Layer | Delay | Purpose |
|-------|-------|---------|
| Between questions | 60s | API recovery between full retrieval cycles |
| Vector → Enhanced | 10s | Between retrieval phases |
| Enhanced → MADAM | 10s | Before debate phase |
| MADAM → Internet | **45s** ✅ NEW | After 15-20 LLM calls (debate phase) |

**Problem**: These delays are **between phases**, not **within the MADAM debate itself**.

The 15-20 OpenRouter API calls happen **sequentially within a single debate phase** with **no delays between them** → **rapid-fire requests trigger rate limits**.

---

## Recommendations

### Option 1: Add Delays Between Debate Rounds
Add 5-10 second delays between MADAM debate rounds to spread out the 15-20 API calls:

```python
# In run_madam_rag.py around line 110-115
for t in range(1, num_rounds):
    if t > 1:
        print("⏳ 5s gap between debate rounds (rate limit protection)...")
        time.sleep(5)
    # ... debate logic
```

**Impact**: Spreads 15-20 calls over ~35-50 seconds instead of rapid-fire
**Risk**: Extends debate phase time further

### Option 2: Add Delays Between Individual Agent Calls
Add 2-3 second delays between each agent's LLM call within the debate phase:

```python
def multi_agent_debate(query: str, documents: List[str], generator, num_rounds: int = 3):
    # ...
    for doc in documents:
        response = agent_response(query, doc, generator)
        time.sleep(2)  # Gap between agent calls
```

**Impact**: Spreads calls naturally; 4 agents × 2s = ~8s overhead per round
**Risk**: Extends total time proportionally

### Option 3: Reduce Debate Complexity
Reduce `debate_rounds` or `debate_top_k` to lower API call volume:

```python
# Current: 15-20 calls per query
# Option: 2 rounds × 4 agents × 2 agg = 10 calls
# Option: 3 rounds × 2 agents × 2 agg = 8 calls
```

**Impact**: Faster execution, fewer rate limit hits
**Risk**: Lower debate quality

### Option 4: Implement OpenRouter Backoff Strategy
Your current code has retry logic. Consider:
- Increase max retries from 5 to 10
- Implement exponential backoff (1s → 2s → 4s → 8s)
- Add circuit breaker: skip debate if 3+ rate limit hits

---

## Current Debate Configuration

```python
# madam_hybrid_system.py line 69-74
def __init__(self, debate_rounds: int = 3, debate_top_k: int = 4):
    self.debate_rounds = debate_rounds      # 3 rounds
    self.debate_top_k = debate_top_k        # 4 agents
```

**API Calls Per Configuration**:
- **3 rounds, 4 agents**: 15-20 calls ✅ Confirmed
- **2 rounds, 4 agents**: 10 calls
- **3 rounds, 2 agents**: 8 calls

---

## Why Query 1 Took 116.47s

1. **Vector phase**: ~4s (no match, quality=0)
2. **Enhanced phase**: ~6s (no match, quality=0)
3. **MADAM debate phase**: ~100s
   - Round 1: ~30s (5 calls: 4 agents + 1 agg)
   - Rate limiting hits (429 errors)
   - Retries with backoff
   - Round 2-3: Similar pattern
4. **All 3 rounds run but produce "unknown"** → return None
5. **Internet phase**: Falls back to internet (included in 116.47s or separate?)

**Total**: 116.47s spent, but result rejected due to "unknown" answer

---

## Recommendation for Your System

**Best approach for ptspRag**: Add **inter-round delays in MADAM debate** (Option 2)

1. Modify `testing/madam-rag/run_madam_rag.py` to add 3-5s delays between agent calls
2. This spreads the 15-20 API calls across ~60-90 seconds instead of rapid-fire
3. Reduces rate limiting without sacrificing debate quality
4. Combined with your existing 45s post-debate gap = solid rate limiting

**Files to modify**:
- `testing/madam-rag/run_madam_rag.py` (add inter-call delays)
- Optional: `madam_hybrid_system.py` (reduce debate_rounds to 2)

