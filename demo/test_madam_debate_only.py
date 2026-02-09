import sys
import os
import logging

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from madam_hybrid_system import MadamHybridRAG

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def test_madam_only():
    print("\n" + "="*60)
    print("TEST: FORCE MAF-RAG DEBATE (Bypassing VOR/EVR)")
    print("="*60)

    # Initialize System
    print("[INIT] Initializing MADAM RAG System...")
    rag = MadamHybridRAG(
        db_connection_string="postgresql://postgres:postgres@localhost:54322/postgres",
        openai_api_key="gsk_...", # Assuming env var is set or passing dummy if using Groq internally
        groq_api_key=os.getenv("GROQ_API_KEY") # Ensure this is picked up
    )

    # OVERRIDE THRESHOLDS to FORCE FAILURE of Phase 1 & 2
    print("[CONFIG] Overriding thresholds to impossible values (2.0)")
    rag.vector_quality_threshold = 2.0  # Impossible to reach (0-1 scale)
    rag.enhanced_quality_threshold = 2.0 # Impossible to reach
    
    # Query designed to trigger debate (though we forced it anyway)
    query = "Bagaimana prosedur lengkap perizinan usaha pertambangan batuan?"
    
    print(f"\n[QUERY] {query}")
    print("[INFO] Starting pipeline... (VOR and EVR should FAIL, triggering MADAM)")
    
    # Run
    result = rag.process_query(query)
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    
    if result:
        print(f"Method Used: {result.get('method')}")
        print(f"Quality Score: {result.get('quality_score')}")
        print("-" * 30)
        print("ANSWER:\n")
        print(result.get('answer'))
        print("-" * 30)
        
        # Print Phase Logs to prove VOR/EVR failed
        print("\n[PHASE LOGS]")
        for log in result.get('phase_log', []):
            phase = log.get('phase')
            status = "SKIPPED/FAILED" 
            if log.get('quality'):
                status = f"Score: {log.get('quality'):.4f}"
            if log.get('skipped'):
                status = "SKIPPED"
            
            print(f" - {phase:<20} : {status}")
            if phase == 'madam_debate':
                print(f"   -> Aggregation Preview: {log.get('aggregation_preview')[:100]}...")

    else:
        print("[FAIL] No result returned.")

if __name__ == "__main__":
    test_madam_only()
