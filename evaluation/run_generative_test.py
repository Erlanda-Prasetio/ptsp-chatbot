"""
Generative Test: LLM Answer Quality Evaluation
================================================

Tests the full RAG system including LLM generation.
Measures: Response time, token usage, accuracy (manual scoring), BERTScore confidence

This test focuses on the quality of generated answers with proper rate limiting.
Requires manual scoring for accuracy assessment.

Usage:
    # Run generative test with 25 custom questions
    python evaluation/run_generative_test.py --name generative_test1 --sample my_25_questions.json
    
    # With 60-second delay between questions (default)
    python evaluation/run_generative_test.py --name generative_test1 --delay 60
    
    # Resume from checkpoint
    python evaluation/run_generative_test.py --name generative_test1 --resume

Author: RAG Evaluation Framework
Date: October 2025
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import subprocess
import sys


class GenerativeTester:
    """
    Tests full RAG system with LLM generation
    Includes BERTScore confidence and manual scoring support
    """
    
    def __init__(
        self, 
        sample_file: str,
        api_url: str = "http://localhost:8001",
        delay_seconds: float = 60.0,
        timeout: int = 35
    ):
        self.sample_file = sample_file
        self.api_url = api_url.rstrip('/')
        self.delay_seconds = delay_seconds
        self.timeout = timeout
        self.queries = []
        
        # Load sample queries
        print(f"[DIR] Loading sample from: {sample_file}")
        with open(sample_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.queries = data if isinstance(data, list) else data.get('queries', [])
        
        print(f"[OK] Loaded {len(self.queries)} queries")
        print(f"[TIME]  Delay between queries: {delay_seconds}s")
        print(f"[TIME]  Estimated total time: ~{(len(self.queries) * (delay_seconds + 15)) / 60:.1f} minutes")
        print()
    
    def test_api_connection(self) -> bool:
        """Test if RAG API is reachable"""
        print(f"[CONNECT] Testing connection to {self.api_url}...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("[OK] API is healthy")
                print(f"   Backend: {data.get('vector_backend', 'unknown')}")
                print(f"   LLM: Enabled")
                print(f"   Hybrid Search: {data.get('hybrid_search_enabled', False)}")
                print(f"   Internet Fallback: {data.get('internet_fallback_enabled', False)}")
                print()
                return True
            else:
                print(f"[FAIL] API returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] Cannot connect to API at {self.api_url}")
            print(f"   Error: {e}")
            print("\n[INFO] Make sure rag_api.py is running:")
            print("   python rag_api.py")
            return False
    
    def query_rag_system(self, query_text: str) -> Dict:
        """
        Call RAG API with full LLM generation
        """
        try:
            payload = {
                "messages": [{"role": "user", "content": query_text}]
            }
            
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "answer": "",
                    "sources": []
                }
                
        except requests.exceptions.Timeout:
            return {
                "error": "Request timeout",
                "answer": "Maaf, waktu pencarian telah habis.",
                "sources": []
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "answer": "",
                "sources": []
            }
    
    def calculate_bertscore_confidence(self, answer: str, ground_truth: str) -> Dict:
        """
        Calculate BERTScore between generated answer and ground truth
        Returns confidence level and score
        
        Confidence levels:
        - >= 0.7: Great
        - 0.6-0.7: Good
        - 0.5-0.6: Marginal
        - < 0.5: Not confident
        """
        try:
            # Try to import BERTScore
            from bert_score import score as bert_score
            
            # Calculate BERTScore
            P, R, F1 = bert_score([answer], [ground_truth], lang='id', verbose=False)
            f1_score = F1.item()
            
            # Determine confidence level
            if f1_score >= 0.7:
                confidence_level = "great"
            elif f1_score >= 0.6:
                confidence_level = "good"
            elif f1_score >= 0.5:
                confidence_level = "marginal"
            else:
                confidence_level = "not_confident"
            
            return {
                "bertscore_f1": round(f1_score, 3),
                "confidence_level": confidence_level,
                "available": True
            }
            
        except ImportError:
            return {
                "bertscore_f1": None,
                "confidence_level": "unavailable",
                "available": False,
                "note": "Install bert-score: pip install bert-score"
            }
        except Exception as e:
            return {
                "bertscore_f1": None,
                "confidence_level": "error",
                "available": False,
                "error": str(e)
            }
    
    def extract_metrics(
        self, 
        response: Dict, 
        query_data: Dict
    ) -> Dict:
        """Extract all metrics from RAG response"""
        
        answer = response.get('answer', '')
        sources = response.get('sources', [])
        enhanced_features = response.get('enhanced_features', {})
        
        # Search method
        search_method = enhanced_features.get('search_method', 'unknown')
        
        # Token usage
        tokens_info = response.get('tokens', {})
        total_tokens = tokens_info.get('total', 0)
        
        # Confidence score from system
        confidence_score = enhanced_features.get('confidence_score', 0)
        
        # BERTScore confidence (if ground truth available)
        ground_truth = query_data.get('ground_truth', '')
        bertscore_data = {}
        if ground_truth and answer:
            bertscore_data = self.calculate_bertscore_confidence(answer, ground_truth)
        
        return {
            "answer": answer,
            "search_method": search_method,
            "sources_count": len(sources),
            "total_tokens": total_tokens,
            "system_confidence": confidence_score,
            "bertscore_f1": bertscore_data.get('bertscore_f1'),
            "bertscore_confidence": bertscore_data.get('confidence_level'),
            "error": response.get('error')
        }
    
    def run_test(
        self, 
        output_name: str,
        resume: bool = False,
        verbose: bool = True
    ) -> str:
        """
        Run generative test on all queries with rate limiting
        Returns path to results file
        """
        if not self.test_api_connection():
            raise RuntimeError("Cannot connect to RAG API. Start it with: python rag_api.py")
        
        print("=" * 70)
        print(f"[TEST] GENERATIVE TEST: {output_name}")
        print("=" * 70)
        print()
        
        # Check for checkpoint
        checkpoint_file = Path(f"evaluation/raw_results/{output_name}_checkpoint.json")
        results = []
        start_index = 0
        
        if resume and checkpoint_file.exists():
            print(f" Found checkpoint file, resuming from previous run...")
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
                results = checkpoint_data.get('results', [])
                start_index = len(results)
            print(f"   [OK] Resuming from question {start_index + 1}/{len(self.queries)}")
        
        start_time = time.time()
        
        try:
            for i in range(start_index, len(self.queries)):
                query_data = self.queries[i]
                query_text = query_data.get('question') or query_data.get('query')
                query_id = query_data.get('id', f'Q{i+1:03d}')
                category = query_data.get('category', 'uncategorized')
                
                if verbose:
                    print(f"[{i+1}/{len(self.queries)}] {query_id} - {category}: {query_text[:60]}...")
                
                # Query RAG system with full generation
                query_start = time.time()
                rag_response = self.query_rag_system(query_text)
                response_time = time.time() - query_start
                
                # Extract metrics
                metrics = self.extract_metrics(rag_response, query_data)
                
                result = {
                    "query_id": query_id,
                    "question": query_text,
                    "category": category,
                    "ground_truth": query_data.get('ground_truth', ''),
                    "answer": metrics['answer'],
                    "search_method": metrics['search_method'],
                    "sources_count": metrics['sources_count'],
                    "response_time_seconds": round(response_time, 2),
                    "total_tokens": metrics['total_tokens'],
                    "system_confidence": metrics['system_confidence'],
                    "bertscore_f1": metrics['bertscore_f1'],
                    "bertscore_confidence": metrics['bertscore_confidence'],
                    "manual_score": None,  # To be filled by manual scoring
                    "error": metrics.get('error')
                }
                
                results.append(result)
                
                if verbose:
                    if result.get('error'):
                        print(f"   [FAIL] Error: {result['error']}")
                    else:
                        method = result['search_method']
                        tokens = result['total_tokens']
                        bert_conf = result.get('bertscore_confidence', 'N/A')
                        print(f"   [OK] {response_time:.2f}s | {method} | tokens={tokens} | bert={bert_conf}")
                
                # Save checkpoint after each query
                checkpoint_data = {
                    "test_name": output_name,
                    "checkpoint_at": datetime.now().isoformat(),
                    "completed": i + 1,
                    "total": len(self.queries),
                    "results": results
                }
                with open(checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
                
                # Add delay between queries (except for last one)
                if i < len(self.queries) - 1:
                    if verbose:
                        print(f"   ⏳ Waiting {self.delay_seconds}s before next query...")
                    time.sleep(self.delay_seconds)
        
        except KeyboardInterrupt:
            print(f"\n\n[WARN]  Interrupted by user at question {len(results)}/{len(self.queries)}")
            print(f"[SAVE] Progress saved to checkpoint: {checkpoint_file}")
            print(f"   Run again with --resume to continue from question {len(results) + 1}")
            raise
        
        total_time = time.time() - start_time
        
        # Save final results
        output_dir = Path("evaluation/raw_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{output_name}.json"
        
        output_data = {
            "test_name": output_name,
            "test_type": "generative",
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(results),
            "total_time_seconds": round(total_time, 2),
            "delay_seconds": self.delay_seconds,
            "sample_file": self.sample_file,
            "api_url": self.api_url,
            "results": results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Remove checkpoint file
        if checkpoint_file.exists():
            checkpoint_file.unlink()
        
        print()
        print("=" * 70)
        print(f"[OK] GENERATIVE TEST COMPLETE!")
        print("=" * 70)
        print(f"[FILE] Results saved to: {output_file}")
        print(f"[TIME]  Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
        print()
        
        return str(output_file)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Run generative test to measure LLM answer quality"
    )
    parser.add_argument(
        '--name', 
        type=str, 
        required=True,
        help='Name for this test run (e.g., generative_test1)'
    )
    parser.add_argument(
        '--sample',
        type=str,
        required=True,
        help='Path to sample queries JSON file (your 25 custom questions)'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8001',
        help='URL of RAG API endpoint'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=60.0,
        help='Delay between queries in seconds (default: 60)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=35,
        help='Timeout for API requests in seconds'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from checkpoint if available'
    )
    parser.add_argument(
        '--no-analyze',
        action='store_true',
        help='Skip automatic analysis after test'
    )
    
    args = parser.parse_args()
    
    try:
        # Run generative test
        tester = GenerativeTester(
            sample_file=args.sample,
            api_url=args.api_url,
            delay_seconds=args.delay,
            timeout=args.timeout
        )
        
        results_file = tester.run_test(
            output_name=args.name,
            resume=args.resume,
            verbose=True
        )
        
        # Auto-analyze results
        if not args.no_analyze:
            print("[SEARCH] Running automatic analysis...")
            print()
            subprocess.run([
                sys.executable,
                'evaluation/analyze_generative_test.py',
                results_file
            ])
        
    except KeyboardInterrupt:
        print("\n[WARN]  Test interrupted - checkpoint saved")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
