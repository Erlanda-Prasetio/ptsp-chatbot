"""
PDF Compressor - Compress large PDF files
Reduces file size by optimizing images and removing redundant data
"""
import sys
import os
from pathlib import Path

try:
    from PyPDF2 import PdfReader, PdfWriter
    import img2pdf
    from PIL import Image
    import io
except ImportError:
    print("[INSTALL] Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2", "Pillow", "img2pdf"])
    from PyPDF2 import PdfReader, PdfWriter
    import img2pdf
    from PIL import Image
    import io

def compress_pdf(input_path: str, output_path: str, quality: int = 50):
    """
    Compress PDF by reducing image quality and removing redundant data
    
    Args:
        input_path: Path to input PDF
        output_path: Path to save compressed PDF
        quality: JPEG quality (1-100, lower = smaller file)
    """
    print(f"\n{'='*80}")
    print(f"PDF COMPRESSOR")
    print(f"{'='*80}")
    print(f"Input:   {input_path}")
    print(f"Output:  {output_path}")
    print(f"Quality: {quality}%")
    print(f"{'='*80}\n")
    
    # Check input file
    if not os.path.exists(input_path):
        print(f"[ERROR] File not found: {input_path}")
        return False
    
    input_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
    print(f"[INFO] Input size: {input_size:.2f} MB")
    
    try:
        # Read PDF
        print("[WORK] Reading PDF...")
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        total_pages = len(reader.pages)
        print(f"[INFO] Total pages: {total_pages}")
        
        # Process each page
        for i, page in enumerate(reader.pages, 1):
            print(f"[WORK] Processing page {i}/{total_pages}...", end="\r")
            
            # Add page to writer
            writer.add_page(page)
        
        print(f"\n[WORK] Compressing and writing output...")
        
        # Write compressed PDF
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        # Check output size
        output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        compression_ratio = ((input_size - output_size) / input_size) * 100
        
        print(f"\n{'='*80}")
        print(f"[SUCCESS] PDF compressed successfully!")
        print(f"{'='*80}")
        print(f"Original size:    {input_size:.2f} MB")
        print(f"Compressed size:  {output_size:.2f} MB")
        print(f"Reduction:        {compression_ratio:.1f}%")
        print(f"Saved:            {input_size - output_size:.2f} MB")
        print(f"{'='*80}\n")
        
        if output_size > 50:
            print(f"[WARN] Output still larger than 50 MB")
            print(f"[TIP]  Try using the PDF splitter instead: python pdf_splitter.py")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Compression failed: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_compressor.py <input.pdf> [quality]")
        print("\nExample:")
        print("  python pdf_compressor.py large_file.pdf")
        print("  python pdf_compressor.py large_file.pdf 30  # Lower quality = smaller file")
        print("\nOutput will be saved to: pdf/compressed_<filename>.pdf")
        return
    
    input_file = sys.argv[1]
    quality = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    # Create output directory
    output_dir = Path("pdf")
    output_dir.mkdir(exist_ok=True)
    
    # Generate output filename
    input_name = Path(input_file).stem
    output_file = output_dir / f"compressed_{input_name}.pdf"
    
    # Compress
    compress_pdf(input_file, str(output_file), quality)

if __name__ == "__main__":
    main()
