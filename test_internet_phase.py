#!/usr/bin/env python3
"""
Test internet search phase specifically
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.hybrid_rag import HybridRAGSystem

def test_internet_search_phase():
    """Test questions that should definitely trigger internet search"""
    hybrid = HybridRAGSystem()
    
    # Questions that vector DB definitely won't have
    test_queries = [
        "What is blockchain technology?",  # Tech question
        "Current weather in Jakarta",      # Real-time question 
        "Bitcoin price today",             # Real-time financial data
        "How to make pizza?",              # General cooking question
    ]
    
    print("🧪 Testing Internet Search Phase")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/{len(test_queries)}: {query}")
        
        result = hybrid.ask_with_fallback(query)
        
        # Print detailed results
        features = result.get("enhanced_features", {})
        method = features.get("search_method", "unknown")
        quality = features.get("quality_score", 0)
        sources = result.get("total_sources", 0)
        phase_times = features.get("phase_times", {})
        
        print(f"\n📊 Results:")
        print(f"   Method: {method}")
        print(f"   Quality: {quality:.2f}")
        print(f"   Sources: {sources}")
        print(f"   Phase times: {phase_times}")
        print(f"   Answer: {result.get('answer', '')[:200]}...")
        
        print("-" * 60)

if __name__ == "__main__":
    test_internet_search_phase()