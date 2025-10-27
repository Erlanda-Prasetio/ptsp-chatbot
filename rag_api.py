"""
FastAPI server for Central Java RAG Chatbot
This serves as the backend API for the Next.js frontend
"""
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Dict, Any, Union
import uvicorn

# Add the src directory to path
sys.path.append('src')

from hybrid_rag import HybridRAGSystem
from config import VECTOR_BACKEND

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup the Hybrid RAG system"""
    global rag_system
    try:
        print("🚀 Initializing Hybrid RAG system with Internet Search fallback...")
        rag_system = HybridRAGSystem()
        print("✅ Hybrid RAG system initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize Hybrid RAG system: {e}")
        rag_system = None
    
    yield
    
    # Cleanup (if needed)
    print("🔄 Shutting down RAG system...")

app = FastAPI(title="Central Java RAG API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # During development allow all origins so the Flutter web/dev server or any local client
    # can reach this API. In production, restrict this to your frontend origins and
    # set `allow_credentials=True` only when using cookies/auth that require it.
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the enhanced RAG system
rag_system = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    message: str
    sources: List[Dict[str, Any]]
    total_sources: int
    enhanced_features: Dict[str, Any]  # Changed to Any to handle complex nested structures

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Central Java RAG API is running",
        "status": "healthy" if rag_system else "unhealthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Try to get chunk count, handle both local and Supabase backends
        count = 0
        if hasattr(rag_system, 'rag_system') and hasattr(rag_system.rag_system, 'store'):
            if hasattr(rag_system.rag_system.store, 'texts'):
                count = len(rag_system.rag_system.store.texts)
            else:
                # For Supabase, we don't have a direct count, so use a placeholder
                count = "Connected to Supabase"
        
        return {
            "status": "healthy",
            "database_chunks": count,
            "backend": "supabase" if VECTOR_BACKEND == "supabase" else "local",
            "smart_features": True,
            "hybrid_search": True,
            "internet_fallback": True,
            "features": {
                "domain_detection": True,
                "query_expansion": True,
                "enhanced_prompting": True,
                "out_of_scope_handling": True,
                "progressive_timeout": "20s (5s vector + 10s enhanced + 5s internet)",
                "quality_assessment": True,
                "internet_engines": ["duckduckgo", "serper"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for RAG queries with improved processing time"""
    if not rag_system:
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
        print(f"🔍 Processing query: {user_message[:100]}...")
        
        # Get hybrid RAG response with progressive fallback
        result = rag_system.ask_with_fallback(user_message.strip())
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Get timing info
        enhanced_features = result.get("enhanced_features", {})
        response_time = enhanced_features.get("response_time", "unknown")
        search_method = enhanced_features.get("search_method", "unknown")
        
        print(f"✅ Query processed using {search_method} in {response_time}")
        
        return ChatResponse(
            message=result["answer"],
            sources=result["sources"],
            total_sources=result["total_sources"],
            enhanced_features=result["enhanced_features"]
        )
        
    except Exception as e:
        print(f"❌ RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

@app.post("/retrieve")
async def retrieve(request: ChatRequest):
    """
    Retrieve chunks only without LLM generation (for retrieval testing)
    Returns sources and search method used (vector_only, enhanced_vector, or internet_fallback)
    """
    if not rag_system:
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
        print(f"🔍 Retrieving chunks for: {user_message[:100]}...")
        
        # Get retrieval results with fallback phases
        result = rag_system.ask_with_fallback(user_message.strip())
        
        sources = result.get("sources", [])
        search_method = result.get("enhanced_features", {}).get("search_method", "unknown")
        
        # Format sources with proper structure
        formatted_sources = []
        for i, chunk in enumerate(sources, 1):
            # Handle Supabase format
            if isinstance(chunk, dict):
                chunk_id = chunk.get("id") or chunk.get("chunk_id") or f"chunk_{i}"
                text = chunk.get("content") or chunk.get("text", "")
                score = chunk.get("similarity") or chunk.get("score", 0)
                metadata = chunk.get("metadata", {})
            else:
                # If chunk is a tuple or other format
                chunk_id = f"chunk_{i}"
                text = str(chunk)
                score = 0
                metadata = {}
            
            formatted_sources.append({
                "rank": i,
                "chunk_id": chunk_id,
                "text": text,
                "score": float(score) if score else 0.0,
                "metadata": metadata
            })
        
        print(f"✅ Retrieved {len(formatted_sources)} chunks using {search_method}")
        
        return {
            "sources": formatted_sources,
            "search_method": search_method,
            "total_sources": len(formatted_sources),
            "query": user_message.strip()
        }
        
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")

@app.get("/suggestions")
async def get_suggestions():
    """Get suggested questions for Central Java DPMPTSP data"""
    return {
        "suggestions": [
            "Apa itu DPMPTSP Jawa Tengah?",
            "Bagaimana cara mengurus izin usaha?",
            "Syarat investasi di Jawa Tengah",
            "Prosedur perizinan online",
            "Layanan pelayanan terpadu satu pintu",
            "Dokumen yang diperlukan untuk izin",
            "Kontak DPMPTSP Jawa Tengah",
            "Biaya pengurusan izin usaha"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Central Java RAG API server...")
    print("📊 Access the API at: http://localhost:8001")
    print("📋 API docs at: http://localhost:8001/docs")
    print("🔗 Connect from Next.js at: http://localhost:3000")
    
    uvicorn.run(
        "rag_api:app",
        host="0.0.0.0",
        port=8001,  # Changed to 8001 to match frontend
        reload=True,
        log_level="info"
    )
