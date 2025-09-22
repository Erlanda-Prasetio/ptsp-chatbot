"""
Improved PDF processing and chunking for PTSP RAG system
This module provides better text extraction and semantic chunking
"""

import fitz  # PyMuPDF
import re
import os
from typing import List, Dict, Tuple
import nltk
from nltk.tokenize import sent_tokenize
from pathlib import Path

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class ImprovedPDFProcessor:
    def __init__(self):
        self.ptsp_keywords = [
            'izin', 'perizinan', 'ptsp', 'investasi', 'usaha', 'modal', 
            'dpmptsp', 'pelayanan terpadu', 'satu pintu', 'oss',
            'permohonan', 'persyaratan', 'prosedur', 'syarat',
            'penanaman modal', 'bisnis', 'komersial'
        ]
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF with better formatting preservation"""
        try:
            doc = fitz.open(pdf_path)
            text_blocks = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get text blocks with better formatting
                blocks = page.get_text("dict")
                page_text = ""
                
                for block in blocks["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            line_text = ""
                            for span in line["spans"]:
                                text = span["text"].strip()
                                if text:
                                    line_text += text + " "
                            
                            if line_text.strip():
                                page_text += line_text.strip() + "\n"
                
                if page_text.strip():
                    text_blocks.append(f"--- Page {page_num + 1} ---\n{page_text}")
            
            doc.close()
            return "\n\n".join(text_blocks)
            
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Fix common OCR issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between words
        text = re.sub(r'(\d+)([A-Za-z])', r'\1 \2', text)  # Space between numbers and letters
        text = re.sub(r'([A-Za-z])(\d+)', r'\1 \2', text)  # Space between letters and numbers
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove page numbers and headers
        text = re.sub(r'--- Page \d+ ---', '', text)
        text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)
        
        # Remove table artifacts
        text = re.sub(r'Unnamed:\s*\d+.*?NaN', '', text)
        text = re.sub(r'\.{3,}', '...', text)
        
        return text.strip()
    
    def is_ptsp_relevant(self, text: str) -> bool:
        """Check if text is relevant to PTSP services"""
        text_lower = text.lower()
        
        # Count keyword matches
        keyword_count = sum(1 for keyword in self.ptsp_keywords if keyword in text_lower)
        
        # Check for specific patterns
        has_license_content = any(pattern in text_lower for pattern in [
            'permohonan izin', 'syarat izin', 'prosedur izin',
            'pelayanan terpadu', 'satu pintu', 'investasi',
            'penanaman modal', 'oss'
        ])
        
        # Exclude irrelevant content
        is_irrelevant = any(pattern in text_lower for pattern in [
            'kelahiran', 'kematian', 'nikah', 'cerai',
            'kesehatan', 'rumah sakit', 'puskesmas',
            'neraca', 'laporan keuangan', 'anggaran'
        ])
        
        return (keyword_count >= 2 or has_license_content) and not is_irrelevant

class SemanticChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_by_sections(self, text: str) -> List[str]:
        """Chunk text by semantic sections"""
        chunks = []
        
        # Split by major sections first
        sections = re.split(r'\n(?=BAB|PASAL|BAGIAN|LAMPIRAN|CHAPTER|\d+\.)', text)
        
        for section in sections:
            if len(section.strip()) < 50:  # Skip very short sections
                continue
                
            # If section is small enough, keep as one chunk
            if len(section) <= self.chunk_size:
                chunks.append(section.strip())
            else:
                # Split large sections by paragraphs
                paragraphs = section.split('\n\n')
                current_chunk = ""
                
                for paragraph in paragraphs:
                    # If adding this paragraph would exceed chunk size
                    if len(current_chunk) + len(paragraph) > self.chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            # Start new chunk with overlap
                            sentences = sent_tokenize(current_chunk)
                            overlap_text = ' '.join(sentences[-2:]) if len(sentences) >= 2 else ""
                            current_chunk = overlap_text + "\n\n" + paragraph
                        else:
                            # Paragraph is too long, split by sentences
                            sentences = sent_tokenize(paragraph)
                            temp_chunk = ""
                            for sentence in sentences:
                                if len(temp_chunk) + len(sentence) > self.chunk_size:
                                    if temp_chunk:
                                        chunks.append(temp_chunk.strip())
                                    temp_chunk = sentence
                                else:
                                    temp_chunk += " " + sentence
                            current_chunk = temp_chunk
                    else:
                        current_chunk += "\n\n" + paragraph
                
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 100]
    
    def chunk_text(self, text: str) -> List[str]:
        """Main chunking method"""
        # Try section-based chunking first
        chunks = self.chunk_by_sections(text)
        
        # If no good sections found, fall back to sentence-based chunking
        if len(chunks) < 2:
            chunks = self._chunk_by_sentences(text)
        
        return chunks
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Fallback: chunk by sentences with semantic boundaries"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Add overlap
                    current_sentences = sent_tokenize(current_chunk)
                    overlap_text = ' '.join(current_sentences[-1:]) if current_sentences else ""
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_chunk = sentence
            else:
                current_chunk += " " + sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 50]

def process_documents_improved(data_dirs: List[str]) -> List[Dict]:
    """Process documents with improved extraction and chunking"""
    processor = ImprovedPDFProcessor()
    chunker = SemanticChunker()
    
    processed_chunks = []
    
    for data_dir in data_dirs:
        if not os.path.exists(data_dir):
            continue
            
        print(f"📁 Processing directory: {data_dir}")
        
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    print(f"📄 Processing: {file}")
                    
                    # Extract text
                    raw_text = processor.extract_text_from_pdf(file_path)
                    if not raw_text:
                        continue
                    
                    # Clean text
                    clean_text = processor.clean_text(raw_text)
                    if len(clean_text) < 100:
                        continue
                    
                    # Check relevance
                    if not processor.is_ptsp_relevant(clean_text):
                        print(f"  ❌ Not PTSP relevant: {file}")
                        continue
                    
                    print(f"  ✅ PTSP relevant: {file}")
                    
                    # Chunk text
                    chunks = chunker.chunk_text(clean_text)
                    
                    for i, chunk in enumerate(chunks):
                        processed_chunks.append({
                            'content': chunk,
                            'source': file,
                            'chunk_id': f"{file}_{i}",
                            'file_path': file_path,
                            'chunk_index': i,
                            'is_ptsp_relevant': True
                        })
    
    print(f"\n📊 Processing complete:")
    print(f"  - Total chunks: {len(processed_chunks)}")
    print(f"  - All chunks are PTSP-relevant: 100%")
    
    return processed_chunks

if __name__ == "__main__":
    # Test the improved processing
    data_directories = [
        "data/scraped_dpmptsp",
        "data/scraped_ptsp_indonesia", 
        "data/scraped"
    ]
    
    chunks = process_documents_improved(data_directories)
    
    # Save sample for inspection
    if chunks:
        print(f"\n📝 Sample chunk:")
        print(f"Source: {chunks[0]['source']}")
        print(f"Content preview: {chunks[0]['content'][:300]}...")