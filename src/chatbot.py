#!/usr/bin/env python3
"""
Interactive RAG Chatbot for Central Java Government Data
Usage: python src/chatbot.py
"""

import sys
import os
from ask import query_llm, build_context
from embed import embed_texts
from vector_store import store
from config import VECTOR_BACKEND

if VECTOR_BACKEND == 'supabase':
    from vector_store_supabase import SupabaseVectorStore

def initialize_rag():
    """Initialize the RAG system"""
    if VECTOR_BACKEND == 'supabase':
        return SupabaseVectorStore()
    else:
        store.load()
        if store.embeddings is None:
            print("[FAIL] Vector store is empty. Please run ingestion first:")
            print("python src/ingest_scraped.py data/scraped")
            sys.exit(1)
        return store

def search_documents(query, vector_store, k=8):
    """Search for relevant documents"""
    if VECTOR_BACKEND == 'supabase':
        return vector_store.search(query, k=k)
    else:
        q_emb = embed_texts([query])[0]
        return vector_store.search(q_emb, k=k)

def print_welcome():
    """Print welcome message"""
    print("\n" + "="*60)
    print("  Central Java Government Data RAG Chatbot")
    print("="*60)
    print("Ask questions about Central Java government data!")
    print("Available data includes:")
    print("• Population and demographics")
    print("• Employment and workforce")
    print("• Health statistics")
    print("• Democracy index")
    print("• Regional government data")
    print("• And much more...")
    print("\n[INFO] Example questions:")
    print("• 'What employment data is available for 2023?'")
    print("• 'Tell me about population statistics'")
    print("• 'What health data do you have?'")
    print("\nType 'quit' or 'exit' to stop.")
    print("-"*60)

def main():
    """Main chatbot loop"""
    try:
        # Initialize the RAG system
        print(" Initializing RAG system...")
        vector_store = initialize_rag()
        print("[OK] RAG system ready!")
        
        print_welcome()
        
        while True:
            try:
                # Get user input
                question = input("\n Your question: ").strip()
                
                # Check for exit commands
                if question.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n Goodbye! Thanks for using the Central Java Data Chatbot!")
                    break
                
                if not question:
                    continue
                
                # Search for relevant documents
                print("[SEARCH] Searching relevant data...")
                hits = search_documents(question, vector_store)
                
                if not hits:
                    print("[FAIL] No relevant data found for your question.")
                    continue
                
                # Build context and query LLM
                context = build_context(hits)
                print(" Generating response...")
                
                answer = query_llm(question, context)
                
                # Display the answer
                print("\n" + "="*60)
                print(" ANSWER:")
                print("="*60)
                print(answer)
                print("="*60)
                
                # Show sources
                print(f"\n[STATS] Based on {len(hits)} data sources")
                
            except KeyboardInterrupt:
                print("\n\n Goodbye! Thanks for using the Central Java Data Chatbot!")
                break
            except Exception as e:
                print(f"\n[FAIL] Error: {e}")
                print("Please try again with a different question.")
    
    except Exception as e:
        print(f"[FAIL] Failed to initialize RAG system: {e}")
        sys.exit(1)
    
    finally:
        if VECTOR_BACKEND == 'supabase':
            vector_store.close()

if __name__ == "__main__":
    main()
