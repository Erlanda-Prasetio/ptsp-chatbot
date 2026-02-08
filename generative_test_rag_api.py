"""
Generative Test with 25 Questions - Tests RAG API against ground truth
Measures: BLEU, ROUGE, BERTScore
Includes 60-second delays between questions to avoid API rate limiting
"""
import csv
import time
import requests
import json
from typing import List, Dict, Any
from pathlib import Path

# For BERTScore calculation
try:
    from bert_score import score as bert_score
    BERT_SCORE_AVAILABLE = True
except ImportError:
    BERT_SCORE_AVAILABLE = False
    print("[WARN]  BERTScore not available - will skip BERT metrics")

# For BLEU score
try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.tokenize import word_tokenize
    import nltk
    nltk.download('punkt', quiet=True)
    BLEU_AVAILABLE = True
except ImportError:
    BLEU_AVAILABLE = False
    print("[WARN]  NLTK/BLEU not available - will skip BLEU metrics")

# For ROUGE score
try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    ROUGE_AVAILABLE = False
    print("[WARN]  ROUGE not available - will skip ROUGE metrics")

# API Configuration
RAG_API_URL = "http://localhost:8001/chat"
INPUT_CSV = "evaluation/generative_test_query.csv"
OUTPUT_CSV = "evaluation/generative_test_results.csv"
DELAY_BETWEEN_QUESTIONS = 60  # seconds

def load_test_queries(filepath: str) -> List[Dict[str, str]]:
    """Load test queries from CSV."""
    queries = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                queries.append(row)
        print(f"[OK] Loaded {len(queries)} test queries from {filepath}\n")
    except Exception as e:
        print(f"[FAIL] Error loading CSV: {e}")
        return []
    return queries

def call_rag_api(question: str) -> Dict[str, Any]:
    """Call the RAG API endpoint."""
    try:
        payload = {
            "messages": [
                {"role": "user", "content": question}
            ]
        }
        response = requests.post(
            RAG_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed - is RAG API running on port 8001?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}
    except Exception as e:
        return {"error": str(e)}

def calculate_bleu_score(reference: str, candidate: str) -> float:
    """Calculate BLEU score (0-1 range)."""
    if not BLEU_AVAILABLE:
        return 0.0
    try:
        ref_tokens = word_tokenize(reference.lower())
        cand_tokens = word_tokenize(candidate.lower())
        smoothing_function = SmoothingFunction().method1
        score = sentence_bleu(
            [ref_tokens],
            cand_tokens,
            smoothing_function=smoothing_function
        )
        return round(score, 4)
    except Exception as e:
        print(f"    [WARN]  BLEU calculation error: {e}")
        return 0.0

def calculate_rouge_score(reference: str, candidate: str) -> Dict[str, float]:
    """Calculate ROUGE scores."""
    if not ROUGE_AVAILABLE:
        return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
    try:
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        scores = scorer.score(reference, candidate)
        return {
            "rouge1": round(scores['rouge1'].fmeasure, 4),
            "rouge2": round(scores['rouge2'].fmeasure, 4),
            "rougeL": round(scores['rougeL'].fmeasure, 4)
        }
    except Exception as e:
        print(f"    [WARN]  ROUGE calculation error: {e}")
        return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}

def calculate_bert_score(reference: str, candidate: str) -> float:
    """Calculate BERTScore."""
    if not BERT_SCORE_AVAILABLE:
        return 0.0
    try:
        P, R, F1 = bert_score([candidate], [reference], lang='id', verbose=False)
        return round(F1.item(), 4)
    except Exception as e:
        print(f"    [WARN]  BERTScore calculation error: {e}")
        return 0.0

def run_generative_test():
    """Run generative test against RAG API."""
    print("\n" + "="*120)
    print(" GENERATIVE TEST - 25 Questions with Ground Truth Comparison")
    print("="*120 + "\n")
    
    # Load queries
    queries = load_test_queries(INPUT_CSV)
    if not queries:
        print("[FAIL] Failed to load test queries")
        return
    
    print("[TIME]  CONFIGURATION:")
    print(f"   • API Endpoint: {RAG_API_URL}")
    print(f"   • Input CSV: {INPUT_CSV}")
    print(f"   • Output CSV: {OUTPUT_CSV}")
    print(f"   • Delay between questions: {DELAY_BETWEEN_QUESTIONS}s")
    print(f"   • Metrics: BLEU, ROUGE-1/2/L, BERTScore")
    print(f"   • Total queries: {len(queries)}")
    print(f"   • Estimated duration: ~{len(queries) * DELAY_BETWEEN_QUESTIONS / 60:.1f} minutes\n")
    
    results = []
    
    for idx, query_row in enumerate(queries, 1):
        query_id = query_row.get('id', f'Q{idx}')
        question = query_row.get('query', '')
        ground_truth = query_row.get('ground_truth', '')
        
        print(f"{''*120}")
        print(f" Query {idx}/{len(queries)}: {query_id}")
        print(f"Q: {question[:100]}...")
        
        # Wait 60 seconds before each question (except the first)
        if idx > 1:
            print(f"⏳ Waiting {DELAY_BETWEEN_QUESTIONS}s before next query (rate limiting)...")
            time.sleep(DELAY_BETWEEN_QUESTIONS)
        
        # Call API
        print(f" Calling RAG API...")
        api_start = time.time()
        api_response = call_rag_api(question)
        api_time = time.time() - api_start
        
        if "error" in api_response:
            print(f"[FAIL] API Error: {api_response['error']}")
            result = {
                "id": query_id,
                "question": question,
                "ground_truth": ground_truth,
                "generated_answer": f"ERROR: {api_response['error']}",
                "api_time_seconds": api_time,
                "bleu_score": 0.0,
                "rouge1_score": 0.0,
                "rouge2_score": 0.0,
                "rougeL_score": 0.0,
                "bert_score": 0.0,
                "status": "error"
            }
        else:
            generated_answer = api_response.get("message", "")
            sources_count = api_response.get("total_sources", 0)
            
            print(f"[OK] API Response received ({api_time:.2f}s)")
            print(f"   • Sources: {sources_count}")
            print(f"   • Answer length: {len(generated_answer)} chars")
            
            # Calculate metrics
            print(f"[STATS] Calculating metrics...")
            bleu = calculate_bleu_score(ground_truth, generated_answer)
            rouge = calculate_rouge_score(ground_truth, generated_answer)
            bert = calculate_bert_score(ground_truth, generated_answer)
            
            print(f"   • BLEU: {bleu}")
            print(f"   • ROUGE-1: {rouge['rouge1']}")
            print(f"   • ROUGE-2: {rouge['rouge2']}")
            print(f"   • ROUGE-L: {rouge['rougeL']}")
            print(f"   • BERTScore: {bert}")
            
            result = {
                "id": query_id,
                "question": question,
                "ground_truth": ground_truth,
                "generated_answer": generated_answer,
                "api_time_seconds": api_time,
                "sources_retrieved": sources_count,
                "bleu_score": bleu,
                "rouge1_score": rouge['rouge1'],
                "rouge2_score": rouge['rouge2'],
                "rougeL_score": rouge['rougeL'],
                "bert_score": bert,
                "status": "success"
            }
        
        results.append(result)
    
    # Save results to CSV
    print(f"\n{''*120}")
    print("[SAVE] Saving results to CSV...")
    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                "id", "question", "ground_truth", "generated_answer",
                "api_time_seconds", "sources_retrieved",
                "bleu_score", "rouge1_score", "rouge2_score", "rougeL_score", "bert_score",
                "status"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"[OK] Results saved to: {OUTPUT_CSV}\n")
    except Exception as e:
        print(f"[FAIL] Error saving results: {e}\n")
    
    # Summary Statistics
    print("="*120)
    print("[STATS] TEST SUMMARY")
    print("="*120 + "\n")
    
    successful = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "error")
    
    print(f"[OK] Successful: {successful}/{len(results)}")
    print(f"[FAIL] Failed: {failed}/{len(results)}")
    
    if successful > 0:
        avg_bleu = sum(r["bleu_score"] for r in results if r["status"] == "success") / successful
        avg_rouge1 = sum(r["rouge1_score"] for r in results if r["status"] == "success") / successful
        avg_rouge2 = sum(r["rouge2_score"] for r in results if r["status"] == "success") / successful
        avg_rougeL = sum(r["rougeL_score"] for r in results if r["status"] == "success") / successful
        avg_bert = sum(r["bert_score"] for r in results if r["status"] == "success") / successful
        avg_time = sum(r["api_time_seconds"] for r in results if r["status"] == "success") / successful
        
        print(f"\n[METRIC] Average Scores:")
        print(f"   • BLEU: {avg_bleu:.4f}")
        print(f"   • ROUGE-1: {avg_rouge1:.4f}")
        print(f"   • ROUGE-2: {avg_rouge2:.4f}")
        print(f"   • ROUGE-L: {avg_rougeL:.4f}")
        print(f"   • BERTScore: {avg_bert:.4f}")
        print(f"   • Avg API Time: {avg_time:.2f}s")
        
        # Performance categorization
        perfect = sum(1 for r in results if r["status"] == "success" and r["bert_score"] >= 0.8)
        good = sum(1 for r in results if r["status"] == "success" and 0.6 <= r["bert_score"] < 0.8)
        fair = sum(1 for r in results if r["status"] == "success" and 0.4 <= r["bert_score"] < 0.6)
        poor = sum(1 for r in results if r["status"] == "success" and r["bert_score"] < 0.4)
        
        print(f"\n[TARGET] Performance Distribution (by BERTScore):")
        print(f"   • Perfect (≥0.8): {perfect}")
        print(f"   • Good (0.6-0.8): {good}")
        print(f"   • Fair (0.4-0.6): {fair}")
        print(f"   • Poor (<0.4): {poor}")
    
    print(f"\n" + "="*120 + "\n")

if __name__ == "__main__":
    run_generative_test()
