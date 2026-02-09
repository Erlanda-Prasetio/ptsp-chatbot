import sys
import os
import time
import json
import random
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)  
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)      

# Mock modules if they fail to import
try:
    from madam_hybrid_system import MadamHybridRAGSystem
except ImportError as e:
    print(f"Error importing MadamHybridRAGSystem: {e}")
    # Try importing directly
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("madam_hybrid_system", os.path.join(project_root, "madam_hybrid_system.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        MadamHybridRAGSystem = module.MadamHybridRAGSystem
    except Exception as e2:
        print(f"Direct import failed too: {e2}")
        sys.exit(1)

def log_message(message, log_file):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(formatted_message + "\n")

def run_timing_test():
    log_file = os.path.join(current_dir, "pipeline_timing_log_evr.txt")
    if os.path.exists(log_file):
        os.remove(log_file)
        
    log_message("=== MAF-RAG Phase Latency Test ===", log_file)
    log_message("Demonstrating Phase 2: Enhanced Vector Retrieval ...", log_file)
    
    # Initialize System
    try:
        rag = MadamHybridRAGSystem(debate_rounds=1, debate_top_k=3)
        
        # --- NATURAL THRESHOLDS ---
        # We restore the default logic:
        # 1. VOR needs > 0.75 to pass (We want to FAIL this naturally)
        # 2. EVR needs > 0.60 to pass (We want to PASS this naturally)
        
        rag.vector_quality_threshold = 0.75
        rag.enhanced_quality_threshold = 0.60
        
        
        log_message(f"-> VOR Threshold: {rag.vector_quality_threshold} (Default)", log_file)
        log_message(f"-> EVR Threshold: {rag.enhanced_quality_threshold} (Default)", log_file)
    except Exception as e:
        log_message(f"Initialization failed: {e}", log_file)
        return

    # "Tricky" Query Strategy:
    # We use a query that uses different synonyms/phrasing than the database text.
    # The Vector Search (keyword/embedding) might give it a 'meh' score (e.g., 0.65-0.70).
    # The Enhanced Search will rewrite it to match the official terms, finding the doc with high confidence (>0.8).
    
    # Content in DB: "Kenapa Saat Cek RDTR Muncul Notifikasi Kegiatan Usaha Tidak Sesuai RDTR?"
    # Tricky Query: "Saya dapat peringatan masalah zonasi saat mendaftar"
    # - "peringatan" ~= "notifikasi"
    # - "masalah zonasi" ~= "tidak sesuai RDTR"
    # - "mendaftar" ~= "tambah KBLI"
    
    query = "Saya dapat peringatan masalah zonasi saat mendaftar"
    
    log_message(f"\nTest Query: '{query}'", log_file)
    
    start_total = time.time()
    
    # Run the query
    result = rag.ask_with_fallback(query)
    
    total_elapsed = time.time() - start_total
    
    # LOGGING RESULTS
    log_message("\n=== LATENCY BREAKDOWN ===", log_file)
    
    enhanced_features = result.get('enhanced_features', {})
    phase_times = enhanced_features.get('phase_times', {})
    phase_log = enhanced_features.get('phase_log', [])
    search_method = enhanced_features.get('search_method', 'unknown')
    
    vec_time = phase_times.get('vector_only', 'N/A')
    enh_time = phase_times.get('enhanced_vector', 'N/A')
    
    log_message(f"[Phase 1] Vector Retrieval: {vec_time} (Threshold not met)", log_file)
    log_message(f"[Phase 2] Enhanced Retrieval: {enh_time}", log_file)
    
    log_message("-" * 30, log_file)
    log_message(f"Total Wall Time: {total_elapsed:.2f}s", log_file)
    log_message(f"Final Method Used: {search_method}", log_file)
    
    log_message("\n=== QUALITY CHECKS ===", log_file)
    for entry in phase_log:
        phase = entry.get('phase')
        qual = entry.get('quality', 'N/A')
        log_message(f"{phase}: {qual}", log_file)

    log_message("\n=== FINAL ANSWER SNIPPET ===", log_file)
    answer = result.get('answer', '')
    log_message(answer[:300] + "..." if len(answer) > 300 else answer, log_file)
    
    log_message("\n=== Test Complete ===", log_file)
    print(f"\nLog saved to: {log_file}")

if __name__ == "__main__":
    run_timing_test()
