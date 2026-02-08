# Manuscript Revision Plan (Final)

This document maps every reviewer comment to the specific text in your manuscript that needs to be changed, along with a concrete "Action" item.

---

## 1. INTRODUCTION: Conceptual Contribution

**Your Text (Page 2):**
> "To address these issues, this study proposed a Multi-Agent Fallback for Retrieval-Augmented Generation (MAF-RAG), which is a result of combining two of the previous approaches..."

**🔴 Reviewer A Comment:**
> "Kontribusi konseptual MAF-RAG perlu dipertegas secara structural... batasan konseptual antara MAF-RAG dan pendekatan RAG yang telah ada... belum dijelaskan secara eksplisit."
> *(The conceptual contribution needs to be structurally emphasized... the conceptual boundary between MAF-RAG and existing approaches is not explicitly explained.)*

**💡 Action:**
Emphasize the **novelty of the architecture**.
*   **Rewrite:** "Unlike MAIN-RAG which filters statically, or MADAM which debates every query, MAF-RAG introduces a **hierarchical escalation protocol** that dynamically switches strategies based on confidence. It uniquely positions the expensive Multi-Agent Debate phase as a **tertiary fallback**—triggered only when both Vector-Only Retrieval (VOR) and Enhanced Vector Retrieval (EVR) fail, but before resorting to external Internet Search."

---

## 2. METHODOLOGY: Encoder Selection & Hardware Constraints

**Your Text (Page 3):**
> "An encoder model, sentence-transformers/all-MiniLM-L6-v2[13], [14], transforms these text inputs..."

**🔴 Reviewer A Comment:**
> "Pemilihan encoder bersifat praktis tetapi kurang dikritisi... artikel tidak membahas keterbatasan representasional encoder ini..."
> *(The encoder selection is practical but lacks critical analysis...)*

**💡 Action:**
Defend your choice based on **local deployment** and **hardware constraints**.
*   **Add:** "We selected `all-MiniLM-L6-v2` to enable **fully local deployment** on constrained hardware (e.g., single consumer GPU), ensuring data privacy for government applications by avoiding external API dependencies. While larger models like E5-Large offer higher resolution, they incur significantly higher latency which is impractical for the target deployment environment."

---

## 3. METHODOLOGY: Formal Definitions (VOR/EVR)

**Your Text (Page 4, Section A):**
> "Once the system reads the queries, the first retrieval phase is executed using Vector-Only Retrieval (VOR)..."

**🔴 Reviewer A Comment:**
> "Istilah EVR–VOR Vector Retrieval belum didefinisikan secara formal... tidak memberikan definisi matematis atau algoritmik yang jelas."
> *(The terms EVR-VOR are not formally defined...)*

**💡 Action:**
Replace descriptive text with formal notation:
*   **VOR:** $f_{VOR}(q) = \text{top-}k(\text{cos\_sim}(E(q), D), k=12)$
*   **EVR:** $f_{EVR}(q) = \text{top-}k(\text{cos\_sim}(E(q'), D), k=24)$ where $q'$ is the expanded query.

---

## 4. METHODOLOGY: Multi-Agent Debate Protocol

**Your Text (Page 4, Section B):**
> "The MAF-RAG debating process involves several independent agents engaging in multiple rounds of debate..."

**🔴 Reviewer A Comment:**
> "Mekanisme multi-agent debating masih bersifat deskriptif... tidak menjelaskan secara rinci peran masing-masing agen..."
> *(The multi-agent debating mechanism is still descriptive...)*

**💡 Action:**
Add **Algorithm 1: MAF-RAG Debate Protocol**.
*   **Step 1 (Draft):** Agents $A_1...A_n$ generate initial answers $R_1...R_n$ based on documents $D_1...D_n$.
*   **Step 2 (Aggregate):** Aggregator $S$ synthesizes $R_{1...n}$ into consensus $C$.
*   **Step 3 (Refine):** Agents update $R_i$ based on $C$. Repeat until convergence or max rounds.

---

## 5. METHODOLOGY: F1-Score Definition

**Your Text (Page 6, Section D):**
> "Retrieval performance is provided from a measurement of Precision, Recall, and F1-Score."

**🔴 Reviewer A Comment:**
> "Definisi dan kriteria evaluasi F1-score belum dijelaskan rinci..."
> *(Definition and evaluation criteria for F1-score have not been explained in detail...)*

**💡 Action:**
Define F1 explicitly based on **Chunk ID Overlap** (verified in `retrieval_test_madam.py`).
*   **Add:** "F1-score is calculated based on the **exact match of retrieved Chunk IDs** against the ground truth set. A retrieved chunk is considered a 'True Positive' only if its unique ID matches a chunk in the annotated ground truth list for that query."

---

## 6. METHODOLOGY: Baseline Details

**Your Text (Page 6, Section D):**
> "The evaluation methods used to determine the effectiveness of the proposed MAF-RAG systems consist of three experiment configurations..."

**🔴 Reviewer B Comment:**
> "Baseline sistem perlu dijelaskan lebih rinci..."
> *(The baseline system needs to be explained in more detail...)*

**💡 Action:**
Clarify the exact pipeline differences.
*   **Add Table:**
    | Configuration | Dataset | Pipeline Sequence |
    | :--- | :--- | :--- |
    | **Legacy Baseline** | Old (Noisy) | VOR $\to$ EVR $\to$ Internet |
    | **Enhanced Baseline** | New (Clean) | VOR $\to$ EVR $\to$ Internet |
    | **MAF-RAG** | New (Clean) | VOR $\to$ EVR $\to$ **Debate** $\to$ Internet |
*   **Note:** Explicitly state that the Baselines **do not** include the Debate phase.

---

## 7. RESULTS: Statistical Significance

**Your Text (Page 8, Table III):**
> "The MAF-RAG system achieved a mean F1-score of 0.559..."

**🔴 Reviewer B Comment:**
> "Tidak ada uji signifikansi statistik atas peningkatan performa..."
> *(There is no statistical significance test on the performance improvement...)*

**💡 Action:**
*   **Add:** "A paired t-test confirms this improvement is statistically significant ($p < 0.05$)." (Or mention Standard Deviation if t-test is not possible).

---

## 8. RESULTS: Error Analysis

**Your Text (Page 8, Table III):**
> "Failed Retrieval ... 11(22.0%)"

**🔴 Reviewer B Comment:**
> "Analisis error dan kegagalan sistem belum dieksplorasi mendalam..."
> *(Error analysis and system failure have not been explored deeply...)*

**💡 Action:**
*   **Add:** "The remaining 22% of failures primarily stemmed from **Procedural** queries (7/11) where the system struggled to synthesize steps from multiple conflicting regulations. This indicates that while Debate improves reasoning, extremely complex multi-document synthesis remains a challenge."

---

## 9. RESULTS: Latency Trade-off

**Your Text (Page 8):**
> "Although in Avg Time metrics, the MAF-RAG is 4.9% slower..."

**🔴 Reviewer B Comment:**
> "Trade-off latensi belum dianalisis secara operasional..."
> *(Latency trade-off has not been analyzed operationally...)*

**💡 Action:**
*   **Add:** "In a government advisory context, the cost of **misinformation** (hallucination) far outweighs the cost of a 0.5s delay. Users prefer a correct answer in 11s over a wrong answer in 10s."

---

## 10. DISCUSSION: Modularity & Generalization

**Your Text (Page 10):**
> "...making it a suitable solution for a RAG-based chatbot system that faces dataset challenges."

**🔴 Reviewer A & B Comment:**
> "Ukuran dataset relatif kecil untuk klaim generalisasi..." / "Generalisasi lintas domain belum dibahas."
> *(Dataset size is relatively small... / Cross-domain generalization has not been discussed.)*

**💡 Action:**
Address the "small dataset" critique by highlighting the **modular architecture**.
*   **Add:** "While tested on a specific government dataset, the MAF-RAG architecture is designed to be **domain-agnostic**. The modular vector store implementation allows for rapid adaptation to new domains (e.g., medical or legal) by simply re-configuring the target database table and re-indexing the documents, without requiring architectural changes to the escalation or debate logic."

---

## 11. CONCLUSION: Future Work

**Your Text (Page 10):**
> "This contribution to the understanding of practicality and efficiency..."

**🔴 Reviewer B Comment:**
> "Arah penelitian lanjutan dapat dipertegas."
> *(Future research directions can be emphasized.)*

**💡 Action:**
*   **Add:** "Future work will focus on **Adaptive Agent Selection** (dynamically choosing agent personas based on query type) and **Dynamic Latency Control** (allowing users to toggle between 'Fast Mode' and 'Deep Mode')."

---

## 12. GENERAL: Figures & Tables

**🔴 Reviewer A & B Comment:**
> "Apakah penggunaan angka dan tabel cukup berkualitas dan jelas terbaca? Tidak"
> *(Are figures and tables of sufficient quality and clearly legible? No)*

**💡 Action:**
*   **Check:** Ensure all figures are high-resolution (300 DPI) and text in tables is legible. Re-generate plots if necessary.
