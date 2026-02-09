#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced RAG system with better query handling and domain detection
Includes improved PDF processing, semantic chunking, and content filtering
"""
import sys
import os
sys.path.append('src')

from embed import embed_texts
from ask import build_context, query_llm
from config import VECTOR_BACKEND
from domain_config import DOMAIN_KEYWORDS, RAG_PROMPT_TEMPLATE
import time
import re

# Import enhanced utilities
try:
    from enhanced_utils import calculate_relevance_score
    ENHANCED_UTILS_AVAILABLE = True
    print("[OK] Full enhanced utils loaded")
except ImportError:
    try:
        from lightweight_utils import calculate_relevance_score
        ENHANCED_UTILS_AVAILABLE = True
        print("[OK] Lightweight enhanced utils loaded")
    except ImportError:
        print("[WARN] Enhanced utils not available, using basic functionality")
        ENHANCED_UTILS_AVAILABLE = False

# Import the appropriate vector store based on backend
if VECTOR_BACKEND == 'supabase':
    from vector_store_supabase_rest import SupabaseRestVectorStore
    store = None  # Will be initialized in __init__
else:
    from vector_store import store
    SupabaseRestVectorStore = None  # type: ignore

class SmartEnhancedRAG:
    def __init__(self):
        """Initialize the enhanced RAG system with smart domain detection"""
        print(f" Initializing Smart Enhanced RAG with {VECTOR_BACKEND} backend...")
        
        if VECTOR_BACKEND == 'supabase':
            self.store = SupabaseRestVectorStore()
            # Check if we have data in Supabase
            try:
                test_results = self.store.search(embed_texts(["test"])[0], top_k=1)
                if not test_results:
                    print("[WARN]  Supabase vector store appears empty. You may need to run ingestion.")
                else:
                    print(f"[OK] Supabase vector store connected with existing data")
            except Exception as e:
                print(f"[WARN]  Supabase connection issue: {e}")
        else:
            self.store = store
            self.store.load()
            if self.store.embeddings is None:
                raise RuntimeError("Vector store is empty. Please run ingest first.")
            print(f"[OK] Local vector store loaded with {len(self.store.texts)} chunks")
        
        # Define relevant keywords for our domain
        self.domain_keywords = DOMAIN_KEYWORDS
        
        print(f"[OK] Smart Enhanced RAG initialized with {VECTOR_BACKEND} backend")
    
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
        Ask a question with smart domain detection and enhanced retrieval
        """
        start_time = time.time()
        
        # Check domain relevance first
        if not self.is_domain_relevant(question):
            return self._out_of_scope_response(question, start_time)
        
        # Expand query for better retrieval
        expanded_question = self._expand_query(question)
        
        # Embed the query
        q_emb = embed_texts([expanded_question])[0]
        
        # Search for similar chunks with enhanced filtering
        if VECTOR_BACKEND == 'supabase':
            hits = self.store.search(q_emb, top_k=k*3)  # Get more candidates
            # Normalize Supabase data format to match local format
            normalized_hits = []
            for hit in hits:
                normalized_hit = {
                    'id': hit.get('id'),  # Preserve chunk ID from Supabase
                    'text': hit.get('content', ''),  # Map 'content' to 'text'
                    'score': hit.get('similarity', 0),  # Map 'similarity' to 'score'
                    'metadata': hit.get('metadata', {}),
                    'source': hit.get('metadata', {}).get('source', 'Unknown')
                }
                # Add enhanced relevance scoring if available
                if ENHANCED_UTILS_AVAILABLE and normalized_hit['text']:
                    relevance_score = calculate_relevance_score(question, normalized_hit['text'])
                    # Combine semantic similarity with keyword relevance
                    normalized_hit['combined_score'] = (normalized_hit['score'] * 0.7) + (relevance_score * 0.3)
                else:
                    normalized_hit['combined_score'] = normalized_hit['score']
                normalized_hits.append(normalized_hit)
            hits = normalized_hits
        else:
            hits = self.store.search(q_emb, k=k*3)  # Get more candidates
            # Add enhanced relevance scoring for local store too
            if ENHANCED_UTILS_AVAILABLE:
                for hit in hits:
                    if hit.get('text'):
                        relevance_score = calculate_relevance_score(question, hit['text'])
                        hit['combined_score'] = (hit.get('score', 0) * 0.7) + (relevance_score * 0.3)
                    else:
                        hit['combined_score'] = hit.get('score', 0)
        
        if not hits:
            return self._no_results_response(start_time)
        
        # Enhanced filtering with adaptive threshold
        base_threshold = 0.35  # Increased from 0.25 for better quality
        
        # Sort by combined score if available, otherwise by original score
        sort_key = 'combined_score' if ENHANCED_UTILS_AVAILABLE else 'score'
        hits_sorted = sorted(hits, key=lambda x: x.get(sort_key, 0), reverse=True)
        
        relevant_hits = [hit for hit in hits_sorted if hit.get(sort_key, 0) >= base_threshold]
        
        if not relevant_hits:
            # Lower threshold for domain-relevant queries but still maintain quality
            relevant_hits = hits_sorted[:3]
        
        # Take top results after enhanced scoring
        final_hits = relevant_hits[:k]
        
        # Build context and query LLM
        context = build_context(final_hits)
        if not context.strip():
            return self._no_results_response(start_time)
            
        # Enhanced prompt for better responses
        enhanced_prompt = RAG_PROMPT_TEMPLATE.format(question=question)

        llm_result = query_llm(enhanced_prompt, context)
        answer = llm_result.get('text', '') if isinstance(llm_result, dict) else llm_result

        # Process sources with enhanced scoring info
        sources = self._process_sources_enhanced(final_hits[:5])
        
        response_time = time.time() - start_time
        
        # Calculate confidence based on top result score
        top_score = final_hits[0].get(sort_key, 0) if final_hits else 0
        confidence = "high" if top_score > 0.6 else "medium" if top_score > 0.4 else "low"
        confidence_score = round(top_score, 2)  # Numeric confidence
        
        return {
            "answer": answer,
            "sources": sources,
            "total_sources": len(relevant_hits),
            "enhanced_features": {
                "query_expansion": expanded_question != question,
                "domain_relevant": True,
                "response_time": f"{response_time:.2f}s",
                "confidence": confidence,
                "confidence_score": confidence_score,  # Add numeric confidence
                "top_similarity": round(top_score, 3),
                "enhanced_scoring": ENHANCED_UTILS_AVAILABLE,
                "model": llm_result.get('model', 'unknown') if isinstance(llm_result, dict) else 'unknown',
                "usage": llm_result.get('usage', {}) if isinstance(llm_result, dict) else {}
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
            "answer": (
                f"Maaf, pertanyaan Anda tentang \"{question}\" berada di luar cakupan sistem informasi DPMPTSP Jawa Tengah.\n\n"
                "Saya dapat membantu Anda dengan informasi tentang:\n"
                "- Layanan dan prosedur DPMPTSP\n"
                "- Perizinan dan investasi di Jawa Tengah\n"
                "- Persyaratan dan dokumen yang diperlukan\n"
                "- Kebijakan pemerintah Provinsi Jawa Tengah\n"
                "- Prosedur pelayanan terpadu satu pintu\n\n"
                "Silakan ajukan pertanyaan yang berkaitan dengan topik-topik tersebut."
            ),
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
                "chunk_id": hit.get('id'),  # Include chunk ID
                "filename": filename,
                "score": hit.get('score', 0),
                "content_preview": hit.get('text', '')[:200] + "...",
                "path": source_path
            })
        
        return sources
    
    def _process_sources_enhanced(self, hits):
        """Process source information with enhanced scoring details"""
        sources = []
        for i, hit in enumerate(hits):
            source_info = hit.get('meta', {}) or hit.get('metadata', {})
            source_path = source_info.get('source', f'chunk_{i}')
            
            # Extract filename from path
            if '\\' in source_path:
                filename = source_path.split('\\')[-1]
            elif '/' in source_path:
                filename = source_path.split('/')[-1]
            else:
                filename = source_path
            
            # Get the appropriate score
            score = hit.get('combined_score', hit.get('score', 0))
            original_score = hit.get('score', 0)
            
            sources.append({
                "chunk_id": hit.get('id'),  # Include chunk ID
                "filename": filename,
                "score": round(score, 3),
                "original_similarity": round(original_score, 3),
                "content_preview": hit.get('text', '')[:200] + "...",
                "path": source_path,
                "enhanced": ENHANCED_UTILS_AVAILABLE
            })
        
        return sources
