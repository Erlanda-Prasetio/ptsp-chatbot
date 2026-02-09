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
    log_file = os.path.join(current_dir, "pipeline_timing_log_maf-rag_real.txt")
    if os.path.exists(log_file):
        os.remove(log_file)
        
    log_message("=== MAF-RAG Phase Latency Test  ===", log_file)
    log_message("Demonstrating Phase 3: MAF-RAG Multi-Agent Debate...", log_file)
    
    # Initialize System
    try:
        rag = MadamHybridRAGSystem(debate_rounds=1, debate_top_k=3)
        
        # --- NATURAL THRESHOLDS ---
        rag.vector_quality_threshold = 0.75
        rag.enhanced_quality_threshold = 0.60
        
        log_message("System configured for Natural Debate Flow:", log_file)
        log_message(f"-> VOR Threshold: {rag.vector_quality_threshold} (Default)", log_file)
        log_message(f"-> EVR Threshold: {rag.enhanced_quality_threshold} (Default)", log_file)
    except Exception as e:
        log_message(f"Initialization failed: {e}", log_file)
        return

    # Query selected from retrieval_test_madam_results.csv (ID: old_304)
    # This query historically triggered 'maf-rag_debate' because procedural questions 
    # often require synthesizing multiple chunks, lower scores in vector/enhanced phases.
    
    query = "Bagaimana cara mengurus izin untuk usaha penyewaan alat berat?"
    
    log_message(f"\nTest Query: '{query}'", log_file)
    log_message("(Source: ID old_304 - Proven to trigger MAF-RAG Debate naturally)", log_file)
    
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
    mad_time = phase_times.get('maf-rag_debate', 'N/A')
    
    log_message(f"[Phase 1] Vector Retrieval: {vec_time}", log_file)
    log_message(f"[Phase 2] Enhanced Retrieval: {enh_time}", log_file)
    if mad_time != 'N/A':
        log_message(f"[Phase 3] MAF-RAG Debate: {mad_time}", log_file)
    
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
