"""
Hybrid RAG specifically for NEW dataset only

This is a wrapper around SmartEnhancedRAG that:
- Forces all queries to use the documents_new table
- Never falls back to OLD dataset
- Provides consistent NEW dataset results
"""

import sys
import os

sys.path.append('src')
sys.path.append('.')

from src.hybrid_rag import SmartEnhancedRAG


class SmartEnhancedRAG_NEW(SmartEnhancedRAG):
    """
    Extended SmartEnhancedRAG but hardcoded to use documents_new table only
    
    All retrieval methods are constrained to the NEW dataset.
    """
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        model_name: str = "mistralai/mistral-small-3.2-24b-instruct:free",
        table_name: str = "documents_new"
    ):
        """Initialize RAG for NEW dataset only"""
        # Force table_name to always be documents_new
        self.forced_table = "documents_new"
        
        # Initialize parent
        super().__init__(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            model_name=model_name,
            table_name="documents_new"  # Always use documents_new
        )
        
        print("✅ SmartEnhancedRAG_NEW initialized for NEW dataset")
    
    def retrieve(self, query: str, top_k: int = 5):
        """
        Retrieve chunks from NEW dataset only
        
        Args:
            query: Query text
            top_k: Number of top chunks to retrieve
            
        Returns:
            Dictionary with sources and search_method
        """
        # Force table to NEW
        original_table = self.table_name
        self.table_name = "documents_new"
        
        try:
            result = super().retrieve(query, top_k)
            return result
        finally:
            self.table_name = original_table
    
    def query(self, query_text: str, temperature: float = 0.7):
        """
        Run full RAG pipeline on NEW dataset only
        
        Args:
            query_text: Query text
            temperature: LLM temperature for generation
            
        Returns:
            Dictionary with answer, sources, and search_method
        """
        # Force table to NEW
        original_table = self.table_name
        self.table_name = "documents_new"
        
        try:
            result = super().query(query_text, temperature)
            return result
        finally:
            self.table_name = original_table
    
    def _search_vector_only(self, query_embedding, top_k: int = 5):
        """Vector search on NEW dataset only"""
        original_table = self.table_name
        self.table_name = "documents_new"
        
        try:
            return super()._search_vector_only(query_embedding, top_k)
        finally:
            self.table_name = original_table
    
    def _search_enhanced(self, query_text: str, query_embedding, top_k: int = 5):
        """Enhanced search on NEW dataset only"""
        original_table = self.table_name
        self.table_name = "documents_new"
        
        try:
            return super()._search_enhanced(query_text, query_embedding, top_k)
        finally:
            self.table_name = original_table
