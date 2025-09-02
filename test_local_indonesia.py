import sys
sys.path.append('src')

from vector_store import store
from embed import embed_texts
import json

def test_local_indonesia():
    """Test local RAG with Indonesian queries"""
    print("🇮🇩 Testing Local RAG with Indonesian PTSP Dataset\n")
    
    # Load the local vector store
    store.load()
    if store.embeddings is None:
        print("❌ Vector store is empty. Need to run ingest first.")
        return
    
    print(f"✅ Vector store loaded with {len(store.texts)} chunks")
    print()
    
    # Indonesian queries
    queries = [
        "investasi Jawa Tengah 2023",
        "data koperasi Jawa Tengah", 
        "tenaga kerja industri",
        "wisatawan Jawa Tengah",
        "PTSP perizinan",
        "kesehatan provinsi",
        "keluarga berencana",
        "APBD 2023"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"🔍 Query {i}: {query}")
        print("-" * 50)
        
        try:
            # Embed the query
            q_emb = embed_texts([query])[0]
            
            # Search for similar chunks
            results = store.search(q_emb, k=5)
            
            if results:
                print(f"✅ Found {len(results)} results")
                
                # Show top result
                top_result = results[0]
                source = top_result.get('meta', {}).get('source', 'Unknown')
                content = top_result.get('text', '')[:200] + "..."
                score = top_result.get('score', 0)
                
                print(f"📁 Source: {source}")
                print(f"📊 Score: {score:.3f}")
                print(f"📄 Content: {content}")
                print()
                
            else:
                print("❌ No results found")
                print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

def check_local_dataset():
    """Check local dataset statistics"""
    try:
        with open("data/default_docs_meta.json", "r", encoding='utf-8') as f:
            docs_meta = json.load(f)
        
        total_chunks = len(docs_meta)
        indonesia_chunks = sum(1 for doc in docs_meta if "scraped_ptsp_indonesia" in doc.get("source", ""))
        
        print(f"📊 Local Dataset Statistics:")
        print(f"   Total chunks: {total_chunks}")
        print(f"   Indonesian chunks: {indonesia_chunks}")
        print(f"   Original chunks: {total_chunks - indonesia_chunks}")
        print()
        
        # Show sample Indonesian files
        indonesia_files = set()
        for doc in docs_meta:
            if "scraped_ptsp_indonesia" in doc.get("source", ""):
                filename = doc['source'].split('\\')[-1] if '\\' in doc['source'] else doc['source'].split('/')[-1]
                indonesia_files.add(filename)
        
        print(f"🗂️ Sample Indonesian files ({min(5, len(indonesia_files))} of {len(indonesia_files)}):")
        for filename in list(indonesia_files)[:5]:
            print(f"   • {filename}")
        print()
        
    except Exception as e:
        print(f"❌ Error checking dataset: {e}")

if __name__ == "__main__":
    print("🚀 Local Indonesian PTSP RAG Test")
    print("=" * 60)
    
    check_local_dataset()
    test_local_indonesia()
