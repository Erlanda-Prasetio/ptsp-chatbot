from typing import List
from config import CHUNK_SIZE, CHUNK_OVERLAP

# Approx token estimate ~ 4 chars per token; we operate on characters for simplicity.

def chunk_text(text: str) -> List[str]:
    cleaned = text.replace('\r', '').strip()
    if not cleaned:
        return []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    chunks = []
    start = 0
    while start < len(cleaned):
        end = start + CHUNK_SIZE
        chunk = cleaned[start:end]
        chunks.append(chunk)
        start += step
    return chunks
