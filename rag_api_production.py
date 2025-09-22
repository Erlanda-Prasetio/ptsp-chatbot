"""
Production-optimized FastAPI server for Railway deployment
Loads models lazily to pass health checks faster
"""
import sys
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import asyncio
from threading import Lock

# Add the src directory to path
sys.path.append('src')

# Global variables
rag_system = None
initialization_lock = Lock()
initialization_complete = False

app = FastAPI(title="Central Java RAG API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    message: str
    sources: List[Dict[str, Any]]
    total_sources: int
    enhanced_features: Dict[str, Any]

def initialize_rag_system():
    """Initialize RAG system in background"""
    global rag_system, initialization_complete
    
    if rag_system is not None:
        return
        
    with initialization_lock:
        if rag_system is not None:
            return
            
        try:
            print("🚀 Initializing Hybrid RAG system...")
            from hybrid_rag import HybridRAGSystem
            rag_system = HybridRAGSystem()
            initialization_complete = True
            print("✅ Hybrid RAG system initialized successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize Hybrid RAG system: {e}")
            initialization_complete = False

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Central Java RAG API is running",
        "status": "healthy",
        "rag_initialized": initialization_complete,
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Basic health check - doesn't require RAG system"""
    return {
        "status": "healthy",
        "service": "ptsp-rag-api",
        "rag_system": "initializing" if not initialization_complete else "ready"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    """Chat endpoint with lazy initialization"""
    global rag_system
    
    # Initialize RAG system if not already done
    if rag_system is None:
        background_tasks.add_task(initialize_rag_system)
        # For first request, initialize synchronously
        initialize_rag_system()
    
    if not initialization_complete:
        raise HTTPException(
            status_code=503, 
            detail="RAG system is still initializing. Please try again in a moment."
        )
    
    try:
        # Get the last user message
        user_message = None
        for msg in reversed(request.messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Use hybrid RAG system
        result = rag_system.ask_with_fallback(user_message)
        
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
    """Get suggested questions"""
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

# Initialize RAG system on startup (background)
@app.on_event("startup")
async def startup_event():
    """Start RAG initialization in background"""
    import threading
    thread = threading.Thread(target=initialize_rag_system)
    thread.start()

if __name__ == "__main__":
    print("🚀 Starting Central Java RAG API server...")
    print("📊 Access the API at: http://localhost:8001")
    print("📋 API docs at: http://localhost:8001/docs")
    
    port = int(os.getenv("PORT", 8001))
    
    uvicorn.run(
        "rag_api_production:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )