"""
Enhanced RAG system for Central Java PTSP data
Uses the improved local vector store with better prompting
"""
import sys
import os
sys.path.append('src')

from vector_store import store
from embed import embed_texts
from ask import build_context, query_llm
from config import VECTOR_BACKEND
import time

class EnhancedRAG:
    def __init__(self):
        """Initialize the enhanced RAG system"""
        # Force local backend
        if VECTOR_BACKEND != 'local':
            raise RuntimeError(f"Expected local backend, got {VECTOR_BACKEND}. Please set VECTOR_BACKEND=local in .env")
        
        self.store = store
        self.reranker = None  # We can add reranking later if needed
        
        # Load the vector store
        self.store.load()
        if self.store.embeddings is None:
            raise RuntimeError("Vector store is empty. Please run ingest first.")
        
        print(f"✅ Enhanced RAG initialized with {len(self.store.texts)} chunks using {VECTOR_BACKEND} backend")
    
    def ask(self, question: str, k: int = 8):
        """
        Ask a question to the enhanced RAG system
        
        Args:
            question: The user's question
            k: Number of chunks to retrieve
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            start_time = time.time()
            
            # Expand query for better retrieval (Indonesian language support)
            expanded_question = self._expand_query(question)
            
            # Embed the query
            q_emb = embed_texts([expanded_question])[0]
            
            # Search for similar chunks
            hits = self.store.search(q_emb, k=k*2)  # Get more candidates
            
            if not hits:
                return self._no_results_response(start_time)
            
            # Filter for relevance
            relevant_hits = [hit for hit in hits if hit.get('score', 0) >= 0.25]
            if not relevant_hits:
                relevant_hits = hits[:3]  # Use top 3 if none meet threshold
            
            # Build context and query LLM
            context = build_context(relevant_hits[:k])
            if not context.strip():
                return self._no_results_response(start_time)
                
            answer = query_llm(question, context)
            
            # Clean answer to remove any remaining document references
            answer = self._clean_answer(answer)
            
            # Process sources for frontend display
            sources = []
            for i, hit in enumerate(relevant_hits[:5]):  # Show top 5 sources
                source_info = hit.get('meta', {})
                source_path = source_info.get('source', f'chunk_{i}')
                
                # Extract filename from path
                if '\\' in source_path:
                    filename = source_path.split('\\')[-1]
                elif '/' in source_path:
                    filename = source_path.split('/')[-1]
                else:
                    filename = source_path
                
                sources.append({
                    "filename": filename,
                    "score": hit.get('score', 0),
                    "content_preview": hit.get('text', '')[:200] + "...",
                    "path": source_path
                })
            
            response_time = time.time() - start_time
            
            return {
                "answer": answer,
                "sources": sources,
                "total_sources": len(relevant_hits),
                "enhanced_features": {
                    "query_expansion": True,
                    "enhanced_prompting": True,
                    "reranking": False
                },
                "response_time": response_time
            }
            
        except Exception as e:
            return {
                "error": f"RAG query failed: {str(e)}",
                "answer": "Maaf, terjadi kesalahan dalam memproses pertanyaan Anda.",
                "sources": [],
                "total_sources": 0,
                "enhanced_features": {
                    "query_expansion": False,
                    "enhanced_prompting": False,
                    "reranking": False
                }
            }
    
    def _expand_query(self, question: str) -> str:
        """Expand query for better retrieval"""
        # Add DPMPTSP context for better matching
        dpmptsp_terms = {
            'dpmptsp': 'DPMPTSP Dinas Penanaman Modal Pelayanan Terpadu Satu Pintu',
            'perizinan': 'perizinan izin permit layanan',
            'investasi': 'investasi penanaman modal',
            'pelayanan': 'pelayanan layanan service'
        }
        
        expanded = question.lower()
        for term, expansion in dpmptsp_terms.items():
            if term in expanded:
                expanded = f"{question} {expansion}"
                break
        
        return expanded
    
    def _clean_answer(self, answer: str) -> str:
        """Remove document references from answer"""
        import re
        # Remove patterns like "Dokumen 1:", "Data Source 2:", etc.
        cleaned = re.sub(r'Dokumen \d+:\s*[^\n]*\n?', '', answer)
        cleaned = re.sub(r'Data Source \d+[^\n]*\n?', '', cleaned)
        cleaned = re.sub(r'---[^-]*---\s*', '', cleaned)
        cleaned = re.sub(r'\(relevance=[0-9.]+\)', '', cleaned)
        return cleaned.strip()
    
    def _no_results_response(self, start_time):
        """Return response when no relevant results found"""
        return {
            "answer": "Maaf, informasi yang Anda cari tidak tersedia dalam database DPMPTSP saat ini. Silakan coba dengan kata kunci yang berbeda atau hubungi langsung kantor DPMPTSP Jawa Tengah.",
            "sources": [],
            "total_sources": 0,
            "enhanced_features": {
                "query_expansion": True,
                "enhanced_prompting": True,
                "reranking": False
            },
            "response_time": time.time() - start_time
        }
    
    def get_stats(self):
        """Get system statistics"""
        return {
            "total_chunks": len(self.store.texts) if self.store.texts else 0,
            "total_embeddings": len(self.store.embeddings) if self.store.embeddings is not None else 0,
            "backend": VECTOR_BACKEND,
            "features": {
                "local_vector_store": True,
                "enhanced_prompting": True,
                "query_expansion": True,
                "reranking": self.reranker is not None
            }
        }

# Test the enhanced RAG system
if __name__ == "__main__":
    print("🚀 Testing Enhanced RAG System")
    print("=" * 50)
    
    try:
        rag = EnhancedRAG()
        stats = rag.get_stats()
        print(f"📊 System stats: {stats}")
        
        # Test with a working query
        test_question = "apa itu dpmptsp"
        print(f"\n🔍 Testing: {test_question}")
        
        result = rag.ask(test_question)
        print(f"📝 Answer: {result['answer']}")
        print(f"📊 Sources: {result['total_sources']}")
        print(f"⏱️ Response time: {result.get('response_time', 0):.2f}s")
        
    except Exception as e:
        print(f"❌ Error: {e}")
