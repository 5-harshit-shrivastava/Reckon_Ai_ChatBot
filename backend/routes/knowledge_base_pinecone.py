"""
Knowledge Base routes using Pinecone-only storage
No PostgreSQL/Neon database required
"""

from fastapi import APIRouter, HTTPException, status, Query, File, UploadFile, Form
from typing import List, Optional, Dict, Any
import sys
import os
from loguru import logger

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge_schemas import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentUploadRequest,
    DocumentUploadResponse, DocumentSearchRequest, DocumentSearchResponse,
    SearchResult, BulkDocumentResponse, DocumentAnalytics
)
from app.schemas import APIResponse
from services.pinecone_document_service import PineconeDocumentService

router = APIRouter(
    prefix="/api/knowledge",
    tags=["knowledge-base"],
    responses={404: {"description": "Not found"}},
)

# Initialize Pinecone document service
pinecone_doc_service = PineconeDocumentService()


@router.post("/documents/", response_model=DocumentUploadResponse)
async def create_document(document_data: DocumentCreate):
    """Create a new document and process it into chunks (Pinecone-only)"""
    try:
        result = pinecone_doc_service.create_document(
            title=document_data.title,
            content=document_data.content,
            document_type=document_data.document_type.value,
            industry_type=document_data.industry_type.value if document_data.industry_type else None,
            language=document_data.language.value
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating document: {result.get('error', 'Unknown error')}"
            )

        # Prepare response
        document_response = DocumentResponse(
            id=result["document_id"],
            title=result["title"],
            content=document_data.content[:500] + "..." if len(document_data.content) > 500 else document_data.content,
            document_type=document_data.document_type.value,
            industry_type=document_data.industry_type.value if document_data.industry_type else None,
            language=document_data.language.value,
            file_path=None,
            file_size=len(document_data.content),
            is_active=True,
            created_at=result["created_at"],
            updated_at=result["created_at"],
            chunk_count=result["chunks_created"]
        )

        return DocumentUploadResponse(
            success=True,
            message=f"Document '{result['title']}' created successfully with {result['chunks_created']} chunks",
            document=document_response,
            chunks_created=result["chunks_created"],
            processing_time_ms=result["processing_time_ms"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating document: {e}")
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
    chunk_overlap: int = Form(200)
):
    """Upload a document file and process it (Pinecone-only)"""
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
            text_content = content.decode('utf-8', errors='ignore')

        # Create document using Pinecone service
        result = pinecone_doc_service.create_document(
            title=title,
            content=text_content,
            document_type=document_type,
            industry_type=industry_type,
            language=language,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading document: {result.get('error', 'Unknown error')}"
            )

        document_response = DocumentResponse(
            id=result["document_id"],
            title=result["title"],
            content=text_content[:500] + "..." if len(text_content) > 500 else text_content,
            document_type=document_type,
            industry_type=industry_type,
            language=language,
            file_path=f"uploads/{file.filename}",
            file_size=len(text_content),
            is_active=True,
            created_at=result["created_at"],
            updated_at=result["created_at"],
            chunk_count=result["chunks_created"]
        )

        return DocumentUploadResponse(
            success=True,
            message=f"File '{file.filename}' uploaded and processed successfully with {result['chunks_created']} chunks",
            document=document_response,
            chunks_created=result["chunks_created"],
            processing_time_ms=result["processing_time_ms"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )


@router.get("/documents/{document_id}", response_model=APIResponse)
async def get_document(document_id: str):
    """Get a document by ID (Pinecone-only)"""
    try:
        result = pinecone_doc_service.get_document(document_id)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        document = result["document"]
        chunks = result["chunks"]

        # Reconstruct content from chunks
        content = "\n\n".join([chunk["chunk_text"] for chunk in chunks])

        document_response = DocumentResponse(
            id=document["id"],
            title=document["title"],
            content=content,
            document_type=document["document_type"],
            industry_type=document["industry_type"],
            language=document["language"],
            file_path=None,
            file_size=len(content),
            is_active=document["is_active"],
            created_at=document["created_at"],
            updated_at=document["updated_at"],
            chunk_count=result["chunk_count"]
        )

        return APIResponse(
            success=True,
            message="Document retrieved successfully",
            data={"document": document_response.dict(), "chunks": chunks}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")
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
    limit: int = Query(50, ge=1, le=100)
):
    """List documents with optional filters (Pinecone-only)"""
    try:
        result = pinecone_doc_service.list_documents(
            document_type=document_type,
            industry_type=industry_type,
            language=language,
            is_active=is_active,
            search=search,
            skip=skip,
            limit=limit
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving documents: {result.get('error', 'Unknown error')}"
            )

        # Convert to response format
        documents_data = []
        for doc in result["documents"]:
            doc_response = DocumentResponse(
                id=doc["id"],
                title=doc["title"],
                content="[Content stored in Pinecone]",  # Don't return full content in list
                document_type=doc["document_type"],
                industry_type=doc["industry_type"],
                language=doc["language"],
                file_path=None,
                file_size=0,
                is_active=doc["is_active"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                chunk_count=doc["chunk_count"]
            )
            documents_data.append(doc_response)

        return BulkDocumentResponse(
            success=True,
            message=f"Retrieved {len(documents_data)} documents",
            documents=documents_data,
            total_count=result["total_count"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}"
        )


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(search_request: DocumentSearchRequest):
    """Search documents and chunks using semantic vector search (Pinecone-only)"""
    try:
        document_types = [dt.value for dt in search_request.document_types] if search_request.document_types else None
        industry_types = [it.value for it in search_request.industry_types] if search_request.industry_types else None
        min_confidence = search_request.min_confidence or 0.0

        result = pinecone_doc_service.search_documents(
            query=search_request.query,
            top_k=search_request.limit,
            document_types=document_types,
            industry_types=industry_types,
            min_confidence=min_confidence
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching documents: {result.get('error', 'Unknown error')}"
            )

        # Convert to response format
        search_results = []
        for r in result["results"]:
            search_result = SearchResult(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                document_title="",  # Not available in current result
                chunk_text=r["chunk_text"],
                chunk_index=0,
                section_title=r.get("section_title"),
                confidence_score=r["similarity_score"],
                keywords=r.get("keywords"),
                document_type="",  # Not available in current result
                industry_type=None
            )
            search_results.append(search_result)

        return DocumentSearchResponse(
            success=True,
            message=f"Found {len(search_results)} relevant chunks",
            query=search_request.query,
            results=search_results,
            total_results=result["total_results"],
            search_time_ms=result["search_time_ms"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )


@router.get("/analytics", response_model=APIResponse)
async def get_knowledge_analytics():
    """Get analytics about the knowledge base (Pinecone-only)"""
    try:
        result = pinecone_doc_service.get_analytics()

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving analytics: {result.get('error', 'Unknown error')}"
            )

        analytics = DocumentAnalytics(
            total_documents=result["total_documents"],
            documents_by_type=result["documents_by_type"],
            documents_by_industry=result["documents_by_industry"],
            documents_by_language=result["documents_by_language"],
            total_chunks=result["total_chunks"],
            average_chunks_per_doc=result["average_chunks_per_doc"],
            total_queries_today=0,  # Not tracked without database
            popular_search_terms=[]  # Not tracked without database
        )

        return APIResponse(
            success=True,
            message="Knowledge base analytics retrieved successfully",
            data={"analytics": analytics.dict(), "index_stats": result.get("index_stats", {})}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics: {str(e)}"
        )


@router.delete("/documents/{document_id}", response_model=APIResponse)
async def delete_document(document_id: str, permanent: bool = Query(False)):
    """Delete a document and all its chunks (Pinecone-only)"""
    try:
        result = pinecone_doc_service.delete_document(
            document_id=document_id,
            soft_delete=not permanent
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        return APIResponse(
            success=True,
            message=result["message"],
            data={"document_id": document_id, "vectors_deleted": result.get("vectors_deleted", 0)}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )


@router.put("/documents/{document_id}", response_model=APIResponse)
async def update_document(document_id: str, document_update: DocumentUpdate):
    """Update a document (Pinecone-only)"""
    try:
        result = pinecone_doc_service.update_document(
            document_id=document_id,
            title=document_update.title,
            content=document_update.content,
            document_type=document_update.document_type.value if document_update.document_type else None,
            industry_type=document_update.industry_type.value if document_update.industry_type else None,
            language=document_update.language.value if document_update.language else None,
            is_active=document_update.is_active
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or update failed"
            )

        return APIResponse(
            success=True,
            message=result["message"],
            data={"document_id": document_id, "chunks_updated": result.get("chunks_updated", 0)}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating document: {str(e)}"
        )
