# Reviewer Comments Mapped to Manuscript Sections

This document maps each specific reviewer comment to the relevant section of your manuscript, explaining *why* they made the comment and *where* you should make the change.

---

## **SECTION: I. INTRODUCTION**

### **Reviewer A: Conceptual Boundaries**
> **Comment:** "Kontribusi konseptual MAF-RAG perlu dipertegas secara structural... batasan konseptual antara MAF-RAG dan pendekatan RAG yang telah ada... belum dijelaskan secara eksplisit."

*   **Where to fix:** Page 2, Paragraphs 3-5 (where you discuss MAIN-RAG and MADAM).
*   **The Issue:** You mention MAIN-RAG and MADAM, and then say "MAF-RAG is a result of combining two of the previous approaches." This sounds derivative.
*   **The Fix:** You need to explicitly state what MAF-RAG does *differently*. Is it the **three-phase escalation** logic? (Most RAGs just do one retrieval). Is it the **fallback** mechanism?
*   **Drafting Tip:** Add a sentence: "Unlike MAIN-RAG which focuses solely on filtering, or MADAM which focuses solely on debate, MAF-RAG introduces a **hierarchical escalation architecture** that dynamically switches between VOR, EVR, and Multi-Agent Debate based on confidence scores, optimizing cost and accuracy."

---

## **SECTION: II. METHODOLOGY**

### **Reviewer A: EVR–VOR Definitions**
> **Comment:** "Istilah EVR–VOR Vector Retrieval belum didefinisikan secara formal... tidak memberikan definisi matematis atau algoritmik yang jelas."

*   **Where to fix:** Page 4, Section A (MAF-RAG Retrieval Testing).
*   **The Issue:** You describe VOR and EVR in text ("...system searches through the datasets..."). This is "descriptive," not "formal." Computer science papers prefer math.
*   **The Fix:** Add a definition block.
    *   **Vector-Only Retrieval (VOR):** Define it as a cosine similarity function over the vector space.
    *   **Enhanced Vector Retrieval (EVR):** Define the "re-ranking mechanism" you mentioned. What algorithm does it use? (e.g., Cross-Encoder? filtering rules?). Write it as a function: $EVR(q) = \text{rerank}(\text{top-}k(q))$.

### **Reviewer A: Encoder Selection**
> **Comment:** "Pemilihan encoder bersifat praktis tetapi kurang dikritisi... artikel tidak membahas keterbatasan representasional encoder ini..."

*   **Where to fix:** Page 3, bottom of left column ("An encoder model, sentence-transformers/all-MiniLM-L6-v2...").
*   **The Issue:** `all-MiniLM-L6-v2` is a small, fast model. It's not the state-of-the-art (SOTA). Reviewers know better models exist (e.g., OpenAI `text-embedding-3`, BGE-M3).
*   **The Fix:** Don't change the model (that requires re-doing experiments). Instead, **defend your choice**.
    *   "We selected `all-MiniLM-L6-v2` for its balance of speed and performance suitable for local deployment on limited hardware (Nvidia CUDA GPU), ensuring data privacy for government applications without external API dependencies."
    *   Acknowledge limitation: "While larger models like E5-Large offer higher semantic resolution, they incur significantly higher latency."

### **Reviewer A: Multi-Agent Debating**
> **Comment:** "Mekanisme multi-agent debating masih bersifat deskriptif... tidak menjelaskan secara rinci peran masing-masing agen..."

*   **Where to fix:** Page 4, Section B (Multi-Agent Debating Procedure) & Figure 3.
*   **The Issue:** You describe the debate in paragraphs. It's hard to visualize the exact logic.
*   **The Fix:** Add **Algorithm 1: MAF-RAG Debate Protocol**.
    *   Listing the steps clearly: 1. Agents generate draft; 2. Aggregator reviews; 3. If conflict -> Debate Round 2; 4. Else -> Final Answer.
    *   Also, explicitly state the **Agent Prompts** or "Personas" (e.g., "Agent 1 acts as a skeptic," "Agent 2 acts as a fact-checker").

### **Reviewer B: Baseline Details**
> **Comment:** "Baseline sistem perlu dijelaskan lebih rinci... spesifikasi arsitektur... belum diuraikan secara lengkap."

*   **Where to fix:** Page 6, Section D (Evaluation Metrics) or a new "Experimental Setup" section.
*   **The Issue:** You compare MAF-RAG vs. "Legacy" vs. "Enhanced." But what *is* the Legacy system? Is it just a keyword search? Is it a basic RAG with no re-ranking?
*   **The Fix:** Add a table: **Table X: Experimental Configurations**.
    *   Rows: Retriever Model, Chunk Size, Re-ranking (Y/N), Agent Count.
    *   Cols: Legacy, Enhanced, MAF-RAG.
    *   This proves the comparison is fair.

---

## **SECTION: III. RESULTS AND DISCUSSION**

### **Reviewer B: Error Analysis**
> **Comment:** "Analisis error dan kegagalan sistem belum dieksplorasi mendalam... artikel tidak membahas jenis pertanyaan atau kondisi retrieval apa yang masih gagal..."

*   **Where to fix:** Page 9, after Figure 11 (Heatmap).
*   **The Issue:** You say failure rate dropped to 22%. But what about that remaining 22%?
*   **The Fix:** Look at the 11 queries that failed. Were they about specific topics? Were they ambiguous?
    *   Add a paragraph: **"Failure Analysis."** "The remaining 22% of failures primarily stemmed from ambiguous user queries where the intent was unclear even to human annotators..." or "queries requiring synthesis of >4 documents."

### **Reviewer B: Latency Trade-off**
> **Comment:** "Trade-off latensi belum dianalisis secara operasional..."

*   **Where to fix:** Page 9, Section C (System Reliability Analysis).
*   **The Issue:** You acknowledge the 4.9% latency increase but dismiss it as "minimal." The reviewer wants you to *prove* it's minimal operationally.
*   **The Fix:** Add context. "While latency increased by ~0.5s, the system remains within the acceptable response window for non-real-time consultative chatbots (typically <15s). In government contexts, the cost of **misinformation** (hallucination) far outweighs the cost of a slightly slower response."

### **Reviewer B: Statistical Significance**
> **Comment:** "Tidak ada uji signifikansi statistik atas peningkatan performa..."

*   **Where to fix:** Page 6, Table III (Overall System Retrieval Performance).
*   **The Issue:** Is the 19.1% improvement real, or just luck with those 50 queries?
*   **The Fix:** If you can, calculate a **p-value** (T-Test) comparing the F1 scores of the 50 queries for Enhanced vs. MAF-RAG.
    *   If $p < 0.05$, state: "This improvement is statistically significant ($p < 0.05$)."
    *   If you can't calculate it easily, mention it as a limitation or add Standard Deviation (±SD) to the table to show the spread.

---

## **SECTION: IV. CONCLUSION / DISCUSSION**

### **Reviewer A: Dataset Size**
> **Comment:** "Ukuran dataset relatif kecil untuk klaim generalisasi..."

*   **Where to fix:** Page 10, Discussion or Conclusion.
*   **The Issue:** 150 queries is small for a "Generalization" claim.
*   **The Fix:** Soften your language. Change "demonstrates MAF-RAG's ability to perform... making it a suitable solution..." to "demonstrates MAF-RAG's potential in **domain-specific** government applications."
*   **Add:** A "Limitations" section acknowledging that 150 queries is a pilot scale and future work should test on larger open benchmarks (like MS MARCO or BEIR).

### **Reviewer A: F1-Score Definition**
> **Comment:** "Definisi dan kriteria evaluasi F1-score belum dijelaskan rinci..."

*   **Where to fix:** Page 6, Section D (Evaluation Metrics).
*   **The Issue:** You wrote the formula, but not the *input*. Is "Precision" based on **words** (n-grams) or **documents** (retrieved IDs)?
*   **The Fix:** Clarify: "F1-score was calculated based on **retrieval relevance** at $k=5$, where a document is considered 'relevant' if it matches the ground truth document ID assigned to the query." (Or however you actually did it).

### **Reviewer B: Future Work**
> **Comment:** "Arah penelitian lanjutan dapat dipertegas..."

*   **Where to fix:** Page 10, Conclusion.
*   **The Issue:** Current future work is generic.
*   **The Fix:** Adopt their specific ideas. "Future work will explore **adaptive agent selection** to reduce latency for simpler queries, and test **cross-domain generalization** in medical or legal datasets."

