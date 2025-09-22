#!/usr/bin/env python3
"""
Test hybrid system with PTSP-related questions
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.hybrid_rag import HybridRAGSystem

def test_ptsp_questions():
    """Test PTSP-related questions that might benefit from internet search"""
    hybrid = HybridRAGSystem()
    
    # PTSP questions with varying relevance to existing data
    test_queries = [
        "prosedur mendirikan usaha kuliner di Jawa Tengah",  # Should be in vector DB
        "kontak email DPMPTSP Jawa Tengah terbaru",         # Might need internet for latest info
        "jam operasional DPMPTSP hari Sabtu",               # Specific info that might need internet
        "persyaratan SIUP untuk toko online",               # General SIUP info should be in DB
    ]
    
    print("🧪 Testing PTSP-Related Questions")
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
    test_ptsp_questions()