"""
Lightweight RAG API for cloud deployment
This version initializes with minimal data and can be expanded later
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []


class HealthResponse(BaseModel):
    status: str
    message: str
    features: Dict[str, Any]


# Simple knowledge base for demonstration
SAMPLE_KNOWLEDGE = {
    "prosedur": "Untuk informasi prosedur PTSP, silakan hubungi kantor DPMPTSP Jawa Tengah.",
    "anggaran": "Informasi anggaran dapat dilihat di website resmi Pemerintah Jawa Tengah.",
    "pelayanan": "PTSP menyediakan berbagai layanan perizinan dan non-perizinan.",
    "izin": "Untuk mengurus izin, Anda dapat datang langsung ke kantor PTSP atau melalui online.",
}


class LightweightRAG:
    def __init__(self):
        self.knowledge_base = SAMPLE_KNOWLEDGE
        self.is_initialized = True
    
    def query(self, question: str) -> Dict[str, Any]:
        """Simple keyword-based search for demonstration"""
        question_lower = question.lower()
        
        # Find relevant information
        relevant_info = []
        for key, value in self.knowledge_base.items():
            if key in question_lower:
                relevant_info.append(value)
        
        if relevant_info:
            response = " ".join(relevant_info)
        else:
            response = """Terima kasih atas pertanyaan Anda tentang PTSP Jawa Tengah. 
            
Saat ini sistem sedang dalam mode terbatas. Untuk informasi lengkap, silakan:
1. Kunjungi website resmi DPMPTSP Jawa Tengah
2. Hubungi hotline PTSP
3. Datang langsung ke kantor PTSP

Maaf atas keterbatasan ini."""
        
        return {
            "response": response,
            "sources": [{"type": "knowledge_base", "relevance": "medium"}]
        }


# Global RAG instance
rag_system = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup the RAG system"""
    global rag_system
    
    print("🚀 Initializing Lightweight PTSP RAG System...")
    
    try:
        rag_system = LightweightRAG()
        print("✅ RAG system initialized successfully!")
        print("📊 Running in lightweight mode for cloud deployment")
        
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        rag_system = None
    
    yield
    
    print("🔄 Shutting down RAG system...")


# FastAPI app
app = FastAPI(
    title="PTSP Jawa Tengah Chatbot API",
    description="Lightweight chatbot API for PTSP (Pelayanan Terpadu Satu Pintu) Jawa Tengah",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "PTSP Jawa Tengah Chatbot API",
        "status": "running",
        "mode": "lightweight"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    return HealthResponse(
        status="healthy",
        message="Lightweight RAG system running",
        features={
            "mode": "lightweight",
            "deployment": "cloud",
            "knowledge_base": "basic"
        }
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        # Process the query
        result = rag_system.query(request.message)
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "system": "PTSP Chatbot",
        "mode": "lightweight",
        "rag_initialized": rag_system is not None,
        "deployment": "cloud"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting PTSP Chatbot API on port {port}")
    print("📋 Running in lightweight mode for cloud deployment")
    
    uvicorn.run(
        "rag_api_light:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
