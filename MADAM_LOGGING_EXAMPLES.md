# MADAM Logging Examples

## What You'll See During Execution

### Console Output (Real-time, INFO level)
```
2025-10-31 14:30:22 - madam_debate - INFO - ================================================================================
2025-10-31 14:30:22 - madam_debate - INFO - 🤖 MADAM DEBATE STARTED
2025-10-31 14:30:22 - madam_debate - INFO - 📌 Query: Perbedaan izin usaha kecil dan besar?
2025-10-31 14:30:22 - madam_debate - INFO - 📊 Agents: 4, Rounds: 3
2025-10-31 14:30:22 - madam_debate - INFO - 📄 Documents: 4 available
2025-10-31 14:30:22 - madam_debate - INFO - ================================================================================

2025-10-31 14:30:22 - madam_debate - INFO - 
2025-10-31 14:30:22 - madam_debate - INFO - 🔄 ROUND 1 - Initial Agent Responses
2025-10-31 14:30:22 - madam_debate - INFO - ────────────────────────────────────────────────────────────────────────────────

2025-10-31 14:30:22 - madam_debate - INFO - 
2025-10-31 14:30:22 - madam_debate - INFO -   🤖 Agent 1/4
2025-10-31 14:30:22 - madam_debate - INFO -      📝 Document preview: Usaha kecil adalah usaha individu atau badan usaha milik...
2025-10-31 14:30:25 - madam_debate - INFO -      ✅ Agent response received (2.34s)
2025-10-31 14:30:25 - madam_debate - INFO -      📌 Answer: Usaha kecil memiliki omset lebih kecil, biasanya di bawah Rp300 juta
2025-10-31 14:30:25 - madam_debate - INFO -      ⏳ 8s gap between agents (rate limit protection)...

2025-10-31 14:30:33 - madam_debate - INFO - 
2025-10-31 14:30:33 - madam_debate - INFO -   🤖 Agent 2/4
2025-10-31 14:30:33 - madam_debate - INFO -      📝 Document preview: Perbedaan utama antara usaha kecil dan besar adalah...
2025-10-31 14:30:36 - madam_debate - INFO -      ✅ Agent response received (2.45s)
2025-10-31 14:30:36 - madam_debate - INFO -      📌 Answer: Usaha besar memiliki tenaga kerja lebih banyak dan struktur organisasi lebih kompleks
2025-10-31 14:30:36 - madam_debate - INFO -      ⏳ 8s gap between agents (rate limit protection)...

2025-10-31 14:30:44 - madam_debate - INFO - 
2025-10-31 14:30:44 - madam_debate - INFO -   🤖 Agent 3/4
2025-10-31 14:30:44 - madam_debate - INFO -      📝 Document preview: Kriteria usaha kecil menurut UU No. 20 Tahun 2008...
2025-10-31 14:30:47 - madam_debate - INFO -      ✅ Agent response received (2.38s)
2025-10-31 14:30:47 - madam_debate - INFO -      📌 Answer: Usaha kecil memiliki aset kurang dari Rp500 juta, sedangkan usaha besar lebih dari itu
2025-10-31 14:30:47 - madam_debate - INFO -      ⏳ 8s gap between agents (rate limit protection)...

2025-10-31 14:30:55 - madam_debate - INFO - 
2025-10-31 14:30:55 - madam_debate - INFO -   🤖 Agent 4/4
2025-10-31 14:30:55 - madam_debate - INFO -      📝 Document preview: Persyaratan izin usaha kecil dan besar berbeda dalam...
2025-10-31 14:30:58 - madam_debate - INFO -      ✅ Agent response received (2.42s)
2025-10-31 14:30:58 - madam_debate - INFO -      📌 Answer: Izin usaha kecil lebih sederhana, sementara usaha besar memerlukan perizinan lebih ketat

2025-10-31 14:30:58 - madam_debate - INFO - 
2025-10-31 14:30:58 - madam_debate - INFO -   🔀 Round 1 Aggregation
2025-10-31 14:30:58 - madam_debate - INFO -      ⏳ 5s gap before aggregation (rate limit protection)...
2025-10-31 14:31:03 - madam_debate - INFO -      🔄 Aggregating 4 agent responses...
2025-10-31 14:31:06 - madam_debate - INFO -      ✅ Aggregation complete (3.12s)
2025-10-31 14:31:06 - madam_debate - INFO -      📌 Aggregated answer: All Correct Answers: ["Omset", "Tenaga kerja", "Aset", "Perizinan"]. Explanation: Agent 1 identifies...

2025-10-31 14:31:06 - madam_debate - INFO - 
2025-10-31 14:31:06 - madam_debate - INFO -   ⏱️  Round 1 Total Time: 47.23s

2025-10-31 14:31:06 - madam_debate - INFO - 
2025-10-31 14:31:06 - madam_debate - INFO - 🔄 ROUND 2 - Iterative Refinement
2025-10-31 14:31:06 - madam_debate - INFO - ────────────────────────────────────────────────────────────────────────────────

2025-10-31 14:31:06 - madam_debate - INFO -   ⏳ 10s gap before round2 (rate limit protection)...

2025-10-31 14:31:16 - madam_debate - INFO - 
2025-10-31 14:31:16 - madam_debate - INFO -   🤖 Agent 1/4
2025-10-31 14:31:16 - madam_debate - INFO -      ✅ Agent response received (2.38s)
2025-10-31 14:31:16 - madam_debate - INFO -      📌 Answer: Perbedaan usaha kecil dan besar mencakup omset, aset, tenaga kerja, dan perizinan
2025-10-31 14:31:16 - madam_debate - INFO -      ⏳ 8s gap between agents (rate limit protection)...

2025-10-31 14:31:24 - madam_debate - INFO - 
2025-10-31 14:31:24 - madam_debate - INFO -   🤖 Agent 2/4
2025-10-31 14:31:24 - madam_debate - INFO -      ✅ Agent response received (2.45s)
2025-10-31 14:31:24 - madam_debate - INFO -      📌 Answer: Perbedaan utama adalah dalam hal modal, skala usaha, dan kompleksitas organisasi
2025-10-31 14:31:24 - madam_debate - INFO -      ⏳ 8s gap between agents (rate limit protection)...

2025-10-31 14:31:32 - madam_debate - INFO - 
2025-10-31 14:31:32 - madam_debate - INFO -   🤖 Agent 3/4
2025-10-31 14:31:32 - madam_debate - INFO -      ✅ Agent response received (2.41s)
2025-10-31 14:31:32 - madam_debate - INFO -      📌 Answer: Kriteria UU 20/2008 membedakan berdasarkan aset dan hasil penjualan tahunan
2025-10-31 14:31:32 - madam_debate - INFO -      ⏳ 8s gap between agents (rate limit protection)...

2025-10-31 14:31:40 - madam_debate - INFO - 
2025-10-31 14:31:40 - madam_debate - INFO -   🤖 Agent 4/4
2025-10-31 14:31:40 - madam_debate - INFO -      ✅ Agent response received (2.39s)
2025-10-31 14:31:40 - madam_debate - INFO -      📌 Answer: Perizinan dan persyaratan administratif berbeda signifikan antara kategori usaha ini

2025-10-31 14:31:40 - madam_debate - INFO - 
2025-10-31 14:31:40 - madam_debate - INFO -   🔀 ROUND 2 Aggregation
2025-10-31 14:31:40 - madam_debate - INFO -      ⏳ 5s gap before aggregation (rate limit protection)...
2025-10-31 14:31:45 - madam_debate - INFO -      🔄 Aggregating 4 agent responses...
2025-10-31 14:31:48 - madam_debate - INFO -      ✅ Aggregation complete (3.05s)
2025-10-31 14:31:48 - madam_debate - INFO -      📌 Aggregated answer: All Correct Answers: ["Perbedaan dalam omset, aset, tenaga kerja", "Perizinan berbeda"]. Explanation: Semua agen...

2025-10-31 14:31:48 - madam_debate - INFO - 
2025-10-31 14:31:48 - madam_debate - INFO -   ⏱️  ROUND 2 Total Time: 51.34s

2025-10-31 14:31:48 - madam_debate - INFO - 
2025-10-31 14:31:48 - madam_debate - INFO - ✅ CONVERGENCE DETECTED - Answers consistent with previous round

2025-10-31 14:31:48 - madam_debate - INFO - 
2025-10-31 14:31:48 - madam_debate - INFO - ================================================================================
2025-10-31 14:31:48 - madam_debate - INFO - ✅ MADAM DEBATE COMPLETED
2025-10-31 14:31:48 - madam_debate - INFO - ⏱️  Total Time: 108.23s (1.8 minutes)
2025-10-31 14:31:48 - madam_debate - INFO - 🎯 Final Answer: Perbedaan utama antara usaha kecil dan besar mencakup omset, aset, tenaga kerja, dan perizinan yang lebih kompleks untuk usaha besar...
2025-10-31 14:31:48 - madam_debate - INFO - ================================================================================
```

## Log File Format

**Location**: `logs/madam_debate_20251031_143022.log`

Each line contains:
```
TIMESTAMP - LOGGER_NAME - LEVEL - MESSAGE
2025-10-31 14:30:22 - madam_debate - INFO - 🤖 MADAM DEBATE STARTED
```

## Key Sections to Look For

### 1. Debate Start
```
🤖 MADAM DEBATE STARTED
📌 Query: [your question]
📊 Agents: 4, Rounds: 3
📄 Documents: 4 available
```

### 2. Agent Responses (Per Agent)
```
🤖 Agent 1/4
   📝 Document preview: [snippet]...
   ✅ Agent response received (2.34s)
   📌 Answer: [agent's answer]
   ⏳ 8s gap between agents (rate limit protection)...
```

### 3. Aggregation
```
🔀 Round 1 Aggregation
   ⏳ 5s gap before aggregation (rate limit protection)...
   🔄 Aggregating 4 agent responses...
   ✅ Aggregation complete (3.12s)
   📌 Aggregated answer: [synthesized answer]
```

### 4. Round Timing
```
⏱️  Round 1 Total Time: 47.23s
⏱️  Round 2 Total Time: 51.34s
```

### 5. Convergence Detection
```
✅ CONVERGENCE DETECTED - Answers consistent with previous round
```
OR
```
⚠️  NO CONVERGENCE - Continuing to next round
```

### 6. Debate Summary
```
✅ MADAM DEBATE COMPLETED
⏱️  Total Time: 108.23s (1.8 minutes)
🎯 Final Answer: [final synthesized answer]
```

## Multiple Queries in Same Log File

When processing 50 queries, the log file will have 50 complete MADAM debate sessions concatenated:

```
[Query 1 Complete Debate Session]
═══════════════════════════════════════════════════════════════════════════════
✅ MADAM DEBATE COMPLETED
Total Time: 108.23s
Final Answer: [answer 1]
═══════════════════════════════════════════════════════════════════════════════

[Query 2 Complete Debate Session - automatically starts next]
🤖 MADAM DEBATE STARTED
📌 Query: Apakah KSO atau JO Bisa Memiliki NIB?
...
═══════════════════════════════════════════════════════════════════════════════
✅ MADAM DEBATE COMPLETED
Total Time: 95.45s
Final Answer: [answer 2]
═══════════════════════════════════════════════════════════════════════════════

[Query 3... and so on for all 50 queries]
```

## Analyzing Timing Patterns

### Example: Extract all timing lines
```powershell
Select-String "Total Time:" logs/madam_debate_*.log
```

Output:
```
logs\madam_debate_20251031_143022.log:98:  ⏱️  Round 1 Total Time: 47.23s
logs\madam_debate_20251031_143022.log:156: ⏱️  Round 2 Total Time: 51.34s
logs\madam_debate_20251031_143022.log:178: ⏱️  Total Time: 108.23s (1.8 minutes)
logs\madam_debate_20251031_143022.log:234: ⏱️  Round 1 Total Time: 45.67s
logs\madam_debate_20251031_143022.log:289: ⏱️  Total Time: 95.45s (1.6 minutes)
```

### Extract convergence outcomes
```powershell
Select-String "CONVERGENCE|NO CONVERGENCE" logs/madam_debate_*.log
```

Output:
```
logs\madam_debate_20251031_143022.log:170: ✅ CONVERGENCE DETECTED - Answers consistent with previous round
logs\madam_debate_20251031_143022.log:289: ⚠️  NO CONVERGENCE - Continuing to next round
logs\madam_debate_20251031_143022.log:301: ✅ CONVERGENCE DETECTED - Answers consistent with previous round
```

## Performance Metrics from Logs

### Count convergence rate
```powershell
$conv = (Select-String "CONVERGENCE DETECTED" logs/madam_debate_*.log).Count
$total = (Select-String "MADAM DEBATE COMPLETED" logs/madam_debate_*.log).Count
Write-Host "Convergence rate: $($conv / $total * 100)%"
```

### Average debate time
```powershell
$times = (Select-String "Total Time: ([\d.]+)s" logs/madam_debate_*.log | 
         ForEach-Object { [float]($_.Matches.Groups[1].Value) })
$avg = $times | Measure-Object -Average | Select-Object -ExpandProperty Average
Write-Host "Average debate time: ${avg}s"
```

### Find slowest queries
```powershell
Select-String "Total Time:" logs/madam_debate_*.log | 
Sort-Object { [float]$_.Line.Split()[-2] } -Descending | 
Select-Object -First 5
```

## Troubleshooting with Logs

### Issue: Finding "unknown" answers
```powershell
Select-String "unknown" logs/madam_debate_*.log
```

If found, it means the aggregation couldn't determine a consensus answer.

### Issue: Finding slow responses
```powershell
Select-String "Agent response received \(([0-9.]+)s\)" logs/madam_debate_*.log |
Where-Object { [float]$_.Matches.Groups[1].Value -gt 5 }
```

Shows agents taking more than 5 seconds (might indicate API issues).

### Issue: Checking gap execution
```powershell
Select-String "gap.*rate limit protection" logs/madam_debate_*.log | 
Measure-Object | Select-Object -ExpandProperty Count
```

Should show: ~11 gaps per query (3 gaps in Round 1, 5 gaps in Round 2, 3 gaps in Round 3)

---

## Log File Size

**Typical sizes**:
- Single query debate: 3-5 KB
- 50 queries: 150-250 KB
- Full test session: ~1-5 MB

**To view file size**:
```powershell
(Get-Item logs/madam_debate_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Select-Object -ExpandProperty Length) / 1KB
```

