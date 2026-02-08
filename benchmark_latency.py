import time
import torch
from sentence_transformers import SentenceTransformer
import numpy as np

# Test data (simulating real queries)
QUERIES = [
    "How do I apply for a business license in Central Java?",
    "What are the requirements for NIB registration?",
    "Procedure for building permit application",
    "Investment opportunities in industrial zones",
    "Tax incentives for foreign investors",
    "Online Single Submission system troubleshooting",
    "Environmental impact assessment documents",
    "Minimum capital requirements for PMA",
    "Local partnership regulations",
    "Timeline for permit issuance"
] * 5  # 50 queries total

def benchmark_model(model_name):
    print(f"\n[BENCHMARK] Testing model: {model_name}")
    print("Loading model... (this may download files if not cached)")
    
    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Device: {device}")
        
        model = SentenceTransformer(model_name, device=device)
        
        # Warmup
        print("Warming up...")
        model.encode(QUERIES[:2])
        
        # Benchmark
        print(f"Encoding {len(QUERIES)} queries...")
        start_time = time.time()
        embeddings = model.encode(QUERIES)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_latency = (total_time / len(QUERIES)) * 1000 # ms
        
        print(f"Total Time: {total_time:.4f}s")
        print(f"Avg Latency: {avg_latency:.2f} ms/query")
        
        return avg_latency
        
    except Exception as e:
        print(f"Failed to load or run {model_name}: {e}")
        return None

def main():
    print("="*60)
    print("LATENCY BENCHMARK: MiniLM vs Large Model")
    print("="*60)
    
    # 1. Test Current Model
    t1 = benchmark_model('sentence-transformers/all-MiniLM-L6-v2')
    
    # 2. Test Large Model (E5-Large)
    # This is the model you mentioned as the alternative
    t2 = benchmark_model('intfloat/e5-large-v2')
    
    if t1 and t2:
        print("\n" + "="*60)
        print("FINAL COMPARISON")
        print("="*60)
        print(f"MiniLM-L6 (Yours): {t1:.2f} ms")
        print(f"E5-Large (Target): {t2:.2f} ms")
        print(f"Slowdown Factor:   {t2/t1:.1f}x slower")
        print("-" * 60)
        
        if t2 > t1:
            print("✅ CONCLUSION: The large model is significantly slower.")
            print(f"   You can write: '...incur significantly higher latency ({t2:.0f}ms vs {t1:.0f}ms per query), which is impractical...'")
        else:
            print("❓ CONCLUSION: Unexpected results. Check GPU usage.")

if __name__ == "__main__":
    main()
