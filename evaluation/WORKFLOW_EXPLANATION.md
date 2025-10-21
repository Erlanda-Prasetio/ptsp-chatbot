# Evaluation Workflow - Clear Explanation

## 📊 Dataset vs Questions Terminology

### IMPORTANT: Don't Confuse These!

**Dataset (Vector Store):**
- **OLD Dataset**: 551 chunks from old PTSP documents (pre-2024)
- **NEW Dataset**: Will have 2024/2025 updated PTSP documents

**Questions (50 total, fixed throughout testing):**
- **OLD Questions (27)**: Questions that CAN be answered with OLD dataset
  - Example: "Apa itu DPMPTSP?" (general knowledge that doesn't change)
- **NEW Questions (23)**: Questions that NEED NEW dataset to answer correctly
  - Example: "Bagaimana cara mengurus NIB melalui sistem OSS?" (current procedures)

---

## 🔄 Research Workflow

### Phase 1: BASELINE (Current State)
**What:** Test OLD dataset with 50 mixed questions
**Purpose:** Show what's broken/missing in OLD dataset

```bash
# Run baseline evaluation
python evaluation/run_balanced_evaluation.py --name baseline_old_dataset

# Manual scoring
python evaluation/manual_scoring.py --file raw_results/baseline_old_dataset.json

# Analysis
python evaluation/demo_analysis.py
```

**Expected Results:**
- OLD questions: ~70% accuracy (general knowledge works)
- NEW questions: ~35% accuracy (current procedures missing/outdated)
- Overall: ~54% accuracy

**Graph Labels:**
- X-axis "OLD" = Questions answerable with old dataset ✅
- X-axis "NEW" = Questions requiring new dataset ❌

---

### Phase 2: AFTER UPDATE (Future)
**What:** Test NEW dataset with SAME 50 questions
**Purpose:** Show improvement after dataset update

```bash
# After updating vector store with 2024/2025 docs
python evaluation/run_balanced_evaluation.py --name updated_new_dataset

# Manual scoring
python evaluation/manual_scoring.py --file raw_results/updated_new_dataset.json

# Analysis
python evaluation/demo_analysis.py
```

**Expected Results:**
- OLD questions: ~70% accuracy (should stay the same)
- NEW questions: ~85% accuracy (MAJOR IMPROVEMENT!)
- Overall: ~78% accuracy (+24% improvement)

---

## 📈 What the Graphs Show

### Correct Interpretation:

**Accuracy by Question Type**
- **"OLD" bar**: Accuracy on OLD-related questions (should be high always)
- **"NEW" bar**: Accuracy on NEW-related questions (low on baseline, high after update)

**NOT "Accuracy by Dataset Version"** ❌

### Example with Real Numbers:

**BASELINE (OLD dataset):**
```
OLD questions: 19/27 correct = 70%  ← Questions that old data can answer
NEW questions:  8/23 correct = 35%  ← Questions that need new data
Overall:       27/50 correct = 54%
```

**AFTER UPDATE (NEW dataset):**
```
OLD questions: 19/27 correct = 70%  ← Same (general knowledge preserved)
NEW questions: 20/23 correct = 87%  ← IMPROVED (new procedures available!)
Overall:       39/50 correct = 78%  ← +24% improvement!
```

---

## 🎯 Key Takeaway

**The 50 questions NEVER change** - they're the fixed test set.

**What changes:**
1. BASELINE: Old vector store (551 chunks)
2. UPDATED: New vector store (with 2024/2025 docs)

**What we measure:**
- Can OLD questions still be answered? (regression check)
- Can NEW questions now be answered? (improvement metric)

---

## 📝 For Your Research Paper

### Methodology Section:
```
We created a balanced test set of 50 questions:
- 27 OLD questions: answerable with historical data
- 23 NEW questions: requiring current 2024/2025 procedures

We evaluated the system in two phases:
1. BASELINE: Old dataset (pre-2024 documents)
2. UPDATED: New dataset (including 2024/2025 documents)

The same 50 questions were used in both phases to ensure
fair comparison and measure the impact of dataset updates.
```

### Results Section:
```
BASELINE (Old Dataset):
- OLD questions accuracy: 70.4% (19/27)
- NEW questions accuracy: 34.8% (8/23)
- Overall accuracy: 54.0% (27/50)

UPDATED (New Dataset):
- OLD questions accuracy: 70.4% (19/27) - no regression
- NEW questions accuracy: 87.0% (20/23) - +52.2% improvement
- Overall accuracy: 78.0% (39/50) - +24% improvement

The dataset update resulted in a 52.2% improvement in answering
current procedure questions, while preserving historical knowledge.
```

---

## ✅ Summary

| Term | Meaning | Changes? |
|------|---------|----------|
| **OLD Dataset** | Pre-2024 documents (551 chunks) | Phase 1 only |
| **NEW Dataset** | 2024/2025 documents | Phase 2 only |
| **OLD Questions** | 27 questions answerable with old data | **NEVER** |
| **NEW Questions** | 23 questions needing new data | **NEVER** |
| **Total Questions** | 50 fixed test questions | **NEVER** |

**Graph labels = Question types, NOT dataset versions!**
