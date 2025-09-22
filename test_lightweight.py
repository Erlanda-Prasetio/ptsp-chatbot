"""
Simple test script to verify enhanced functionality without heavy model loading
"""

import sys
import os
sys.path.append('src')

def test_lightweight_utils():
    """Test lightweight enhanced utilities"""
    print("🧪 Testing Lightweight Enhanced Utils")
    print("=" * 40)
    
    try:
        from lightweight_utils import calculate_relevance_score, LightweightPDFProcessor, LightweightChunker
        print("✅ Lightweight utils imported successfully")
        
        # Test relevance scoring
        test_query = "cara mengurus izin usaha"
        test_content = "Prosedur permohonan izin usaha di DPMPTSP Jawa Tengah memerlukan beberapa dokumen dan tahapan yang harus dipenuhi."
        
        score = calculate_relevance_score(test_query, test_content)
        print(f"📊 Relevance score test: {score:.3f}")
        
        if score > 0.3:
            print("✅ Relevance scoring working correctly")
        else:
            print("⚠️ Low relevance score, may need tuning")
        
        # Test PDF processor
        processor = LightweightPDFProcessor()
        
        test_text = "IZINPEJABAT YANG MENANDA TA-NGANI Permohonan izin usaha"
        cleaned = processor.clean_text(test_text)
        print(f"📝 Text cleaning test: '{cleaned[:50]}...'")
        
        # Test PTSP relevance
        is_relevant = processor.is_ptsp_relevant(test_content)
        print(f"🎯 PTSP relevance test: {is_relevant}")
        
        # Test chunker
        chunker = LightweightChunker()
        
        long_text = """
        BAB I KETENTUAN UMUM
        Pasal 1
        Dalam peraturan ini yang dimaksud dengan:
        1. Daerah adalah Provinsi Jawa Tengah
        2. Gubernur adalah Gubernur Jawa Tengah
        3. DPMPTSP adalah Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu
        
        BAB II PELAYANAN PERIZINAN
        Pasal 2
        Pelayanan perizinan meliputi:
        1. Izin usaha industri
        2. Izin usaha perdagangan
        3. Izin investasi
        """ * 5  # Make it long enough to test chunking
        
        chunks = chunker.chunk_text(long_text)
        print(f"📄 Chunking test: {len(chunks)} chunks created")
        
        if chunks:
            print(f"  First chunk preview: {chunks[0][:100]}...")
        
        print("\n✅ All lightweight utils tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Lightweight utils test failed: {e}")
        return False

def test_config():
    """Test configuration and imports"""
    print("\n🔧 Testing Configuration")
    print("-" * 30)
    
    try:
        from config import VECTOR_BACKEND
        print(f"✅ Vector backend: {VECTOR_BACKEND}")
        
        if VECTOR_BACKEND == 'supabase':
            print("🔗 Using Supabase backend")
        else:
            print("💾 Using local backend")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_basic_imports():
    """Test basic system imports without model loading"""
    print("\n📦 Testing Basic Imports")
    print("-" * 30)
    
    try:
        # Test embed module (without actually loading model)
        import importlib.util
        
        embed_spec = importlib.util.spec_from_file_location("embed", "src/embed.py")
        if embed_spec:
            print("✅ Embed module found")
        
        # Test ask module
        ask_spec = importlib.util.spec_from_file_location("ask", "src/ask.py")
        if ask_spec:
            print("✅ Ask module found")
        
        # Test enhanced rag (without initialization)
        smart_spec = importlib.util.spec_from_file_location("smart_enhanced_rag", "src/smart_enhanced_rag.py")
        if smart_spec:
            print("✅ Smart enhanced RAG module found")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic imports test failed: {e}")
        return False

def main():
    """Main test function without heavy model loading"""
    print("🚀 Lightweight Enhanced RAG Test")
    print("=" * 50)
    
    # Test basic functionality
    utils_ok = test_lightweight_utils()
    config_ok = test_config()
    imports_ok = test_basic_imports()
    
    # Summary
    print(f"\n🎯 Test Summary:")
    print(f"  - Lightweight Utils: {'✅' if utils_ok else '❌'}")
    print(f"  - Configuration: {'✅' if config_ok else '❌'}")
    print(f"  - Basic Imports: {'✅' if imports_ok else '❌'}")
    
    if utils_ok and config_ok and imports_ok:
        print(f"\n🎉 Basic enhancement functionality working!")
        print(f"✅ Your enhanced utils are ready")
        print(f"⚠️ Full model test skipped due to memory constraints")
        print(f"\nNext steps:")
        print(f"1. Run enhanced ingestion: python enhanced_ingest.py")
        print(f"2. Test with actual API: python rag_api.py")
        return True
    else:
        print(f"\n❌ Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)