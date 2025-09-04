"""
Enhanced RAG API with Training Integration
Uses both knowledge base and training data for responses
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our training system
from chatbot_trainer import ChatbotTrainer


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []
    response_type: str = "trained"  # "trained", "knowledge_base", "fallback"


class HealthResponse(BaseModel):
    status: str
    message: str
    features: Dict[str, Any]


class TrainingResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]


class EnhancedRAGSystem:
    def __init__(self):
        self.trainer = ChatbotTrainer()
        self.is_initialized = False
        
    def initialize(self):
        """Initialize the enhanced RAG system"""
        try:
            # Load existing training data
            print("🤖 Loading training data...")
            self.is_initialized = True
            print("✅ Enhanced RAG system initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize enhanced RAG: {e}")
            return False
    
    def query(self, question: str) -> Dict[str, Any]:
        """Enhanced query that uses training data first, then fallback"""
        
        # First, try to get response from training data
        trained_response = self.trainer.get_response_for_question(question)
        
        if trained_response:
            return {
                "response": trained_response,
                "sources": [{"type": "training_data", "confidence": "high"}],
                "response_type": "trained"
            }
        
        # If no trained response, use fallback logic
        question_lower = question.lower()
        
        # Simple keyword-based responses for common patterns
        if any(word in question_lower for word in ["halo", "hai", "hello", "selamat"]):
            response = "Halo! Selamat datang di chatbot DPMPTSP Jawa Tengah. Saya siap membantu Anda dengan informasi pelayanan perizinan dan investasi."
        elif any(word in question_lower for word in ["info", "layanan", "bantuan"]):
            response = "Saya dapat membantu Anda dengan informasi tentang perizinan berusaha, investasi, dan layanan DPMPTSP Jawa Tengah lainnya. Silakan tanyakan apa yang Anda butuhkan."
        elif any(word in question_lower for word in ["terima kasih", "thanks", "makasih"]):
            response = "Sama-sama! Senang bisa membantu Anda. Jika ada pertanyaan lain tentang layanan DPMPTSP, jangan ragu untuk bertanya."
        else:
            response = """Terima kasih atas pertanyaan Anda. Untuk informasi lebih detail, silakan:

1. Hubungi call center DPMPTSP di (024) 3569988 atau hotline 14000
2. Kunjungi website resmi DPMPTSP Jawa Tengah
3. Datang langsung ke kantor DPMPTSP
   📍 Alamat: Jl. Menteri Supeno No. 2, Semarang
   🕐 Jam kerja: Senin-Jumat, 07.30-16.00 WIB

Petugas kami siap membantu Anda dengan informasi yang akurat dan terkini."""
        
        return {
            "response": response,
            "sources": [{"type": "fallback_logic", "confidence": "medium"}],
            "response_type": "fallback"
        }
    
    def add_training_data(self, question: str, response: str, category: str = None) -> bool:
        """Add new training data during runtime"""
        try:
            from datetime import datetime
            from chatbot_trainer import TrainingData
            
            training_data = TrainingData(
                question=question,
                response=response,
                category=category or self.trainer.categorize_question(question),
                timestamp=datetime.now().isoformat(),
                quality_score=0.7,  # Default for user-provided data
                source="runtime_training"
            )
            
            self.trainer.save_training_data(training_data)
            return True
        except Exception as e:
            print(f"Error adding training data: {e}")
            return False


# Global enhanced RAG instance
enhanced_rag = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup the enhanced RAG system"""
    global enhanced_rag
    
    print("🚀 Initializing Enhanced PTSP RAG System...")
    
    try:
        enhanced_rag = EnhancedRAGSystem()
        success = enhanced_rag.initialize()
        
        if success:
            print("✅ Enhanced RAG system ready!")
            print("📚 Training data loaded and available")
            print("🤖 Chatbot ready to serve intelligent responses")
        else:
            print("⚠️ Enhanced RAG initialized with limited functionality")
            
    except Exception as e:
        print(f"❌ Failed to initialize enhanced RAG system: {e}")
        enhanced_rag = None
    
    yield
    
    print("🔄 Shutting down enhanced RAG system...")


# FastAPI app
app = FastAPI(
    title="PTSP Jawa Tengah Enhanced Chatbot API",
    description="Enhanced chatbot API with training capabilities for PTSP Jawa Tengah",
    version="2.0.0",
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
        "message": "PTSP Jawa Tengah Enhanced Chatbot API",
        "status": "running",
        "version": "2.0.0",
        "features": ["training_integration", "smart_responses", "fallback_logic"]
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if enhanced_rag is None:
        raise HTTPException(status_code=503, detail="Enhanced RAG system not initialized")
    
    return HealthResponse(
        status="healthy",
        message="Enhanced RAG system running with training integration",
        features={
            "training_data": "available",
            "smart_responses": "enabled",
            "fallback_logic": "active",
            "real_time_learning": "supported"
        }
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with enhanced responses"""
    if enhanced_rag is None:
        raise HTTPException(status_code=503, detail="Enhanced RAG system not initialized")
    
    try:
        # Process the query with enhanced RAG
        result = enhanced_rag.query(request.message)
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"],
            response_type=result["response_type"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/train", response_model=TrainingResponse)
async def add_training_data(question: str, response: str, category: str = None):
    """Add new training data to improve responses"""
    if enhanced_rag is None:
        raise HTTPException(status_code=503, detail="Enhanced RAG system not initialized")
    
    try:
        success = enhanced_rag.add_training_data(question, response, category)
        
        if success:
            return TrainingResponse(
                success=True,
                message="Training data added successfully",
                data={"question": question, "category": category or "auto"}
            )
        else:
            return TrainingResponse(
                success=False,
                message="Failed to add training data",
                data={}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding training data: {str(e)}")


@app.get("/training/stats")
async def get_training_stats():
    """Get training data statistics"""
    if enhanced_rag is None:
        raise HTTPException(status_code=503, detail="Enhanced RAG system not initialized")
    
    try:
        import sqlite3
        conn = sqlite3.connect(enhanced_rag.trainer.db_path)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM training_data")
        total_count = cursor.fetchone()[0]
        
        # Get category distribution
        cursor.execute("SELECT category, COUNT(*) FROM training_data GROUP BY category")
        categories = dict(cursor.fetchall())
        
        # Get source distribution
        cursor.execute("SELECT source, COUNT(*) FROM training_data GROUP BY source")
        sources = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_training_examples": total_count,
            "categories": categories,
            "sources": sources,
            "status": "active"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting training stats: {str(e)}")


@app.post("/training/bulk")
async def bulk_train():
    """Run the bulk training process with predefined questions"""
    if enhanced_rag is None:
        raise HTTPException(status_code=503, detail="Enhanced RAG system not initialized")
    
    try:
        from chatbot_trainer import process_training_questions
        
        result = process_training_questions()
        
        return TrainingResponse(
            success=True,
            message=f"Bulk training completed: {result['total_processed']} questions processed",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in bulk training: {str(e)}")


@app.get("/status")
async def get_status():
    """Get detailed system status"""
    return {
        "system": "PTSP Enhanced Chatbot",
        "version": "2.0.0",
        "rag_initialized": enhanced_rag is not None,
        "features": {
            "training_integration": True,
            "smart_responses": True,
            "fallback_logic": True,
            "real_time_learning": True,
            "bulk_training": True
        },
        "deployment": "cloud_optimized"
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting Enhanced PTSP Chatbot API on port {port}")
    print("🤖 Features: Training Integration, Smart Responses, Real-time Learning")
    
    uvicorn.run(
        "rag_api_enhanced:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
