# MADAM Logging Quick Reference

## View Latest Log File

**PowerShell**:
```powershell
# Watch the latest log in real-time
Get-Content -Path (Get-ChildItem logs/madam_debate_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Wait

# Or open it
code (Get-ChildItem logs/madam_debate_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

**Bash/Linux**:
```bash
tail -f $(ls -t logs/madam_debate_*.log | head -1)
```

## Log Output Example (During Execution)

```
2025-10-31 14:30:22 - madam_debate - INFO - ================================================================================
2025-10-31 14:30:22 - madam_debate - INFO - 🤖 MADAM DEBATE STARTED
2025-10-31 14:30:22 - madam_debate - INFO - 📌 Query: Perbedaan izin usaha kecil dan besar?
2025-10-31 14:30:22 - madam_debate - INFO - 📊 Agents: 4, Rounds: 3
2025-10-31 14:30:22 - madam_debate - INFO - 📄 Documents: 4 available
2025-10-31 14:30:22 - madam_debate - INFO - ================================================================================

2025-10-31 14:30:22 - madam_debate - INFO - 🔄 ROUND 1 - Initial Agent Responses
2025-10-31 14:30:22 - madam_debate - INFO - ────────────────────────────────────────────────────────────────────────────────

2025-10-31 14:30:22 - madam_debate - INFO -   🤖 Agent 1/4
2025-10-31 14:30:22 - madam_debate - INFO -      📝 Document preview: Usaha kecil adalah usaha individu...
2025-10-31 14:30:25 - madam_debate - INFO -      ✅ Agent response received (2.34s)
2025-10-31 14:30:25 - madam_debate - INFO -      📌 Answer: Usaha kecil memiliki modal kurang dari...
2025-10-31 14:30:25 - madam_debate - INFO -      ⏳ 8s gap between agents (rate limit protection)...

2025-10-31 14:30:33 - madam_debate - INFO -   🤖 Agent 2/4
2025-10-31 14:30:33 - madam_debate - INFO -      📝 Document preview: Perbedaan utama antara usaha kecil...
2025-10-31 14:30:36 - madam_debate - INFO -      ✅ Agent response received (2.45s)
2025-10-31 14:30:36 - madam_debate - INFO -      📌 Answer: Usaha besar memiliki omset lebih besar...
2025-10-31 14:30:36 - madam_debate - INFO -      ⏳ 8s gap between agents (rate limit protection)...

...

2025-10-31 14:32:10 - madam_debate - INFO - ================================================================================
2025-10-31 14:32:10 - madam_debate - INFO - ✅ MADAM DEBATE COMPLETED
2025-10-31 14:32:10 - madam_debate - INFO - ⏱️  Total Time: 108.23s (1.8 minutes)
2025-10-31 14:32:10 - madam_debate - INFO - 🎯 Final Answer: Usaha kecil dan besar memiliki perbedaan...
2025-10-31 14:32:10 - madam_debate - INFO - ================================================================================
```

## Log File Location During Test Run

When you run the retrieval test:
```bash
python evaluation/run_retrieval_test.py --csv evaluation/retrieval_test_baseline.csv --name madam --timeout 180
```

A new log file is created: `logs/madam_debate_YYYYMMDD_HHMMSS.log`

### Multiple Queries = Multiple Log Entries

If the test runs 50 queries, **ONE log file** will contain all 50 MADAM debate sessions:

```
logs/madam_debate_20251031_143022.log
├─ Query 1: "Perbedaan izin usaha kecil dan besar?"
├─ Query 2: "Apakah KSO atau JO Bisa Memiliki NIB?"
├─ Query 3: "Apa Saja KBLI yang Diwajibkan Bermitra dengan UMKM?"
├─ ...
└─ Query 50: "Bagaimana cara mengurus izin untuk usaha katering rumahan?"
```

## Searching Logs

### Find specific query
```powershell
Select-String "Query: Perbedaan izin" logs/madam_debate_*.log
```

### Find convergence patterns
```powershell
Select-String "CONVERGENCE|NO CONVERGENCE" logs/madam_debate_*.log
```

### Find timing information
```powershell
Select-String "Total Time:" logs/madam_debate_*.log
```

### Find errors
```powershell
Select-String "ERROR|❌" logs/madam_debate_*.log
```

## Key Information to Track

### ✅ Signs of Good Execution
- [ ] All agents respond within 2-3 seconds each
- [ ] Aggregations complete within 3-5 seconds
- [ ] Convergence detected (usually in Round 2)
- [ ] Final answer is NOT "unknown"
- [ ] Total time ~45-75 seconds per query

### ⚠️ Signs of Issues
- [ ] Agent response times > 5 seconds (slow/stuck)
- [ ] Aggregation times > 10 seconds
- [ ] Final answer = "unknown" (no consensus)
- [ ] No convergence after 3 rounds
- [ ] Any "ERROR" or HTTP errors in logs

## File Management

```powershell
# List all logs
Get-ChildItem logs/madam_debate_*.log | Sort-Object LastWriteTime -Descending

# Delete logs older than 7 days
Get-ChildItem logs/madam_debate_*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item

# Count total log size
(Get-ChildItem logs/madam_debate_*.log | Measure-Object -Property Length -Sum).Sum / 1MB
```

## Log Interpretation

### Timing Analysis
Example log line timestamps:
```
14:30:22 - Start Round 1
14:30:25 - Agent 1 done (3s)
14:30:33 - Agent 2 done (8s including gap)
14:32:10 - Debate complete (108s total)
```

### Rate Limiting Protection Verification
Look for these patterns:
```
⏳ 8s gap between agents (rate limit protection)...
⏳ 5s gap before aggregation (rate limit protection)...
⏳ 10s gap before round2 (rate limit protection)...
```

If you DON'T see these gaps being logged → Check if code has spaces/indentation issues

### Convergence Tracking
- **Round 1**: Diverse answers expected
- **Round 2**: Agents refine based on others' input
- **Convergence**: When answers become similar
  ```
  ✅ CONVERGENCE DETECTED - Answers consistent with previous round
  ```
- **No Convergence**: Debate continues to Round 3

## Integration with Retrieval Test

When you run:
```bash
python evaluation/run_retrieval_test.py --csv evaluation/retrieval_test_baseline.csv --name madam --timeout 180
```

The workflow is:
1. Test loads 50 queries from CSV
2. For EACH query:
   - Vector phase (4s) - no logging
   - Enhanced phase (6s) - no logging
   - **MADAM debate phase (75s) - FULL LOGGING TO FILE**
   - Internet phase (if needed) - no logging
3. Single log file captures all MADAM activity

### To Monitor in Real-Time
**PowerShell** (in another terminal):
```powershell
$logFile = (Get-ChildItem logs/madam_debate_*.log -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1)
if ($logFile) { Get-Content $logFile.FullName -Wait }
```

This will show MADAM debate progress as queries are processed!

