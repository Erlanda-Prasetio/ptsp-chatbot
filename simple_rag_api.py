"""
Simple FastAPI server for Central Java RAG Chatbot
Uses the improved local ask.py directly
"""
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import time

# Add the src directory to path
sys.path.append('src')

# Import our improved local system
from vector_store import store
from embed import embed_texts
from ask import build_context, query_llm
from config import VECTOR_BACKEND

app = FastAPI(title="Central Java RAG API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global flag to track initialization
rag_initialized = False

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    message: str
    sources: List[Dict[str, Any]]
    total_sources: int
    enhanced_features: Dict[str, bool]

def initialize_rag():
    """Initialize the RAG system"""
    global rag_initialized
    try:
        print("🚀 Initializing Central Java RAG system...")
        print(f"📊 Backend: {VECTOR_BACKEND}")
        
        if VECTOR_BACKEND != 'local':
            raise RuntimeError(f"Expected local backend, got {VECTOR_BACKEND}")
        
        # Load the vector store
        store.load()
        if store.embeddings is None:
            raise RuntimeError("Vector store is empty. Please run ingest first.")
        
        print(f"✅ RAG system initialized with {len(store.texts)} chunks!")
        rag_initialized = True
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        rag_initialized = False
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    initialize_rag()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Central Java RAG API is running",
        "status": "healthy" if rag_initialized else "unhealthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    if not rag_initialized:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        count = len(store.texts) if store.texts else 0
        return {
            "status": "healthy",
            "database_chunks": count,
            "backend": VECTOR_BACKEND,
            "features": {
                "query_expansion": True,
                "enhanced_prompting": True,
                "reranking": False
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for RAG queries"""
    if not rag_initialized:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    # Get the latest user message
    user_message = None
    for message in reversed(request.messages):
        if message.role == "user":
            user_message = message.content
            break
    
    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")
    
    try:
        start_time = time.time()
        
        # Embed the query
        q_emb = embed_texts([user_message.strip()])[0]
        
        # Search for similar chunks
        hits = store.search(q_emb, k=8)
        
        if not hits:
            return ChatResponse(
                message="Maaf, saya tidak dapat menemukan informasi yang relevan untuk pertanyaan Anda.",
                sources=[],
                total_sources=0,
                enhanced_features={
                    "query_expansion": False,
                    "enhanced_prompting": True,
                    "reranking": False
                }
            )
        
        # Build context and query LLM
        context = build_context(hits)
        answer = query_llm(user_message, context)
        
        # Process sources for frontend display
        sources = []
        for i, hit in enumerate(hits[:5]):  # Show top 5 sources
            source_info = hit.get('meta', {})
            source_path = source_info.get('source', f'chunk_{i}')
            
            # Extract filename from path
            if '\\' in source_path:
                filename = source_path.split('\\')[-1]
            elif '/' in source_path:
                filename = source_path.split('/')[-1]
            else:
                filename = source_path
            
            sources.append({
                "filename": filename,
                "score": hit.get('score', 0),
                "content_preview": hit.get('text', '')[:200] + "...",
                "path": source_path
            })
        
        response_time = time.time() - start_time
        print(f"🔍 Query: {user_message} | Response time: {response_time:.2f}s")
        
        return ChatResponse(
            message=answer,
            sources=sources,
            total_sources=len(hits),
            enhanced_features={
                "query_expansion": True,
                "enhanced_prompting": True,
                "reranking": False
            }
        )
        
    except Exception as e:
        print(f"❌ RAG query error: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

@app.get("/suggestions")
async def get_suggestions():
    """Get suggested questions for Central Java data"""
    return {
        "suggestions": [
            "Kabupaten Kendal tenaga kerja",
            "persentase penduduk miskin",
            "Kabupaten Brebes penempatan 2023",
            "proyeksi investasi Jawa Tengah",
            "statistik Kabupaten Temanggung",
            "layanan PTSP perizinan",
            "data tenaga kerja Jawa Tengah",
            "data kemiskinan Jawa Tengah"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Central Java RAG API server...")
    print("📊 Access the API at: http://localhost:8001")
    print("📋 API docs at: http://localhost:8001/docs")
    print("🔗 Connect from Next.js at: http://localhost:3000")
    
    uvicorn.run(
        "simple_rag_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
