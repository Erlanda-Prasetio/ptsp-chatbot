"""
MADAM Debate Only - For Thesis Demonstration
This version skips vector and enhanced phases and runs MADAM debate directly
Shows the complete multi-agent debate process with detailed logging
"""
import sys
sys.path.insert(0, 'src')

import time
import csv
from datetime import datetime
from typing import List, Dict, Any
import importlib.util
from pathlib import Path

# Import components
from smart_enhanced_rag import SmartEnhancedRAG
from hybrid_rag import query_llm

# Load MADAM debate module
try:
    _MADAM_MODULE_PATH = Path(__file__).resolve().parent / "testing" / "madam-rag" / "run_madam_rag.py"
    _MADAM_SPEC = importlib.util.spec_from_file_location("madam_rag_debate", str(_MADAM_MODULE_PATH))
    _MADAM_MODULE = importlib.util.module_from_spec(_MADAM_SPEC) if _MADAM_SPEC else None
    if _MADAM_SPEC and _MADAM_SPEC.loader and _MADAM_MODULE:
        _MADAM_SPEC.loader.exec_module(_MADAM_MODULE)
        multi_agent_debate = getattr(_MADAM_MODULE, "multi_agent_debate")
    else:
        raise ImportError("Unable to load MADAM debate module")
except Exception as exc:
    print(f"[ERROR] Could not load MADAM debate module: {exc}")
    exit(1)


class _MadamDebateGenerator:
    """Adapter for MADAM debate generator"""
    
    def __call__(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 256,
        top_p: float = None,
        do_sample: bool = False,
    ) -> List[Dict[str, Any]]:
        prompt = "\n".join(msg.get("content", "") for msg in messages)
        result = query_llm(prompt, "")
        if isinstance(result, dict):
            text = result.get("text", "")
            model = result.get("model", "unknown")
            usage = result.get("usage", {})
        else:
            text = str(result)
            model = "unknown"
            usage = {}
        return [
            {
                "generated_text": [
                    {"role": "user", "content": prompt},
                    {
                        "role": "assistant",
                        "content": text,
                        "model": model,
                        "usage": usage,
                    },
                ]
            }
        ]


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_subheader(title):
    """Print a formatted subheader"""
    print(f"\n{title}")
    print("-" * 80)


def load_queries_from_csv(csv_path):
    """Load test queries from CSV file"""
    queries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            queries.append({
                'id': row['query_id'],
                'question': row['question'],
                'category': row['category']
            })
    return queries


def get_documents_from_rag(rag_system, question: str, top_k: int = 4) -> List[str]:
    """Get raw document texts directly from RAG system for debate"""
    from embed import embed_texts
    
    # Get embedding
    q_emb = embed_texts([question])[0]
    
    # Search for chunks
    hits = rag_system.store.search(q_emb, top_k=top_k)
    
    documents = []
    for hit in hits:
        text = hit.get('content', hit.get('text', ''))
        if text and len(text.strip()) > 50:
            documents.append(text)
    
    return documents


def run_madam_debate_test():
    """Run MADAM debate test for thesis demonstration"""
    
    # Load queries from CSV
    csv_path = r"D:\backup\ptspRag\evaluation\retrieval_test_3queries.csv"
    queries = load_queries_from_csv(csv_path)
    
    print_header("MADAM MULTI-AGENT DEBATE - THESIS DEMONSTRATION")
    print(f"Queries: {len(queries)}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nConfiguration:")
    print(f"  - Debate Rounds: 3")
    print(f"  - Agents per Round: 4")
    print(f"  - Documents per Agent: 4")
    print(f"  - GPU: ENABLED (RTX 3070)")
    
    # Initialize RAG for document retrieval
    print_subheader("INITIALIZING SYSTEM")
    print("[INIT] Loading RAG system for document retrieval...")
    rag_system = SmartEnhancedRAG()
    print("[OK] RAG system ready")
    
    print("[INIT] Loading MADAM debate generator...")
    debate_generator = _MadamDebateGenerator()
    print("[OK] Debate generator ready")
    
    # Process each query
    for query_data in queries:
        query_id = query_data['id']
        question = query_data['question']
        category = query_data['category']
        
        print_header(f"{query_id}: {question}")
        print(f"Category: {category}")
        
        start_time = time.time()
        
        try:
            # Step 1: Retrieve documents
            print_subheader("STEP 1: DOCUMENT RETRIEVAL")
            print(f"[SEARCH] Retrieving relevant documents from knowledge base...")
            
            retrieval_start = time.time()
            documents = get_documents_from_rag(rag_system, question, top_k=4)
            retrieval_time = time.time() - retrieval_start
            
            print(f"[OK] Retrieved {len(documents)} documents ({retrieval_time:.2f}s)")
            
            # Preview documents
            print(f"\n[INFO] Document Preview:")
            for i, doc in enumerate(documents, 1):
                preview = doc[:150].replace('\n', ' ')
                print(f"  Doc {i}: {preview}...")
            
            # Step 2: Run MADAM Debate
            print_subheader("STEP 2: MADAM MULTI-AGENT DEBATE")
            print(f"[START] Initiating debate with 4 agents, 3 rounds maximum")
            print(f"[INFO] This will take several minutes due to API rate limiting")
            print(f"[INFO] Check logs/madam_debate_*.log for detailed agent conversations\n")
            
            debate_start = time.time()
            debate_records = multi_agent_debate(
                query=question,
                documents=documents,
                generator=debate_generator,
                num_rounds=3
            )
            debate_time = time.time() - debate_start
            
            print(f"\n[OK] Debate completed ({debate_time:.2f}s = {debate_time/60:.1f} minutes)")
            
            # Step 3: Show Results
            print_subheader("STEP 3: DEBATE RESULTS")
            
            # Show round summaries
            for round_num in range(1, 4):
                round_key = f"round{round_num}"
                if round_key not in debate_records:
                    break
                
                round_data = debate_records[round_key]
                print(f"\n[ROUND {round_num}] Agent Answers:")
                for i, answer in enumerate(round_data.get('answers', []), 1):
                    print(f"  Agent {i}: {answer[:200]}..." if len(answer) > 200 else f"  Agent {i}: {answer}")
                
                if 'aggregation' in round_data:
                    agg = round_data['aggregation']
                    print(f"\n[ROUND {round_num}] Aggregation:")
                    print(f"  {agg[:300]}..." if len(agg) > 300 else f"  {agg}")
            
            # Final answer
            if 'final_aggregation' in debate_records:
                print(f"\n[FINAL] Aggregated Answer:")
                final = debate_records['final_aggregation']
                print(f"  {final}")
            
            total_time = time.time() - start_time
            print(f"\n[TIME] Total: {total_time:.2f}s ({total_time/60:.1f} minutes)")
            print(f"  - Retrieval: {retrieval_time:.2f}s")
            print(f"  - Debate: {debate_time:.2f}s")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"\n[ERROR] {str(e)}")
            print(f"Time elapsed: {elapsed:.2f}s")
            import traceback
            traceback.print_exc()
        
        # Wait between queries (except after last one)
        if query_data != queries[-1]:
            print_header("Waiting 15 seconds before next query...")
            time.sleep(15)
    
    print_header("THESIS DEMONSTRATION COMPLETED")
    print(f"\n[INFO] Detailed debate logs saved to: logs/madam_debate_*.log")
    print(f"[INFO] These logs show:")
    print(f"  - Individual agent responses per round")
    print(f"  - Step-by-step reasoning from each agent")
    print(f"  - Aggregation process and consensus building")
    print(f"  - Convergence detection across rounds")
    print(f"\n[DONE] All queries processed successfully!")


if __name__ == "__main__":
    run_madam_debate_test()
