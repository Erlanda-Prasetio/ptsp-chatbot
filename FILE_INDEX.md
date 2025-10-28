# Multi-Dataset System - File Index & Quick Navigation

## 🎯 Start Here

**New to this system?** Start with one of these:

### Interactive Learning (Easiest)
```bash
python MULTI_DATASET_QUICKSTART.py
```
→ Interactive menu with all system information

### Quick Reference
📄 **README_MULTI_DATASET.md** - This guide in one file

### Full Documentation  
📄 **MULTI_DATASET_SYSTEM.md** - Complete step-by-step guide

---

## 📚 All Documentation Files

| File | Purpose | Length | Read When |
|------|---------|--------|-----------|
| **README_MULTI_DATASET.md** | Complete reference (this file) | 5 min | First read |
| **MULTI_DATASET_SYSTEM.md** | Full system docs | 15 min | Need detailed info |
| **MULTI_DATASET_IMPLEMENTATION.md** | Implementation summary | 10 min | Want to understand architecture |
| **MULTI_DATASET_QUICKSTART.py** | Interactive guide | Tool | Want interactive menu |

---

## 🔧 System Files By Category

### 📋 Configuration (1 file)
```
config_datasets.py
├─ DatasetConfig class
├─ get_dataset_config(type) → config for any dataset
├─ list_datasets() → show all
└─ Usage: from config_datasets import get_dataset_config
```

**Run to test:**
```bash
python config_datasets.py
```

### 📥 Ingestion (1 file)
```
ingest_supabase_datasets.py
├─ load_documents_from_dir() → smart format loader
├─ ingest_dataset(type) → universal ingestion
├─ Supports: HTML (old), NDJSON (new), both (combined)
└─ CLI: --dataset OLD|NEW|COMBINED, --list
```

**Run to ingest:**
```bash
python ingest_supabase_datasets.py --dataset OLD
python ingest_supabase_datasets.py --dataset COMBINED
```

### 🌐 API Server (1 file)
```
rag_api_datasets.py
├─ DatasetState class → manages all RAG systems
├─ /retrieve?dataset=X → main endpoint
├─ /chat?dataset=X → chat endpoint
├─ Supports: NEW, OLD, COMBINED datasets
└─ Default port: 8001
```

**Run to start:**
```bash
python rag_api_datasets.py
```

### 🧪 Testing (1 file)
```
run_retrieval_test_datasets.py
├─ load_test_questions() → load test queries
├─ retrieve_chunks() → call API for each
├─ save_retrieval_results_csv() → export results
└─ analyze_results() → calculate metrics
```

**Run tests:**
```bash
python run_retrieval_test_datasets.py --dataset NEW --limit 50
```

### 📊 Analysis (1 file)
```
analyze_retrieval_test_datasets.py
├─ find_latest_results() → find newest CSV
├─ calculate_statistics() → compute all metrics
├─ print_comparison_table() → side-by-side view
└─ print_problem_queries() → identify failures
```

**Run analysis:**
```bash
python analyze_retrieval_test_datasets.py
```

### ✅ Verification (1 file)
```
verify_multi_dataset_system.py
├─ verify_files() → check all exist
├─ verify_dependencies() → check imports work
├─ verify_supabase_connection() → check DB access
├─ verify_api_requirements() → check API can start
└─ verify_testing_requirements() → check tests run
```

**Run verification:**
```bash
python verify_multi_dataset_system.py
```

---

## 📋 Working Workflow

### Phase 1: Setup (First Time)
```
1. Verify system works
   $ python verify_multi_dataset_system.py

2. Ingest OLD dataset (3-5 min)
   $ python ingest_supabase_datasets.py --dataset OLD

3. Ingest COMBINED dataset (5-7 min)
   $ python ingest_supabase_datasets.py --dataset COMBINED
```

### Phase 2: Testing (Repeatable)
```
Terminal 1:
$ python rag_api_datasets.py
(Start server, will initialize all 3 datasets)

Terminal 2:
$ python run_retrieval_test_datasets.py --dataset NEW --limit 50
$ python run_retrieval_test_datasets.py --dataset OLD --limit 50
$ python run_retrieval_test_datasets.py --dataset COMBINED --limit 50
(Each takes 10-15 minutes)

Terminal 3 (After tests complete):
$ python analyze_retrieval_test_datasets.py
(Generates comparison and analysis)
```

---

## 🔑 Key Concepts

### Three Datasets
| Name | Table | Source | Purpose |
|------|-------|--------|---------|
| NEW | documents | data_oss/ | Current data |
| OLD | documents_old | scraped_dpmptsp/ | Historical |
| COMBINED | documents_combined | Both | Comprehensive |

### Query Parameter Changes Everything
```
POST /retrieve?dataset=NEW        → Uses 'documents' table
POST /retrieve?dataset=OLD        → Uses 'documents_old' table
POST /retrieve?dataset=COMBINED   → Uses 'documents_combined' table
```

### Search Methods
- **vector_only**: Direct similarity
- **enhanced_vector**: Similarity + keywords
- **internet_fallback**: Internet search (0% precision expected)

### Metrics
- **Precision**: % of retrieved chunks that were correct
- **Recall**: % of correct chunks that were retrieved
- **F1 Score**: Harmonic mean (balanced metric)

---

## 💾 Output Files

Tests create CSV files in `evaluation/` directory:

```
evaluation/
├── retrieval_test_result_NEW_20240101_100000.csv
├── retrieval_test_result_OLD_20240101_100500.csv
├── retrieval_test_result_COMBINED_20240101_101000.csv
└── comparison_summary_3_datasets.json
```

**CSV Columns:**
```
query_id | question | category | dataset_source | retrieved_chunks | 
chunk1_id | chunk2_id | ... | generated_chunks | search_method | 
retrieval_time_seconds | precision | recall | f1_score | notes
```

---

## 🎓 Learning Resources

### Quick Understanding (5 min)
1. Read this file (section: Key Concepts)
2. Run: `python MULTI_DATASET_QUICKSTART.py`

### Full Setup (20 min)
1. Read: **MULTI_DATASET_SYSTEM.md** (Setup Instructions section)
2. Run: `python verify_multi_dataset_system.py`
3. Follow: Workflow (next section)

### Deep Understanding (30 min)
1. Read: **MULTI_DATASET_SYSTEM.md** (all sections)
2. Review: Code comments in each Python file
3. Run: `python -c "from config_datasets import list_datasets; list_datasets()"`

---

## ⚡ Quick Commands Reference

### Check System
```bash
python verify_multi_dataset_system.py              # Full check
python verify_multi_dataset_system.py --fix        # Auto-fix issues
```

### Show Configuration
```bash
python config_datasets.py                          # List datasets
```

### Ingest Datasets
```bash
python ingest_supabase_datasets.py --dataset OLD
python ingest_supabase_datasets.py --dataset COMBINED
python ingest_supabase_datasets.py --list          # Show configs
```

### Start API
```bash
python rag_api_datasets.py                         # With NEW default
python rag_api_datasets.py --dataset OLD           # With OLD default
python rag_api_datasets.py --port 8002             # Different port
```

### Run Tests
```bash
# Test any dataset
python run_retrieval_test_datasets.py --dataset NEW --limit 50
python run_retrieval_test_datasets.py --dataset OLD --limit 30
python run_retrieval_test_datasets.py --dataset COMBINED --limit 50

# Quick test
python run_retrieval_test_datasets.py --dataset NEW --limit 10
```

### Test API
```bash
# Check server is running
curl http://localhost:8001

# List datasets
curl http://localhost:8001/datasets

# Test retrieve (OLD dataset)
curl -X POST http://localhost:8001/retrieve?dataset=OLD \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "test question"}]}'
```

### Analyze Results
```bash
python analyze_retrieval_test_datasets.py          # Auto find latest
python analyze_retrieval_test_datasets.py \
  --csv-files evaluation/retrieval_test_result_NEW_*.csv \
               evaluation/retrieval_test_result_OLD_*.csv
```

### Interactive Guide
```bash
python MULTI_DATASET_QUICKSTART.py                 # Menu
python MULTI_DATASET_QUICKSTART.py --workflow      # Show workflow
python MULTI_DATASET_QUICKSTART.py --commands      # Show commands
python MULTI_DATASET_QUICKSTART.py --api           # Show API examples
python MULTI_DATASET_QUICKSTART.py --metrics       # Explain metrics
```

---

## 🎯 Common Scenarios

### Scenario 1: First Time Setup
```bash
Step 1: python verify_multi_dataset_system.py
Step 2: python ingest_supabase_datasets.py --dataset OLD
Step 3: python ingest_supabase_datasets.py --dataset COMBINED
Step 4: Start API and run tests (see Phase 2 workflow)
```

### Scenario 2: Quick Test of All Datasets
```bash
# Terminal 1
python rag_api_datasets.py

# Terminal 2 (wait for Terminal 1 to initialize)
python run_retrieval_test_datasets.py --dataset NEW --limit 10
python run_retrieval_test_datasets.py --dataset OLD --limit 10
python run_retrieval_test_datasets.py --dataset COMBINED --limit 10
```

### Scenario 3: Full Evaluation
```bash
# Same as Phase 2 workflow with --limit 50 instead of 10
```

### Scenario 4: API Testing Only
```bash
# Terminal 1
python rag_api_datasets.py

# Terminal 2
curl http://localhost:8001/datasets
curl -X POST http://localhost:8001/retrieve?dataset=NEW \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "question"}]}'
```

---

## 📞 Help & Support

### System Not Working?
```bash
python verify_multi_dataset_system.py --detailed
```
→ Shows exactly what's wrong

### Need Examples?
```bash
python MULTI_DATASET_QUICKSTART.py --api
```
→ Shows API usage examples

### Forgot a Command?
```bash
python MULTI_DATASET_QUICKSTART.py --commands
```
→ Lists all common commands

### Need Full Docs?
See **MULTI_DATASET_SYSTEM.md**

---

## ✨ System Summary

| Aspect | Details |
|--------|---------|
| **Datasets** | 3 (NEW, OLD, COMBINED) |
| **Supabase Tables** | 3 separate tables per dataset |
| **API Endpoints** | 6 main endpoints |
| **Testing Capability** | Full retrieval + timing + metrics |
| **Comparison** | Automatic side-by-side analysis |
| **Setup Time** | ~15 min (first time) |
| **Test Time** | ~10-15 min per dataset |
| **Total Files** | 9 new system files |

---

**You're ready to go! Pick a scenario above and start!** 🚀
