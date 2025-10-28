# 🔍 MADAM Hybrid RAG System - Retrieval Test Report

## Executive Summary

The MADAM Hybrid RAG System was tested on **50 ground-truth queries** from the baseline dataset. The system uses a 4-phase fallback strategy:
1. **Vector Search** (pure vector embedding similarity)
2. **Enhanced Vector** (with contextual enhancement)
3. **MADAM Debate** (multi-agent debate phase)
4. **Internet Fallback** (online search if needed)

### Key Metrics
- **Total Queries Tested**: 50
- **Mean F1 Score**: 0.556
- **Mean Precision**: 0.556
- **Mean Recall**: 0.556
- **Perfect Retrievals (F1=1.0)**: 19 queries (38%)
- **Failed Retrievals (F1=0.0)**: 11 queries (22%)

---

## 📊 Performance by Search Method

| Method | Queries | Avg F1 | Avg Precision | Avg Recall | High (>0.7) | Perfect (1.0) |
|--------|---------|--------|---------------|------------|-------------|---------------|
| **enhanced_vector** | 19 | 0.737 | 0.737 | 0.737 | 12 | 11 |
| **vector_only** | 15 | 0.627 | 0.627 | 0.627 | 6 | 6 |
| **madam_debate** | 16 | 0.275 | 0.275 | 0.275 | 2 | 2 |

### Key Findings:

**✅ Enhanced Vector Performs Best**
- Average F1: 0.737 (highest)
- 63% high performance queries (12/19)
- 58% perfect retrievals (11/19)

**⚠️ Vector-Only Shows Moderate Performance**
- Average F1: 0.627 (middle)
- 40% high performance queries (6/15)
- 40% perfect retrievals (6/15)

**❌ MADAM Debate Underperforms**
- Average F1: 0.275 (lowest)
- Only 13% high performance queries (2/16)
- Only 13% perfect retrievals (2/16)
- Trigger Issues: MADAM debate seems to be triggered for harder queries, which impacts performance

---

## 📂 Performance by Question Category

| Category | Count | Avg F1 | Perfect | High | Medium | Low | Failed |
|----------|-------|--------|---------|------|--------|-----|--------|
| **Technical** | 9 | 0.867 | 7 | 0 | 2 | 0 | 0 |
| **NIB** | 4 | 0.850 | 3 | 0 | 1 | 0 | 0 |
| **General** | 7 | 0.686 | 4 | 0 | 2 | 0 | 1 |
| **Procedure** | 24 | 0.417 | 4 | 1 | 11 | 1 | 7 |
| **Licensing** | 5 | 0.280 | 1 | 0 | 1 | 0 | 3 |
| **Support** | 1 | 0.400 | 0 | 0 | 1 | 0 | 0 |

### Category Insights:

**🟢 Strongest Categories**
- **Technical** (F1: 0.867): Best performance, 78% perfect match
- **NIB** (F1: 0.850): Very consistent, 75% perfect match
- **General** (F1: 0.686): Good baseline questions perform well

**🔴 Weakest Categories**
- **Procedure** (F1: 0.417): Largest category with most failures (7/24 failed)
- **Licensing** (F1: 0.280): Most problematic, 60% failure rate

---

## 🗂️ Performance by Dataset

| Dataset | Count | Avg F1 | Perfect | High | Medium | Low | Failed |
|---------|-------|--------|---------|------|--------|-----|--------|
| **OLD Dataset** | 27 | 0.533 | 11 | 0 | 14 | 1 | 1 |
| **NEW Dataset** | 23 | 0.583 | 8 | 1 | 4 | 0 | 10 |

- **NEW Dataset has more failures** (10 vs 1), but higher average F1
- **OLD Dataset is more consistent** (lower variance)

---

## ❌ Failed Retrievals Analysis (F1 = 0.0)

**11 queries (22%) had complete retrieval failures:**

1. **Procedure-related failures (7 queries)**
   - Procedure mergers, OSS processes, licensing procedures
   - These require complex procedural understanding

2. **Licensing failures (3 queries)**
   - Risk-based oversight, MPP advantages, business license differences
   - Specialized licensing knowledge not well covered

3. **General failures (1 query)**
   - "Siapa penanggung jawab layanan DPMPTSP di daerah?"
   - Administrative responsibility questions

**Root Causes:**
- Low semantic similarity between query and relevant chunks
- Questions requiring exact procedural knowledge
- Specialized licensing/regulatory terminology mismatches

---

## ✅ Perfect Retrievals (F1 = 1.0)

**19 queries (38%) achieved perfect matches:**

Distribution:
- **enhanced_vector**: 11 (58%)
- **vector_only**: 6 (32%)
- **madam_debate**: 2 (11%)

Examples:
- "Apakah KSO atau JO Bisa Memiliki NIB?" ✅
- "Apa Saja KBLI yang Diwajibkan Bermitra dengan UMKM?" ✅
- "Saya khawatir data OSS saya hilang, apa backupnya?" ✅

---

## 🎯 Recommendations

### 1. **Improve MADAM Debate Handling**
- Current F1: 0.275 (significant underperformance)
- The debate phase is triggered for complex queries but reduces retrieval accuracy
- **Action**: Refine when MADAM debate is triggered (only for ambiguous cases)

### 2. **Enhance Procedure Category Performance**
- Currently: F1: 0.417 (24 queries, most failures)
- **Actions**:
  - Add more structured procedure documentation
  - Improve chunk segmentation for step-by-step procedures
  - Use template-based retrieval for procedure queries

### 3. **Strengthen Licensing Knowledge Base**
- Currently: F1: 0.280 (5 queries, 60% failure)
- **Actions**:
  - Ensure comprehensive licensing regulation chunks
  - Create better taxonomy for licensing types
  - Add comparison chunks (e.g., small vs. large license differences)

### 4. **Optimize Search Method Selection**
- **Keep enhanced_vector as default** (F1: 0.737)
- Reduce reliance on MADAM debate (F1: 0.275)
- Vector-only as fallback (F1: 0.627)

### 5. **Dataset-Specific Improvements**
- **NEW Dataset**: Reduce failures (10 failures vs 1 in OLD)
- **OLD Dataset**: Maintain consistency, good baseline

---

## 📈 Distribution Analysis

```
Performance Distribution:
✅ Perfect (1.0):   19 queries (38%)
🟡 High (0.7-1.0):   1 query   (2%)
🟠 Medium (0.3-0.7): 18 queries (36%)
🔴 Low (0-0.3):      1 query   (2%)
❌ Failed (0.0):    11 queries (22%)
```

---

## 🔧 System Configuration

- **API**: FastAPI on port 8001
- **LLM Backend**: OpenRouter (mistralai/mistral-small-3.2-24b-instruct:free)
- **Vector Backend**: Supabase with pgvector
- **Rate Limiting**: 2-second throttle between requests, 60-second delay for 429 errors
- **Retry Logic**: 5 attempts with 3^n exponential backoff

---

## 📝 Conclusion

The MADAM Hybrid RAG System achieves a **55.6% average F1 score** on retrieval tasks. Performance varies significantly by question type:
- **Strong areas**: Technical and NIB questions (80%+ F1)
- **Weak areas**: Licensing and Procedure questions (28-42% F1)

The **enhanced_vector method** is the most reliable, while the **MADAM debate phase** needs optimization for retrieval tasks. The system successfully retrieves all relevant chunks in 38% of cases and provides useful partial matches in 36% of cases.

---

**Test Date**: 2024
**Total Test Duration**: ~25 seconds (0.5s per query)
**Dataset**: 50 ground-truth queries with 5 expected chunk IDs each
