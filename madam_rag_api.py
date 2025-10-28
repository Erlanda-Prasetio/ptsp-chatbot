"""FastAPI server exposing the MADAM-enhanced RAG pipeline."""
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add the src directory to path for downstream imports
sys.path.append('src')

from config import VECTOR_BACKEND  # type: ignore
from madam_hybrid_system import MadamHybridRAGSystem

rag_system: Optional[MadamHybridRAGSystem] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and tear down the MADAM Hybrid RAG system."""
    global rag_system
    try:
        print("🚀 Initializing Madam Hybrid RAG system with multi-agent debate...")
        rag_system = MadamHybridRAGSystem()
        print("✅ Madam Hybrid RAG system initialized successfully!")
    except Exception as exc:
        print(f"❌ Failed to initialize Madam Hybrid RAG system: {exc}")
        rag_system = None
    try:
        yield
    finally:
        print("🔄 Shutting down MADAM RAG system...")


app = FastAPI(title="Central Java MADAM RAG API", version="1.0.0", lifespan=lifespan)

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


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "message": "Central Java MADAM RAG API is running",
        "status": "healthy" if rag_system else "unhealthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    try:
        count: Any = 0
        if hasattr(rag_system, 'rag_system') and hasattr(rag_system.rag_system, 'store'):
            store = rag_system.rag_system.store
            if hasattr(store, 'texts'):
                count = len(store.texts)
            else:
                count = "Connected to Supabase"

        return {
            "status": "healthy",
            "database_chunks": count,
            "backend": "supabase" if VECTOR_BACKEND == "supabase" else "local",
            "smart_features": True,
            "hybrid_search": True,
            "madam_debate": getattr(rag_system, 'debate_available', False),
            "internet_fallback": True,
            "features": {
                "domain_detection": True,
                "query_expansion": True,
                "madam_multi_agent": True,
                "out_of_scope_handling": True,
                "progressive_timeout": "30s (5s vector + 10s enhanced + 8s debate + 7s internet)",
                "quality_assessment": True,
                "internet_engines": ["duckduckgo", "serper"],
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Health check failed: {exc}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    user_message = next((m.content for m in reversed(request.messages) if m.role == "user"), None)
    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    try:
        print(f"🔍 Processing MADAM query: {user_message[:100]}...")
        result = rag_system.ask_with_fallback(user_message.strip())
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        features = result.get("enhanced_features", {})
        response_time = features.get("response_time", "unknown")
        method = features.get("search_method", "unknown")
        print(f"✅ MADAM query processed using {method} in {response_time}")

        return ChatResponse(
            message=result.get("answer", ""),
            sources=result.get("sources", []),
            total_sources=result.get("total_sources", len(result.get("sources", []))),
            enhanced_features=features,
        )
    except HTTPException:
        raise
    except Exception as exc:
        print(f"❌ MADAM RAG query failed: {exc}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {exc}")


@app.post("/retrieve")
async def retrieve(request: ChatRequest) -> Dict[str, Any]:
    if not rag_system:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    user_message = next((m.content for m in reversed(request.messages) if m.role == "user"), None)
    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    try:
        print(f"🔍 Retrieving MADAM chunks for: {user_message[:100]}...")
        result = rag_system.ask_with_fallback(user_message.strip())
        sources = result.get("sources", [])
        method = result.get("enhanced_features", {}).get("search_method", "unknown")

        formatted_sources: List[Dict[str, Any]] = []
        for idx, chunk in enumerate(sources, 1):
            if isinstance(chunk, dict):
                chunk_id = chunk.get("chunk_id") or chunk.get("id") or f"chunk_{idx}"
                text = chunk.get("text") or chunk.get("content") or chunk.get("content_preview", "")
                score = chunk.get("score") or chunk.get("similarity") or 0
                metadata = chunk.get("metadata", {})
            else:
                chunk_id = f"chunk_{idx}"
                text = str(chunk)
                score = 0
                metadata = {}

            formatted_sources.append(
                {
                    "rank": idx,
                    "chunk_id": chunk_id,
                    "text": text,
                    "score": float(score) if score else 0.0,
                    "metadata": metadata,
                }
            )

        print(f"✅ Retrieved {len(formatted_sources)} chunks via {method}")
        return {
            "sources": formatted_sources,
            "search_method": method,
            "total_sources": len(formatted_sources),
            "query": user_message.strip(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"❌ MADAM retrieval failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {exc}")


@app.get("/suggestions")
async def get_suggestions() -> Dict[str, Any]:
    return {
        "suggestions": [
            "Apa itu DPMPTSP Jawa Tengah?",
            "Bagaimana cara mengurus izin usaha?",
            "Syarat investasi di Jawa Tengah",
            "Prosedur perizinan online",
            "Layanan pelayanan terpadu satu pintu",
            "Dokumen yang diperlukan untuk izin",
            "Kontak DPMPTSP Jawa Tengah",
            "Biaya pengurusan izin usaha",
        ]
    }


if __name__ == "__main__":
    print("🚀 Starting Central Java MADAM RAG API server...")
    print("📊 Access the API at: http://localhost:8001")
    print("📋 API docs at: http://localhost:8001/docs")
    print("🔗 Connect from frontend at: http://localhost:3000")

    uvicorn.run(
        "madam_rag_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
