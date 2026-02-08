"""
PDF Splitter - Split large PDF into multiple smaller files
Divides PDF into equal parts or by size limit
"""
import sys
import os
from pathlib import Path

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("[INSTALL] Installing PyPDF2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    from PyPDF2 import PdfReader, PdfWriter

def split_pdf_by_parts(input_path: str, num_parts: int = 6, output_dir: str = "pdf"):
    """
    Split PDF into equal parts
    
    Args:
        input_path: Path to input PDF
        num_parts: Number of parts to split into
        output_dir: Directory to save split PDFs
    """
    print(f"\n{'='*80}")
    print(f"PDF SPLITTER - Split into {num_parts} parts")
    print(f"{'='*80}")
    print(f"Input:  {input_path}")
    print(f"Output: {output_dir}/")
    print(f"Parts:  {num_parts}")
    print(f"{'='*80}\n")
    
    # Check input file
    if not os.path.exists(input_path):
        print(f"[ERROR] File not found: {input_path}")
        return False
    
    input_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
    print(f"[INFO] Input size: {input_size:.2f} MB")
    print(f"[INFO] Target per file: ~{input_size/num_parts:.2f} MB\n")
    
    try:
        # Read PDF
        print("[WORK] Reading PDF...")
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        print(f"[INFO] Total pages: {total_pages}")
        
        # Calculate pages per part
        pages_per_part = total_pages // num_parts
        remainder = total_pages % num_parts
        
        print(f"[INFO] Pages per part: ~{pages_per_part}")
        print(f"[INFO] Extra pages: {remainder}\n")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Base filename
        base_name = Path(input_path).stem
        
        # Split PDF
        start_page = 0
        for part in range(1, num_parts + 1):
            # Calculate end page for this part
            pages_in_this_part = pages_per_part + (1 if part <= remainder else 0)
            end_page = start_page + pages_in_this_part
            
            print(f"[WORK] Creating part {part}/{num_parts} (pages {start_page+1}-{end_page})...")
            
            # Create writer for this part
            writer = PdfWriter()
            
            # Add pages
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            # Save part
            output_file = output_path / f"{base_name}_part{part}of{num_parts}.pdf"
            with open(output_file, "wb") as f:
                writer.write(f)
            
            # Check size
            part_size = os.path.getsize(output_file) / (1024 * 1024)
            print(f"[OK]   Saved: {output_file.name} ({part_size:.2f} MB, {pages_in_this_part} pages)")
            
            start_page = end_page
        
        print(f"\n{'='*80}")
        print(f"[SUCCESS] PDF split into {num_parts} parts!")
        print(f"{'='*80}")
        print(f"Original: {input_size:.2f} MB ({total_pages} pages)")
        print(f"Location: {output_dir}/")
        print(f"Files:")
        
        for part in range(1, num_parts + 1):
            part_file = output_path / f"{base_name}_part{part}of{num_parts}.pdf"
            part_size = os.path.getsize(part_file) / (1024 * 1024)
            print(f"  • {part_file.name}: {part_size:.2f} MB")
        
        print(f"{'='*80}\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Split failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def split_pdf_by_size(input_path: str, max_size_mb: int = 50, output_dir: str = "pdf"):
    """
    Split PDF by maximum file size
    
    Args:
        input_path: Path to input PDF
        max_size_mb: Maximum size per file in MB
        output_dir: Directory to save split PDFs
    """
    print(f"\n{'='*80}")
    print(f"PDF SPLITTER - Split by size limit ({max_size_mb} MB)")
    print(f"{'='*80}")
    print(f"Input:      {input_path}")
    print(f"Output:     {output_dir}/")
    print(f"Max size:   {max_size_mb} MB per file")
    print(f"{'='*80}\n")
    
    # Check input
    if not os.path.exists(input_path):
        print(f"[ERROR] File not found: {input_path}")
        return False
    
    input_size = os.path.getsize(input_path) / (1024 * 1024)
    print(f"[INFO] Input size: {input_size:.2f} MB")
    
    # Estimate number of parts needed
    estimated_parts = int(input_size / max_size_mb) + 1
    print(f"[INFO] Estimated parts: ~{estimated_parts}\n")
    
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        print(f"[INFO] Total pages: {total_pages}\n")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        base_name = Path(input_path).stem
        
        # Split by tracking size
        part_num = 1
        current_writer = PdfWriter()
        current_pages = 0
        
        for page_num, page in enumerate(reader.pages, 1):
            current_writer.add_page(page)
            current_pages += 1
            
            # Check if we should save this part
            # Save every ~pages based on proportion
            pages_per_part = total_pages // estimated_parts
            
            if current_pages >= pages_per_part or page_num == total_pages:
                # Save current part
                output_file = output_path / f"{base_name}_part{part_num}.pdf"
                
                with open(output_file, "wb") as f:
                    current_writer.write(f)
                
                part_size = os.path.getsize(output_file) / (1024 * 1024)
                print(f"[OK] Part {part_num}: {output_file.name} ({part_size:.2f} MB, {current_pages} pages)")
                
                # Start new part
                part_num += 1
                current_writer = PdfWriter()
                current_pages = 0
        
        print(f"\n{'='*80}")
        print(f"[SUCCESS] PDF split into {part_num-1} parts!")
        print(f"{'='*80}\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Split failed: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python pdf_splitter.py <input.pdf> [num_parts]")
        print("\nExamples:")
        print("  python pdf_splitter.py large_file.pdf          # Split into 6 parts")
        print("  python pdf_splitter.py large_file.pdf 10       # Split into 10 parts")
        print("\nOutput will be saved to: pdf/")
        return
    
    input_file = sys.argv[1]
    num_parts = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    
    split_pdf_by_parts(input_file, num_parts, output_dir="pdf")

if __name__ == "__main__":
    main()
