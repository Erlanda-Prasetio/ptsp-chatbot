"""Minimal FastAPI server strictly using local vector store (no Supabase import)"""
import sys, os, time
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Ensure only local backend
os.environ['VECTOR_BACKEND'] = 'local'

sys.path.append('src')
from enhanced_rag import EnhancedRAG  # uses local store

app = FastAPI(title="Mini Central Java RAG API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

rag = None

@app.on_event("startup")
async def _startup():
    global rag
    rag = EnhancedRAG()

@app.get("/health")
async def health():
    if not rag:
        raise HTTPException(status_code=503, detail="Not ready")
    stats = rag.get_stats()
    return {"status": "ok", **stats}

@app.post("/chat")
async def chat(req: ChatRequest):
    if not rag:
        raise HTTPException(status_code=503, detail="Not ready")
    # last user msg
    for m in reversed(req.messages):
        if m.role == 'user':
            question = m.content
            break
    else:
        raise HTTPException(status_code=400, detail="No user message")
    result = rag.ask(question)
    return {
        "message": result["answer"],
        "sources": result["sources"],
        "features": result["enhanced_features"],
        "time": result.get("response_time", 0)
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("mini_api:app", host="0.0.0.0", port=8010, reload=False)
