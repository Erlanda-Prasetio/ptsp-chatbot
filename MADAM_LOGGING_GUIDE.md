# MADAM Debate Logging Guide

## Overview

Comprehensive logging has been added to the MADAM debate phase to track every step of the multi-agent reasoning process. All logs are saved to disk and displayed in the console.

## Log Locations

**Log Directory**: `logs/`

**Log File Naming**: `madam_debate_YYYYMMDD_HHMMSS.log`

Example: `logs/madam_debate_20251031_143022.log`

## What Gets Logged

### Session Start
```
================================================================================
🤖 MADAM DEBATE STARTED
📌 Query: [Your question here]
📊 Agents: 4, Rounds: 3
📄 Documents: 4 available
================================================================================
```

### Round 1: Initial Agent Responses
```
🔄 ROUND 1 - Initial Agent Responses
────────────────────────────────────────────────────────────────────────────────

  🤖 Agent 1/4
     📝 Document preview: [document snippet]...
     ✅ Agent response received (2.34s)
     📌 Answer: [agent's answer]
     ⏳ 8s gap between agents (rate limit protection)...

  🤖 Agent 2/4
     ...

  🤖 Agent 3/4
     ...

  🤖 Agent 4/4
     📝 Document preview: [document snippet]...
     ✅ Agent response received (2.45s)
     📌 Answer: [agent's answer]

  🔀 Round 1 Aggregation
     ⏳ 5s gap before aggregation (rate limit protection)...
     🔄 Aggregating 4 agent responses...
     ✅ Aggregation complete (3.12s)
     📌 Aggregated answer: [synthesized answer]

  ⏱️  Round 1 Total Time: 47.23s
```

### Round 2-3: Iterative Refinement (if no convergence)
```
🔄 ROUND 2 - Iterative Refinement
────────────────────────────────────────────────────────────────────────────────

  ⏳ 10s gap before round2 (rate limit protection)...

  🤖 Agent 1/4
     ✅ Agent response received (2.38s)
     📌 Answer: [updated answer]
     ⏳ 8s gap between agents (rate limit protection)...

  [... agents 2-4 ...]

  🔀 ROUND 2 Aggregation
     ⏳ 5s gap before aggregation (rate limit protection)...
     🔄 Aggregating 4 agent responses...
     ✅ Aggregation complete (3.05s)
     📌 Aggregated answer: [refined answer]

  ⏱️  ROUND 2 Total Time: 51.34s

✅ CONVERGENCE DETECTED - Answers consistent with previous round
```

### Session End
```
================================================================================
✅ MADAM DEBATE COMPLETED
⏱️  Total Time: 120.45s (2.0 minutes)
🎯 Final Answer: [final synthesized answer]
================================================================================
```

## Log Levels

| Level | Symbol | Purpose |
|-------|--------|---------|
| **INFO** | ✅, 🤖, 📌 | Main process flow, answers, decisions |
| **DEBUG** | 📝, ⏳, ⏱️ | Detailed timing, gaps, document previews |

- **Console Output**: INFO level (visible during execution)
- **File Output**: DEBUG level (complete detailed log)

## Key Metrics Tracked

1. **Per Agent**
   - Agent number and response time
   - Answer snippet
   - Rate limit gap delays

2. **Per Aggregation**
   - Number of responses being synthesized
   - Aggregation completion time
   - Aggregated answer preview

3. **Per Round**
   - Round name and iteration number
   - Total time for round
   - Convergence status

4. **Session Total**
   - Total debate time
   - Final answer quality check
   - Convergence history

## Example Log Analysis

### Timing Breakdown
```
Round 1 Total Time: 47.23s
  = 8s + 2.34s (agent 1)
  + 8s + 2.45s (agent 2)
  + 8s + 2.38s (agent 3)
  + 2.42s (agent 4, no gap after)
  + 5s (aggregation gap)
  + 3.12s (aggregation)
  ≈ 47.23s ✓
```

### Rate Limiting Effectiveness
```
Total API calls: 15-20 per query
Spread across: 120-150 seconds
Gaps added: 8s between agents × 3 + 10s per round × 2 + 5s per agg × 3
Result: Prevents OpenRouter 429 errors, Groq handles easily
```

### Convergence Pattern
```
Round 1: Agents give diverse answers
Round 2: Agents refine after hearing others
✅ Convergence: All agents agree (or converge to similar answer)
→ Debate stops, returns Round 2 aggregation
```

## Using the Logs

### Find a Specific Query
```bash
grep "Query: Your question" logs/madam_debate_*.log
```

### Check Total Time
```bash
grep "Total Time:" logs/madam_debate_*.log
```

### View Rate Limiting Behavior
```bash
grep "gap" logs/madam_debate_*.log
```

### Check Convergence
```bash
grep "CONVERGENCE\|NO CONVERGENCE" logs/madam_debate_*.log
```

### Get All Final Answers
```bash
grep "Final Answer:" logs/madam_debate_*.log
```

## File Management

- **New log file per session** (named with timestamp)
- **Keep logs for debugging** rate limiting and convergence issues
- **Clear old logs** with: `rm logs/madam_debate_*.log` (older than 7 days)

## Integration Points

Logging is automatic in:
- `testing/madam-rag/run_madam_rag.py` - Multi-agent debate core
- Called by `madam_hybrid_system.py` - Main RAG system
- Used by `rag_api.py` - FastAPI endpoint

All logs are written to disk regardless of where MADAM debate is invoked.

## What to Look For

### ✅ Healthy Execution
- All agents return responses within 2-3 seconds
- Aggregations complete within 3-5 seconds
- Convergence typically achieved by Round 2
- No rate limiting errors (no 429 HTTP errors)
- Final answer is NOT "unknown"

### ⚠️ Issues to Watch
- Agent response times > 5 seconds (timeout/overload)
- Aggregation times > 10 seconds (stuck/error)
- No convergence after all 3 rounds (conflicting documents)
- Final answer contains "unknown" (no consensus)
- Any HTTP/network errors in logs

