import json
import sys

def analyze_chunking():
    try:
        with open('d:/backup/ptspRag/data/default_docs_meta.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        texts = data.get('texts', [])
        print(f"Total chunks: {len(texts)}")
        
        # Analyze chunk sizes
        chunk_sizes = [len(chunk) for chunk in texts]
        print(f"\nChunk size statistics:")
        print(f"  Average: {sum(chunk_sizes) / len(chunk_sizes):.0f} characters")
        print(f"  Min: {min(chunk_sizes)} characters")
        print(f"  Max: {max(chunk_sizes)} characters")
        
        # Check chunks without source information
        chunks_without_source = 0
        chunks_with_poor_content = 0
        
        for chunk in texts:
            if not chunk.startswith('Source:'):
                chunks_without_source += 1
            
            # Check for poor content (mostly formatting/headers)
            if any(indicator in chunk.lower() for indicator in [
                'unnamed:', 'nan', 'formulir', 'sheet:', 'file type:', 'path:'
            ]):
                chunks_with_poor_content += 1
        
        print(f"\nContent quality issues:")
        print(f"  Chunks without source: {chunks_without_source}")
        print(f"  Chunks with poor content: {chunks_with_poor_content}")
        print(f"  Quality percentage: {((len(texts) - chunks_with_poor_content) / len(texts) * 100):.1f}%")
        
        # Check for Indonesian vs English content
        indonesian_chunks = 0
        english_chunks = 0
        
        for chunk in texts:
            chunk_lower = chunk.lower()
            if any(word in chunk_lower for word in ['tahun', 'kabupaten', 'provinsi', 'jawa tengah', 'pemerintah']):
                indonesian_chunks += 1
            elif any(word in chunk_lower for word in ['year', 'regency', 'government', 'central java']):
                english_chunks += 1
        
        print(f"\nLanguage distribution:")
        print(f"  Indonesian content chunks: {indonesian_chunks}")
        print(f"  English content chunks: {english_chunks}")
        print(f"  Mixed/unclear: {len(texts) - indonesian_chunks - english_chunks}")
        
        # Look for PTSP-specific content
        ptsp_chunks = 0
        for chunk in texts:
            if any(term in chunk.lower() for term in [
                'ptsp', 'pelayanan terpadu', 'perizinan', 'izin usaha', 'dpmptsp'
            ]):
                ptsp_chunks += 1
        
        print(f"\nPTSP-relevant chunks: {ptsp_chunks}")
        print(f"PTSP relevance: {(ptsp_chunks / len(texts) * 100):.1f}%")
        
        # Sample problematic chunks
        print(f"\nProblematic chunk examples:")
        count = 0
        for chunk in texts:
            if ('unnamed:' in chunk.lower() or 'nan' in chunk.lower()) and count < 3:
                print(f"\n{count+1}. {chunk[:300]}...")
                count += 1
        
    except Exception as e:
        print(f"Error analyzing chunking: {e}")

if __name__ == "__main__":
    analyze_chunking()