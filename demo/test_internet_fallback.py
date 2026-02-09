import sys
from dotenv import load_dotenv
load_dotenv()
import os
import time

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

try:
    from internet_search import EnhancedInternetSearch
    from ask import query_llm
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def log_message(message, log_file):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(formatted_message + "\n")

def run_demo():
    log_file = os.path.join(current_dir, "internet_fallback_log.txt")
    
    log_message("=== Starting Internet Fallback Demo ===", log_file)
    
    # Initialize
    log_message("Initializing EnhancedInternetSearch...", log_file)
    try:
        searcher = EnhancedInternetSearch()
        log_message("Initialization successful.", log_file)
    except Exception as e:
        log_message(f"Initialization failed: {e}", log_file)
        return

    # Using a real query from the dataset
    query = "Apa kode KBLI untuk usaha laundry?"
    log_message(f"Test Query: '{query}'", log_file)

    # 1. Enhance Query (Visual demonstration)
    log_message("\n[Logic Check] Step 1: Enhancing Query...", log_file)
    enhanced_query = searcher.enhance_query_for_ptsp(query)
    log_message(f"Original Query: {query}", log_file)
    log_message(f"Enhanced Query: {enhanced_query}", log_file)

    # 2. Run Search
    log_message("\n[Execution] Step 2: Running Multi-Engine Search...", log_file)
    
    start_time = time.time()
    results = searcher.search_multiple_engines(query)
    elapsed = time.time() - start_time
    
    log_message(f"Search completed in {elapsed:.2f} seconds.", log_file)
    log_message(f"Found {len(results)} results.", log_file)

    # 3. Format Context
    log_message("\n[Processing] Step 3: Formatting context for LLM...", log_file)
    context = searcher.format_internet_context(results)
    
    # 4. Generate Answer using LLM
    log_message("\n[Generation] Step 4: Generating Answer using LLM...", log_file)
    
    # query_llm takes (question, context) directly
    # It constructs the system prompt internally using SYSTEM_INSTR from the same file
    start_gen = time.time()
    try:
        log_message(f"Calling query_llm(question='{query}', context=...)", log_file)
        # Fix: passing context as second argument, not constructing a custom prompt template here
        # query_llm handles the prompt formatting internally
        response = query_llm(query, context)
        gen_elapsed = time.time() - start_gen
        
        answer_text = response.get('text', 'No text generated') if isinstance(response, dict) else str(response)
        
        log_message("-" * 40, log_file)
        log_message("FINAL LLM ANSWER:", log_file)
        log_message("-" * 40, log_file)
        log_message(answer_text, log_file)
        log_message("-" * 40, log_file)
        log_message(f"Generation time: {gen_elapsed:.2f}s", log_file)
        log_message(f"Model used: {response.get('model', 'unknown')}", log_file)
        
    except Exception as e:
        log_message(f"generation failed: {e}", log_file)

    log_message("\n=== Demo Complete ===", log_file)
    print(f"\nLog saved to: {log_file}")

if __name__ == "__main__":
    run_demo()
