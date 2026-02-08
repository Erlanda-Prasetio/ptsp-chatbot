"""
Retrieval Test for MADAM Hybrid RAG System WITH TIMING
Tests the /retrieve endpoint using the baseline CSV with 50 queries
Calculates precision, recall, F1 scores, AND retrieval time
"""
import csv
import json
import time
from typing import List, Dict, Any
import sys

try:
    import requests
except ImportError:
    print("[WARN] requests library not found, installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

API_URL = "http://localhost:8001/retrieve"
CSV_FILE = "evaluation/retrieval_test_baseline.csv"
RESULTS_FILE = "evaluation/MAF-RAG-TEST.csv"

def extract_chunk_ids(chunk_str: str) -> List[str]:
    """Extract chunk IDs from CSV format (comma-separated string)"""
    if not chunk_str or chunk_str.strip() == "":
        return []
    return [cid.strip() for cid in str(chunk_str).split(",")]

def get_chunk_id_from_response(chunk_dict: Dict[str, Any]) -> str:
    """Extract chunk ID from response"""
    return str(chunk_dict.get("chunk_id", ""))

def calculate_metrics(relevant_chunks: List[str], retrieved_chunks: List[str]) -> Dict[str, float]:
    """Calculate precision, recall, F1 score"""
    if not relevant_chunks:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    if not retrieved_chunks:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    
    # Convert to sets for comparison
    relevant_set = set(relevant_chunks)
    retrieved_set = set(retrieved_chunks)
    
    # Calculate intersection
    true_positives = len(relevant_set & retrieved_set)
    
    # Precision: among retrieved, how many are relevant
    precision = true_positives / len(retrieved_set) if retrieved_set else 0.0
    
    # Recall: among relevant, how many were retrieved
    recall = true_positives / len(relevant_set) if relevant_set else 0.0
    
    # F1 score
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3)
    }

def test_retrieval(question: str) -> Dict[str, Any]:
    """Test retrieval endpoint WITH TIMING"""
    payload = {
        "messages": [
            {"role": "user", "content": question}
        ]
    }
    
    # START TIMING
    start_time = time.time()
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=60  # Increased to 60 seconds (1 minute)
        )
        response.raise_for_status()
        data = response.json()
        
        # END TIMING
        end_time = time.time()
        retrieval_time = round(end_time - start_time, 2)
        
        # Extract chunk IDs from sources
        chunk_ids = [get_chunk_id_from_response(src) for src in data.get("sources", [])]
        
        return {
            "success": True,
            "chunk_ids": chunk_ids,
            "total_sources": data.get("total_sources", 0),
            "search_method": data.get("search_method", "unknown"),
            "retrieval_time_seconds": retrieval_time,
            "error": None
        }
    except Exception as exc:
        # END TIMING (even on error)
        end_time = time.time()
        retrieval_time = round(end_time - start_time, 2)
        
        return {
            "success": False,
            "chunk_ids": [],
            "total_sources": 0,
            "search_method": "error",
            "retrieval_time_seconds": retrieval_time,
            "error": str(exc)
        }

def main():
    """Run retrieval tests on baseline CSV"""
    print("=" * 80)
    print("[SEARCH] MADAM Hybrid RAG System - Retrieval Test WITH TIMING")
    print("=" * 80)
    print(f"[DIR] Input: {CSV_FILE}")
    print(f"[STATS] Output: {RESULTS_FILE}")
    print()
    
    # Read CSV
    rows = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        print(f"[OK] Loaded {len(rows)} queries from CSV\n")
    except FileNotFoundError:
        print(f"[FAIL] CSV file not found: {CSV_FILE}")
        return
    
    results = []
    total_precision = 0.0
    total_recall = 0.0
    total_f1 = 0.0
    total_time = 0.0
    successful_tests = 0
    failed_tests = 0
    
    for idx, row in enumerate(rows, 1):
        query_id = row.get("query_id", f"query_{idx}")
        question = row.get("question", "")
        category = row.get("category", "")
        
        # Parse relevant chunk IDs (from columns chunk1_id to chunk5_id)
        relevant_ids = []
        for i in range(1, 6):
            chunk_id = row.get(f"chunk{i}_id", "").strip()
            if chunk_id and chunk_id != "":
                relevant_ids.append(chunk_id)
        
        print(f"[{idx:2d}/50] {query_id}: {question[:45]}...", end=" ")
        
        # Test retrieval
        test_result = test_retrieval(question)
        
        if not test_result["success"]:
            print(f"[FAIL] {test_result['retrieval_time_seconds']}s - {test_result['error'][:30]}")
            failed_tests += 1
            results.append({
                "query_id": query_id,
                "question": question,
                "category": category,
                "search_method": "error",
                "retrieved_count": 0,
                "relevant_count": len(relevant_ids),
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "retrieval_time_seconds": test_result["retrieval_time_seconds"],
                "error": test_result['error']
            })
            continue
        
        # Calculate metrics
        retrieved_ids = test_result["chunk_ids"]
        metrics = calculate_metrics(relevant_ids, retrieved_ids)
        
        total_precision += metrics["precision"]
        total_recall += metrics["recall"]
        total_f1 += metrics["f1"]
        total_time += test_result["retrieval_time_seconds"]
        successful_tests += 1
        
        # Print status
        status = "[OK]" if metrics["f1"] > 0.5 else "[WARN]" if metrics["f1"] > 0.2 else "[FAIL]"
        print(f"{status} F1={metrics['f1']:.2f} Time={test_result['retrieval_time_seconds']}s")
        
        results.append({
            "query_id": query_id,
            "question": question,
            "category": category,
            "search_method": test_result["search_method"],
            "retrieved_count": len(retrieved_ids),
            "relevant_count": len(relevant_ids),
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "retrieval_time_seconds": test_result["retrieval_time_seconds"],
            "error": None
        })
        
        # No delay needed for local API testing
        # time.sleep(0.5)  # Removed to speed up testing
    
    # Calculate averages
    if successful_tests > 0:
        avg_precision = total_precision / successful_tests
        avg_recall = total_recall / successful_tests
        avg_f1 = total_f1 / successful_tests
        avg_time = total_time / successful_tests
    else:
        avg_precision = avg_recall = avg_f1 = avg_time = 0.0
    
    # Write results to CSV
    try:
        with open(RESULTS_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                "query_id", "question", "category", "search_method",
                "retrieved_count", "relevant_count", "precision", "recall", "f1", 
                "retrieval_time_seconds", "error"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\n[OK] Results saved to {RESULTS_FILE}")
    except Exception as exc:
        print(f"\n[FAIL] Failed to save results: {exc}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("[STATS] SUMMARY")
    print("=" * 80)
    print(f"Total Tests:           {len(rows)}")
    print(f"Successful:            {successful_tests} [OK]")
    print(f"Failed:                {failed_tests} [FAIL]")
    print()
    print(f"Average Precision:     {avg_precision:.3f}")
    print(f"Average Recall:        {avg_recall:.3f}")
    print(f"Average F1 Score:      {avg_f1:.3f}")
    print(f"Average Response Time: {avg_time:.2f}s")
    print()
    
    # Categorize results
    high_perf = sum(1 for r in results if r.get("f1", 0) > 0.7)
    mid_perf = sum(1 for r in results if 0.3 < r.get("f1", 0) <= 0.7)
    low_perf = sum(1 for r in results if 0 < r.get("f1", 0) <= 0.3)
    
    print(f"High Performance (F1 > 0.7):  {high_perf} queries")
    print(f"Mid Performance (0.3-0.7):    {mid_perf} queries")
    print(f"Low Performance (F1 <= 0.3):  {low_perf} queries")
    
    # Timing analysis by phase
    print("\n" + "=" * 80)
    print("[TIMING] Response Time by Search Method")
    print("=" * 80)
    methods = {}
    for r in results:
        if r.get("search_method") != "error":
            method = r["search_method"]
            if method not in methods:
                methods[method] = []
            methods[method].append(r["retrieval_time_seconds"])
    
    for method, times in sorted(methods.items()):
        avg = sum(times) / len(times) if times else 0
        print(f"{method:20s}: {avg:6.2f}s (n={len(times)})")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
