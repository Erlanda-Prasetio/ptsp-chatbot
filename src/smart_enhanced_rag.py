"""
Enhanced RAG system with better query handling and domain detection
"""
import sys
import os
sys.path.append('src')

from vector_store import store
from embed import embed_texts
from ask import build_context, query_llm
from config import VECTOR_BACKEND
import time
import re

class SmartEnhancedRAG:
    def __init__(self):
        """Initialize the enhanced RAG system with smart domain detection"""
        # Force local backend
        if VECTOR_BACKEND != 'local':
            raise RuntimeError(f"Expected local backend, got {VECTOR_BACKEND}. Please set VECTOR_BACKEND=local in .env")
        
        self.store = store
        self.store.load()
        if self.store.embeddings is None:
            raise RuntimeError("Vector store is empty. Please run ingest first.")
        
        # Define relevant keywords for our domain
        self.domain_keywords = {
            'dpmptsp', 'perizinan', 'izin', 'investasi', 'jawa tengah', 'central java',
            'penanaman modal', 'pelayanan terpadu', 'satu pintu', 'provinsi',
            'gubernur', 'pemerintah', 'kebijakan', 'layanan', 'prosedur',
            'pendaftaran', 'berkas', 'persyaratan', 'dokumen', 'online',
            'usaha', 'bisnis', 'perusahaan', 'cv', 'pt', 'umkm', 'startup'
        }
        
        print(f"✅ Smart Enhanced RAG initialized with {len(self.store.texts)} chunks")
    
    def is_domain_relevant(self, query: str) -> bool:
        """Check if query is relevant to our domain"""
        query_lower = query.lower()
        
        # Check for domain keywords
        for keyword in self.domain_keywords:
            if keyword in query_lower:
                return True
        
        # Check for common irrelevant patterns
        irrelevant_patterns = [
            r'\bweather\b', r'\bnews\b', r'\bprice\b', r'\bcovid\b',
            r'\bbitcoin\b', r'\bcrypto\b', r'\bfood\b', r'\brecipe\b',
            r'\bmovie\b', r'\bmusic\b', r'\bgame\b', r'\bsport\b'
        ]
        
        for pattern in irrelevant_patterns:
            if re.search(pattern, query_lower):
                return False
        
        return True
    
    def ask(self, question: str, k: int = 8):
        """
        Ask a question with smart domain detection
        """
        start_time = time.time()
        
        # Check domain relevance first
        if not self.is_domain_relevant(question):
            return self._out_of_scope_response(question, start_time)
        
        # Expand query for better retrieval
        expanded_question = self._expand_query(question)
        
        # Embed the query
        q_emb = embed_texts([expanded_question])[0]
        
        # Search for similar chunks
        hits = self.store.search(q_emb, k=k*2)
        
        if not hits:
            return self._no_results_response(start_time)
        
        # Filter for relevance with adaptive threshold
        base_threshold = 0.25
        relevant_hits = [hit for hit in hits if hit.get('score', 0) >= base_threshold]
        
        if not relevant_hits:
            # Lower threshold for domain-relevant queries
            relevant_hits = hits[:3]
        
        # Build context and query LLM
        context = build_context(relevant_hits[:k])
        if not context.strip():
            return self._no_results_response(start_time)
            
        # Enhanced prompt for better responses
        enhanced_prompt = f"""
        Berdasarkan konteks dokumen pemerintah Jawa Tengah tentang DPMPTSP dan pelayanan publik,
        jawab pertanyaan berikut dengan lengkap dan akurat:
        
        Pertanyaan: {question}
        
        Berikan jawaban yang:
        1. LENGKAP dan DETAIL - jangan potong jawaban di tengah
        2. Spesifik dan relevan dengan DPMPTSP Jawa Tengah
        3. Menggunakan bahasa Indonesia yang jelas dan mudah dipahami
        4. Menyertakan prosedur atau langkah-langkah jika relevan
        5. Merujuk pada peraturan atau kebijakan yang berlaku
        6. Pastikan semua informasi penting tersampaikan dengan baik
        
        PENTING: Berikan jawaban yang UTUH dan TIDAK TERPOTONG sampai selesai.
        """
        
        answer = query_llm(enhanced_prompt, context)
        answer = self._clean_answer(answer)
        
        # Process sources
        sources = self._process_sources(relevant_hits[:5])
        
        response_time = time.time() - start_time
        
        return {
            "answer": answer,
            "sources": sources,
            "total_sources": len(relevant_hits),
            "enhanced_features": {
                "query_expansion": expanded_question != question,
                "domain_relevant": True,
                "response_time": f"{response_time:.2f}s",
                "confidence": "high" if relevant_hits and relevant_hits[0].get('score', 0) > 0.5 else "medium"
            }
        }
    
    def _expand_query(self, question: str) -> str:
        """Expand query with synonyms and related terms"""
        expansions = {
            'dpmptsp': 'dpmptsp dinas penanaman modal pelayanan terpadu satu pintu',
            'izin': 'izin perizinan permit license',
            'investasi': 'investasi penanaman modal investment',
            'prosedur': 'prosedur langkah cara tahapan procedure',
            'syarat': 'syarat persyaratan requirement dokumen berkas'
        }
        
        expanded = question.lower()
        for key, expansion in expansions.items():
            if key in expanded:
                expanded = expanded.replace(key, expansion)
        
        return expanded
    
    def _out_of_scope_response(self, question: str, start_time: float):
        """Response for out-of-scope queries"""
        response_time = time.time() - start_time
        
        return {
            "answer": f"""
            Maaf, pertanyaan Anda tentang "{question}" berada di luar cakupan sistem informasi DPMPTSP Jawa Tengah.
            
            Saya dapat membantu Anda dengan informasi tentang:
            • Layanan dan prosedur DPMPTSP
            • Perizinan dan investasi di Jawa Tengah
            • Persyaratan dan dokumen yang diperlukan
            • Kebijakan pemerintah Provinsi Jawa Tengah
            • Prosedur pelayanan terpadu satu pintu
            
            Silakan ajukan pertanyaan yang berkaitan dengan topik-topik tersebut.
            """,
            "sources": [],
            "total_sources": 0,
            "enhanced_features": {
                "query_expansion": False,
                "domain_relevant": False,
                "response_time": f"{response_time:.2f}s",
                "confidence": "high",
                "reason": "out_of_scope"
            }
        }
    
    def _no_results_response(self, start_time: float):
        """Response when no relevant documents found"""
        response_time = time.time() - start_time
        
        return {
            "answer": "Maaf, saya tidak menemukan informasi yang relevan untuk pertanyaan Anda dalam database saat ini. Silakan coba dengan kata kunci yang berbeda atau hubungi DPMPTSP Jawa Tengah langsung.",
            "sources": [],
            "total_sources": 0,
            "enhanced_features": {
                "query_expansion": False,
                "domain_relevant": True,
                "response_time": f"{response_time:.2f}s",
                "confidence": "low",
                "reason": "no_results"
            }
        }
    
    def _clean_answer(self, answer: str) -> str:
        """Clean up the answer text"""
        # Remove document references
        cleaned = re.sub(r'\[Doc\d+\]', '', answer)
        cleaned = re.sub(r'Document \d+:', '', cleaned)
        cleaned = re.sub(r'Source:.*', '', cleaned)
        
        # Clean up whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _process_sources(self, hits):
        """Process source information for display"""
        sources = []
        for i, hit in enumerate(hits):
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
        
        return sources
