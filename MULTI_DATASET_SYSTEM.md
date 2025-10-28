# Multi-Dataset Retrieval Testing System

This document describes how to use the interchangeable Supabase dataset system for comprehensive RAG testing.

## Overview

The system supports three dataset variants for testing:

| Dataset | Table Name | Sources | Use Case |
|---------|-----------|---------|----------|
| **NEW** | `documents` | `data/data_oss/` | Current production data |
| **OLD** | `documents_old` | `data/scraped_dpmptsp/` | Historical data for comparison |
| **COMBINED** | `documents_combined` | Both sources | Comprehensive dataset |

## System Architecture

```
Configuration Management (config_datasets.py)
    ↓
Universal Ingestion (ingest_supabase_datasets.py)
    ├─ OLD: documents_old table
    ├─ NEW: documents table
    └─ COMBINED: documents_combined table
    ↓
Multi-Dataset RAG API (rag_api_datasets.py)
    ├─ ?dataset=NEW
    ├─ ?dataset=OLD
    └─ ?dataset=COMBINED
    ↓
Retrieval Tests (run_retrieval_test_datasets.py)
    ↓
Comparative Analysis (analyze_retrieval_test_datasets.py)
```

## Setup Instructions

### 1. Create Dataset Configuration

The configuration system is already created in `config_datasets.py`. It provides:

- **Function**: `get_dataset_config(dataset_type)` - Returns configuration for any dataset
- **Datasets**: NEW, OLD, COMBINED (all pre-configured)
- **Returns**: DatasetConfig with table_name, source_dirs, description

### 2. Ingest Datasets to Supabase

Use the universal ingestion script to populate all three tables:

```bash
# Ingest OLD dataset (scraped_dpmptsp)
python ingest_supabase_datasets.py --dataset OLD

# Ingest NEW dataset (data_oss)
python ingest_supabase_datasets.py --dataset NEW

# Ingest COMBINED dataset (both)
python ingest_supabase_datasets.py --dataset COMBINED
```

**Features:**
- Handles both old HTML format (scraped_dpmptsp) and new NDJSON format (data_oss)
- Automatic embedding generation
- Batch processing with rate limiting
- Progress tracking and error reporting

**Output Example:**
```
🚀 Ingesting OLD dataset...
📂 Loading from: data/scraped_dpmptsp
📄 Found 1,250 HTML documents
🔄 Generating embeddings...
📊 Batch processing: 125 batches of 10 documents
✅ Successfully ingested 1,250 documents to documents_old table
```

### 3. Start Multi-Dataset API Server

```bash
# Start server with NEW as default
python rag_api_datasets.py

# Or specify default dataset
python rag_api_datasets.py --dataset OLD --port 8001
```

**API Endpoints:**

| Endpoint | Purpose | Dataset Selection |
|----------|---------|-------------------|
| `GET /` | Health check | Current default |
| `GET /health?dataset=OLD` | Detailed status | Query parameter |
| `GET /datasets` | List all datasets | All datasets |
| `POST /chat?dataset=OLD` | Chat with specific dataset | Query parameter |
| `POST /retrieve?dataset=COMBINED` | Retrieve chunks | Query parameter |
| `GET /suggestions?dataset=OLD` | Get suggestions | Query parameter |

**Examples:**

```bash
# Chat with OLD dataset
curl -X POST http://localhost:8001/chat?dataset=OLD \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Apa itu DPMPTSP?"}]}'

# Retrieve chunks with COMBINED dataset
curl -X POST http://localhost:8001/retrieve?dataset=COMBINED \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Prosedur perizinan"}]}'

# List all datasets
curl http://localhost:8001/datasets
```

### 4. Run Retrieval Tests

Test each dataset individually:

```bash
# Test NEW dataset with 50 queries
python run_retrieval_test_datasets.py --dataset NEW --limit 50

# Test OLD dataset
python run_retrieval_test_datasets.py --dataset OLD --limit 50

# Test COMBINED dataset
python run_retrieval_test_datasets.py --dataset COMBINED --limit 50
```

**Output:**
- CSV file: `evaluation/retrieval_test_result_{DATASET}_{TIMESTAMP}.csv`
- Console summary with metrics and timing

**CSV Columns:**
- query_id, question, category, dataset_source
- retrieved_chunks, chunk1_id through chunk5_id
- generated_chunks (ground truth)
- search_method, retrieval_time_seconds
- precision, recall, f1_score, notes

### 5. Analyze and Compare Results

After running tests for all datasets:

```bash
# Find latest results and compare
python analyze_retrieval_test_datasets.py

# Or specify specific CSV files
python analyze_retrieval_test_datasets.py \
  --csv-files evaluation/retrieval_test_result_NEW_20240101_120000.csv \
                evaluation/retrieval_test_result_OLD_20240101_120100.csv \
                evaluation/retrieval_test_result_COMBINED_20240101_120200.csv
```

**Output:**
- Comparison table across datasets
- Search methods breakdown
- Category breakdown
- Problem queries identification
- Summary JSON file for further analysis

## File Reference

### Configuration

**`config_datasets.py`** - Dataset configuration management
- DatasetConfig: Named tuple with name, dataset_type, table_name, description, source_dirs
- DATASET_CONFIGS: Pre-configured dictionary with NEW, OLD, COMBINED
- get_dataset_config(type): Get configuration for any dataset
- list_datasets(): List all available datasets

### Ingestion

**`ingest_supabase_datasets.py`** - Universal ingestion script
- load_documents_from_dir(directory): Multi-format loader
  - Handles HTML (old format from scraped_dpmptsp)
  - Handles NDJSON (new format from data_oss)
- ingest_dataset(dataset_type): Main ingestion orchestration
  - Batch processing (10 docs/batch)
  - Rate limiting
  - Embedding generation
  - Error handling
- CLI: `--dataset`, `--list`, `--help`

### API Server

**`rag_api_datasets.py`** - Multi-dataset RAG API
- DatasetState: Global state management
- Lifespan events: Initialize/shutdown RAG systems
- Endpoints:
  - `GET /`: Root health check
  - `GET /health?dataset=X`: Detailed status
  - `GET /datasets`: List all datasets
  - `POST /chat?dataset=X`: Chat endpoint
  - `POST /retrieve?dataset=X`: Retrieval-only endpoint
  - `GET /suggestions?dataset=X`: Question suggestions
- Query parameter: `?dataset=NEW|OLD|COMBINED`

### Testing

**`run_retrieval_test_datasets.py`** - Multi-dataset retrieval tests
- load_test_questions(): Load 30 balanced test questions
- retrieve_chunks(): Call API for chunk retrieval
- save_retrieval_results_csv(): Export results to CSV
- analyze_results(): Calculate metrics
- Main loop: Process all questions, calculate P/R/F1, capture timing

**`analyze_retrieval_test_datasets.py`** - Comparative analysis
- find_latest_results(): Find newest CSV for each dataset
- parse_csv_results(): Load results from CSV
- calculate_statistics(): Compute all metrics
- print_comparison_table(): Side-by-side comparison
- print_problem_queries(): Identify retrieval failures

## Workflow Example

### Complete Testing Workflow

```bash
# Step 1: Check configuration
python config_datasets.py

# Step 2: Ingest all datasets (only needed once)
python ingest_supabase_datasets.py --dataset OLD
python ingest_supabase_datasets.py --dataset COMBINED

# Step 3: Start API server (in separate terminal)
python rag_api_datasets.py

# Step 4: Run tests for each dataset
python run_retrieval_test_datasets.py --dataset NEW --limit 50
python run_retrieval_test_datasets.py --dataset OLD --limit 50
python run_retrieval_test_datasets.py --dataset COMBINED --limit 50

# Step 5: Compare results
python analyze_retrieval_test_datasets.py
```

### Expected Output Structure

```
evaluation/
├── retrieval_test_result_NEW_20240101_100000.csv
├── retrieval_test_result_OLD_20240101_100500.csv
├── retrieval_test_result_COMBINED_20240101_101000.csv
└── comparison_summary_3_datasets.json
```

## Metrics Explanation

### Per-Query Metrics

- **Precision**: Intersection of retrieved ∩ ground_truth / |retrieved|
- **Recall**: Intersection of retrieved ∩ ground_truth / |ground_truth|
- **F1 Score**: 2 * (P * R) / (P + R)
- **Retrieval Time**: Seconds to retrieve chunks

### Search Methods

- **vector_only**: Direct vector similarity search
- **enhanced_vector**: Vector search with keyword enhancement
- **internet_fallback**: Fallback to internet search (expected 0 precision with local ground truth)

### Dataset Statistics

- **Avg Metrics**: Mean precision/recall/f1 across all queries
- **Zero Precision Count**: Queries with 0% precision (includes fallback)
- **Real Issues**: Zero precision from non-fallback methods (actual problems)
- **Fallback Zero**: Zero precision from internet_fallback (expected behavior)

## Comparison Insights

The system enables:

1. **Data Quality**: Compare retrieval effectiveness across dataset versions
2. **Historical Analysis**: See how performance changed from OLD to NEW
3. **Completeness**: Verify COMBINED dataset includes best of both
4. **Method Effectiveness**: Understand which search phases work best with each dataset

## Troubleshooting

### Issue: "Dataset not initialized"
**Solution:** Run ingestion first: `python ingest_supabase_datasets.py --dataset OLD`

### Issue: "Cannot connect to API"
**Solution:** Verify API server is running: `python rag_api_datasets.py`

### Issue: Zero precision on all queries
**Solution:** Check if it's all internet_fallback (expected) or real issue (check search methods in CSV)

### Issue: CSV parsing error
**Solution:** Ensure retrieval tests ran successfully and CSV is not corrupted

## Performance Notes

- Ingestion time: ~2-5 minutes per dataset
- Average retrieval time: 8-15 seconds per query
- Total test time for 50 queries: ~7-12 minutes
- CSV file size: ~50-100 KB per test run

## Future Enhancements

Potential improvements:

1. **Parallel Testing**: Run all three datasets simultaneously
2. **Result Caching**: Cache embeddings to speed up re-ingestion
3. **A/B Testing**: Built-in statistical significance testing
4. **Visualization**: Generate comparison graphs and charts
5. **Delta Analysis**: Show exactly what changed between datasets
6. **Performance Tracking**: Track metrics over time
