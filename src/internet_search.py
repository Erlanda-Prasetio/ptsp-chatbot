"""
Enhanced Internet Search Module for PTSP RAG System
Provides intelligent fallback search when vector database results are insufficient
"""
import os
import requests
from typing import List, Dict, Optional
import time
import json
from urllib.parse import quote_plus
import re

class EnhancedInternetSearch:
    """
    Enhanced internet search with multiple engines and PTSP context enhancement
    """
    
    def __init__(self):
        # API Keys (optional, fallback to free services if not available)
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.bing_key = os.getenv("BING_SEARCH_KEY")
        
        # Settings
        self.max_results = 5
        self.timeout = 10  # Increased from 5 to 10 seconds
        self.enabled = True
        
        print(f"🔍 Internet search initialized (Serper: {'✓' if self.serper_key else '✗'}, Bing: {'✓' if self.bing_key else '✗'})")
    
    def enhance_query_for_ptsp(self, query: str) -> str:
        """Enhance query with PTSP-specific context for better web search results"""
        query_lower = query.lower()
        
        # Add PTSP context if not present
        ptsp_terms = ['dpmptsp', 'ptsp', 'jawa tengah', 'central java']
        has_ptsp_context = any(term in query_lower for term in ptsp_terms)
        
        if not has_ptsp_context:
            # Add relevant context based on query content
            if any(term in query_lower for term in ['izin', 'siup', 'tdp', 'perizinan']):
                enhanced = f"{query} DPMPTSP Jawa Tengah perizinan usaha"
            elif any(term in query_lower for term in ['investasi', 'penanaman modal']):
                enhanced = f"{query} DPMPTSP Jawa Tengah investasi"
            elif any(term in query_lower for term in ['kontak', 'alamat', 'telepon']):
                enhanced = f"{query} DPMPTSP Provinsi Jawa Tengah kontak"
            else:
                enhanced = f"{query} DPMPTSP Provinsi Jawa Tengah"
        else:
            enhanced = query
            
        return enhanced
    
    def search_duckduckgo_instant(self, query: str) -> List[Dict[str, any]]:
        """Search using DuckDuckGo Instant Answer API (free, no API key needed)"""
        try:
            enhanced_query = self.enhance_query_for_ptsp(query)
            
            url = "https://api.duckduckgo.com/"
            params = {
                'q': enhanced_query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            # Try with shorter timeout first
            response = requests.get(url, params=params, timeout=3)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract abstract if available
            if data.get('Abstract') and len(data.get('Abstract', '')) > 50:
                results.append({
                    'title': data.get('AbstractSource', 'DuckDuckGo Knowledge'),
                    'content': data.get('Abstract'),
                    'url': data.get('AbstractURL', ''),
                    'source': 'duckduckgo_abstract',
                    'relevance_score': 0.8  # High relevance for abstracts
                })
            
            # Extract related topics
            for topic in data.get('RelatedTopics', [])[:3]:
                if topic.get('Text') and len(topic.get('Text', '')) > 30:
                    results.append({
                        'title': self._extract_title_from_url(topic.get('FirstURL', '')),
                        'content': topic.get('Text'),
                        'url': topic.get('FirstURL', ''),
                        'source': 'duckduckgo_related',
                        'relevance_score': 0.6
                    })
            
            return results
            
        except Exception as e:
            print(f"⚠️  DuckDuckGo search failed: {e}")
            # Fallback to simple web search
            return self.search_simple_web(query)
    
    def search_simple_web(self, query: str) -> List[Dict[str, any]]:
        """Simple web search fallback using basic HTTP requests"""
        try:
            enhanced_query = self.enhance_query_for_ptsp(query)
            
            # Use DuckDuckGo HTML interface as fallback
            url = "https://html.duckduckgo.com/html/"
            params = {
                'q': enhanced_query
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=8)
            response.raise_for_status()
            
            # For now, return a generic helpful response if we can connect
            if response.status_code == 200:
                return [{
                    'title': 'Web Search Results',
                    'content': f'Based on your query "{query}", you may find relevant information by contacting DPMPTSP Jawa Tengah directly or visiting their official website.',
                    'url': 'https://dpmptsp.jatengprov.go.id',
                    'source': 'fallback_web',
                    'relevance_score': 0.4
                }]
            
        except Exception as e:
            print(f"⚠️  Simple web search also failed: {e}")
            
        # Final fallback - return helpful generic response
        return [{
            'title': 'DPMPTSP Information',
            'content': f'Untuk pertanyaan "{query}", Anda dapat menghubungi DPMPTSP Jawa Tengah langsung di (024) 3569961 atau mengunjungi website resmi dpmptsp.jatengprov.go.id untuk informasi terkini.',
            'url': 'https://dpmptsp.jatengprov.go.id',
            'source': 'fallback_info',
            'relevance_score': 0.3
        }]
    
    def search_serper_google(self, query: str) -> List[Dict[str, any]]:
        """Search using Serper API (Google Search)"""
        if not self.serper_key:
            return []
            
        try:
            enhanced_query = self.enhance_query_for_ptsp(query)
            
            url = "https://google.serper.dev/search"
            headers = {
                'X-API-KEY': self.serper_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': enhanced_query,
                'num': self.max_results,
                'hl': 'id',  # Indonesian language
                'gl': 'id',  # Indonesia region
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract organic results
            for result in data.get('organic', [])[:self.max_results]:
                # Score relevance based on domain and content
                relevance_score = self._calculate_relevance_score(
                    result.get('link', ''), 
                    result.get('title', ''), 
                    result.get('snippet', '')
                )
                
                results.append({
                    'title': result.get('title', ''),
                    'content': result.get('snippet', ''),
                    'url': result.get('link', ''),
                    'source': 'serper_google',
                    'relevance_score': relevance_score
                })
            
            return results
            
        except Exception as e:
            print(f"⚠️  Serper search failed: {e}")
            return []
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract meaningful title from URL"""
        if not url:
            return "Related Topic"
        
        # Extract from URL path
        parts = url.split('/')
        if len(parts) > 1:
            title = parts[-1].replace('_', ' ').replace('-', ' ').title()
            return title if title else "Related Topic"
        return "Related Topic"
    
    def _calculate_relevance_score(self, url: str, title: str, content: str) -> float:
        """Calculate relevance score for search result"""
        score = 0.3  # Base score
        
        # Boost government and official sites
        if any(domain in url.lower() for domain in ['gov.id', 'go.id', 'jatengprov.go.id']):
            score += 0.4
        
        # Boost PTSP-related content
        text = f"{title} {content}".lower()
        ptsp_keywords = ['dpmptsp', 'ptsp', 'jawa tengah', 'izin', 'investasi', 'perizinan']
        for keyword in ptsp_keywords:
            if keyword in text:
                score += 0.1
        
        # Penalize low-quality content
        if len(content) < 50:
            score -= 0.2
        
        return min(1.0, max(0.1, score))
    
    def search_multiple_engines(self, query: str) -> List[Dict[str, any]]:
        """Search using multiple engines and combine results"""
        if not self.enabled:
            return []
        
        all_results = []
        
        print(f"🔍 Internet search for: {query}")
        
        # DuckDuckGo (always available, free)
        ddg_results = self.search_duckduckgo_instant(query)
        all_results.extend(ddg_results)
        print(f"📋 DuckDuckGo: {len(ddg_results)} results")
        
        # Serper (if API key available)
        if self.serper_key:
            serper_results = self.search_serper_google(query)
            all_results.extend(serper_results)
            print(f"📋 Serper: {len(serper_results)} results")
        
        # Remove duplicates and sort by relevance
        unique_results = self._deduplicate_and_rank(all_results)
        
        print(f"🎯 Final results: {len(unique_results)}")
        return unique_results
    
    def _deduplicate_and_rank(self, results: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Remove duplicates and rank results by relevance"""
        seen_content = set()
        unique_results = []
        
        for result in results:
            content = result.get('content', '').strip()
            content_key = content.lower()[:100]  # First 100 chars for comparison
            
            if (content_key not in seen_content and 
                len(content) > 30 and 
                result.get('relevance_score', 0) > 0.2):
                seen_content.add(content_key)
                unique_results.append(result)
        
        # Sort by relevance score
        unique_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return unique_results[:self.max_results]
    
    def format_internet_context(self, results: List[Dict[str, any]]) -> str:
        """Format internet search results into context for LLM"""
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Untitled')
            content = result.get('content', '')
            url = result.get('url', '')
            score = result.get('relevance_score', 0)
            
            # Clean content
            content = re.sub(r'\s+', ' ', content.strip())
            if len(content) > 400:
                content = content[:397] + "..."
            
            context_part = f"[Web Source {i}] {title} (Score: {score:.2f})\n{content}"
            if url and any(domain in url for domain in ['gov.id', 'go.id']):
                context_part += f"\n🏛️ Official Source: {url}"
            elif url:
                context_part += f"\n🔗 Source: {url}"
            
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)


# Legacy class for compatibility
class SafeInternetSearch(EnhancedInternetSearch):
    def __init__(self):
        super().__init__()
        
    def is_safe_to_search(self, query: str) -> bool:
        """Check if query is safe for internet search"""
        if not self.enabled:
            return False
            
        # Block sensitive queries
        sensitive_patterns = [
            'password', 'login', 'secret', 'token', 'key',
            'personal', 'private', 'confidential'
        ]
        
        query_lower = query.lower()
        for pattern in sensitive_patterns:
            if pattern in query_lower:
                return False
        
        return True
    
    def search_web(self, query: str) -> Optional[List[Dict]]:
        """Legacy method for compatibility"""
        if not self.is_safe_to_search(query):
            return None
        return self.search_multiple_engines(query)
        """
        Perform safe web search with government domain preference
        """
        if not self.is_safe_to_search(query):
            return None
        
        try:
            # Prefer government sources
            gov_query = f"{query} site:gov.id OR site:go.id"
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': gov_query,
                'num': self.max_results,
                'safe': 'high'  # Enable safe search
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                # Additional safety check
                domain = self._extract_domain(item.get('link', ''))
                if self._is_trusted_domain(domain):
                    results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'domain': domain
                    })
            
            return results
            
        except Exception as e:
            print(f"⚠️  Search error: {e}")
            return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except:
            return ""
    
    def _is_trusted_domain(self, domain: str) -> bool:
        """Check if domain is in our trusted list"""
        for safe_domain in self.safe_domains:
            if safe_domain in domain:
                return True
        return False

class HybridRAG:
    """
    RAG system with optional internet search fallback
    """
    
    def __init__(self, rag_system):
        self.rag = rag_system
        self.web_search = SafeInternetSearch()
        
    def ask(self, question: str, use_web_fallback: bool = False):
        """
        Ask question with optional web search fallback
        """
        # First try local RAG
        result = self.rag.ask(question)
        
        # If RAG finds relevant info, return it
        if (result["enhanced_features"]["domain_relevant"] and 
            len(result["sources"]) > 0 and
            result["enhanced_features"]["confidence"] != "low"):
            return result
        
        # If enabled and safe, try web search as fallback
        if (use_web_fallback and 
            self.web_search.enabled and 
            not result["enhanced_features"]["domain_relevant"]):
            
            web_results = self.web_search.search_web(question)
            if web_results:
                return self._combine_web_results(question, result, web_results)
        
        return result
    
    def _combine_web_results(self, question: str, rag_result: dict, web_results: List[Dict]) -> dict:
        """Combine RAG and web search results"""
        web_info = []
        for result in web_results:
            web_info.append(f"• {result['title']}: {result['snippet']} (Sumber: {result['domain']})")
        
        combined_answer = f"""
        Informasi dari database DPMPTSP tidak tersedia untuk pertanyaan ini.
        
        Berikut adalah informasi dari sumber web terpercaya:
        
        {chr(10).join(web_info)}
        
        ⚠️  Informasi di atas berasal dari internet dan mungkin tidak selalu akurat atau terkini.
        Untuk informasi resmi DPMPTSP, silakan hubungi langsung kantor DPMPTSP Jawa Tengah.
        """
        
        web_sources = [
            {
                "filename": f"Web: {result['domain']}",
                "score": 0.8,
                "content_preview": result['snippet'],
                "path": result['link']
            }
            for result in web_results
        ]
        
        return {
            "answer": combined_answer,
            "sources": web_sources,
            "total_sources": len(web_sources),
            "enhanced_features": {
                **rag_result["enhanced_features"],
                "web_search_used": True,
                "web_results_count": len(web_results)
            }
        }

# Example configuration for .env file
EXAMPLE_ENV_CONFIG = """
# Internet Search Configuration (OPTIONAL)
# WARNING: Only enable in controlled environments
ENABLE_INTERNET_SEARCH=false
SEARCH_API_KEY=your_google_custom_search_api_key
SEARCH_ENGINE_ID=your_custom_search_engine_id
"""

if __name__ == "__main__":
    print("Internet Search Module Configuration:")
    print(EXAMPLE_ENV_CONFIG)
