import sys
sys.path.append('src')

from vector_store import store
from embed import embed_texts
import json

def find_complete_data():
    """Find chunks with complete, meaningful data"""
    print("🔍 Searching for Complete Data Chunks\n")
    
    # Load the local vector store
    store.load()
    if store.embeddings is None:
        print("❌ Vector store is empty.")
        return
    
    print(f"✅ Vector store loaded with {len(store.texts)} chunks")
    
    # Look for chunks with substantial content
    substantial_chunks = []
    for i, text in enumerate(store.texts):
        if len(text) > 500:  # At least 500 characters
            substantial_chunks.append({
                'index': i,
                'length': len(text),
                'text': text,
                'source': store.meta[i].get('source', 'Unknown')
            })
    
    # Sort by length
    substantial_chunks.sort(key=lambda x: x['length'], reverse=True)
    
    print(f"📊 Found {len(substantial_chunks)} substantial chunks (>500 chars)")
    print("\n🏆 Top 10 longest chunks:")
    
    for i, chunk in enumerate(substantial_chunks[:10]):
        source = chunk['source'].split('\\')[-1] if '\\' in chunk['source'] else chunk['source']
        print(f"  {i+1}. {chunk['length']:,} chars | {source}")
        # Show preview
        text_preview = chunk['text'][:300].replace('\n', ' ').strip()
        print(f"     Preview: {text_preview}...")
        print()
    
    # Look specifically for Indonesian investment/data content
    print("\n🇮🇩 Searching for Investment/Data Content:")
    keywords = ['investasi', 'realisasi', 'tenaga kerja', 'penyerapan', 'wisatawan', 'kunjungan', 'PTSP']
    
    relevant_chunks = []
    for chunk in substantial_chunks[:50]:  # Check top 50 substantial chunks
        text_lower = chunk['text'].lower()
        if any(keyword.lower() in text_lower for keyword in keywords):
            # Count keyword occurrences
            keyword_count = sum(text_lower.count(keyword.lower()) for keyword in keywords)
            chunk['keyword_count'] = keyword_count
            relevant_chunks.append(chunk)
    
    # Sort by keyword relevance
    relevant_chunks.sort(key=lambda x: x['keyword_count'], reverse=True)
    
    print(f"📈 Found {len(relevant_chunks)} relevant data chunks:")
    for i, chunk in enumerate(relevant_chunks[:5]):
        source = chunk['source'].split('\\')[-1] if '\\' in chunk['source'] else chunk['source']
        print(f"  {i+1}. {chunk['keyword_count']} keywords | {chunk['length']:,} chars | {source}")
        # Show preview with keywords highlighted
        text_preview = chunk['text'][:400].replace('\n', ' ').strip()
        print(f"     Preview: {text_preview}...")
        print()

if __name__ == "__main__":
    find_complete_data()
