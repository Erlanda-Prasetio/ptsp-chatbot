"""
PTSP-RAG Evaluation Tests - Essential Files Index
==================================================

This directory contains the core testing methodology that has been proven and validated.

STRUCTURE:
----------

1. CHUNK TESTING (Direct Vector Search)
   - chunk_test_with_metrics.py - Queries Supabase RPC directly for chunk confidence
   - chunk_test_old_dataset_metrics.csv - Results from chunk test on OLD dataset

2. RETRIEVAL TESTING (RAG API - Vector + Fallback)
   - run_retrieval_test.py - Tests RAG API retrieval quality with metrics
   - old_dataset_retrieval_test_template.csv - Results from retrieval test on OLD dataset
   - new_dataset_retrieval_test_template.csv - Results from retrieval test on NEW dataset
   
3. GENERATIVE TESTING (RAG API - Full LLM Response)
   - [To be created] - Tests full RAG generation quality
   - [To be created] - Results CSV
   
4. ANALYZERS
   - analyze_retrieval_test.py - Analyzes retrieval test results (Precision, Recall, F1)
   - [To be created] - Analyzer for generative test results

5. VALIDATION & COMPARISON
   - check_chunk_match.py - Compares chunk IDs between test methods
   - detailed_chunk_comparison_fixed.py - Detailed side-by-side chunk analysis
   - validate_chunk_csv.py - Validates chunk test results

DATASETS:
---------
- OLD Dataset: 218 documents (original PTSP data)
- NEW/CURRENT Dataset: [Updated PTSP data]

METHODOLOGY:
-----------
1. Chunk Test → Direct Supabase RPC (fast baseline, ~0.35s avg)
2. Retrieval Test → RAG API without generation (~14.57s avg, includes fallback)
3. Generative Test → RAG API with LLM generation (full system test)

KEY METRICS:
-----------
- Precision: % of retrieved chunks that match ground truth
- Recall: % of ground truth chunks that were retrieved
- F1-Score: Harmonic mean of Precision and Recall
- Search Method Distribution: vector_only, enhanced_vector, internet_fallback

TESTED & PROVEN:
---------------
✅ Chunk test matches retrieval test (100% alignment on chunk IDs)
✅ Retrieval test metrics are accurate (17 perfect matches = 34% F1 with fallback)
✅ System is consistent and reliable
✅ 40s timeout is sufficient for all queries
✅ Ground truth has been validated and updated

NEXT STEPS:
-----------
1. Create generative test script (full LLM generation with metrics)
2. Create generative test analyzer
3. Run tests on both OLD and CURRENT datasets
4. Compare results across datasets
"""
