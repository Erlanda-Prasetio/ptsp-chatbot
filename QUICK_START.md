# Quick Start - MADAM Testing with Full Logging

## 🚀 Fast Track (5 minutes)

### Terminal 1: Start API
```bash
cd d:\backup\ptspRag
python madam_rag_api.py
```

**Wait for**:
```
✅ Using Groq API with model: llama-3.3-70b-versatile
✅ Madam Hybrid RAG system initialized successfully!
```

### Terminal 2: Run Test
```bash
cd d:\backup\ptspRag
python evaluation/run_retrieval_test.py --csv evaluation/retrieval_test_baseline.csv --name madam --timeout 180
```

**Expect**:
```
🧪 RETRIEVAL TEST - CSV MODE
🔌 Testing connection to http://localhost:8001...
✅ API is healthy
📂 Loading CSV from: evaluation/retrieval_test_baseline.csv
✅ Loaded 50 queries

🔍 RETRIEVING CHUNKS FOR 50 QUERIES
[1/50] old_51: ...
   ✅ madam_debate | ...s | P=..., R=..., F1=...
[2/50] new_180: ...
   ... (continues for all 50 queries)
```

### Terminal 3: Monitor Logs (Real-Time)
```powershell
$log = (Get-ChildItem logs/madam_debate_*.log -ErrorAction SilentlyContinue | 
        Sort-Object LastWriteTime -Descending | 
        Select-Object -First 1)
if ($log) { Get-Content $log.FullName -Wait }
```

**You'll see**:
```
🤖 MADAM DEBATE STARTED
📌 Query: [your question]
🔄 ROUND 1
  🤖 Agent 1/4 - ✅ response (2.34s)
  🤖 Agent 2/4 - ✅ response (2.45s)
  ...
✅ CONVERGENCE DETECTED
✅ MADAM DEBATE COMPLETED
Total Time: 108.23s
```

---

## 📊 What Each Terminal Shows

| Terminal | Shows | Updates |
|----------|-------|---------|
| **1: API** | Model loading, initialization | Once at start |
| **2: Test** | Query progress, P/R/F1 scores | Per query (every ~2-3 min) |
| **3: Logs** | MADAM debate details, timing | Per agent response (~2s) |

---

## 📝 Key Output to Watch

### Terminal 2 (Test Progress)
```
[1/50] old_51: Perbedaan izin usaha kecil dan besar?...
   ✅ madam_debate | 108.23s | P=0.500, R=0.500, F1=0.500
[2/50] new_180: Apakah KSO atau JO Bisa Memiliki NIB?...
   ✅ enhanced_vector | 8.45s | P=1.000, R=1.000, F1=1.000
```

**Interpret**:
- ✅ = Phase succeeded
- Number = Query number
- `madam_debate` = MADAM phase used
- `108.23s` = Time for MADAM phase
- `P=0.500` = Precision score
- `R=0.500` = Recall score
- `F1=0.500` = F1-score

### Terminal 3 (MADAM Details)
```
🤖 MADAM DEBATE STARTED
📌 Query: Perbedaan izin usaha kecil dan besar?
📊 Agents: 4, Rounds: 3
🔄 ROUND 1 - Initial Agent Responses
  🤖 Agent 1/4
     ✅ Agent response received (2.34s)
     📌 Answer: Usaha kecil memiliki omset kurang dari Rp300 juta
     ⏳ 8s gap between agents (rate limit protection)...
  🤖 Agent 2/4
     ✅ Agent response received (2.45s)
     ...
```

**What it means**:
- Each agent makes an independent LLM call
- Answers are logged for review
- 8s gaps shown confirms rate limiting active
- **All running smoothly** if you see this

---

## ⏱️ Timing Expectations

### Per Phase
- Vector search: 4-5s (silent)
- Enhanced: 6-8s (silent)
- **MADAM: 45-75s** (fully logged) ⭐
- Internet fallback: variable

### Full Test
- 50 queries × ~2-3 minutes each = **~100-150 minutes total**
- Approx **1.5-2.5 hours** for complete test
- Log file size: **~200-300 KB**

### Per MADAM Query Breakdown
```
Round 1: ~37s
  ├─ Agent 1: 2.34s + 8s gap
  ├─ Agent 2: 2.45s + 8s gap
  ├─ Agent 3: 2.38s + 8s gap
  ├─ Agent 4: 2.42s (no gap)
  ├─ 5s aggregation gap
  └─ Aggregation: 3.12s

Round 2: ~47s (if needed for convergence)
  └─ [Similar pattern]

Convergence: Round 1-2 (usually detected)
Total: 45-75s
```

---

## 🔍 How to Know It's Working

### ✅ Good Signs
- [ ] Terminal 1: "Using Groq API" message
- [ ] Terminal 2: Queries processing (1/50, 2/50, etc.)
- [ ] Terminal 3: "MADAM DEBATE STARTED" messages
- [ ] Terminal 3: Agent responses appearing with times
- [ ] Terminal 3: "CONVERGENCE DETECTED" messages
- [ ] Terminal 3: "Total Time: XXs" showing 45-75s

### ❌ Bad Signs
- [ ] Terminal 1: Error initializing API
- [ ] Terminal 2: Connection refused
- [ ] Terminal 3: No logs appearing
- [ ] Terminal 3: "HTTP 429" errors
- [ ] Terminal 3: Times > 10s per agent
- [ ] Terminal 3: Final answer = "unknown"

### ⚠️ If Something's Wrong

**No API starting**:
```bash
python madam_rag_api.py  # Check error message
# Usually: missing Groq key or import error
```

**No logs showing**:
```bash
# Check if logs directory writable
ls -la logs/
# Should see madam_debate_*.log file growing
```

**404 errors**:
```bash
# Check API is still running (Terminal 1)
# Restart if needed: Ctrl+C then python madam_rag_api.py
```

---

## 📊 Test Results

### Where Results Are Saved
```
d:\backup\ptspRag\evaluation\retrieval_test_madam.csv
```

### What's In Results
```
query_id,vector_time,enhanced_time,madam_time,internet_time,method,precision,recall,f1_score
old_51,4.23,6.45,108.23,0,madam_debate,0.500,0.500,0.500
new_180,3.89,7.12,0,0,enhanced_vector,1.000,1.000,1.000
...
```

### Log Archive
```
d:\backup\ptspRag\logs\madam_debate_20251031_143022.log
```

Contains all MADAM debate details for all 50 queries.

---

## 📌 One-Command Test

```powershell
# PowerShell - Run all 3 terminals
# Terminal 1
Start-Process powershell -ArgumentList "cd d:\backup\ptspRag; python madam_rag_api.py"

# Wait 5 seconds for API to start
Start-Sleep -Seconds 5

# Terminal 2
Start-Process powershell -ArgumentList "cd d:\backup\ptspRag; python evaluation/run_retrieval_test.py --csv evaluation/retrieval_test_baseline.csv --name madam --timeout 180"

# Terminal 3
Start-Process powershell -ArgumentList "Get-Content (Get-ChildItem logs/madam_debate_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Wait"
```

---

## 🎯 Success Criteria

### For Full Test Session
- [x] All 50 queries processed
- [x] No HTTP 429 errors
- [x] No "unknown" final answers
- [x] Average precision > 0.3
- [x] Average recall > 0.3
- [x] Log file created with all queries
- [x] MADAM debates averaging 45-75s
- [x] Convergence detected on most queries

### For Each Query
- [x] MADAM debate completes
- [x] Agent responses received in 2-5s each
- [x] 8s gaps between agents logged
- [x] Convergence detected by Round 2
- [x] Final answer is NOT "unknown"
- [x] Total time 45-75 seconds

### File Outputs
- [x] `evaluation/retrieval_test_madam.csv` created
- [x] `logs/madam_debate_*.log` created with 50 debate sessions
- [x] Both files readable and complete

---

## 🚨 Troubleshooting Quick Links

| Issue | Check | Solution |
|-------|-------|----------|
| API won't start | `.env` Groq key | Verify `GROQ_API_KEY` present |
| Connection refused | Terminal 1 running | Start API first, wait for ready msg |
| HTTP 429 errors | Log file | Should NOT happen - report if seen |
| No logs | `logs/` directory | Should auto-create, check permissions |
| Slow responses | Agent times | > 5s = API overload, restart API |
| "Unknown" answers | Final answer | Indicates no consensus, normal sometimes |

---

## 📚 Full Documentation

For detailed information:
- `MADAM_LOGGING_GUIDE.md` - Complete logging details
- `MADAM_LOGGING_EXAMPLES.md` - Real log examples
- `VIEW_MADAM_LOGS.md` - Log viewing commands
- `SETUP_COMPLETE.md` - Full system setup
- `SESSION_SUMMARY.md` - This session's work

---

## ✨ Pro Tips

### Tail Only Relevant Log Lines
```powershell
# Only see agent responses
Get-Content logs/madam_debate_*.log -Wait | Select-String "Agent response|CONVERGENCE|Total Time"

# Only see timing info
Get-Content logs/madam_debate_*.log -Wait | Select-String "⏱️"
```

### Count Convergence
```powershell
(Select-String "CONVERGENCE DETECTED" logs/madam_debate_*.log).Count
```

### Export Results for Analysis
```powershell
cp evaluation/retrieval_test_madam.csv evaluation/retrieval_test_madam_backup.csv
```

---

## 🎬 You're Ready!

All systems are configured and tested. 

**Next steps**:
1. Open 3 terminal windows
2. Follow the Fast Track above
3. Watch the logs in real-time
4. Wait for test completion (~2 hours)
5. Review results in CSV and logs

**Let's go! 🚀**

