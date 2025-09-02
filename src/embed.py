import os
import requests
from typing import List
from config import OPENROUTER_API_KEY, EMB_MODEL

# Check if we should use local embeddings
USE_LOCAL_EMBEDDINGS = os.getenv("USE_LOCAL_EMBEDDINGS", "true").lower() == "true"

if USE_LOCAL_EMBEDDINGS:
    from sentence_transformers import SentenceTransformer
    import torch
    
    # Initialize the model
    _model = None
    
    def get_model():
        global _model
        if _model is None:
            model_name = EMB_MODEL if EMB_MODEL.startswith("sentence-transformers/") else "sentence-transformers/all-MiniLM-L6-v2"
            model_name = model_name.replace("sentence-transformers/", "")
            
            # Initialize model with CUDA if available
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"🔥 Loading embedding model on: {device}")
            
            _model = SentenceTransformer(model_name, device=device)
            
            if torch.cuda.is_available():
                print(f"🚀 GPU Model loaded: {model_name}")
                print(f"📊 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            else:
                print(f"💻 CPU Model loaded: {model_name}")
                
        return _model

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "http://localhost",
    "X-Title": "ptspRag"
}

EMBED_URL = "https://openrouter.ai/api/v1/embeddings"

def embed_texts(texts: List[str]) -> List[List[float]]:
    if USE_LOCAL_EMBEDDINGS:
        model = get_model()
        
        # For GPU, use larger batch sizes for efficiency
        if hasattr(model, 'device') and 'cuda' in str(model.device):
            # GPU batch processing
            batch_size = 64  # Adjust based on your GPU memory
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = model.encode(batch, batch_size=len(batch), show_progress_bar=False)
                all_embeddings.extend(batch_embeddings.tolist())
            
            return all_embeddings
        else:
            # CPU processing
            embeddings = model.encode(texts, show_progress_bar=len(texts) > 10)
            return embeddings.tolist()
    else:
        # OpenRouter API fallback
        r = requests.post(EMBED_URL, headers=HEADERS, json={"model": EMB_MODEL, "input": texts})
        r.raise_for_status()
        data = r.json()["data"]
        return [d["embedding"] for d in data]
