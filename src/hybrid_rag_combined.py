"""
Hybrid RAG specifically for COMBINED dataset

This is a wrapper around SmartEnhancedRAG that:
- Forces all queries to use the documents_combined table
- Uses both OLD and NEW datasets merged together
- Provides consistent COMBINED dataset results
"""

import sys
import os

# MUST set environment variable BEFORE importing SmartEnhancedRAG
os.environ['PG_TABLE'] = 'documents_combined'

sys.path.append('src')
sys.path.append('.')

from src.smart_enhanced_rag import SmartEnhancedRAG


class SmartEnhancedRAG_COMBINED(SmartEnhancedRAG):
    """
    Extended SmartEnhancedRAG but hardcoded to use documents_combined table only
    
    All retrieval methods are constrained to the COMBINED dataset.
    """
    
    def __init__(self):
        """Initialize COMBINED dataset RAG - forces documents_combined table"""
        # Ensure environment variable is set before parent init
        os.environ['PG_TABLE'] = 'documents_combined'
        super().__init__()
        print("✅ SmartEnhancedRAG_COMBINED initialized for documents_combined table")
