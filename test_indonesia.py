import json
import numpy as np
from pathlib import Path
import sys
sys.path.append('src')
from enhanced_rag import EnhancedRAG

def test_indonesia_queries():
    """Test the RAG system with Indonesian queries"""
    print("🇮🇩 Testing RAG System dengan Dataset Indonesia PTSP\n")
    
    # Initialize enhanced RAG
    rag = EnhancedRAG()
    
    # Indonesian queries about Central Java government services
    queries = [
        "Bagaimana cara mengurus izin investasi di Jawa Tengah?",
        "Data investasi PMA di Jawa Tengah tahun 2023",
        "Jumlah tenaga kerja di sektor industri Jawa Tengah",
        "Prosedur perizinan PTSP Provinsi Jawa Tengah",
        "Statistik koperasi di Jawa Tengah 2023",
        "Data wisatawan yang berkunjung ke Jawa Tengah",
        "Bagaimana kondisi infrastruktur jalan di Jawa Tengah?",
        "Pelayanan kesehatan di Provinsi Jawa Tengah",
        "Program keluarga berencana di Jawa Tengah",
        "Realisasi APBD Provinsi Jawa Tengah 2023"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"{'='*60}")
        print(f"🔍 Query {i}: {query}")
        print(f"{'='*60}")
        
        try:
            # Use enhanced RAG system
            response = rag.search_enhanced(query)
            
            print("📋 **Jawaban:**")
            print(response)
            print("\n")
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    print("✅ Testing complete!")

def check_dataset_stats():
    """Check statistics about our dataset"""
    print("📊 Dataset Statistics:")
    
    # Load metadata
    try:
        with open("data/default_docs_meta.json", "r") as f:
            docs_meta = json.load(f)
        
        total_chunks = len(docs_meta)
        
        # Count Indonesian files
        indonesia_chunks = sum(1 for doc in docs_meta if "scraped_ptsp_indonesia" in doc.get("source", ""))
        old_chunks = total_chunks - indonesia_chunks
        
        print(f"📈 Total chunks: {total_chunks}")
        print(f"🇮🇩 Indonesian PTSP chunks: {indonesia_chunks}")
        print(f"📁 Original dataset chunks: {old_chunks}")
        
        # Sample sources
        print(f"\n📂 Sample Indonesian files:")
        indonesia_sources = set()
        for doc in docs_meta:
            if "scraped_ptsp_indonesia" in doc.get("source", ""):
                source = Path(doc["source"]).name
                indonesia_sources.add(source)
                if len(indonesia_sources) <= 5:
                    print(f"   • {source}")
        
        print(f"🗂️ Total Indonesian files processed: {len(indonesia_sources)}")
        
    except Exception as e:
        print(f"❌ Error reading dataset: {e}")

if __name__ == "__main__":
    print("🚀 Testing Indonesian PTSP RAG System")
    print("=" * 60)
    
    # Check dataset first
    check_dataset_stats()
    print("\n")
    
    # Test with Indonesian queries
    test_indonesia_queries()
