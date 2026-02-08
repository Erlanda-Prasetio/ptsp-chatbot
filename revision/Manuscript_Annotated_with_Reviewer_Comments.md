# Manuscript with Reviewer Annotations

This document places the reviewer comments directly next to the relevant sections of your manuscript text. Use this as a guide to rewrite specific paragraphs.

---

## 1. INTRODUCTION: Conceptual Contribution

**Your Text (Page 2):**
> "To address these issues, this study proposed a Multi-Agent Fallback for Retrieval-Augmented Generation (MAF-RAG), which is a result of combining two of the previous approaches: a hybrid RAG-based chatbot system that engages in multi-agent debate from MADAM, and with a confidence filtering mechanism from MAIN-RAG..."

**🔴 Reviewer A Comment:**
> "Kontribusi konseptual MAF-RAG perlu dipertegas secara structural... batasan konseptual antara MAF-RAG dan pendekatan RAG yang telah ada... belum dijelaskan secara eksplisit."
> *(The conceptual contribution needs to be structurally emphasized... the conceptual boundary between MAF-RAG and existing approaches is not explicitly explained.)*

**💡 Action:**
Stop saying you are "combining" them. It sounds like you just glued two things together. Instead, emphasize the **novelty of the architecture**:
*   "Unlike MAIN-RAG which filters statically, or MADAM which debates every query, MAF-RAG introduces a **hierarchical escalation protocol** that dynamically switches strategies based on confidence, optimizing the trade-off between cost and accuracy."

---

## 2. METHODOLOGY: Encoder Selection

**Your Text (Page 3):**
> "An encoder model, sentence-transformers/all-MiniLM-L6-v2[13], [14], transforms these text inputs into fixed-size 384-dimensional embeddings..."

**🔴 Reviewer A Comment:**
> "Pemilihan encoder bersifat praktis tetapi kurang dikritisi... artikel tidak membahas keterbatasan representasional encoder ini..."
> *(The encoder selection is practical but lacks critical analysis... the article does not discuss the representational limitations of this encoder...)*

**💡 Action:**
You are using a small, older model. You need to defend why.
*   **Add:** "We selected `all-MiniLM-L6-v2` to enable **fully local deployment** on constrained hardware (e.g., single consumer GPU), ensuring data privacy for government applications by avoiding external API dependencies. While larger models like E5-Large offer higher resolution, they incur significantly higher latency."

---

## 3. METHODOLOGY: Formal Definitions (VOR/EVR)

**Your Text (Page 4, Section A):**
> "Once the system reads the queries, the first retrieval phase is executed using Vector-Only Retrieval (VOR). In this phase, the system searches through the datasets and retrieves the top 5 relevant documents... If the retrieval confidence rating falls below 0.6, the system advances to the second phase... utilizing Enhanced Vector Retrieval (EVR). EVR implements a re-ranking mechanism..."

**🔴 Reviewer A Comment:**
> "Istilah EVR–VOR Vector Retrieval belum didefinisikan secara formal... tidak memberikan definisi matematis atau algoritmik yang jelas."
> *(The terms EVR-VOR are not formally defined... no clear mathematical or algorithmic definition is provided.)*

**💡 Action:**
Replace the descriptive text with formal notation:
*   **VOR:** $f_{VOR}(q) = \text{top-}k(\text{cos\_sim}(E(q), D), k=12)$
*   **EVR:** $f_{EVR}(q) = \text{top-}k(\text{cos\_sim}(E(q'), D), k=24)$ where $q'$ is the expanded query.

---

## 4. METHODOLOGY: Multi-Agent Debate

**Your Text (Page 4, Section B):**
> "The MAF-RAG debating process involves several independent agents engaging in multiple rounds of debate... Depending on the previously retrieved documents, the debate operates for a maximum of three rounds..."

**🔴 Reviewer A Comment:**
> "Mekanisme multi-agent debating masih bersifat deskriptif... tidak menjelaskan secara rinci peran masing-masing agen..."
> *(The multi-agent debating mechanism is still descriptive... it does not explain in detail the role of each agent...)*

**💡 Action:**
The text is too "story-like".
*   **Add:** **Algorithm 1: MAF-RAG Debate Protocol**. List the steps clearly (1. Generate, 2. Aggregate, 3. Refine).
*   **Clarify Roles:** Explicitly state that Agent $i$ is responsible for defending Document $i$.

---

## 5. METHODOLOGY: Baseline Details

**Your Text (Page 6, Section D):**
> "The evaluation methods used to determine the effectiveness of the proposed MAF-RAG systems consist of three experiment configurations: a baseline RAG-based chatbot with the Legacy Dataset, a Baseline RAG-based chatbot with the Enhanced Dataset, and MAF-RAG."

**🔴 Reviewer B Comment:**
> "Baseline sistem perlu dijelaskan lebih rinci... spesifikasi arsitektur... belum diuraikan secara lengkap."
> *(The baseline system needs to be explained in more detail... architecture specifications... have not been fully outlined.)*

**💡 Action:**
It's unclear if the "Baseline" uses the same retrieval logic as MAF-RAG (just without debate) or if it's a totally different code.
*   **Add:** A table comparing the configurations (e.g., "Baseline = VOR only", "MAF-RAG = VOR + EVR + Debate").

---

## 6. RESULTS: Statistical Significance

**Your Text (Page 8, Table III):**
> "The MAF-RAG system achieved a mean F1-score of 0.559, a 19.1% improvement over the Enhanced Dataset baseline system..."

**🔴 Reviewer B Comment:**
> "Tidak ada uji signifikansi statistik atas peningkatan performa..."
> *(There is no statistical significance test on the performance improvement...)*

**💡 Action:**
Is 19% real or luck?
*   **Add:** "A paired t-test confirms this improvement is statistically significant ($p < 0.05$)." (If you can calculate it). If not, at least mention the Standard Deviation to show consistency.

---

## 7. RESULTS: Latency Trade-off

**Your Text (Page 8):**
> "Although in Avg Time metrics, the MAF-RAG is 4.9% slower than the Enhanced Baseline... But this trade-off is minimal compared to the advantages..."

**🔴 Reviewer B Comment:**
> "Trade-off latensi belum dianalisis secara operasional..."
> *(Latency trade-off has not been analyzed operationally...)*

**💡 Action:**
"Minimal" is an opinion. Give an operational reason.
*   **Add:** "In a government advisory context, the cost of **misinformation** (hallucination) far outweighs the cost of a 0.5s delay. Users prefer a correct answer in 11s over a wrong answer in 10s."

---

## 8. RESULTS: Error Analysis

**Your Text (Page 8, Table III):**
> "Failed Retrieval ... 11(22.0%)"

**🔴 Reviewer B Comment:**
> "Analisis error dan kegagalan sistem belum dieksplorasi mendalam... artikel tidak membahas jenis pertanyaan atau kondisi retrieval apa yang masih gagal..."
> *(Error analysis and system failure have not been explored deeply... the article does not discuss what types of questions or retrieval conditions still fail...)*

**💡 Action:**
You list the number 11, but not *what* they are.
*   **Add:** A paragraph analyzing the failures. "The remaining 22% of failures primarily stemmed from **Procedural** queries (7/11) where the system struggled to synthesize steps from multiple conflicting regulations."

---

## 9. CONCLUSION: Generalization Claim

**Your Text (Page 10):**
> "...making it a suitable solution for a RAG-based chatbot system that faces dataset challenges."

**🔴 Reviewer A Comment:**
> "Ukuran dataset relatif kecil untuk klaim generalisasi..."
> *(Dataset size is relatively small for generalization claims...)*

**💡 Action:**
You only tested 150 queries. Don't claim it solves *all* RAG challenges.
*   **Change to:** "...demonstrates MAF-RAG's potential in **domain-specific** government applications."
