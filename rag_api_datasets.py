"""
FastAPI RAG Server with Dataset Selection
==========================================

Supports testing with different datasets (NEW, OLD, COMBINED).
Pass ?dataset=OLD or ?dataset=COMBINED in requests to switch datasets.

Usage:
    python rag_api_datasets.py --dataset OLD
    python rag_api_datasets.py --dataset COMBINED
"""

import sys
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Dict, Any, Union, Optional
import uvicorn

# Add src to path
sys.path.append('src')

from hybrid_rag import HybridRAGSystem
from config import VECTOR_BACKEND
from config_datasets import get_dataset_config, DatasetType, list_datasets


# Global state for dataset management
class DatasetState:
    def __init__(self):
        self.current_dataset: DatasetType = 'NEW'
        self.rag_systems: Dict[DatasetType, HybridRAGSystem] = {}


dataset_state = DatasetState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize RAG systems for all datasets"""
    try:
        print("🚀 Initializing Hybrid RAG systems with dataset selection...")
        
        # Initialize for each dataset
        for dataset_type in ['NEW', 'OLD', 'COMBINED']:
            print(f"\n  Initializing {dataset_type} dataset...")
            config = get_dataset_config(dataset_type)
            
            try:
                rag_system = HybridRAGSystem(table_name=config.table_name)
                dataset_state.rag_systems[dataset_type] = rag_system
                print(f"    ✅ {dataset_type} initialized (table: {config.table_name})")
            except Exception as e:
                print(f"    ⚠️  {dataset_type} failed: {e}")
        
        if dataset_state.rag_systems:
            print(f"\n✅ {len(dataset_state.rag_systems)} RAG systems initialized successfully!")
        else:
            print("❌ Failed to initialize any RAG systems!")
            
    except Exception as e:
        print(f"❌ Failed to initialize RAG systems: {e}")
    
    yield
    
    print("🔄 Shutting down RAG systems...")


app = FastAPI(
    title="Central Java RAG API - Multi-Dataset",
    version="2.0.0",
    lifespan=lifespan
)

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
    dataset_used: str


def get_rag_system(dataset: Optional[DatasetType] = None) -> HybridRAGSystem:
    """Get RAG system for the specified dataset"""
    if dataset is None:
        dataset = dataset_state.current_dataset
    
    if dataset not in dataset_state.rag_systems:
        raise HTTPException(
            status_code=400,
            detail=f"Dataset '{dataset}' not initialized. Available: {list(dataset_state.rag_systems.keys())}"
        )
    
    return dataset_state.rag_systems[dataset]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Central Java RAG API (Multi-Dataset) is running",
        "status": "healthy" if dataset_state.rag_systems else "unhealthy",
        "version": "2.0.0",
        "available_datasets": list(dataset_state.rag_systems.keys()),
        "current_dataset": dataset_state.current_dataset,
    }


@app.get("/health")
async def health_check(dataset: Optional[DatasetType] = Query(None)):
    """Detailed health check for a specific dataset"""
    if not dataset_state.rag_systems:
        raise HTTPException(status_code=503, detail="No RAG systems initialized")
    
    try:
        rag_system = get_rag_system(dataset)
        
        return {
            "status": "healthy",
            "backend": "supabase" if VECTOR_BACKEND == "supabase" else "local",
            "dataset": dataset or dataset_state.current_dataset,
            "smart_features": True,
            "hybrid_search": True,
            "internet_fallback": True,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")


@app.get("/datasets")
async def list_available_datasets():
    """List all available datasets and their status"""
    datasets = {}
    for dataset_type, rag_system in dataset_state.rag_systems.items():
        config = get_dataset_config(dataset_type)
        datasets[dataset_type] = {
            "description": config.description,
            "table_name": config.table_name,
            "sources": config.source_dirs,
        }
    
    return {
        "datasets": datasets,
        "current_dataset": dataset_state.current_dataset,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, dataset: Optional[DatasetType] = Query(None)):
    """
    Main chat endpoint with dataset selection
    
    Query Parameters:
        dataset: Dataset to use (NEW, OLD, or COMBINED). If not specified, uses current dataset.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    # Get user message
    user_message = None
    for message in reversed(request.messages):
        if message.role == "user":
            user_message = message.content
            break
    
    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")
    
    try:
        # Get RAG system for the specified dataset
        rag_system = get_rag_system(dataset)
        current_dataset = dataset or dataset_state.current_dataset
        
        print(f"🔍 Processing query with {current_dataset} dataset: {user_message[:100]}...")
        
        # Get response
        result = rag_system.ask_with_fallback(user_message.strip())
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Get timing info
        enhanced_features = result.get("enhanced_features", {})
        response_time = enhanced_features.get("response_time", "unknown")
        search_method = enhanced_features.get("search_method", "unknown")
        
        print(f"✅ Query processed using {search_method} in {response_time} ({current_dataset})")
        
        return ChatResponse(
            message=result["answer"],
            sources=result["sources"],
            total_sources=result["total_sources"],
            enhanced_features=result["enhanced_features"],
            dataset_used=current_dataset,
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")


@app.post("/retrieve")
async def retrieve(request: ChatRequest, dataset: Optional[DatasetType] = Query(None)):
    """
    Retrieve chunks only (for retrieval testing) with dataset selection
    
    Query Parameters:
        dataset: Dataset to use (NEW, OLD, or COMBINED). If not specified, uses current dataset.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    # Get user message
    user_message = None
    for message in reversed(request.messages):
        if message.role == "user":
            user_message = message.content
            break
    
    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")
    
    try:
        # Get RAG system for the specified dataset
        rag_system = get_rag_system(dataset)
        current_dataset = dataset or dataset_state.current_dataset
        
        print(f"🔍 Retrieving chunks with {current_dataset} dataset: {user_message[:100]}...")
        
        # Get retrieval results
        result = rag_system.ask_with_fallback(user_message.strip())
        
        sources = result.get("sources", [])
        search_method = result.get("enhanced_features", {}).get("search_method", "unknown")
        
        # Format sources
        formatted_sources = []
        for i, chunk in enumerate(sources, 1):
            if isinstance(chunk, dict):
                chunk_id = chunk.get("id") or chunk.get("chunk_id") or f"chunk_{i}"
                text = chunk.get("content") or chunk.get("text", "")
                score = chunk.get("similarity") or chunk.get("score", 0)
                metadata = chunk.get("metadata", {})
            else:
                chunk_id = f"chunk_{i}"
                text = str(chunk)
                score = 0
                metadata = {}
            
            formatted_sources.append({
                "rank": i,
                "chunk_id": chunk_id,
                "text": text,
                "score": float(score) if score else 0.0,
                "metadata": metadata,
            })
        
        print(f"✅ Retrieved {len(formatted_sources)} chunks using {search_method} ({current_dataset})")
        
        return {
            "sources": formatted_sources,
            "search_method": search_method,
            "total_sources": len(formatted_sources),
            "query": user_message.strip(),
            "dataset_used": current_dataset,
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {e}")


@app.get("/suggestions")
async def get_suggestions(dataset: Optional[DatasetType] = Query(None)):
    """Get suggested questions for the selected dataset"""
    current_dataset = dataset or dataset_state.current_dataset
    
    suggestions = {
        "NEW": [
            "Apa itu DPMPTSP Jawa Tengah?",
            "Bagaimana cara mengurus izin usaha?",
            "Syarat investasi di Jawa Tengah",
            "Prosedur perizinan online",
            "Layanan pelayanan terpadu satu pintu",
            "Dokumen yang diperlukan untuk izin",
        ],
        "OLD": [
            "Informasi umum perizinan",
            "Cara mendaftar usaha",
            "Persyaratan dasar",
            "Proses bisnis online",
            "Layanan terintegrasi",
        ],
        "COMBINED": [
            "Apa itu DPMPTSP Jawa Tengah?",
            "Bagaimana cara mengurus izin usaha?",
            "Syarat investasi di Jawa Tengah",
            "Persyaratan dasar usaha",
            "Informasi terkini tentang perizinan",
        ],
    }
    
    return {
        "dataset": current_dataset,
        "suggestions": suggestions.get(current_dataset, suggestions["NEW"]),
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Dataset RAG API Server')
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['NEW', 'OLD', 'COMBINED'],
        default='NEW',
        help='Default dataset to use',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8001,
        help='Port to run the server on',
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to',
    )
    
    args = parser.parse_args()
    dataset_state.current_dataset = args.dataset
    
    print("\n" + "="*70)
    print("CENTRAL JAVA RAG API - MULTI-DATASET")
    print("="*70)
    print(f"🚀 Starting server on {args.host}:{args.port}")
    print(f"📊 Default dataset: {args.dataset}")
    print(f"📋 API docs: http://localhost:{args.port}/docs")
    print(f"🔗 Datasets endpoint: http://localhost:{args.port}/datasets")
    print("\nUsage:")
    print(f"  Chat with NEW: POST /chat?dataset=NEW")
    print(f"  Chat with OLD: POST /chat?dataset=OLD")
    print(f"  Chat with COMBINED: POST /chat?dataset=COMBINED")
    print(f"  Retrieve with dataset: POST /retrieve?dataset=OLD")
    print("="*70 + "\n")
    
    uvicorn.run(
        "rag_api_datasets:app",
        host=args.host,
        port=args.port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
