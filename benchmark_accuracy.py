import time
import torch
from sentence_transformers import SentenceTransformer, util

# ==========================================
# 1. DATA PREPARATION (Ground Truth)
# ==========================================

# Simulating database chunks (Documents)
DOCS = {
    "NIB_Chunk": "Nomor Induk Berusaha (NIB) adalah identitas pelaku usaha yang diterbitkan oleh Lembaga OSS. NIB wajib dimiliki oleh setiap pelaku usaha sebelum menjalankan kegiatan operasional dan komersial.",
    "KKPR_Chunk": "Persetujuan Kesesuaian Kegiatan Pemanfaatan Ruang (PKKPR) menggantikan Izin Lokasi. PKKPR berfungsi sebagai acuan pemanfaatan ruang dan persyaratan dasar perizinan berusaha.",
    "LKPM_Chunk": "Laporan Kegiatan Penanaman Modal (LKPM) adalah laporan mengenai perkembangan realisasi penanaman modal dan permasalahan yang dihadapi pelaku usaha yang wajib disampaikan secara berkala."
}

# Queries targeting specific chunks
QUERIES = [
    ("Apa itu NIB dan fungsinya?", "NIB_Chunk"),
    ("Bagaimana aturan tentang tata ruang lokasi?", "KKPR_Chunk"),
    ("Siapa yang wajib lapor LKPM?", "LKPM_Chunk")
]

def format_e5(text, is_query=False):
    # E5 expects "query: " or "passage: " prefixes
    prefix = "query: " if is_query else "passage: "
    return prefix + text

def benchmark_accuracy(model_name, use_prefix=False):
    print(f"\n[TESTING] Model: {model_name}")
    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = SentenceTransformer(model_name, device=device)
        
        # Prepare texts
        doc_names = list(DOCS.keys())
        doc_texts = list(DOCS.values())
        query_texts = [q[0] for q in QUERIES]
        
        if use_prefix:
            print("   -> Applying 'query:' and 'passage:' prefixes (E5-Standard)")
            encoded_docs = model.encode([format_e5(d, False) for d in doc_texts], convert_to_tensor=True)
            encoded_queries = model.encode([format_e5(q, True) for q in query_texts], convert_to_tensor=True)
        else:
            encoded_docs = model.encode(doc_texts, convert_to_tensor=True)
            encoded_queries = model.encode(query_texts, convert_to_tensor=True)

        # Compute Cosine Similarity Matrix
        # shape: [num_queries, num_docs]
        cos_scores = util.cos_sim(encoded_queries, encoded_docs)
        
        total_margin = 0
        print(f"\n   {'Query':<40} | {'Correct Match':<15} | {'Score':<8} | {'Distractor':<8} | {'Margin':<8}")
        print("-" * 100)
        
        for i, (q_text, target_doc_key) in enumerate(QUERIES):
            target_idx = doc_names.index(target_doc_key)
            
            # Score for the correct document
            correct_score = cos_scores[i][target_idx].item()
            
            # Get max score of NON-target documents (Distractors)
            # Mask the correct index with -1
            scores_clone = cos_scores[i].clone()
            scores_clone[target_idx] = -1.0 
            distractor_score = torch.max(scores_clone).item()
            
            margin = correct_score - distractor_score
            total_margin += margin
            
            q_short = (q_text[:35] + '..') if len(q_text) > 35 else q_text
            print(f"   {q_short:<40} | {target_doc_key:<15} | {correct_score:.4f}   | {distractor_score:.4f}   | {margin:+.4f}")

        avg_margin = total_margin / len(QUERIES)
        print("-" * 100)
        print(f"   AVERAGE SEPARATION MARGIN: {avg_margin:+.4f}")
        return avg_margin

    except Exception as e:
        print(f"Error: {e}")
        return 0

def main():
    print("="*80)
    print("ACCURACY SENSITIVITY TEST: MiniLM vs E5-Large")
    print("Goal: Check if E5 is 'smarter' at separating correct docs from wrong ones.")
    print("Metric: 'Margin' = (Score of Correct Doc) - (Score of Best Wrong Doc)")
    print("="*80)

    # 1. MiniLM
    margin_mini = benchmark_accuracy('sentence-transformers/all-MiniLM-L6-v2', use_prefix=False)

    # 2. E5 Large
    margin_e5 = benchmark_accuracy('intfloat/e5-large-v2', use_prefix=True)

    print("\n" + "="*80)
    print("FINAL CONCLUSION (Accuracy)")
    print("="*80)
    print(f"MiniLM Avg Margin: {margin_mini:.4f}")
    print(f"E5-Large Avg Margin: {margin_e5:.4f}")
    
    diff = margin_e5 - margin_mini
    print(f"Difference: {diff:+.4f}")
    
    if diff > 0.05:
        print("RESULT: E5-Large is SIGNIFICANTLY more distinct (Cleaner separation).")
    elif diff > 0:
        print("RESULT: E5-Large is SLIGHTLY better, but comparable.")
    else:
        print("RESULT: MiniLM is ACTUALLY BETTER or EQUAL for this data.")

if __name__ == "__main__":
    main()
