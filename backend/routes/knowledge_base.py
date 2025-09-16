from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import List, Optional, Dict, Any
import sys
import os
import time
import json
from loguru import logger

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db, create_tables
from models.knowledge_base import Document, DocumentChunk, KnowledgeBaseQuery
from models.user import User
from models.chat import ChatSession
from app.knowledge_schemas import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentUploadRequest,
    DocumentUploadResponse, DocumentSearchRequest, DocumentSearchResponse,
    SearchResult, BulkDocumentResponse, DocumentAnalytics, DocumentChunkResponse
)
from app.schemas import APIResponse
from services.document_processor import DocumentProcessor
from services.vector_search import VectorSearchService

router = APIRouter(
    prefix="/api/knowledge",
    tags=["knowledge-base"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
document_processor = DocumentProcessor()
vector_search_service = VectorSearchService()

# Initialize database tables
create_tables()

@router.post("/documents/", response_model=DocumentUploadResponse)
async def create_document(document_data: DocumentCreate, db: Session = Depends(get_db)):
    """Create a new document and process it into chunks"""
    try:
        start_time = time.time()
        
        # Use document processor to save document and create chunks
        document, chunks, processing_time = document_processor.save_document_with_chunks(
            db=db,
            title=document_data.title,
            content=document_data.content,
            document_type=document_data.document_type.value,
            industry_type=document_data.industry_type.value if document_data.industry_type else None,
            language=document_data.language.value
        )
        
        # Create embeddings for the chunks
        embeddings_created = 0
        try:
            embeddings_created = vector_search_service.store_chunk_embeddings(db, chunks)
        except Exception as e:
            logger.warning(f"Failed to create embeddings: {e}")
        
        # Prepare response
        document_response = DocumentResponse(
            id=document.id,
            title=document.title,
            content=document.content,
            document_type=document.document_type,
            industry_type=document.industry_type,
            language=document.language,
            file_path=document.file_path,
            file_size=document.file_size,
            is_active=document.is_active,
            created_at=document.created_at,
            updated_at=document.updated_at,
            chunk_count=len(chunks)
        )
        
        return DocumentUploadResponse(
            success=True,
            message=f"Document '{document.title}' created successfully with {len(chunks)} chunks and {embeddings_created} embeddings",
            document=document_response,
            chunks_created=len(chunks),
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating document: {str(e)}"
        )

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    industry_type: str = Form(None),
    language: str = Form("en"),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    db: Session = Depends(get_db)
):
    """Upload a document file and process it"""
    try:
        # Validate file type
        allowed_types = ["text/plain", "text/markdown", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not supported. Allowed types: {allowed_types}"
            )
        
        # Read file content
        content = await file.read()
        
        # Handle different file types
        if file.content_type == "text/plain" or file.content_type == "text/markdown":
            text_content = content.decode('utf-8')
        else:
            # For PDF and other types, we'd need additional libraries
            # For now, treat as text
            text_content = content.decode('utf-8', errors='ignore')
        
        # Create document using processor
        document, chunks, processing_time = document_processor.save_document_with_chunks(
            db=db,
            title=title,
            content=text_content,
            document_type=document_type,
            industry_type=industry_type,
            language=language,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Update file path in document
        document.file_path = f"uploads/{file.filename}"
        db.commit()
        
        # Create embeddings for the chunks
        embeddings_created = 0
        try:
            embeddings_created = vector_search_service.store_chunk_embeddings(db, chunks)
        except Exception as e:
            logger.warning(f"Failed to create embeddings for uploaded file: {e}")
        
        document_response = DocumentResponse(
            id=document.id,
            title=document.title,
            content=document.content[:500] + "..." if len(document.content) > 500 else document.content,
            document_type=document.document_type,
            industry_type=document.industry_type,
            language=document.language,
            file_path=document.file_path,
            file_size=document.file_size,
            is_active=document.is_active,
            created_at=document.created_at,
            updated_at=document.updated_at,
            chunk_count=len(chunks)
        )
        
        return DocumentUploadResponse(
            success=True,
            message=f"File '{file.filename}' uploaded and processed successfully with {len(chunks)} chunks and {embeddings_created} embeddings",
            document=document_response,
            chunks_created=len(chunks),
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )

@router.get("/documents/{document_id}", response_model=APIResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a document by ID"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get chunk count
        chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).count()
        
        document_response = DocumentResponse(
            id=document.id,
            title=document.title,
            content=document.content,
            document_type=document.document_type,
            industry_type=document.industry_type,
            language=document.language,
            file_path=document.file_path,
            file_size=document.file_size,
            is_active=document.is_active,
            created_at=document.created_at,
            updated_at=document.updated_at,
            chunk_count=chunk_count
        )
        
        return APIResponse(
            success=True,
            message="Document retrieved successfully",
            data={"document": document_response.dict()}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}"
        )

@router.get("/documents/", response_model=BulkDocumentResponse)
async def list_documents(
    document_type: Optional[str] = Query(None),
    industry_type: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List documents with optional filters"""
    try:
        query = db.query(Document)
        
        # Apply filters
        if document_type:
            query = query.filter(Document.document_type == document_type)
        if industry_type:
            query = query.filter(Document.industry_type == industry_type)
        if language:
            query = query.filter(Document.language == language)
        if is_active is not None:
            query = query.filter(Document.is_active == is_active)
        if search:
            query = query.filter(Document.title.contains(search) | Document.content.contains(search))
        
        total_count = query.count()
        documents = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()
        
        # Convert to response format with chunk counts
        documents_data = []
        for doc in documents:
            chunk_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
            
            doc_response = DocumentResponse(
                id=doc.id,
                title=doc.title,
                content=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                document_type=doc.document_type,
                industry_type=doc.industry_type,
                language=doc.language,
                file_path=doc.file_path,
                file_size=doc.file_size,
                is_active=doc.is_active,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                chunk_count=chunk_count
            )
            documents_data.append(doc_response)
        
        return BulkDocumentResponse(
            success=True,
            message=f"Retrieved {len(documents_data)} documents",
            documents=documents_data,
            total_count=total_count
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}"
        )

@router.get("/documents/{document_id}/chunks", response_model=APIResponse)
async def get_document_chunks(
    document_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get chunks for a specific document"""
    try:
        # Verify document exists
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        query = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id)
        total_count = query.count()
        chunks = query.order_by(DocumentChunk.chunk_index).offset(skip).limit(limit).all()
        
        chunks_data = []
        for chunk in chunks:
            chunk_response = DocumentChunkResponse(
                id=chunk.id,
                document_id=chunk.document_id,
                chunk_text=chunk.chunk_text,
                chunk_index=chunk.chunk_index,
                chunk_size=chunk.chunk_size,
                overlap_with_previous=chunk.overlap_with_previous,
                embedding_id=chunk.embedding_id,
                embedding_created=chunk.embedding_created,
                keywords=chunk.keywords,
                section_title=chunk.section_title,
                confidence_score=chunk.confidence_score,
                created_at=chunk.created_at
            )
            chunks_data.append(chunk_response.dict())
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(chunks_data)} chunks for document {document_id}",
            data={
                "document_title": document.title,
                "chunks": chunks_data,
                "total_chunks": total_count,
                "pagination": {
                    "skip": skip,
                    "limit": limit,
                    "has_more": (skip + len(chunks_data)) < total_count
                }
            }
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document chunks: {str(e)}"
        )

@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(search_request: DocumentSearchRequest, db: Session = Depends(get_db)):
    """Search documents and chunks using semantic vector search"""
    try:
        start_time = time.time()

        # Use semantic search with vector embeddings
        document_types = [dt.value for dt in search_request.document_types] if search_request.document_types else None
        industry_types = [it.value for it in search_request.industry_types] if search_request.industry_types else None
        min_confidence = search_request.min_confidence or 0.0

        # Perform semantic search using VectorSearchService
        vector_results = vector_search_service.semantic_search(
            query=search_request.query,
            top_k=search_request.limit,
            document_types=document_types,
            industry_types=industry_types,
            min_confidence=min_confidence
        )

        # Convert vector search results to API response format
        search_results = []
        for result in vector_results:
            # Get document info for each result
            document = db.query(Document).filter(Document.id == result["document_id"]).first()

            if document:
                search_result = SearchResult(
                    chunk_id=result["chunk_id"],
                    document_id=result["document_id"],
                    document_title=document.title,
                    chunk_text=result["chunk_text"],
                    chunk_index=result.get("chunk_index", 0),
                    section_title=result.get("section_title"),
                    confidence_score=result["similarity_score"],  # Use similarity score as confidence
                    keywords=result.get("keywords"),
                    document_type=document.document_type,
                    industry_type=document.industry_type
                )
                search_results.append(search_result)

        search_time = int((time.time() - start_time) * 1000)

        return DocumentSearchResponse(
            success=True,
            message=f"Found {len(search_results)} relevant chunks",
            query=search_request.query,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=search_time
        )

    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )

@router.get("/analytics", response_model=APIResponse)
async def get_knowledge_analytics(db: Session = Depends(get_db)):
    """Get analytics about the knowledge base"""
    try:
        # Basic counts
        total_docs = db.query(Document).count()
        total_chunks = db.query(DocumentChunk).count()
        
        # Documents by type
        doc_types = db.query(Document.document_type, func.count(Document.id)).group_by(Document.document_type).all()
        documents_by_type = {doc_type: count for doc_type, count in doc_types}
        
        # Documents by industry
        industries = db.query(Document.industry_type, func.count(Document.id)).group_by(Document.industry_type).all()
        documents_by_industry = {industry or "general": count for industry, count in industries}
        
        # Documents by language
        languages = db.query(Document.language, func.count(Document.id)).group_by(Document.language).all()
        documents_by_language = {lang: count for lang, count in languages}
        
        # Average chunks per document
        avg_chunks = total_chunks / total_docs if total_docs > 0 else 0
        
        analytics = DocumentAnalytics(
            total_documents=total_docs,
            documents_by_type=documents_by_type,
            documents_by_industry=documents_by_industry,
            documents_by_language=documents_by_language,
            total_chunks=total_chunks,
            average_chunks_per_doc=round(avg_chunks, 2),
            total_queries_today=0,  # Will be implemented with query tracking
            popular_search_terms=[]  # Will be implemented with query tracking
        )
        
        return APIResponse(
            success=True,
            message="Knowledge base analytics retrieved successfully",
            data={"analytics": analytics.dict()}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics: {str(e)}"
        )

@router.delete("/documents/{document_id}", response_model=APIResponse)
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and all its chunks"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete associated chunks (cascade should handle this, but being explicit)
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
        
        # Delete document
        db.delete(document)
        db.commit()
        
        return APIResponse(
            success=True,
            message=f"Document '{document.title}' and all its chunks deleted successfully",
            data={"document_id": document_id}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )