#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Detailed MADAM Debate Test - Shows Step-by-Step Process
========================================================

This script runs the multi-agent debate system with detailed logging
to visualize how agents debate and the aggregator makes decisions.

Usage:
    python test_madam_detailed.py

Author: RAG Evaluation Framework
Date: November 2025
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import MADAM system
from madam_hybrid_system import MadamHybridRAGSystem

# Test queries
TEST_QUERIES = [
    {
        "id": 1,
        "question": "Bagaimana cara menambahkan KBLI pada perizinan usaha?",
        "category": "Procedure"
    },
    {
        "id": 2,
        "question": "Apakah KSO atau Joint Operation bisa memiliki NIB?",
        "category": "Legal"
    }
]

def print_header(text, char="="):
    """Print a formatted header"""
    print("\n" + char * 80)
    print(f" {text}")
    print(char * 80)

def print_subheader(text):
    """Print a formatted subheader"""
    print(f"\n{'-' * 80}")
    print(f"  {text}")
    print(f"{'-' * 80}")

def test_query_detailed(rag_system, query_data):
    """Test a single query with detailed logging"""
    question = query_data['question']
    category = query_data['category']
    
    print_header(f"QUERY {query_data['id']}: {question}")
    print(f"Category: {category}")
    
    # Start timer
    start_time = time.time()
    
    print("\n[PHASE 1] Vector Search...")
    print("-" * 80)
    
    try:
        # Call ask_with_fallback which includes MADAM debate
        result = rag_system.ask_with_fallback(
            question=question,
            k=12
        )
        
        elapsed = time.time() - start_time
        
        # Extract search method and phases
        search_method = result.get('search_method', 'unknown')
        
        print_header(f"SEARCH METHOD: {search_method.upper()}")
        
        # Show vector search results
        if 'vector_results' in result:
            vector_results = result['vector_results']
            print_subheader("VECTOR SEARCH RESULTS")
            print(f"  Chunks Retrieved: {len(vector_results)}")
            print(f"  Top Chunk Score: {vector_results[0].get('score', 0):.3f if vector_results else 0}")
        
        # Show MADAM debate if used
        if search_method == 'madam_debate' and 'debate_log' in result:
            debate_log = result['debate_log']
            
            print_subheader("MADAM DEBATE PROCESS")
            print(f"  Number of Agents: {debate_log.get('num_agents', 4)}")
            print(f"  Max Rounds: {debate_log.get('max_rounds', 3)}")
            print(f"  Convergence Threshold: {debate_log.get('convergence_threshold', 0.8)}")
            
            rounds = debate_log.get('rounds', [])
            print(f"  Total Rounds Executed: {len(rounds)}")
            
            for round_idx, round_data in enumerate(rounds, 1):
                print_subheader(f"ROUND {round_idx}")
                
                agent_responses = round_data.get('responses', [])
                for agent_idx, response in enumerate(agent_responses, 1):
                    answer = response.get('answer', 'N/A')
                    confidence = response.get('confidence', 0)
                    
                    print(f"\n  [AGENT {agent_idx}]")
                    print(f"    Answer: {answer[:150]}{'...' if len(answer) > 150 else ''}")
                    print(f"    Confidence: {confidence:.3f}")
                    
                    time.sleep(0.3)  # Slow down for readability
                
                # Round summary
                confidences = [r.get('confidence', 0) for r in agent_responses]
                if confidences:
                    print(f"\n  [ROUND SUMMARY]")
                    print(f"    Average Confidence: {sum(confidences)/len(confidences):.3f}")
                    print(f"    Confidence Range: {min(confidences):.3f} - {max(confidences):.3f}")
                
                # Check convergence
                if round_data.get('converged', False):
                    print(f"\n  [CONVERGENCE] Consensus reached after {round_idx} rounds!")
                    break
                
                time.sleep(0.5)
            
            # Aggregation
            if 'aggregation' in debate_log:
                agg = debate_log['aggregation']
                print_subheader("AGGREGATOR PROCESS")
                print(f"  Method: {agg.get('method', 'unknown')}")
                print(f"  Final Confidence: {agg.get('confidence', 0):.3f}")
                print(f"  Selected Answer: {agg.get('answer', 'N/A')[:200]}...")
        
        # Show final result
        print_header("FINAL RESULT")
        print(f"  Answer: {result.get('answer', 'N/A')[:300]}")
        print(f"  Method: {search_method}")
        print(f"  Sources: {len(result.get('sources', []))} chunks")
        print(f"  Total Time: {elapsed:.2f}s")
        
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[ERROR] {e}")
        print(f"Time elapsed: {elapsed:.2f}s")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function"""
    print_header("MADAM DEBATE DETAILED TEST", "=")
    print(f"Test Queries: {len(TEST_QUERIES)}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize RAG system
    print("\n[INIT] Initializing MADAM Hybrid RAG System...")
    try:
        rag_system = MadamHybridRAGSystem()
        print("[OK] System initialized successfully")
    except Exception as e:
        print(f"[ERROR] Failed to initialize system: {e}")
        return
    
    # Run tests
    results = []
    for query in TEST_QUERIES:
        result = test_query_detailed(rag_system, query)
        if result:
            results.append({
                'query': query,
                'result': result
            })
        
        if query['id'] < len(TEST_QUERIES):
            print("\n" + "=" * 80)
            print("Waiting 5 seconds before next query...")
            print("=" * 80)
            time.sleep(5)
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"Total Queries: {len(TEST_QUERIES)}")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(TEST_QUERIES) - len(results)}")
    
    if results:
        methods = [r['result'].get('search_method', 'unknown') for r in results]
        print(f"\nSearch Methods Used:")
        for method in set(methods):
            count = methods.count(method)
            print(f"  - {method}: {count}")
    
    print("\n[DONE] Test completed!")

if __name__ == "__main__":
    main()
