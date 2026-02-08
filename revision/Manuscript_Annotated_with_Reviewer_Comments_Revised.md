# Manuscript with Reviewer Annotations (Revised)

This document places the reviewer comments directly next to the relevant sections of your manuscript text. Use this as a guide to rewrite specific paragraphs.

---

## 1. INTRODUCTION: Conceptual Contribution

**Your Text (Page 2):**
> "To address these issues, this study proposed a Multi-Agent Fallback for Retrieval-Augmented Generation (MAF-RAG), which is a result of combining two of the previous approaches..."

**🔴 Reviewer A Comment:**
> "Kontribusi konseptual MAF-RAG perlu dipertegas secara structural..."
> *(The conceptual contribution needs to be structurally emphasized...)*

**💡 Action:**
Emphasize the **novelty of the architecture**.
*   **Rewrite:** "Unlike MAIN-RAG which filters statically, or MADAM which debates every query, MAF-RAG introduces a **hierarchical escalation protocol** that dynamically switches strategies based on confidence. It uniquely positions the expensive Multi-Agent Debate phase as a **tertiary fallback**—triggered only when both Vector-Only Retrieval (VOR) and Enhanced Vector Retrieval (EVR) fail, but before resorting to external Internet Search."

---

## 2. METHODOLOGY: Encoder Selection & Hardware Constraints

**Your Text (Page 3):**
> "An encoder model, sentence-transformers/all-MiniLM-L6-v2[13], [14], transforms these text inputs..."

**🔴 Reviewer A Comment:**
> "Pemilihan encoder bersifat praktis tetapi kurang dikritisi..."
> *(The encoder selection is practical but lacks critical analysis...)*

**💡 Action:**
Defend your choice based on **local deployment** and **hardware constraints**.
*   **Add:** "We selected `all-MiniLM-L6-v2` to enable **fully local deployment** on constrained hardware (e.g., single consumer GPU), ensuring data privacy for government applications by avoiding external API dependencies. While larger models like E5-Large offer higher resolution, they incur significantly higher latency which is impractical for the target deployment environment."

---

## 3. METHODOLOGY: Formal Definitions (VOR/EVR)

**Your Text (Page 4, Section A):**
> "Once the system reads the queries, the first retrieval phase is executed using Vector-Only Retrieval (VOR)..."

**🔴 Reviewer A Comment:**
> "Istilah EVR–VOR Vector Retrieval belum didefinisikan secara formal..."
> *(The terms EVR-VOR are not formally defined...)*

**💡 Action:**
Replace descriptive text with formal notation:
*   **VOR:** $f_{VOR}(q) = \text{top-}k(\text{cos\_sim}(E(q), D), k=12)$
*   **EVR:** $f_{EVR}(q) = \text{top-}k(\text{cos\_sim}(E(q'), D), k=24)$ where $q'$ is the expanded query.

---

## 4. METHODOLOGY: Baseline Details

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

## 5. DISCUSSION: Modularity & Generalization

**Your Text (Page 10):**
> "...making it a suitable solution for a RAG-based chatbot system that faces dataset challenges."

**🔴 Reviewer A Comment:**
> "Ukuran dataset relatif kecil untuk klaim generalisasi..."
> *(Dataset size is relatively small for generalization claims...)*

**💡 Action:**
Address the "small dataset" critique by highlighting the **modular architecture**.
*   **Add:** "While tested on a specific government dataset, the MAF-RAG architecture is designed to be **domain-agnostic**. The modular vector store implementation allows for rapid adaptation to new domains by simply re-configuring the target database table and re-indexing the documents, without requiring architectural changes to the escalation or debate logic."

---

## 6. RESULTS: Error Analysis

**Your Text (Page 8, Table III):**
> "Failed Retrieval ... 11(22.0%)"

**🔴 Reviewer B Comment:**
> "Analisis error dan kegagalan sistem belum dieksplorasi mendalam..."
> *(Error analysis and system failure have not been explored deeply...)*

**💡 Action:**
*   **Add:** "The remaining 22% of failures primarily stemmed from **Procedural** queries (7/11) where the system struggled to synthesize steps from multiple conflicting regulations. This indicates that while Debate improves reasoning, extremely complex multi-document synthesis remains a challenge."
