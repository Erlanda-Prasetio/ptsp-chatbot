from typing import List, Dict

# Placeholder for future re-ranking integration (e.g., sentence-transformers cross-encoder)
# For now this just passes through.

def rerank(query: str, hits: List[Dict]) -> List[Dict]:
    return hits
