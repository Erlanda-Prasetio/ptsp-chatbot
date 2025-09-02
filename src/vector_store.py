import json
import os
import numpy as np
from typing import List, Dict, Tuple

from config import STORE_PATH, DOCS_INDEX_PATH

class VectorStore:
    def __init__(self):
        self.embeddings = None  # shape (N, D)
        self.texts: List[str] = []
        self.meta: List[Dict] = []

    def add(self, embeddings: List[List[float]], chunks: List[str], metas: List[Dict]):
        arr = np.array(embeddings, dtype=np.float32)
        if self.embeddings is None:
            self.embeddings = arr
        else:
            self.embeddings = np.vstack([self.embeddings, arr])
        self.texts.extend(chunks)
        self.meta.extend(metas)

    def save(self):
        if self.embeddings is None:
            return
        os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
        np.save(STORE_PATH, self.embeddings)
        with open(DOCS_INDEX_PATH, 'w', encoding='utf-8') as f:
            json.dump({'texts': self.texts, 'meta': self.meta}, f, ensure_ascii=False, indent=2)

    def load(self):
        if os.path.exists(STORE_PATH):
            self.embeddings = np.load(STORE_PATH)
        if os.path.exists(DOCS_INDEX_PATH):
            with open(DOCS_INDEX_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.texts = data['texts']
                self.meta = data['meta']

    def search(self, query_emb: List[float], k: int = 6):
        if self.embeddings is None or len(self.texts) == 0:
            return []
        q = np.array(query_emb, dtype=np.float32)
        # cosine similarity
        denom = (np.linalg.norm(self.embeddings, axis=1) * (np.linalg.norm(q) + 1e-9))
        sims = (self.embeddings @ q) / (denom + 1e-9)
        idxs = np.argsort(-sims)[:k]
        results = []
        for i in idxs:
            results.append({'score': float(sims[i]), 'text': self.texts[i], 'meta': self.meta[i]})
        return results

store = VectorStore()
