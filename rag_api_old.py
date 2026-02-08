#!/usr/bin/env python3
"""
FastAPI server for OLD dataset RAG
Routes all queries to the documents_old table only

Usage:
    python rag_api_old.py
    
Default port: 8002
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Dict, Any, Union
from dotenv import load_dotenv
import uvicorn

load_dotenv()

sys.path.append('src')
sys.path.append('.')

from src.hybrid_rag_old_v2 import HybridRAGSystem_OLD

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup the Hybrid RAG system for OLD dataset"""
    global rag_system
    try:
        print("[START] Initializing Hybrid RAG system for OLD dataset...")
        rag_system = HybridRAGSystem_OLD()
        print("[OK] Hybrid RAG system initialized successfully!")
    except Exception as e:
        print(f"[FAIL] Failed to initialize Hybrid RAG system: {e}")
        import traceback
        traceback.print_exc()
        rag_system = None
    
    yield
    
    # Cleanup (if needed)
    print(" Shutting down RAG system...")

app = FastAPI(
    title="OLD Dataset RAG API",
    description="RAG API for OLD dataset only (documents_old table)",
    version="1.0",
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

# Request/Response models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message] = []
    temperature: float = 0.7

class ChatResponse(BaseModel):
    message: str
    sources: List[Dict[str, Any]] = []
    total_sources: int = 0
    enhanced_features: Dict[str, Any] = {}

# Global RAG system
rag_system = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = "healthy" if rag_system else "error"
    return {
        "status": status,
        "dataset": "OLD",
        "table": "documents_old",
        "features": {
            "vector_search": True,
            "query_expansion": True,
            "enhanced_prompting": True,
            "internet_fallback": False,  # Only using vector search for OLD dataset
            "quality_assessment": True
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for OLD dataset RAG queries"""
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
        print(f"[SEARCH] Processing query (OLD): {user_message[:100]}...")
        
        # Get hybrid RAG response
        result = rag_system.ask_with_fallback(user_message.strip())
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Get timing info
        enhanced_features = result.get("enhanced_features", {})
        response_time = enhanced_features.get("response_time", "unknown")
        search_method = enhanced_features.get("search_method", "unknown")
        
        print(f"[OK] Query processed using {search_method} in {response_time}")
        
        return ChatResponse(
            message=result["answer"],
            sources=result["sources"],
            total_sources=result["total_sources"],
            enhanced_features=result["enhanced_features"]
        )
        
    except Exception as e:
        print(f"[FAIL] RAG query failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

@app.post("/retrieve")
async def retrieve(request: ChatRequest):
    """Retrieval only endpoint for OLD dataset (no generation)"""
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
        print(f" Retrieving (OLD): {user_message[:100]}...")
        
        # Get retrieval results (no generation)
        result = rag_system.ask_with_fallback(user_message.strip())
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
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
        
        print(f"[OK] Retrieved {len(formatted_sources)} chunks using {search_method}")
        
        return {
            "sources": formatted_sources,
            "search_method": search_method,
            "total_sources": len(formatted_sources),
            "query": user_message.strip()
        }
        
    except Exception as e:
        print(f"[FAIL] Retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("[START] OLD Dataset RAG API")
    print("="*70)
    print("[STATS] Dataset: documents_old table only")
    print(" URL: http://localhost:8002")
    print(" Endpoints: /chat, /retrieve, /health")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
