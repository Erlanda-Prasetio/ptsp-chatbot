"""
Hybrid RAG specifically for OLD dataset only

This is a wrapper around SmartEnhancedRAG that:
- Forces all queries to use the documents_old table
- Never falls back to NEW dataset
- Provides consistent OLD dataset results
"""

import sys
import os

# MUST set environment variable BEFORE importing SmartEnhancedRAG
os.environ['PG_TABLE'] = 'documents_old'

sys.path.append('src')
sys.path.append('.')

from src.smart_enhanced_rag import SmartEnhancedRAG


class SmartEnhancedRAG_OLD(SmartEnhancedRAG):
    """
    Extended SmartEnhancedRAG but hardcoded to use documents_old table only
    
    All retrieval methods are constrained to the OLD dataset.
    """
    
    def __init__(self):
        """Initialize OLD dataset RAG - forces documents_old table"""
        # Ensure environment variable is set before parent init
        os.environ['PG_TABLE'] = 'documents_old'
        super().__init__()
        print("✅ SmartEnhancedRAG_OLD initialized for documents_old table")
