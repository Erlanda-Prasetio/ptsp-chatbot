#!/usr/bin/env python3
"""
FastAPI server for COMBINED dataset RAG
Routes all queries to the documents_combined table

Usage:
    python rag_api_combined.py
    
Default port: 8003
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()

sys.path.append('src')
sys.path.append('.')

from src.hybrid_rag_combined import SmartEnhancedRAG_COMBINED

app = FastAPI(
    title="COMBINED Dataset RAG API",
    description="RAG API for COMBINED dataset (documents_combined table)",
    version="1.0"
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
    retrieve_only: bool = False
    temperature: float = 0.7

class ChatResponse(BaseModel):
    message: str = ""
    sources: list = []
    total_sources: int = 0
    search_method: str = "unknown"
    dataset: str = "COMBINED"

# Initialize COMBINED dataset RAG (forces documents_combined table)
try:
    rag_system = SmartEnhancedRAG_COMBINED()
    print("✅ COMBINED Dataset RAG initialized (documents_combined table)")
except Exception as e:
    print(f"❌ Failed to initialize RAG: {e}")
    import traceback
    traceback.print_exc()
    rag_system = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = "healthy" if rag_system else "error"
    return {
        "status": status,
        "dataset": "COMBINED",
        "table": "documents_combined"
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Full RAG pipeline on COMBINED dataset only
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
        print(f"🔍 Query: {user_message[:100]}...")
        
        # Run RAG pipeline on COMBINED dataset
        result = rag_system.ask(user_message.strip(), k=5)
        
        return ChatResponse(
            message=result.get("answer", ""),
            sources=result.get("sources", []),
            total_sources=len(result.get("sources", [])),
            search_method=result.get("search_method", "unknown"),
            dataset="COMBINED"
        )
        
    except Exception as e:
        print(f"❌ Query error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retrieve")
async def retrieve(request: ChatRequest):
    """
    Retrieval only (no generation) on COMBINED dataset
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
        print(f"📚 Retrieving: {user_message[:100]}...")
        
        # Ask but don't generate (just get sources)
        result = rag_system.ask(user_message.strip(), k=5)
        
        # Filter out generation, just return retrieval results
        return ChatResponse(
            message="",  # No message generation for retrieval-only
            sources=result.get("sources", []),
            total_sources=len(result.get("sources", [])),
            search_method=result.get("search_method", "unknown"),
            dataset="COMBINED"
        )
        
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 COMBINED Dataset RAG API")
    print("="*70)
    print("📊 Dataset: documents_combined table only")
    print("🌐 URL: http://localhost:8003")
    print("📚 Endpoints: /chat, /retrieve, /health")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)
