"""
Enhanced RAG system with improved accuracy
- Better prompting and context formatting
- Query preprocessing and expansion  
- Reranking with cross-encoder
- Improved metadata usage
"""
import sys
import os
import re
from typing import List, Dict, Any, Tuple
sys.path.append('src')

from vector_store_supabase_rest import SupabaseRestVectorStore
from embed import embed_texts
import requests
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class EnhancedRAG:
    def __init__(self):
        self.store = SupabaseRestVectorStore()
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('GEN_MODEL', 'mistralai/mistral-small')
        
        # Try to load reranker (optional)
        self.reranker = None
        try:
            from sentence_transformers import CrossEncoder
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            print("✅ Reranker loaded for improved accuracy")
        except ImportError:
            print("⚠️  Reranker not available. Install: pip install sentence-transformers")
    
    def preprocess_query(self, query: str) -> List[str]:
        """Enhanced query preprocessing and expansion"""
        # Original query
        queries = [query.strip()]
        
        # Add variations
        if "employment" in query.lower() or "kerja" in query.lower():
            queries.extend([
                query + " tenaga kerja",
                query + " employment placement",
                query.replace("employment", "job placement"),
                query.replace("kerja", "employment")
            ])
        
        if "population" in query.lower() or "penduduk" in query.lower():
            queries.extend([
                query + " demographic data",
                query + " census",
                query.replace("population", "demographic"),
                query.replace("penduduk", "population")
            ])
        
        if "health" in query.lower() or "kesehatan" in query.lower():
            queries.extend([
                query + " medical services",
                query + " healthcare statistics",
                query.replace("health", "medical"),
                query.replace("kesehatan", "health")
            ])
        
        # Add location variations for Central Java
        if any(term in query.lower() for term in ["central java", "jawa tengah", "jateng"]):
            location_queries = []
            for q in queries:
                location_queries.extend([
                    q.replace("central java", "jawa tengah"),
                    q.replace("jawa tengah", "central java"),
                    q.replace("jateng", "central java")
                ])
            queries.extend(location_queries)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)
        
        return unique_queries[:5]  # Limit to top 5 variations
    
    def search_enhanced(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        """Enhanced search with query expansion and reranking - optimized for large datasets"""
        
        # Get multiple query variations (limited for speed)
        query_variants = self.preprocess_query(query)[:3]  # Limit to 3 variants for speed
        print(f"🔍 Searching with {len(query_variants)} query variants")
        
        all_results = []
        seen_ids = set()
        
        # Use smaller top_k for each variant to reduce processing time
        variant_top_k = max(3, top_k // len(query_variants))
        
        # Search with each query variant
        for variant in query_variants:
            try:
                variant_embedding = embed_texts([variant])[0]
                results = self.store.search(variant_embedding, top_k=variant_top_k)
                
                # Add results, avoiding duplicates
                for result in results:
                    result_id = result.get('id')
                    if result_id not in seen_ids:
                        result['query_variant'] = variant
                        all_results.append(result)
                        seen_ids.add(result_id)
                        
            except Exception as e:
                print(f"⚠️  Error with variant '{variant}': {e}")
        
        # Apply higher similarity threshold for better quality with large dataset
        min_similarity = 0.4  # Increased threshold for better quality
        filtered_results = [r for r in all_results if r.get('similarity', 0) > min_similarity]
        
        # Rerank only top candidates for speed
        if self.reranker and filtered_results:
            # Limit reranking to top 10 candidates for speed
            top_candidates = sorted(filtered_results, key=lambda x: x.get('similarity', 0), reverse=True)[:10]
            print("🔄 Reranking top results for better accuracy...")
            reranked_top = self.rerank_results(query, top_candidates)
            # Combine reranked top results with remaining results
            remaining = filtered_results[10:] if len(filtered_results) > 10 else []
            filtered_results = reranked_top + remaining
        
        # Sort by similarity and return top results
        filtered_results.sort(key=lambda x: x.get('rerank_score', x.get('similarity', 0)), reverse=True)
        return filtered_results[:top_k]
    
    def rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank results using cross-encoder for better accuracy"""
        if not self.reranker or not results:
            return results
        
        try:
            # Prepare query-document pairs
            pairs = []
            for result in results:
                content = result.get('content', '')
                # Combine content with metadata for better context
                metadata = result.get('metadata', {})
                source = metadata.get('source', '')
                enhanced_content = f"{source}: {content}"
                pairs.append([query, enhanced_content])
            
            # Get reranking scores
            scores = self.reranker.predict(pairs)
            
            # Update results with reranking scores
            for i, result in enumerate(results):
                result['rerank_score'] = float(scores[i])
            
            # Sort by reranking scores
            results.sort(key=lambda x: x.get('rerank_score', 0), reverse=True)
            print(f"✅ Reranked {len(results)} results")
            
        except Exception as e:
            print(f"⚠️  Reranking failed: {e}")
        
        return results
    
    def build_enhanced_context(self, results: List[Dict[str, Any]], query: str) -> str:
        """Build enhanced context with better formatting and metadata"""
        if not results:
            return "Tidak ada informasi relevan yang ditemukan."
        
        context_parts = []
        
        # Add a summary if we have multiple sources
        if len(results) > 1:
            sources = set()
            for result in results:
                metadata = result.get('metadata', {})
                source = metadata.get('source', 'Unknown')
                if source != 'Unknown':
                    sources.add(source)
            
            if sources:
                context_parts.append(f"SUMBER DATA: {', '.join(list(sources)[:5])}")
                context_parts.append("")
        
        # Add each result with enhanced formatting
        for i, result in enumerate(results, 1):
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Sumber tidak diketahui')
            similarity = result.get('similarity', 'N/A')
            rerank_score = result.get('rerank_score')
            
            # Create clean header
            header = f"### DOKUMEN {i}: {source}"
            if isinstance(similarity, float):
                relevance_pct = int(similarity * 100)
                header += f" (Relevansi: {relevance_pct}%)"
            
            context_parts.append(header)
            context_parts.append("")
            
            # Clean and format content
            clean_content = content.strip()
            # Remove excessive whitespace and format for readability
            clean_content = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_content)
            clean_content = re.sub(r'\s+', ' ', clean_content)
            
            context_parts.append(clean_content)
            context_parts.append("")
            context_parts.append("---")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def get_enhanced_response(self, context: str, question: str) -> str:
        """Get response with enhanced prompting"""
        
        system_prompt = """Anda adalah analis ahli data pemerintahan Jawa Tengah yang berpengalaman dalam menganalisis statistik dan informasi resmi. Anda memiliki akses ke dataset resmi meliputi ketenagakerjaan, demografi, kesehatan, ekonomi, dan administrasi dari berbagai kabupaten/kota di Provinsi Jawa Tengah.

PANDUAN RESPONS:
1. **Struktur Jelas**: Gunakan format terorganisir dengan header, bullet points, dan numbering
2. **Data Spesifik**: Sebutkan angka eksak, tanggal, dan lokasi dari data
3. **Konteks Bermakna**: Jelaskan signifikansi data dan implikasinya
4. **Bahasa yang Tepat**: Gunakan bahasa Indonesia yang formal namun mudah dipahami
5. **Formatasi Professional**: Gunakan markdown untuk struktur yang rapi

FORMAT JAWABAN:
- Mulai dengan ringkasan singkat (2-3 kalimat)
- Gunakan ### untuk judul utama
- Gunakan #### untuk sub-bagian  
- Gunakan bullet points (•) untuk daftar
- Gunakan **bold** untuk highlight penting
- Akhiri dengan kesimpulan atau rekomendasi jika relevan

GAYA BAHASA:
- Formal namun mudah dipahami
- Hindari jargon teknis yang tidak perlu
- Gunakan istilah Indonesia yang tepat
- Struktur kalimat yang jelas dan efektif"""

        user_prompt = f"""Berdasarkan dataset resmi Pemerintah Jawa Tengah berikut, jawablah pertanyaan dengan komprehensif dan terstruktur:

DATASET KONTEKS:
{context}

PERTANYAAN: {question}

INSTRUKSI KHUSUS:
- Berikan respons yang terorganisir dengan baik menggunakan markdown
- Mulai dengan ringkasan singkat, lalu detail data yang relevan
- Sertakan angka spesifik, lokasi, dan periode waktu jika tersedia
- Jelaskan konteks dan signifikansi data
- Jika ada pola atau trend, highlight dengan jelas
- Gunakan bahasa Indonesia yang formal namun mudah dipahami

FORMAT RESPONS:
1. **Ringkasan** (2-3 kalimat overview)
2. **Data Utama** (angka dan fakta kunci)
3. **Analisis** (interpretasi dan konteks)
4. **Kesimpulan** (insight atau rekomendasi jika relevan)"""

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/your-repo',
            'X-Title': 'Enhanced Central Java RAG System'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'max_tokens': 2000,
            'temperature': 0.1,
            'top_p': 0.9
        }
        
        try:
            response = requests.post('https://openrouter.ai/api/v1/chat/completions', 
                                   headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error generating response: {e}"
    
    def ask(self, question: str, top_k: int = 8) -> Dict[str, Any]:
        """Enhanced question answering with improved accuracy"""
        print(f"🤔 Question: {question}")
        print("🔍 Enhanced search in progress...")
        
        try:
            count = self.store.get_count()
            print(f"📊 Database contains {count} chunks")
            
            if count == 0:
                return {"error": "No data found in database"}
            
            # Enhanced search with query expansion and reranking
            results = self.search_enhanced(question, top_k=top_k)
            
            if not results:
                print("⚠️  No relevant information found for query")
                return {
                    "question": question,
                    "answer": "Maaf, saya tidak menemukan informasi yang relevan untuk pertanyaan tersebut dalam basis data saat ini.",
                    "sources": [],
                    "total_sources": 0,
                    "enhanced_features": {
                        "query_expansion": True,
                        "reranking": self.reranker is not None,
                        "enhanced_prompting": True
                    }
                }
            
            print(f"✅ Found {len(results)} relevant results")
            
            # Build enhanced context
            context = self.build_enhanced_context(results, question)
            
            print("🤖 Generating enhanced response...")
            
            # Get enhanced response (graceful fallback on failure)
            try:
                response = self.get_enhanced_response(context, question)
            except Exception as gen_err:
                print(f"⚠️  Response generation failed: {gen_err}")
                response = "Maaf, terjadi kesalahan saat menghasilkan jawaban."
            
            return {
                "question": question,
                "answer": response,
                "sources": [
                    {
                        "source": r.get('metadata', {}).get('source', 'Unknown'),
                        "similarity": r.get('similarity', 'N/A'),
                        "rerank_score": r.get('rerank_score'),
                        "content_preview": r.get('content', '')[:100] + "..."
                    }
                    for r in results
                ],
                "total_sources": len(results),
                "enhanced_features": {
                    "query_expansion": True,
                    "reranking": self.reranker is not None,
                    "enhanced_prompting": True
                }
            }
            
        except Exception as e:
            return {"error": f"Enhanced RAG error: {e}"}

def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        
        # Initialize enhanced RAG
        rag = EnhancedRAG()
        
        # Get enhanced response
        result = rag.ask(question)
        
        if "error" in result:
            print(f"❌ {result['error']}")
            return
        
        # Display results
        print(f"\n💡 **Enhanced Answer:**\n{result['answer']}")
        
        # Display sources with enhanced info
        print(f"\n📚 **Sources** ({result['total_sources']} documents):")
        for i, source in enumerate(result['sources'], 1):
            similarity = source['similarity']
            rerank_score = source['rerank_score']
            
            if isinstance(similarity, float):
                similarity = f"{similarity:.3f}"
            
            score_info = f"Similarity: {similarity}"
            if rerank_score is not None:
                score_info += f", Rerank: {rerank_score:.3f}"
                
            print(f"  {i}. {source['source']} ({score_info})")
            print(f"     Preview: {source['content_preview']}")
        
        # Display enhancement info
        features = result['enhanced_features']
        enhancements = []
        if features['query_expansion']:
            enhancements.append("Query Expansion")
        if features['reranking']:
            enhancements.append("Cross-Encoder Reranking")
        if features['enhanced_prompting']:
            enhancements.append("Enhanced Prompting")
            
        print(f"\n🚀 **Accuracy Enhancements Active:** {', '.join(enhancements)}")
        
    else:
        print("Usage: python enhanced_rag.py \"Your question here\"")
        print("Example: python enhanced_rag.py \"What employment data is available for Central Java?\"")

if __name__ == "__main__":
    main()
