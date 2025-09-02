"""
Monitor scraping progress
"""
import time
import json
from pathlib import Path

def monitor_progress():
    data_dir = Path("data/scraped_dpmptsp")
    pages_dir = data_dir / "pages"
    files_dir = data_dir / "files"
    
    print("📊 DPMPTSP Scraping Progress Monitor")
    print("=" * 50)
    
    while True:
        try:
            # Count files
            page_count = len(list(pages_dir.glob("*.txt"))) if pages_dir.exists() else 0
            file_count = len([f for f in files_dir.iterdir() if f.is_file()]) if files_dir.exists() else 0
            
            # Check for summary
            summary_file = data_dir / "crawl_summary.json"
            partial_summary_file = data_dir / "crawl_summary_partial.json"
            
            status = "Running"
            if summary_file.exists():
                with open(summary_file, 'r') as f:
                    summary = json.load(f)
                status = f"Complete - {summary['successful_pages']} pages successful"
            elif partial_summary_file.exists():
                with open(partial_summary_file, 'r') as f:
                    summary = json.load(f)
                status = f"Partial - {summary['successful_pages']} pages so far"
            
            print(f"\r📄 Pages: {page_count:3d} | 📁 Files: {file_count:3d} | Status: {status}", end="", flush=True)
            
            if summary_file.exists():
                print("\n🎉 Scraping completed!")
                break
                
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"\n❌ Error monitoring: {e}")
            break

if __name__ == "__main__":
    monitor_progress()
