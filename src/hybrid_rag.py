"""
Hybrid RAG System with Internet Search Fallback
Progressive strategy: Vector Search → Enhanced Vector → Internet Search
"""
import time
from typing import Dict, List, Any, Optional, Tuple
import sys
import os

# Add the src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from smart_enhanced_rag import SmartEnhancedRAG
from internet_search import EnhancedInternetSearch
from ask import query_llm

class HybridRAGSystem:
    """
    Intelligent RAG system with progressive fallback:
    1. Vector search (5s)
    2. Enhanced vector search with query expansion (10s) 
    3. Internet search (5s)
    Total timeout: 20s
    """
    
    def __init__(self):
        print("🚀 Initializing Hybrid RAG System...")
        
        # Initialize components
        self.rag_system = SmartEnhancedRAG()
        self.internet_search = EnhancedInternetSearch()
        
        # Timeout configuration (total 20s)
        self.vector_timeout = 5.0      # Phase 1: Initial vector search
        self.enhanced_timeout = 10.0   # Phase 2: Enhanced vector search  
        self.internet_timeout = 5.0    # Phase 3: Internet search
        self.total_timeout = 20.0      # Maximum total time
        
        # Quality thresholds (made more strict)
        self.min_similarity = 0.65     # Increased minimum similarity for good results
        self.min_sources = 3           # Minimum sources for confidence
        self.confidence_threshold = 0.75 # Increased overall confidence threshold
        
        print("✅ Hybrid RAG System initialized")
        print(f"⏱️  Timeouts: Vector({self.vector_timeout}s) + Enhanced({self.enhanced_timeout}s) + Internet({self.internet_timeout}s) = {self.total_timeout}s")
    
    def assess_result_quality(self, result: Dict[str, Any]) -> Tuple[float, str]:
        """
        Assess the quality of RAG results
        Returns: (quality_score, reason)
        """
        if not result or "error" in result:
            return 0.0, "error_in_result"
        
        # Get enhanced features
        features = result.get("enhanced_features", {})
        top_similarity = features.get("top_similarity", 0.0)
        total_sources = result.get("total_sources", 0)
        
        # Calculate base quality score
        quality_score = 0.0
        reasons = []
        
        # Similarity score (50% weight) - much stricter
        if top_similarity >= 0.8:
            quality_score += 0.5
        elif top_similarity >= 0.7:
            quality_score += 0.3
        elif top_similarity >= 0.6:
            quality_score += 0.15
        else:
            reasons.append("low_similarity")
        
        # Source count (25% weight) - stricter requirements
        if total_sources >= 10:
            quality_score += 0.25
        elif total_sources >= 5:
            quality_score += 0.15
        elif total_sources >= 3:
            quality_score += 0.1
        else:
            reasons.append("insufficient_sources")
        
        # Domain relevance (15% weight) - require strong domain match
        if features.get("domain_relevant", False):
            quality_score += 0.15
        else:
            reasons.append("not_domain_relevant")
        
        # Answer length and completeness (10% weight)
        answer = result.get("answer", "")
        if len(answer) > 300:
            quality_score += 0.1
        elif len(answer) > 150:
            quality_score += 0.05
        else:
            reasons.append("short_answer")
        
        # Determine main reason for low quality
        if reasons:
            main_reason = reasons[0]
        elif quality_score >= self.confidence_threshold:
            main_reason = "good_quality"
        else:
            main_reason = "marginal_quality"
        
        return quality_score, main_reason
    
    def expand_query_for_retry(self, original_query: str) -> str:
        """Expand query with related terms for better vector search"""
        query_lower = original_query.lower()
        
        expansions = {
            'siup': 'siup surat izin usaha perdagangan',
            'tdp': 'tdp tanda daftar perusahaan',
            'izin usaha': 'izin usaha perizinan berusaha',
            'investasi': 'investasi penanaman modal',
            'kontak': 'kontak alamat telepon email',
            'prosedur': 'prosedur tata cara langkah',
            'syarat': 'syarat persyaratan dokumen',
            'biaya': 'biaya tarif ongkos'
        }
        
        expanded = original_query
        for term, expansion in expansions.items():
            if term in query_lower and expansion not in expanded.lower():
                expanded = f"{expanded} {expansion}"
        
        return expanded
    
    def ask_with_fallback(self, question: str, k: int = 12) -> Dict[str, Any]:
        """
        Main method with progressive fallback strategy
        """
        start_time = time.time()
        phase_times = {}
        
        print(f"🔍 Hybrid search for: {question}")
        print(f"⏱️  Max time: {self.total_timeout}s")
        
        # PHASE 1: Initial Vector Search (5s)
        print("\n📋 Phase 1: Vector Search")
        phase1_start = time.time()
        
        try:
            vector_result = self.rag_system.ask(question, k=k)
            phase1_time = time.time() - phase1_start
            phase_times['vector'] = phase1_time
            
            print(f"⏱️  Vector search: {phase1_time:.2f}s")
            
            # Assess quality
            quality_score, reason = self.assess_result_quality(vector_result)
            print(f"📊 Quality: {quality_score:.2f} ({reason})")
            
            if quality_score >= self.confidence_threshold:
                print("✅ Vector search succeeded!")
                vector_result["enhanced_features"]["search_method"] = "vector_only"
                vector_result["enhanced_features"]["quality_score"] = quality_score
                vector_result["enhanced_features"]["phase_times"] = phase_times
                return vector_result
                
        except Exception as e:
            print(f"❌ Vector search failed: {e}")
            phase1_time = time.time() - phase1_start
            phase_times['vector'] = phase1_time
        
        # Check remaining time
        elapsed = time.time() - start_time
        if elapsed >= self.total_timeout:
            return self._timeout_response(question, phase_times)
        
        # PHASE 2: Enhanced Vector Search (10s)
        print("\n🔄 Phase 2: Enhanced Vector Search")
        phase2_start = time.time()
        
        try:
            # Expand query and search with more sources
            expanded_query = self.expand_query_for_retry(question)
            print(f"🔍 Expanded query: {expanded_query}")
            
            enhanced_result = self.rag_system.ask(expanded_query, k=k*2)
            phase2_time = time.time() - phase2_start
            phase_times['enhanced_vector'] = phase2_time
            
            print(f"⏱️  Enhanced search: {phase2_time:.2f}s")
            
            # Assess quality
            quality_score, reason = self.assess_result_quality(enhanced_result)
            print(f"📊 Quality: {quality_score:.2f} ({reason})")
            
            if quality_score >= self.confidence_threshold * 0.8:  # Lower threshold for phase 2
                print("✅ Enhanced vector search succeeded!")
                enhanced_result["enhanced_features"]["search_method"] = "enhanced_vector"
                enhanced_result["enhanced_features"]["quality_score"] = quality_score
                enhanced_result["enhanced_features"]["phase_times"] = phase_times
                enhanced_result["enhanced_features"]["expanded_query"] = expanded_query
                return enhanced_result
                
        except Exception as e:
            print(f"❌ Enhanced search failed: {e}")
            phase2_time = time.time() - phase2_start
            phase_times['enhanced_vector'] = phase2_time
        
        # Check remaining time
        elapsed = time.time() - start_time
        if elapsed >= self.total_timeout:
            return self._timeout_response(question, phase_times)
        
        # PHASE 3: Internet Search (5s)
        print("\n🌐 Phase 3: Internet Search")
        phase3_start = time.time()
        
        try:
            # Search internet
            internet_results = self.internet_search.search_multiple_engines(question)
            
            if internet_results:
                # Format as context
                internet_context = self.internet_search.format_internet_context(internet_results)
                
                # Generate response using LLM with internet context
                llm_result = query_llm(question, internet_context)
                internet_answer = llm_result['text'] if isinstance(llm_result, dict) else llm_result
                
                phase3_time = time.time() - phase3_start
                phase_times['internet'] = phase3_time
                
                print(f"⏱️  Internet search: {phase3_time:.2f}s")
                print(f"🎯 Found {len(internet_results)} internet sources")
                
                # Format as standard response
                internet_response = {
                    "answer": internet_answer,
                    "sources": [
                        {
                            "text": result.get("content", ""),
                            "metadata": {
                                "source": result.get("url", ""),
                                "title": result.get("title", ""),
                                "relevance_score": result.get("relevance_score", 0)
                            }
                        }
                        for result in internet_results
                    ],
                    "total_sources": len(internet_results),
                    "enhanced_features": {
                        "search_method": "internet_fallback",
                        "quality_score": 0.7,  # Base score for internet results
                        "confidence_score": 0.50,  # Lower confidence for internet results
                        "phase_times": phase_times,
                        "internet_engines": ["duckduckgo"] + (["serper"] if self.internet_search.serper_key else []),
                        "response_time": f"{time.time() - start_time:.2f}s",
                        "model": llm_result.get('model', 'unknown') if isinstance(llm_result, dict) else 'unknown',
                        "usage": llm_result.get('usage', {}) if isinstance(llm_result, dict) else {}
                    }
                }
                
                print("✅ Internet search succeeded!")
                return internet_response
            else:
                print("❌ No internet results found")
                
        except Exception as e:
            print(f"❌ Internet search failed: {e}")
            phase3_time = time.time() - phase3_start
            phase_times['internet'] = phase3_time
        
        # All phases failed
        print("💔 All search phases failed")
        return self._fallback_response(question, phase_times)
    
    def _timeout_response(self, question: str, phase_times: Dict[str, float]) -> Dict[str, Any]:
        """Response when timeout is reached"""
        return {
            "answer": f"""Maaf, waktu pencarian telah habis untuk pertanyaan "{question}". 
            
Silakan coba dengan pertanyaan yang lebih spesifik atau hubungi DPMPTSP Jawa Tengah langsung:
- Website: dpmptsp.jatengprov.go.id  
- Telepon: (024) 3569961
- Email: info@dpmptsp.jatengprov.go.id""",
            "sources": [],
            "total_sources": 0,
            "enhanced_features": {
                "search_method": "timeout",
                "quality_score": 0.0,
                "phase_times": phase_times,
                "timeout_reached": True,
                "response_time": f"{self.total_timeout:.2f}s"
            }
        }
    
    def _fallback_response(self, question: str, phase_times: Dict[str, float]) -> Dict[str, Any]:
        """Response when all methods fail"""
        return {
            "answer": f"""Maaf, sistem tidak dapat menemukan informasi yang relevan untuk pertanyaan "{question}".

Namun, Anda dapat menghubungi DPMPTSP Jawa Tengah langsung untuk bantuan:

**Kontak DPMPTSP Jawa Tengah:**
- **Website:** dpmptsp.jatengprov.go.id
- **Telepon:** (024) 3569961  
- **Email:** info@dpmptsp.jatengprov.go.id
- **Alamat:** Jl. Menteri Supeno No. 2, Semarang

**Jam Layanan:**
- Senin-Jumat: 08.00-15.00 WIB
- Sabtu: 08.00-12.00 WIB

Staf DPMPTSP akan memberikan informasi terkini dan akurat sesuai kebutuhan Anda.""",
            "sources": [],
            "total_sources": 0,
            "enhanced_features": {
                "search_method": "all_failed",
                "quality_score": 0.0,
                "phase_times": phase_times,
                "response_time": f"{sum(phase_times.values()):.2f}s"
            }
        }


def test_hybrid_system():
    """Test the hybrid system with various queries"""
    hybrid = HybridRAGSystem()
    
    test_queries = [
        "cara mengurus SIUP dan TDP toko retail",
        "prosedur investasi asing di Jawa Tengah", 
        "kontak DPMPTSP Jawa Tengah",
        "syarat izin mendirikan bangunan",
        "biaya pengurusan izin usaha",
        "random question about weather"  # Should trigger fallback
    ]
    
    print("🧪 Testing Hybrid RAG System")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/{len(test_queries)}: {query}")
        
        start_time = time.time()
        result = hybrid.ask_with_fallback(query)
        total_time = time.time() - start_time
        
        # Print summary
        features = result.get("enhanced_features", {})
        method = features.get("search_method", "unknown")
        quality = features.get("quality_score", 0)
        sources = result.get("total_sources", 0)
        
        print(f"\n📊 Results:")
        print(f"   Method: {method}")
        print(f"   Quality: {quality:.2f}")
        print(f"   Sources: {sources}")
        print(f"   Time: {total_time:.2f}s")
        print(f"   Answer: {result.get('answer', '')[:150]}...")
        
        if "phase_times" in features:
            print(f"   Phase times: {features['phase_times']}")
        
        print("-" * 60)


if __name__ == "__main__":
    test_hybrid_system()