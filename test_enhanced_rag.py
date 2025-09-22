"""
Test script for enhanced RAG system
Verifies improvements work with existing rag_api.py deployment
"""

import sys
import os
sys.path.append('src')

import time
import json
from smart_enhanced_rag import SmartEnhancedRAG

def test_enhanced_rag():
    """Test the enhanced RAG system with sample queries"""
    print("🧪 Testing Enhanced RAG System")
    print("=" * 50)
    
    # Initialize RAG system
    try:
        rag = SmartEnhancedRAG()
        print("✅ RAG system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        return False
    
    # Test queries that previously had low scores
    test_queries = [
        "cara mengurus izin usaha di PTSP",
        "persyaratan permohonan izin investasi", 
        "prosedur DPMPTSP untuk penanaman modal",
        "syarat izin mendirikan bangunan",
        "pelayanan terpadu satu pintu jawa tengah",
        "biaya pengurusan izin usaha",
        "dokumen yang diperlukan untuk izin",
        "kontak DPMPTSP Jawa Tengah"
    ]
    
    results = []
    total_similarity = 0
    high_quality_count = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/{len(test_queries)}: {query}")
        
        try:
            start_time = time.time()
            result = rag.ask(query)
            response_time = time.time() - start_time
            
            # Extract metrics
            enhanced_features = result.get('enhanced_features', {})
            top_similarity = enhanced_features.get('top_similarity', 0)
            confidence = enhanced_features.get('confidence', 'unknown')
            total_sources = result.get('total_sources', 0)
            
            total_similarity += top_similarity
            
            print(f"  📊 Similarity: {top_similarity:.3f}")
            print(f"  🎯 Confidence: {confidence}")
            print(f"  📄 Sources: {total_sources}")
            print(f"  ⏱️ Time: {response_time:.2f}s")
            print(f"  📝 Answer preview: {result['answer'][:100]}...")
            
            # Check if high quality (>0.6 similarity)
            if top_similarity > 0.6:
                high_quality_count += 1
                print("  ✅ High quality result")
            elif top_similarity > 0.4:
                print("  ⚠️ Medium quality result")
            else:
                print("  ❌ Low quality result")
            
            results.append({
                'query': query,
                'similarity': top_similarity,
                'confidence': confidence,
                'sources': total_sources,
                'response_time': response_time,
                'enhanced_features': enhanced_features
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({
                'query': query,
                'error': str(e),
                'similarity': 0,
                'confidence': 'error'
            })
    
    # Calculate overall metrics
    avg_similarity = total_similarity / len(test_queries)
    high_quality_percentage = (high_quality_count / len(test_queries)) * 100
    
    print(f"\n📊 Overall Test Results:")
    print(f"  - Average similarity: {avg_similarity:.3f}")
    print(f"  - High quality (>0.6): {high_quality_percentage:.1f}%")
    print(f"  - Total tests: {len(test_queries)}")
    print(f"  - Enhanced features: {results[0].get('enhanced_features', {}).get('enhanced_scoring', False)}")
    
    # Determine if improvement achieved
    improvement_target = 0.65  # Target average similarity
    success = avg_similarity >= improvement_target
    
    if success:
        print(f"\n✅ Enhancement SUCCESS!")
        print(f"  - Achieved {avg_similarity:.3f} avg similarity (target: {improvement_target})")
        print(f"  - Expected accuracy improvement: 58.3% → 75%+")
    else:
        print(f"\n⚠️ Enhancement needs more work")
        print(f"  - Current: {avg_similarity:.3f} (target: {improvement_target})")
        print(f"  - Consider running enhanced ingestion first")
    
    # Save detailed results
    test_summary = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'avg_similarity': avg_similarity,
        'high_quality_percentage': high_quality_percentage,
        'improvement_achieved': success,
        'target_similarity': improvement_target,
        'test_results': results
    }
    
    with open('enhanced_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n📝 Detailed results saved to: enhanced_test_results.json")
    
    return success

def test_api_compatibility():
    """Test that enhanced system is compatible with rag_api.py"""
    print("\n🔌 Testing API Compatibility")
    print("-" * 30)
    
    try:
        # Import and test the same way rag_api.py does
        from smart_enhanced_rag import SmartEnhancedRAG
        
        rag_system = SmartEnhancedRAG()
        
        # Test the same interface used by rag_api.py
        test_message = "cara mengurus izin usaha"
        result = rag_system.ask(test_message)
        
        # Check expected response format
        required_keys = ['answer', 'sources', 'total_sources', 'enhanced_features']
        for key in required_keys:
            if key not in result:
                print(f"❌ Missing key: {key}")
                return False
        
        print("✅ API compatibility confirmed")
        print(f"  - All required response keys present")
        print(f"  - Enhanced features available: {result['enhanced_features'].get('enhanced_scoring', False)}")
        return True
        
    except Exception as e:
        print(f"❌ API compatibility failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Enhanced RAG System Test Suite")
    print("=" * 60)
    
    # Test API compatibility first
    api_compatible = test_api_compatibility()
    
    if not api_compatible:
        print("\n❌ API compatibility test failed!")
        print("Your rag_api.py deployment may have issues.")
        return False
    
    # Test enhanced functionality
    enhanced_working = test_enhanced_rag()
    
    # Final summary
    print(f"\n🎯 Final Summary:")
    print(f"  - API Compatible: {'✅' if api_compatible else '❌'}")
    print(f"  - Enhanced Working: {'✅' if enhanced_working else '❌'}")
    
    if api_compatible and enhanced_working:
        print(f"\n🎉 SUCCESS! Your enhanced rag_api.py is ready!")
        print(f"Expected accuracy improvement: 58.3% → 75%+")
    elif api_compatible:
        print(f"\n⚠️ API works but enhancement may need more data processing")
        print(f"Consider running: python enhanced_ingest.py")
    else:
        print(f"\n❌ Issues detected. Check dependencies and setup.")
    
    return api_compatible and enhanced_working

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)