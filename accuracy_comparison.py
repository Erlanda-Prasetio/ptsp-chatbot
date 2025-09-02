"""
RAG Accuracy Comparison Tool
Compare standard vs enhanced RAG performance
"""
import sys
import time
import os
sys.path.append('src')

from enhanced_rag import EnhancedRAG
from vector_store_supabase_rest import SupabaseRestVectorStore
from embed import embed_texts
import requests
from dotenv import load_dotenv

load_dotenv()

class RAGComparison:
    def __init__(self):
        self.enhanced_rag = EnhancedRAG()
        self.store = SupabaseRestVectorStore()
        
    def standard_search(self, question: str, top_k: int = 5):
        """Standard RAG search (original method)"""
        try:
            question_embedding = embed_texts([question])[0]
            results = self.store.search(question_embedding, top_k=top_k)
            return results
        except Exception as e:
            print(f"❌ Standard search error: {e}")
            return []
    
    def compare_searches(self, question: str):
        """Compare standard vs enhanced search results"""
        print(f"🔍 **Comparing RAG Methods for:** {question}")
        print("=" * 70)
        
        # Standard search
        print("📊 **Standard RAG Search:**")
        start_time = time.time()
        standard_results = self.standard_search(question)
        standard_time = time.time() - start_time
        
        print(f"  • Found: {len(standard_results)} results")
        print(f"  • Time: {standard_time:.2f}s")
        if standard_results:
            avg_similarity = sum(r.get('similarity', 0) for r in standard_results) / len(standard_results)
            print(f"  • Avg similarity: {avg_similarity:.3f}")
        
        # Enhanced search  
        print("\n🚀 **Enhanced RAG Search:**")
        start_time = time.time()
        enhanced_results = self.enhanced_rag.search_enhanced(question)
        enhanced_time = time.time() - start_time
        
        print(f"  • Found: {len(enhanced_results)} results")
        print(f"  • Time: {enhanced_time:.2f}s")
        if enhanced_results:
            avg_similarity = sum(r.get('similarity', 0) for r in enhanced_results) / len(enhanced_results)
            avg_rerank = sum(r.get('rerank_score', 0) for r in enhanced_results if r.get('rerank_score') is not None) / len(enhanced_results)
            print(f"  • Avg similarity: {avg_similarity:.3f}")
            print(f"  • Avg rerank score: {avg_rerank:.3f}")
        
        # Compare top results
        print("\n📋 **Top Results Comparison:**")
        
        print("\n**Standard RAG Top 3:**")
        for i, result in enumerate(standard_results[:3], 1):
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            similarity = result.get('similarity', 0)
            content_preview = result.get('content', '')[:60] + "..."
            print(f"  {i}. {source} (sim: {similarity:.3f})")
            print(f"     {content_preview}")
        
        print("\n**Enhanced RAG Top 3:**")
        for i, result in enumerate(enhanced_results[:3], 1):
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            similarity = result.get('similarity', 0)
            rerank_score = result.get('rerank_score', 'N/A')
            content_preview = result.get('content', '')[:60] + "..."
            print(f"  {i}. {source} (sim: {similarity:.3f}, rerank: {rerank_score})")
            print(f"     {content_preview}")
        
        return {
            'standard': {'results': standard_results, 'time': standard_time},
            'enhanced': {'results': enhanced_results, 'time': enhanced_time}
        }

def test_accuracy_improvements():
    """Test various questions to demonstrate accuracy improvements"""
    
    test_questions = [
        "What employment data is available for Central Java?",
        "Show me population statistics for Central Java",
        "What health data is available?",
        "Employment trends in Kabupaten Cilacap",
        "Data about Wonosobo employment",
        "Central Java labor force statistics"
    ]
    
    comparator = RAGComparison()
    
    print("🧪 **RAG Accuracy Testing Suite**")
    print("=" * 60)
    print("Testing multiple questions to compare standard vs enhanced RAG performance\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔬 **Test {i}/{len(test_questions)}**")
        comparison = comparator.compare_searches(question)
        
        print("\n" + "─" * 70)
        input("Press Enter to continue to next test...")
    
    print("\n🎯 **Accuracy Improvements Summary:**")
    print("✅ Enhanced RAG provides:")
    print("  • Query expansion for better coverage")
    print("  • Cross-encoder reranking for relevance")
    print("  • Better context formatting")
    print("  • Improved prompting for accuracy")
    print("  • Metadata-aware search")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        comparator = RAGComparison()
        comparator.compare_searches(question)
    else:
        print("Usage:")
        print("  python accuracy_comparison.py \"Your question\" - Compare single question")
        print("  python accuracy_comparison.py test - Run full test suite")
        
        if len(sys.argv) == 2 and sys.argv[1] == "test":
            test_accuracy_improvements()
        else:
            print("\nExample: python accuracy_comparison.py \"What employment data is available?\"")
            print("Or run: python accuracy_comparison.py test")
