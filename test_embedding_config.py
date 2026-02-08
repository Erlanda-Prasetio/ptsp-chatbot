#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify embedding model dimensions and chunking configuration
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CONTEXT_TOKENS, EMB_MODEL, VECTOR_BACKEND
from src.embed import embed_texts
from src.chunk import chunk_text

# Load environment variables
load_dotenv()

def test_embedding_dimensions():
    """Test actual embedding model dimensions"""
    print("="*80)
    print("EMBEDDING MODEL TEST")
    print("="*80)
    
    print(f"\n[CONFIG] EMB_MODEL from .env: {EMB_MODEL}")
    
    # Generate a test embedding
    test_text = "This is a test sentence to verify embedding dimensions."
    print(f"\n[TEST] Generating embedding for: '{test_text}'")
    
    try:
        embeddings = embed_texts([test_text])
        if embeddings and len(embeddings) > 0:
            embedding = embeddings[0]
            dimensions = len(embedding)
            
            print(f"\n[RESULT] Embedding dimensions: {dimensions}")
            print(f"[RESULT] Embedding shape: {embedding.shape if hasattr(embedding, 'shape') else 'N/A'}")
            print(f"[RESULT] First 5 values: {embedding[:5]}")
            
            # Determine which model based on dimensions
            if dimensions == 384:
                print("\n✅ CONFIRMED: Using all-MiniLM-L6-v2 (384 dimensions)")
            elif dimensions == 768:
                print("\n✅ CONFIRMED: Using mpnet-base-v2 or similar (768 dimensions)")
            else:
                print(f"\n⚠️  UNEXPECTED: {dimensions} dimensions (non-standard model)")
                
            return dimensions
        else:
            print("\n❌ ERROR: Failed to generate embeddings")
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None


def test_chunking_config():
    """Test chunking configuration and behavior"""
    print("\n" + "="*80)
    print("CHUNKING CONFIGURATION TEST")
    print("="*80)
    
    print(f"\n[CONFIG] CHUNK_SIZE: {CHUNK_SIZE} characters")
    print(f"[CONFIG] CHUNK_OVERLAP: {CHUNK_OVERLAP} characters")
    print(f"[CONFIG] Step size: {CHUNK_SIZE - CHUNK_OVERLAP} characters")
    print(f"[CONFIG] MAX_CONTEXT_TOKENS: {MAX_CONTEXT_TOKENS} tokens")
    
    # Calculate approximate token counts
    chars_per_token = 4  # Heuristic from chunk.py
    chunk_tokens = CHUNK_SIZE / chars_per_token
    overlap_tokens = CHUNK_OVERLAP / chars_per_token
    
    print(f"\n[ESTIMATE] Chunk size: ~{chunk_tokens:.0f} tokens (using {chars_per_token} chars/token)")
    print(f"[ESTIMATE] Overlap: ~{overlap_tokens:.0f} tokens")
    
    # Test with sample text
    sample_text = """
    This is a sample document for testing chunking behavior. 
    The system should split this text into overlapping chunks based on character count.
    Each chunk should be approximately {CHUNK_SIZE} characters long.
    With an overlap of {CHUNK_OVERLAP} characters between consecutive chunks.
    This ensures that information spanning chunk boundaries remains accessible.
    The chunking algorithm uses a simple sliding window approach.
    It does not consider semantic boundaries like sentence or paragraph breaks.
    Instead, it prioritizes consistent chunk sizes for predictable vector operations.
    """ * 5  # Repeat to get multiple chunks
    
    print(f"\n[TEST] Sample text length: {len(sample_text)} characters")
    
    chunks = chunk_text(sample_text)
    
    print(f"\n[RESULT] Generated {len(chunks)} chunks")
    print(f"[RESULT] First chunk length: {len(chunks[0])} characters")
    if len(chunks) > 1:
        print(f"[RESULT] Last chunk length: {len(chunks[-1])} characters")
        
        # Check overlap
        if len(chunks) > 1:
            overlap_start = CHUNK_SIZE - CHUNK_OVERLAP
            chunk1_end = chunks[0][overlap_start:]
            chunk2_start = chunks[1][:CHUNK_OVERLAP]
            
            if chunk1_end == chunk2_start:
                print(f"\n✅ CONFIRMED: {CHUNK_OVERLAP} character overlap verified")
            else:
                print(f"\n⚠️  WARNING: Overlap mismatch detected")
    
    print(f"\n[PREVIEW] First chunk (first 200 chars):")
    print(f"  {chunks[0][:200]}...")
    
    if len(chunks) > 1:
        print(f"\n[PREVIEW] Second chunk (first 200 chars):")
        print(f"  {chunks[1][:200]}...")


def test_vector_backend():
    """Test vector backend configuration"""
    print("\n" + "="*80)
    print("VECTOR BACKEND TEST")
    print("="*80)
    
    print(f"\n[CONFIG] VECTOR_BACKEND: {VECTOR_BACKEND}")
    
    if VECTOR_BACKEND == 'supabase':
        supabase_url = os.getenv('SUPABASE_URL')
        pg_table = os.getenv('PG_TABLE')
        print(f"[CONFIG] SUPABASE_URL: {supabase_url}")
        print(f"[CONFIG] PG_TABLE: {pg_table}")
        print("\n✅ Using Supabase with pgvector")
        print("⚠️  Ensure your rag_chunks_jateng table uses vector(384) for embeddings!")
    else:
        print("\n✅ Using local vector store")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("CONFIGURATION VERIFICATION TEST")
    print("="*80)
    
    # Test 1: Embedding dimensions
    dimensions = test_embedding_dimensions()
    
    # Test 2: Chunking configuration
    test_chunking_config()
    
    # Test 3: Vector backend
    test_vector_backend()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if dimensions:
        print(f"\n✅ Embedding model: {EMB_MODEL}")
        print(f"✅ Vector dimensions: {dimensions}")
        print(f"✅ Chunk size: {CHUNK_SIZE} chars (~{CHUNK_SIZE/4:.0f} tokens)")
        print(f"✅ Chunk overlap: {CHUNK_OVERLAP} chars (~{CHUNK_OVERLAP/4:.0f} tokens)")
        print(f"✅ Vector backend: {VECTOR_BACKEND}")
        
        print("\n" + "="*80)
        print("CORRECT STATEMENT FOR YOUR THESIS:")
        print("="*80)
        print(f"""
The document preprocessing pipeline employs a character-based fixed-size 
chunking strategy with sliding window overlap. Documents are segmented into 
chunks of {CHUNK_SIZE} characters (approximately {CHUNK_SIZE/4:.0f} tokens using the heuristic 
of ~4 characters per token) with {CHUNK_OVERLAP} characters (approximately {CHUNK_OVERLAP/4:.0f} tokens) 
of overlap between consecutive chunks.

The embedding model configuration employs `{EMB_MODEL}`, 
producing dense vector representations of {dimensions} dimensions that capture 
semantic relationships between text passages. These normalized embeddings enable 
efficient cosine similarity computation through dot product operations during retrieval.
        """)
    else:
        print("\n❌ Could not verify embedding dimensions")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
