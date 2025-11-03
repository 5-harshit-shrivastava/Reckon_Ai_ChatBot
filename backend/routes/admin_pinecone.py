"""
Admin routes using Pinecone-only storage
No PostgreSQL/Neon database required
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import os
from loguru import logger

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.pinecone_document_service import PineconeDocumentService
from pydantic import BaseModel
import time

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

# Initialize Pinecone document service
pinecone_doc_service = PineconeDocumentService()


# Response Models
class DashboardStats(BaseModel):
    total_conversations: int
    total_conversations_change: str
    knowledge_base_entries: int
    knowledge_base_entries_change: str
    total_users: int
    total_users_change: str
    success_rate: float
    success_rate_change: str


class RecentActivity(BaseModel):
    id: str
    action: str
    details: str
    timestamp: str
    status: str


class TopQuery(BaseModel):
    query: str
    count: int
    category: str


class KnowledgeBaseEntry(BaseModel):
    id: str
    title: str
    document_type: str
    industry_type: Optional[str]
    language: str
    is_active: bool
    created_at: str
    chunk_count: int


class KnowledgeBaseCreate(BaseModel):
    title: str
    content: str
    document_type: str
    industry_type: Optional[str] = None
    language: str = "en"


class KnowledgeBaseUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    document_type: Optional[str] = None
    industry_type: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics from Pinecone"""
    try:
        # Get analytics from Pinecone
        analytics = pinecone_doc_service.get_analytics()

        if not analytics["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching stats: {analytics.get('error', 'Unknown error')}"
            )

        knowledge_base_entries = analytics["total_documents"]

        # Simplified stats (without database)
        return DashboardStats(
            total_conversations=0,  # Not tracked without database
            total_conversations_change="+0.0%",
            knowledge_base_entries=knowledge_base_entries,
            knowledge_base_entries_change="+0.0%",  # Can't calculate without history
            total_users=0,  # Not tracked without database
            total_users_change="+0.0%",
            success_rate=95.0,  # Placeholder
            success_rate_change="+2.1%"
        )

    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")


@router.get("/dashboard/recent-activities", response_model=List[RecentActivity])
async def get_recent_activities(limit: int = 10):
    """Get recent activities from Pinecone"""
    try:
        # Get recent documents from Pinecone
        result = pinecone_doc_service.list_documents(
            is_active=True,
            skip=0,
            limit=limit
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching recent activities: {result.get('error', 'Unknown error')}"
            )

        activities = []
        for doc in result["documents"]:
            try:
                created_at = datetime.fromisoformat(doc["created_at"])
                current_time = datetime.utcnow()
                time_diff = current_time - created_at
                hours_ago = int(time_diff.total_seconds() / 3600)

                activities.append(RecentActivity(
                    id=doc["id"],
                    action="Knowledge Base Updated",
                    details=f"Document: {doc['title']}",
                    timestamp=f"{hours_ago} hours ago" if hours_ago > 0 else "Just now",
                    status="success"
                ))
            except Exception as e:
                logger.warning(f"Error processing activity for doc {doc.get('id')}: {e}")
                continue

        return activities[:limit]

    except Exception as e:
        logger.error(f"Error fetching recent activities: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching recent activities: {str(e)}")


@router.get("/dashboard/top-queries", response_model=List[TopQuery])
async def get_top_queries(limit: int = 5):
    """Get top queries (mock data without database)"""
    try:
        # Without database, return sample data
        return [
            TopQuery(query="How to file GST returns?", count=15, category="GST"),
            TopQuery(query="Setup inventory tracking", count=12, category="Inventory"),
            TopQuery(query="Configure ERP system", count=10, category="ERP"),
            TopQuery(query="Generate invoice reports", count=8, category="Billing"),
            TopQuery(query="Multi-location setup", count=6, category="Configuration")
        ][:limit]

    except Exception as e:
        logger.error(f"Error fetching top queries: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching top queries: {str(e)}")


# CRUD Operations for Knowledge Base
@router.get("/knowledge-base", response_model=List[KnowledgeBaseEntry])
async def get_knowledge_base_entries(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    document_type: Optional[str] = None
):
    """Get knowledge base entries from Pinecone"""
    try:
        result = pinecone_doc_service.list_documents(
            document_type=document_type,
            is_active=True,
            search=search,
            skip=skip,
            limit=limit
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching knowledge base entries: {result.get('error', 'Unknown error')}"
            )

        entries = []
        for doc in result["documents"]:
            entries.append(KnowledgeBaseEntry(
                id=doc["id"],
                title=doc["title"],
                document_type=doc["document_type"],
                industry_type=doc["industry_type"],
                language=doc["language"],
                is_active=doc["is_active"],
                created_at=doc["created_at"],
                chunk_count=doc["chunk_count"]
            ))

        return entries

    except Exception as e:
        logger.error(f"Error fetching knowledge base entries: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching knowledge base entries: {str(e)}")


@router.post("/knowledge-base", response_model=Dict[str, Any])
async def create_knowledge_base_entry(entry: KnowledgeBaseCreate):
    """Create a new knowledge base entry in Pinecone"""
    try:
        start_time = time.time()

        result = pinecone_doc_service.create_document(
            title=entry.title,
            content=entry.content,
            document_type=entry.document_type,
            industry_type=entry.industry_type,
            language=entry.language
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating knowledge base entry: {result.get('error', 'Unknown error')}"
            )

        total_time = int((time.time() - start_time) * 1000)

        return {
            "id": result["document_id"],
            "message": f"Knowledge base entry created successfully with {result['chunks_created']} chunks",
            "status": "success",
            "chunks_created": result["chunks_created"],
            "embeddings_created": result["chunks_created"],  # Same as chunks in Pinecone
            "processing_time_ms": total_time
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating knowledge base entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating knowledge base entry: {str(e)}")


@router.put("/knowledge-base/{entry_id}", response_model=Dict[str, Any])
async def update_knowledge_base_entry(
    entry_id: str,
    entry_update: KnowledgeBaseUpdate
):
    """Update a knowledge base entry in Pinecone"""
    try:
        result = pinecone_doc_service.update_document(
            document_id=entry_id,
            title=entry_update.title,
            content=entry_update.content,
            document_type=entry_update.document_type,
            industry_type=entry_update.industry_type,
            language=entry_update.language,
            is_active=entry_update.is_active
        )

        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail="Knowledge base entry not found or update failed"
            )

        content_changed = entry_update.content is not None

        return {
            "id": entry_id,
            "message": result.get("message", "Knowledge base entry updated successfully"),
            "status": "success",
            "content_changed": content_changed,
            "chunks_updated": result.get("chunks_updated", 0),
            "embeddings_updated": result.get("chunks_updated", 0)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating knowledge base entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating knowledge base entry: {str(e)}")


@router.get("/debug/document-ids", response_model=Dict[str, Any])
async def debug_document_ids():
    """Debug endpoint to list all document IDs in Pinecone"""
    try:
        docs = pinecone_doc_service.list_documents(
            limit=100,
            is_active=True
        )
        
        doc_ids = [doc["id"] for doc in docs["documents"]]
        
        return {
            "success": True,
            "total_documents": len(doc_ids),
            "document_ids": doc_ids,
            "first_few_docs": docs["documents"][:3] if docs["documents"] else []
        }
    except Exception as e:
        logger.error(f"Error listing document IDs: {e}")
        return {
            "success": False,
            "error": str(e),
            "document_ids": []
        }


@router.delete("/knowledge-base/{entry_id}", response_model=Dict[str, Any])
async def delete_knowledge_base_entry(entry_id: str):
    """Delete a knowledge base entry from Pinecone (soft delete)"""
    try:
        logger.info(f"Attempting to delete knowledge base entry: {entry_id}")
        
        # First check if document exists in the list
        list_result = pinecone_doc_service.list_documents(limit=1000)
        existing_doc_ids = [doc["id"] for doc in list_result.get("documents", [])]
        
        logger.info(f"Existing document IDs: {existing_doc_ids[:5]}...")  # Log first 5 IDs
        
        if entry_id not in existing_doc_ids:
            logger.warning(f"Document {entry_id} not found in list of existing documents")
            # Check if it might be already deleted (inactive)
            inactive_result = pinecone_doc_service.list_documents(is_active=False, limit=1000)
            inactive_doc_ids = [doc["id"] for doc in inactive_result.get("documents", [])]
            
            if entry_id in inactive_doc_ids:
                return {
                    "id": entry_id,
                    "message": "Knowledge base entry was already deleted",
                    "status": "success",
                    "vectors_deleted": 0
                }
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Knowledge base entry not found: {entry_id}"
                )
        
        result = pinecone_doc_service.delete_document(
            document_id=entry_id,
            soft_delete=True  # Soft delete by default
        )

        logger.info(f"Delete result for {entry_id}: {result}")

        if not result["success"]:
            logger.warning(f"Document deletion failed for: {entry_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Failed to delete knowledge base entry: {entry_id}"
            )

        return {
            "id": entry_id,
            "message": result.get("message", "Knowledge base entry deleted successfully"),
            "status": "success",
            "vectors_deleted": result.get("vectors_deleted", 0)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge base entry {entry_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting knowledge base entry: {str(e)}")


@router.get("/knowledge-base/{entry_id}", response_model=Dict[str, Any])
async def get_knowledge_base_entry(entry_id: str):
    """Get a specific knowledge base entry from Pinecone"""
    try:
        result = pinecone_doc_service.get_document(entry_id)

        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail="Knowledge base entry not found"
            )

        document = result["document"]
        chunks = result["chunks"]

        return {
            "id": document["id"],
            "title": document["title"],
            "content": "\n\n".join([chunk["chunk_text"] for chunk in chunks]),
            "document_type": document["document_type"],
            "industry_type": document["industry_type"],
            "language": document["language"],
            "is_active": document["is_active"],
            "created_at": document["created_at"],
            "updated_at": document["updated_at"],
            "chunk_count": len(chunks),
            "chunks": [
                {
                    "id": f"{entry_id}_chunk_{chunk['chunk_index']}",
                    "content": chunk["chunk_text"][:200] + "..." if len(chunk["chunk_text"]) > 200 else chunk["chunk_text"]
                }
                for chunk in chunks
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching knowledge base entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching knowledge base entry: {str(e)}")


@router.get("/system/status", response_model=Dict[str, Any])
async def get_system_status():
    """Get system status for admin dashboard"""
    try:
        # Check Pinecone connectivity
        analytics = pinecone_doc_service.get_analytics()

        if analytics["success"]:
            return {
                "database_status": "not_used",
                "api_services_status": "online",
                "vector_store_status": "connected",
                "total_documents": analytics["total_documents"],
                "total_chunks": analytics["total_chunks"],
                "total_sessions": 0,  # Not tracked without database
                "storage_type": "pinecone_only",
                "last_updated": datetime.utcnow().isoformat()
            }
        else:
            return {
                "database_status": "not_used",
                "api_services_status": "online",
                "vector_store_status": "error",
                "error": analytics.get("error", "Unknown error"),
                "storage_type": "pinecone_only",
                "last_updated": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "database_status": "not_used",
            "api_services_status": "error",
            "vector_store_status": "error",
            "error": str(e),
            "storage_type": "pinecone_only",
            "last_updated": datetime.utcnow().isoformat()
        }
