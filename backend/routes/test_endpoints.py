from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from config.database import get_db
from services.rag_service import RAGService
from services.vector_search import VectorSearchService
from services.gemini_service import GeminiService
from loguru import logger

router = APIRouter(prefix="/api/test", tags=["Testing Endpoints"])

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    industry_context: Optional[str] = None
    top_k: Optional[int] = 5

class EmbeddingRequest(BaseModel):
    text: str
    is_query: Optional[bool] = False

class TestResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    processing_time_ms: Optional[int] = None

@router.get("/status", response_model=TestResponse)
async def system_status():
    """Get overall system status"""
    try:
        import time
        start_time = time.time()

        # Check services
        status = {
            "database": False,
            "gemini": False,
            "embeddings": False,
            "pinecone": False,
            "total_documents": 0,
            "embedded_chunks": 0
        }

        # Database check
        try:
            from config.database import get_db
            from models.knowledge_base import Document, DocumentChunk
            db = next(get_db())
            status["total_documents"] = db.query(Document).count()
            status["embedded_chunks"] = db.query(DocumentChunk).filter(
                DocumentChunk.embedding_created == True
            ).count()
            status["database"] = True
            db.close()
        except:
            pass

        # Gemini check
        try:
            gemini = GeminiService()
            status["gemini"] = gemini.test_connection()
        except:
            pass

        # Embeddings check
        try:
            vs = VectorSearchService()
            test_emb = vs.create_embedding("test")
            status["embeddings"] = len(test_emb) == 768 and sum(abs(x) for x in test_emb) > 0.1
        except:
            pass

        # Pinecone check
        try:
            vs = VectorSearchService()
            if vs.pinecone_index:
                stats = vs.pinecone_index.describe_index_stats()
                status["pinecone"] = True
                status["pinecone_vectors"] = stats.get('total_vector_count', 0)
        except:
            pass

        processing_time = int((time.time() - start_time) * 1000)

        return TestResponse(
            success=True,
            message="System status retrieved",
            data=status,
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embedding", response_model=TestResponse)
async def test_embedding(request: EmbeddingRequest):
    """Test embedding generation"""
    try:
        import time
        start_time = time.time()

        vs = VectorSearchService()
        embedding = vs.create_embedding(request.text, request.is_query)

        processing_time = int((time.time() - start_time) * 1000)

        # Analyze embedding quality
        non_zero_count = sum(1 for x in embedding if abs(x) > 0.001) if embedding else 0
        magnitude = sum(x*x for x in embedding) ** 0.5 if embedding else 0

        return TestResponse(
            success=len(embedding) == 768,
            message=f"Embedding generated: {len(embedding)} dimensions",
            data={
                "dimensions": len(embedding) if embedding else 0,
                "non_zero_values": non_zero_count,
                "magnitude": magnitude,
                "quality": "good" if non_zero_count > 100 else "poor",
                "first_5_values": embedding[:5] if embedding else []
            },
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Embedding test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=TestResponse)
async def test_search(request: QueryRequest):
    """Test semantic search"""
    try:
        import time
        start_time = time.time()

        vs = VectorSearchService()
        results = vs.semantic_search(
            query=request.query,
            top_k=request.top_k,
            industry_types=[request.industry_context] if request.industry_context else None
        )

        processing_time = int((time.time() - start_time) * 1000)

        return TestResponse(
            success=True,
            message=f"Search completed: {len(results)} results found",
            data={
                "query": request.query,
                "results_count": len(results),
                "results": [
                    {
                        "chunk_id": r.get("chunk_id"),
                        "similarity_score": r.get("similarity_score"),
                        "section_title": r.get("section_title"),
                        "preview": r.get("chunk_text", "")[:200] + "..."
                    }
                    for r in results
                ]
            },
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Search test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag", response_model=TestResponse)
async def test_rag(request: QueryRequest, db: Session = Depends(get_db)):
    """Test complete RAG pipeline"""
    try:
        import time
        start_time = time.time()

        rag_service = RAGService()
        result = rag_service.generate_rag_response(
            db=db,
            user_query=request.query,
            industry_context=request.industry_context,
            language=request.language
        )

        processing_time = int((time.time() - start_time) * 1000)

        return TestResponse(
            success=result["success"],
            message="RAG pipeline completed",
            data={
                "query": request.query,
                "response": result.get("response", ""),
                "confidence": result.get("confidence", 0),
                "sources_used": result.get("chunks_used", 0),
                "model_used": result.get("model_used", ""),
                "sources": result.get("sources", [])
            },
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"RAG test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/gemini", response_model=TestResponse)
async def test_gemini(request: QueryRequest):
    """Test Google Gemini Pro directly"""
    try:
        import time
        start_time = time.time()

        gemini = GeminiService()
        result = gemini.generate_response(
            user_query=request.query,
            context="ReckonSales is a comprehensive ERP system for small businesses.",
            industry_context=request.industry_context,
            language=request.language
        )

        processing_time = int((time.time() - start_time) * 1000)

        return TestResponse(
            success=result["success"],
            message="Gemini response generated",
            data={
                "query": request.query,
                "response": result.get("response", ""),
                "confidence": result.get("confidence", 0),
                "model_used": result.get("model_used", ""),
                "generation_time_ms": result.get("generation_time_ms", 0)
            },
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error(f"Gemini test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sample-queries")
async def get_sample_queries():
    """Get sample queries for testing"""
    return {
        "english_queries": [
            "How to manage inventory in ReckonSales?",
            "What are the GST features in ReckonSales?",
            "How to create invoices in ReckonSales?",
            "What reports are available in ReckonSales?",
            "How to set up customers in ReckonSales?"
        ],
        "hindi_queries": [
            "ReckonSales में इन्वेंटरी कैसे मैनेज करें?",
            "GST billing कैसे करते हैं?",
            "Customer management कैसे करें?",
            "Reports कैसे generate करें?",
            "System setup कैसे करें?"
        ],
        "industry_specific": {
            "pharmacy": [
                "How to manage medicine inventory?",
                "What are the pharmacy features?",
                "How to track expiry dates?"
            ],
            "auto_parts": [
                "How to manage auto parts inventory?",
                "What are vehicle compatibility features?",
                "How to handle part numbers?"
            ]
        }
    }

@router.delete("/reset-embeddings")
async def reset_embeddings(db: Session = Depends(get_db)):
    """Reset all embeddings (for testing)"""
    try:
        from models.knowledge_base import DocumentChunk

        # Mark all chunks as not embedded
        chunks = db.query(DocumentChunk).all()
        for chunk in chunks:
            chunk.embedding_created = False
            chunk.embedding_id = None

        db.commit()

        # Clear Pinecone index
        vs = VectorSearchService()
        if vs.pinecone_index:
            vs.pinecone_index.delete(delete_all=True, namespace="reckon-knowledge-base")

        return TestResponse(
            success=True,
            message=f"Reset {len(chunks)} embeddings",
            data={"chunks_reset": len(chunks)}
        )

    except Exception as e:
        logger.error(f"Reset embeddings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))