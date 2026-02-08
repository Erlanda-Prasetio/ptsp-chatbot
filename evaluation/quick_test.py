"""
Quick Test: Test 2 Questions to Verify RAG System
=================================================

This tests your RAG API with 2 sample questions to verify:
- API is reachable
- Responses are generated
- Metrics are collected
- Everything works before full evaluation

Usage:
    python evaluation/quick_test.py
"""

import requests
import json
import time
from datetime import datetime


def test_rag_api(api_url: str = "http://localhost:8001"):
    """Test RAG API with 2 sample questions"""
    
    print("\n" + "="*70)
    print("[TEST] QUICK RAG SYSTEM TEST (2 Questions)")
    print("="*70 + "\n")
    
    # Test questions (1 OLD, 1 NEW)
    test_questions = [
        {
            "id": "TEST_001",
            "query": "Apa itu DPMPTSP?",
            "source": "OLD",
            "category": "General",
            "expected": "Should explain DPMPTSP is the office for investment and licensing services"
        },
        {
            "id": "TEST_002",
            "query": "Bagaimana cara mengurus NIB melalui sistem OSS?",
            "source": "NEW",
            "category": "Procedure",
            "expected": "Should explain OSS registration process for NIB"
        }
    ]
    
    # Test connection first
    print("[CONNECT] Testing API connection...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"[OK] API is running")
            print(f"   Backend: {health.get('backend', 'unknown')}")
            print(f"   Status: {health.get('status', 'unknown')}")
            print(f"   Database Chunks: {health.get('database_chunks', 'unknown')}")
            print(f"   Hybrid Search: {health.get('hybrid_search', False)}")
            print()
        else:
            print(f"[FAIL] API returned status {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Cannot connect to API at {api_url}")
        print(f"   Make sure rag_api.py is running!")
        return
    except Exception as e:
        print(f"[FAIL] Connection test failed: {e}")
        return
    
    # Test each question
    results = []
    
    for i, test in enumerate(test_questions, 1):
        print(f"{'='*70}")
        print(f" TEST {i}/2: {test['id']} ({test['source']} - {test['category']})")
        print(f"{'='*70}\n")
        
        print(f" QUESTION:")
        print(f"   {test['query']}\n")
        
        print(f"[TARGET] EXPECTED:")
        print(f"   {test['expected']}\n")
        
        # Measure response time
        start_time = time.time()
        
        try:
            # Send request
            response = requests.post(
                f"{api_url}/chat",
                json={"messages": [{"role": "user", "content": test['query']}]},
                timeout=60  # Increased for slow queries
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract data
                answer = data.get('message', '')
                sources = data.get('sources', [])
                enhanced = data.get('enhanced_features', {})
                
                # Display results
                print(f"[OK] SYSTEM ANSWER:")
                print(f"   {answer[:300]}...")
                print()
                
                print(f"[STATS] METRICS:")
                print(f"   [TIME]  Response Time: {response_time:.2f}s")
                print(f"    Model: {enhanced.get('model', 'unknown')}")
                print(f"   [TARGET] Confidence: {enhanced.get('confidence_score', 0):.2f}")
                print(f"   [SEARCH] Search Method: {enhanced.get('search_method', 'unknown')}")
                print(f"    Sources Retrieved: {len(sources)}")
                
                usage = enhanced.get('usage', {})
                if isinstance(usage, dict):
                    total = usage.get('total_tokens', 0)
                    prompt = usage.get('prompt_tokens', 0)
                    completion = usage.get('completion_tokens', 0)
                    print(f"    Tokens: {total} ({prompt} prompt + {completion} completion)")
                
                print()
                
                if sources:
                    print(f" SOURCES:")
                    for j, src in enumerate(sources[:3], 1):
                        # Try different source formats (vector vs internet)
                        metadata = src.get('metadata', {})
                        filename = (
                            src.get('filename') or  # Vector search
                            metadata.get('title') or  # Internet search
                            metadata.get('source') or  # Internet URL
                            src.get('source') or
                            'unknown'
                        )
                        score = src.get('score') or metadata.get('relevance_score', 0)
                        print(f"   {j}. {filename} (score: {score:.3f})")
                    print()
                
                # Save result
                results.append({
                    "test_id": test['id'],
                    "query": test['query'],
                    "source_type": test['source'],
                    "category": test['category'],
                    "answer": answer,
                    "response_time": response_time,
                    "model": enhanced.get('model', 'unknown'),
                    "confidence": enhanced.get('confidence_score', 0),
                    "num_sources": len(sources),
                    "total_tokens": usage.get('total_tokens', 0) if isinstance(usage, dict) else 0,
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"[OK] Test {i}/2 PASSED\n")
                
            else:
                print(f"[FAIL] API Error: {response.status_code}")
                print(f"   {response.text[:200]}\n")
                
        except requests.exceptions.Timeout:
            print(f"[FAIL] Request timeout (>60s)\n")
        except Exception as e:
            print(f"[FAIL] Error: {e}\n")
    
    # Summary
    print("="*70)
    print("[STATS] TEST SUMMARY")
    print("="*70 + "\n")
    
    if len(results) == 2:
        print("[OK] ALL TESTS PASSED!\n")
        
        avg_time = sum(r['response_time'] for r in results) / len(results)
        avg_conf = sum(r['confidence'] for r in results) / len(results)
        avg_tokens = sum(r['total_tokens'] for r in results) / len(results)
        
        print(f"[METRIC] AVERAGE METRICS:")
        print(f"   Response Time: {avg_time:.2f}s")
        print(f"   Confidence: {avg_conf:.2f}")
        print(f"   Tokens/Query: {avg_tokens:.0f}")
        print()
        
        print("[TARGET] NEXT STEPS:")
        print("   1. Review the answers above - do they look good?")
        print("   2. If yes, run full evaluation with 50 questions:")
        print("      python evaluation/run_balanced_evaluation.py --name baseline_old_dataset")
        print()
        
        # Save results
        output_file = "evaluation/quick_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "api_url": api_url,
                "total_tests": len(results),
                "passed_tests": len(results),
                "average_metrics": {
                    "response_time": avg_time,
                    "confidence": avg_conf,
                    "tokens_per_query": avg_tokens
                },
                "results": results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"[SAVE] Results saved to: {output_file}")
        
    else:
        print(f"[WARN]  Only {len(results)}/2 tests passed")
        print("   Check the errors above and fix before running full evaluation")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick test with 2 questions")
    parser.add_argument(
        '--api-url',
        default='http://localhost:8001',
        help='RAG API base URL (default: http://localhost:8001)'
    )
    
    args = parser.parse_args()
    
    test_rag_api(args.api_url)
