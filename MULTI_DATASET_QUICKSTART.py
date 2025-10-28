#!/usr/bin/env python3
"""
Multi-Dataset System - Quick Start Guide
=========================================

This script provides an interactive guide for using the multi-dataset system.
Run this to understand the workflow or execute commands.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner(text):
    """Print formatted banner"""
    width = 80
    print("\n" + "="*width)
    print(f"  {text}")
    print("="*width)


def print_section(title, items):
    """Print formatted section"""
    print(f"\n📌 {title}")
    print("-" * 60)
    for i, item in enumerate(items, 1):
        print(f"   {i}. {item}")


def show_overview():
    """Show system overview"""
    print_banner("MULTI-DATASET RETRIEVAL TESTING SYSTEM")
    
    print("""
    This system enables testing with three interchangeable Supabase datasets:
    
    ┌─ NEW Dataset (Current Production)
    │  └─ Table: documents
    │     Source: data/data_oss/
    │     Status: Ready
    │
    ├─ OLD Dataset (Historical Data)
    │  └─ Table: documents_old
    │     Source: data/scraped_dpmptsp/
    │     Status: Needs ingestion
    │
    └─ COMBINED Dataset (Both)
       └─ Table: documents_combined
          Sources: data/scraped_dpmptsp/ + data/data_oss/
          Status: Needs ingestion
    """)


def show_files():
    """Show created files"""
    print_banner("SYSTEM FILES CREATED")
    
    files = {
        "Configuration": [
            ("config_datasets.py", "Dataset configuration management"),
        ],
        "Ingestion": [
            ("ingest_supabase_datasets.py", "Multi-format ingestion script"),
        ],
        "API": [
            ("rag_api_datasets.py", "Multi-dataset RAG API server"),
        ],
        "Testing": [
            ("run_retrieval_test_datasets.py", "Dataset-aware retrieval tests"),
            ("analyze_retrieval_test_datasets.py", "Comparative analysis tool"),
        ],
        "Documentation": [
            ("MULTI_DATASET_SYSTEM.md", "Comprehensive system documentation"),
            ("MULTI_DATASET_QUICKSTART.py", "This file"),
        ],
    }
    
    for category, file_list in files.items():
        print(f"\n📂 {category}")
        for filename, description in file_list:
            status = "✅" if Path(filename).exists() else "❌"
            print(f"   {status} {filename:<35} - {description}")


def show_workflow():
    """Show recommended workflow"""
    print_banner("RECOMMENDED WORKFLOW")
    
    print("""
    STEP 1: Verify Configuration
    ───────────────────────────
    $ python config_datasets.py
    
    Lists all datasets and their configuration:
    - NEW (documents table, data_oss source)
    - OLD (documents_old table, scraped_dpmptsp source)
    - COMBINED (documents_combined table, both sources)
    
    
    STEP 2: Ingest Datasets (First Time Only)
    ──────────────────────────────────────────
    # Ingest OLD dataset
    $ python ingest_supabase_datasets.py --dataset OLD
    
    # Ingest COMBINED dataset
    $ python ingest_supabase_datasets.py --dataset COMBINED
    
    (NEW is already ingested if you've used the system)
    
    ⏱️ Expected time: 3-5 minutes per dataset
    
    
    STEP 3: Start API Server (New Terminal)
    ───────────────────────────────────────
    $ python rag_api_datasets.py
    
    Server will initialize all three datasets and listen on port 8001
    - Endpoint: http://localhost:8001
    - Docs: http://localhost:8001/docs
    
    
    STEP 4: Run Retrieval Tests
    ───────────────────────────
    # Test each dataset (run in different terminal)
    $ python run_retrieval_test_datasets.py --dataset NEW --limit 50
    $ python run_retrieval_test_datasets.py --dataset OLD --limit 50
    $ python run_retrieval_test_datasets.py --dataset COMBINED --limit 50
    
    ⏱️ Expected time: 10-15 minutes per dataset
    Output: CSV file with results in evaluation/ directory
    
    
    STEP 5: Compare Results
    ───────────────────────
    $ python analyze_retrieval_test_datasets.py
    
    Generates:
    - Comparison table
    - Search method breakdown
    - Category statistics
    - Problem query identification
    - Summary JSON file
    """)


def show_commands():
    """Show useful commands"""
    print_banner("QUICK COMMANDS")
    
    commands = {
        "Configuration": [
            ("python config_datasets.py", "List all datasets"),
            ("python config_datasets.py --help", "Show options"),
        ],
        "Ingestion": [
            ("python ingest_supabase_datasets.py --dataset OLD", "Ingest OLD dataset"),
            ("python ingest_supabase_datasets.py --dataset COMBINED", "Ingest COMBINED"),
            ("python ingest_supabase_datasets.py --list", "Show available configs"),
        ],
        "API Server": [
            ("python rag_api_datasets.py", "Start with NEW as default"),
            ("python rag_api_datasets.py --dataset OLD", "Start with OLD as default"),
            ("python rag_api_datasets.py --port 8002", "Use different port"),
        ],
        "Testing": [
            ("python run_retrieval_test_datasets.py --dataset NEW", "Test NEW (50 queries)"),
            ("python run_retrieval_test_datasets.py --dataset OLD --limit 30", "Test OLD (30 queries)"),
            ("python analyze_retrieval_test_datasets.py", "Compare all results"),
        ],
    }
    
    for category, cmd_list in commands.items():
        print(f"\n📌 {category}")
        for cmd, description in cmd_list:
            print(f"   $ {cmd}")
            print(f"     → {description}\n")


def show_api_examples():
    """Show API usage examples"""
    print_banner("API USAGE EXAMPLES")
    
    print("""
    Retrieve chunks with specific dataset:
    ──────────────────────────────────────
    
    # NEW dataset
    $ curl -X POST http://localhost:8001/retrieve?dataset=NEW \\
        -H "Content-Type: application/json" \\
        -d '{"messages": [{"role": "user", "content": "Apa itu DPMPTSP?"}]}'
    
    # OLD dataset
    $ curl -X POST http://localhost:8001/retrieve?dataset=OLD \\
        -H "Content-Type: application/json" \\
        -d '{"messages": [{"role": "user", "content": "Perizinan usaha"}]}'
    
    # COMBINED dataset
    $ curl -X POST http://localhost:8001/retrieve?dataset=COMBINED \\
        -H "Content-Type: application/json" \\
        -d '{"messages": [{"role": "user", "content": "Investasi"}]}'
    
    
    List all datasets:
    ──────────────────
    $ curl http://localhost:8001/datasets | python -m json.tool
    
    
    Check dataset health:
    ──────────────────────
    $ curl http://localhost:8001/health?dataset=OLD
    $ curl http://localhost:8001/health?dataset=COMBINED
    
    
    Get suggestions for dataset:
    ────────────────────────────
    $ curl http://localhost:8001/suggestions?dataset=OLD
    """)


def show_csv_columns():
    """Show CSV output format"""
    print_banner("CSV OUTPUT FORMAT")
    
    columns = [
        ("query_id", "Unique query identifier"),
        ("question", "The test question"),
        ("category", "Question category"),
        ("dataset_source", "Dataset used (NEW/OLD/COMBINED)"),
        ("retrieved_chunks", "Pipe-separated chunk IDs retrieved"),
        ("chunk1_id to chunk5_id", "Individual chunk IDs"),
        ("generated_chunks", "Ground truth chunks"),
        ("search_method", "Phase used (vector_only/enhanced_vector/internet_fallback)"),
        ("retrieval_time_seconds", "Time to retrieve in seconds"),
        ("precision", "Precision score (0-1)"),
        ("recall", "Recall score (0-1)"),
        ("f1_score", "F1 score (0-1)"),
        ("notes", "Additional notes (e.g., [🌐 FALLBACK])"),
    ]
    
    print("\nColumns in retrieval test CSV:")
    for i, (col, desc) in enumerate(columns, 1):
        print(f"   {i:2d}. {col:<30} - {desc}")


def show_metrics():
    """Show metrics explanation"""
    print_banner("METRICS EXPLANATION")
    
    print("""
    Per-Query Metrics:
    ─────────────────
    
    Precision (P)
      = Correctly retrieved ∩ Ground truth / Total retrieved
      = How many of the retrieved chunks were correct
      
    Recall (R)
      = Correctly retrieved ∩ Ground truth / Total ground truth
      = How many of the correct chunks did we retrieve
      
    F1 Score
      = 2 * (P * R) / (P + R)
      = Harmonic mean of precision and recall
      = Best overall metric for ranking
    
    
    Search Methods:
    ───────────────
    
    vector_only
      - Direct vector similarity search
      - Fastest, baseline method
      
    enhanced_vector
      - Vector search with keyword enhancement
      - Better accuracy, moderate speed
      
    internet_fallback
      - Fallback to internet search
      - Expected 0% precision with local ground truth
      - Indicates no local answer found
    
    
    Zero Precision Analysis:
    ────────────────────────
    
    Real Issues (⚠️)
      - Zero precision from vector_only or enhanced_vector
      - Indicates retrieval system didn't find answers
      - Needs investigation
      
    Expected Fallback (🌐)
      - Zero precision from internet_fallback
      - Expected behavior (comparing local ground truth to internet results)
      - Not an issue, normal operation
    """)


def show_comparison_insights():
    """Show what comparisons reveal"""
    print_banner("WHAT COMPARISONS REVEAL")
    
    print("""
    NEW vs OLD Dataset
    ──────────────────
    Tells you:
    - How much performance improved from old to new data
    - Which questions work better with current data
    - Areas where old data was better (if any)
    
    
    NEW vs COMBINED Dataset
    ─────────────────────────
    Tells you:
    - Whether old data helps or hurts current performance
    - If keeping historical data is beneficial
    - Redundancy between datasets
    
    
    OLD vs COMBINED Dataset
    ────────────────────────
    Tells you:
    - How much improvement came from new data
    - Which old questions still work
    - Coverage improvements
    
    
    All Three Comparison
    ────────────────────
    Reveals:
    - Overall data quality progression
    - Optimal dataset for different use cases
    - Search method effectiveness per dataset
    - Category-specific performance trends
    """)


def show_troubleshooting():
    """Show troubleshooting tips"""
    print_banner("TROUBLESHOOTING")
    
    issues = {
        "Dataset not initialized": [
            "Cause: Ingestion not run yet",
            "Solution: python ingest_supabase_datasets.py --dataset OLD",
            "Time: 3-5 minutes",
        ],
        "Cannot connect to API": [
            "Cause: Server not running",
            "Solution: python rag_api_datasets.py (in separate terminal)",
            "Check: curl http://localhost:8001",
        ],
        "Zero precision on all queries": [
            "Check: Look at search_method column in CSV",
            "If all internet_fallback: Expected behavior",
            "Otherwise: Real issue - check API logs",
        ],
        "CSV parsing error": [
            "Cause: Retrieval test crashed",
            "Check: API logs for errors",
            "Solution: Re-run retrieval test",
        ],
        "Slow ingestion": [
            "Cause: Large dataset or slow connection",
            "Note: This is normal (2-5 min per dataset)",
            "Monitor: Check console for progress",
        ],
    }
    
    for issue, steps in issues.items():
        print(f"\n❌ {issue}")
        for step in steps:
            print(f"   • {step}")


def main():
    """Main interactive menu"""
    
    while True:
        print_banner("QUICK START MENU")
        
        menu_items = [
            "System Overview",
            "System Files",
            "Workflow Guide",
            "Quick Commands",
            "API Examples",
            "CSV Format",
            "Metrics Explained",
            "Comparison Insights",
            "Troubleshooting",
            "Exit",
        ]
        
        for i, item in enumerate(menu_items, 1):
            print(f"   {i}. {item}")
        
        print("\n" + "="*80)
        choice = input("Select option (1-10) or 'q' to quit: ").strip()
        
        if choice == 'q' or choice == '10':
            print("\n✅ Thank you for using the Multi-Dataset System!")
            break
        
        try:
            choice_idx = int(choice) - 1
            
            if choice_idx == 0:
                show_overview()
            elif choice_idx == 1:
                show_files()
            elif choice_idx == 2:
                show_workflow()
            elif choice_idx == 3:
                show_commands()
            elif choice_idx == 4:
                show_api_examples()
            elif choice_idx == 5:
                show_csv_columns()
            elif choice_idx == 6:
                show_metrics()
            elif choice_idx == 7:
                show_comparison_insights()
            elif choice_idx == 8:
                show_troubleshooting()
            else:
                print("Invalid choice!")
                
        except ValueError:
            print("Please enter a number between 1-10")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line arguments
        if sys.argv[1] == "--overview":
            show_overview()
        elif sys.argv[1] == "--files":
            show_files()
        elif sys.argv[1] == "--workflow":
            show_workflow()
        elif sys.argv[1] == "--commands":
            show_commands()
        elif sys.argv[1] == "--api":
            show_api_examples()
        elif sys.argv[1] == "--csv":
            show_csv_columns()
        elif sys.argv[1] == "--metrics":
            show_metrics()
        elif sys.argv[1] == "--comparison":
            show_comparison_insights()
        elif sys.argv[1] == "--help":
            print("""
            Multi-Dataset Quick Start Guide
            
            Usage: python MULTI_DATASET_QUICKSTART.py [option]
            
            Options:
              --overview        Show system overview
              --files          List system files
              --workflow       Show recommended workflow
              --commands       Show quick commands
              --api            Show API examples
              --csv            Show CSV format
              --metrics        Explain metrics
              --comparison     Show comparison insights
              --help           Show this help
              
            Run without arguments for interactive menu.
            """)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Interactive mode
        main()
