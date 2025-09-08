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

from smart_enhanced_rag import SmartEnhancedRAG
from config import VECTOR_BACKEND

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup the RAG system"""
    global rag_system
    try:
        print(" Initializing Smart Enhanced Central Java RAG system...")
        rag_system = SmartEnhancedRAG()
        print(" Smart Enhanced RAG system initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        rag_system = None
    
    yield
    
    # Cleanup (if needed)
    print("🔄 Shutting down RAG system...")

app = FastAPI(title="Central Java RAG API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
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
    enhanced_features: Dict[str, Union[str, bool, int, float]]

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
        if hasattr(rag_system, 'store'):
            if hasattr(rag_system.store, 'texts'):
                count = len(rag_system.store.texts)
            else:
                # For Supabase, we don't have a direct count, so use a placeholder
                count = "Connected to Supabase"
        
        return {
            "status": "healthy",
            "database_chunks": count,
            "backend": "supabase" if VECTOR_BACKEND == "supabase" else "local",
            "smart_features": True,
            "features": {
                "domain_detection": True,
                "query_expansion": True,
                "enhanced_prompting": True,
                "out_of_scope_handling": True
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
        
        # Get enhanced RAG response with timeout protection
        result = rag_system.ask(user_message.strip())
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        print(f"✅ Query processed successfully in {result.get('enhanced_features', {}).get('response_time', 'unknown')} seconds")
        
        return ChatResponse(
            message=result["answer"],
            sources=result["sources"],
            total_sources=result["total_sources"],
            enhanced_features=result["enhanced_features"]
        )
        
    except Exception as e:
        print(f"❌ RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

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
