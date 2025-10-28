"""
Hybrid RAG System for OLD dataset only
Routes all queries to documents_old table
"""
import os
import sys

# Set environment BEFORE any imports
os.environ['PG_TABLE'] = 'documents_old'

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append('src')

from hybrid_rag import HybridRAGSystem

class HybridRAGSystem_OLD(HybridRAGSystem):
    """
    Hybrid RAG System specialized for OLD dataset
    Inherits all functionality but forces use of documents_old table
    """
    
    def __init__(self):
        """Initialize Hybrid RAG System for OLD dataset"""
        # Ensure environment variable is set
        os.environ['PG_TABLE'] = 'documents_old'
        
        # Call parent initialization which will use documents_old
        super().__init__()
        
        print("✅ HybridRAGSystem_OLD initialized for documents_old table")
