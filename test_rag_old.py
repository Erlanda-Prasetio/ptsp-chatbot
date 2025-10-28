#!/usr/bin/env python3
"""
Test SmartEnhancedRAG_OLD initialization and search
"""

import os
import sys

# Set environment BEFORE imports
os.environ['PG_TABLE'] = 'documents_old'

sys.path.append('src')
sys.path.append('.')

from src.hybrid_rag_old import SmartEnhancedRAG_OLD

print("="*70)
print("Testing SmartEnhancedRAG_OLD initialization...")
print("="*70)

try:
    print("\n1. Initializing SmartEnhancedRAG_OLD...")
    rag = SmartEnhancedRAG_OLD()
    print("✅ Initialization successful")
    
    print("\n2. Testing a simple query...")
    query = "Apa itu DPMPTSP?"
    print(f"   Query: {query}")
    
    result = rag.ask(query, k=3)
    print(f"\n   ✅ Query successful!")
    print(f"   Answer: {result.get('answer', '')[:200]}...")
    print(f"   Sources found: {len(result.get('sources', []))}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
