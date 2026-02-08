"""
Ground Truth & Chunk Verification Tool
Helps prepare the 50 questions for evaluation by:
1. Listing all questions for ground truth entry
2. Checking which chunks exist in Supabase
3. Validating logging setup
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


def load_questions():
    """Load the 50 balanced questions"""
    with open('evaluation/sample_50_balanced.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def check_supabase_chunks():
    """Check available chunks in Supabase"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not supabase_key:
            print("[FAIL] Supabase credentials not found in .env")
            return None
        
        client = create_client(supabase_url, supabase_key)
        
        # Get total chunks
        response = client.table('rag_chunks_jateng').select('id, content, metadata', count='exact').execute()
        
        print(f"\n[STATS] SUPABASE CHUNKS:")
        print(f"   Total chunks: {len(response.data)}")
        
        # Sample chunks
        print(f"\n   Sample chunk IDs:")
        for i, chunk in enumerate(response.data[:5], 1):
            chunk_id = chunk.get('id')
            metadata = chunk.get('metadata', {})
            filename = metadata.get('filename', 'unknown')
            print(f"   {i}. ID: {chunk_id} - File: {filename}")
        
        return response.data
        
    except Exception as e:
        print(f"[FAIL] Error checking Supabase: {e}")
        return None


def display_questions_for_ground_truth(data):
    """Display questions for ground truth entry"""
    print("\n" + "="*80)
    print(" 50 QUESTIONS FOR GROUND TRUTH ENTRY")
    print("="*80)
    print()
    print("For each question, you need to provide:")
    print("1. ground_truth: Expected correct answer (1-2 sentences)")
    print("2. relevant_chunk_ids: List of chunk IDs that should be retrieved")
    print()
    print("="*80)
    
    queries = data['queries']
    
    # Group by category
    by_category = {}
    for q in queries:
        cat = q['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(q)
    
    print(f"\n[STATS] DISTRIBUTION:")
    for cat, qs in by_category.items():
        print(f"   {cat}: {len(qs)} questions")
    
    print("\n" + "="*80)
    print("QUESTIONS LIST")
    print("="*80)
    
    for i, q in enumerate(queries, 1):
        print(f"\n[{i}/50] {q['eval_id']} - {q['category']} ({q['dataset_source']})")
        print(f"   Q: {q['query']}")
        print(f"   Ground Truth: {q['ground_truth'] or '[FAIL] MISSING'}")
        print(f"   Relevant Chunks: {q['relevant_chunk_ids'] or '[FAIL] EMPTY'}")


def create_ground_truth_template():
    """Create a CSV template for easy ground truth entry"""
    data = load_questions()
    queries = data['queries']
    
    import csv
    
    output_file = 'evaluation/ground_truth_template.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'eval_id', 'query', 'dataset_source', 'category', 
            'ground_truth', 'relevant_chunk_ids', 'notes'
        ])
        
        for q in queries:
            writer.writerow([
                q['eval_id'],
                q['query'],
                q['dataset_source'],
                q['category'],
                '',  # ground_truth - to be filled
                '',  # relevant_chunk_ids - to be filled (comma-separated)
                ''   # notes
            ])
    
    print(f"\n[OK] Template created: {output_file}")
    print(f"   Fill in 'ground_truth' and 'relevant_chunk_ids' columns")
    print(f"   Then run: python evaluation/import_ground_truth.py")


def check_logging_setup():
    """Verify metrics logger is working"""
    try:
        from evaluation.metrics_logger import MetricsLogger
        
        print("\n" + "="*80)
        print("[OK] LOGGING VERIFICATION")
        print("="*80)
        
        # Test logger
        logger = MetricsLogger(experiment_name="test_verification")
        logger.start_query("TEST_001", "Test query", "Test ground truth")
        
        # Test retrieval logging
        logger.log_retrieval(
            retrieved_chunks=[
                {"chunk_id": "chunk_1", "similarity": 0.85, "text": "Test chunk 1"},
                {"chunk_id": "chunk_2", "similarity": 0.75, "text": "Test chunk 2"}
            ],
            relevant_chunk_ids=["chunk_1", "chunk_3"]
        )
        
        # Test response logging
        logger.log_response(
            response_text="Test answer",
            model_name="test-model",
            token_usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            confidence_score=0.85,
            is_correct=True
        )
        
        logger.save()
        
        print("\n[OK] Metrics Logger Working!")
        print(f"   Test log saved to: {logger.log_file}")
        
        # Show what's logged
        print("\n[STATS] LOGGED METRICS:")
        print("   [OK] Query ID, text, ground truth")
        print("   [OK] Retrieval: chunks, precision, recall, F1")
        print("   [OK] Response: text, model, tokens, confidence")
        print("   [OK] Timing: response_time_seconds")
        print("   [OK] Accuracy: is_correct, confident_wrong")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Logging Error: {e}")
        return False


def check_run_evaluation_script():
    """Check if run_evaluation.py uses ground truth properly"""
    eval_file = Path('evaluation/run_balanced_evaluation.py')
    
    if not eval_file.exists():
        print("\n[FAIL] evaluation/run_balanced_evaluation.py not found")
        return False
    
    with open(eval_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n" + "="*80)
    print(" EVALUATION SCRIPT CHECK")
    print("="*80)
    
    checks = {
        "Loads questions": 'sample_50_balanced.json' in content,
        "Uses ground_truth": 'ground_truth' in content,
        "Uses relevant_chunk_ids": 'relevant_chunk_ids' in content,
        "Logs metrics": 'MetricsLogger' in content or 'metrics_logger' in content,
        "Saves results": '.json' in content
    }
    
    for check, passed in checks.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"   {status} {check}")
    
    all_passed = all(checks.values())
    
    if all_passed:
        print("\n[OK] Evaluation script ready!")
    else:
        print("\n[WARN]  Some checks failed - script may need updates")
    
    return all_passed


def main():
    print("\n" + "="*80)
    print("[SEARCH] PRE-EVALUATION VERIFICATION")
    print("="*80)
    
    # 1. Load questions
    print("\n1⃣ Loading 50 questions...")
    data = load_questions()
    print(f"   [OK] Loaded {data['metadata']['total_queries']} questions")
    
    # 2. Check Supabase chunks
    print("\n2⃣ Checking Supabase chunks...")
    chunks = check_supabase_chunks()
    
    # 3. Check logging
    print("\n3⃣ Verifying metrics logging...")
    check_logging_setup()
    
    # 4. Check evaluation script
    print("\n4⃣ Checking evaluation script...")
    check_run_evaluation_script()
    
    # 5. Display questions
    print("\n5⃣ Displaying questions for ground truth...")
    display_questions_for_ground_truth(data)
    
    # 6. Offer to create template
    print("\n" + "="*80)
    print(" NEXT STEPS")
    print("="*80)
    print("\n1. Create ground truth template:")
    print("   python evaluation/prepare_ground_truth.py --create-template")
    print()
    print("2. Fill in the CSV with ground truth answers and chunk IDs")
    print()
    print("3. Import ground truth back to JSON:")
    print("   python evaluation/prepare_ground_truth.py --import-csv")
    print()
    print("4. Run full evaluation:")
    print("   python evaluation/run_balanced_evaluation.py --name baseline_old_dataset")
    
    # Ask if user wants template
    response = input("\n Create ground truth template CSV now? (y/n): ").strip().lower()
    if response == 'y':
        create_ground_truth_template()


if __name__ == "__main__":
    main()
