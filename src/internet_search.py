"""
Optional Internet Search Module for RAG System
WARNING: Use with caution in production environments
"""
import os
import requests
from typing import List, Dict, Optional
import time

class SafeInternetSearch:
    """
    A controlled internet search module with safety measures
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_INTERNET_SEARCH", "false").lower() == "true"
        self.api_key = os.getenv("SEARCH_API_KEY")  # Google Custom Search API
        self.search_engine_id = os.getenv("SEARCH_ENGINE_ID")
        
        # Safety settings
        self.max_results = 3
        self.timeout = 5
        self.safe_domains = {
            'gov.id', 'go.id', 'jatengprov.go.id',
            'wikipedia.org', 'kemenkeu.go.id'
        }
        
        if self.enabled and not (self.api_key and self.search_engine_id):
            print("⚠️  Internet search enabled but missing API credentials")
            self.enabled = False
    
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
