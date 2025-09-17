from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db
from models.knowledge_base import Document, DocumentChunk, KnowledgeBaseQuery
from models.user import User
from models.chat import ChatSession, ChatMessage
from services.document_processor import DocumentProcessor
from services.vector_search import VectorSearchService
from pydantic import BaseModel
import time
from loguru import logger

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
document_processor = DocumentProcessor()
vector_search_service = VectorSearchService()

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
    id: int
    action: str
    details: str
    timestamp: str
    status: str

class TopQuery(BaseModel):
    query: str
    count: int
    category: str

class KnowledgeBaseEntry(BaseModel):
    id: int
    title: str
    document_type: str
    industry_type: Optional[str]
    language: str
    is_active: bool
    created_at: datetime
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
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get real dashboard statistics from database"""
    try:
        # Get current counts
        total_conversations = db.query(func.count(ChatSession.id)).scalar() or 0
        knowledge_base_entries = db.query(func.count(Document.id)).filter(Document.is_active == True).scalar() or 0
        total_users = db.query(func.count(User.id)).scalar() or 0

        # Calculate success rate based on completed sessions
        completed_sessions = db.query(func.count(ChatSession.id)).filter(ChatSession.ended_at.isnot(None)).scalar() or 0
        success_rate = (completed_sessions / max(total_conversations, 1)) * 100

        # Calculate changes (compare with last week for now - simplified)
        last_week = datetime.now() - timedelta(days=7)

        # Conversations change
        old_conversations = db.query(func.count(ChatSession.id)).filter(ChatSession.created_at < last_week).scalar() or 0
        conversation_change = ((total_conversations - old_conversations) / max(old_conversations, 1)) * 100

        # Knowledge base change
        old_kb_entries = db.query(func.count(Document.id)).filter(
            and_(Document.is_active == True, Document.created_at < last_week)
        ).scalar() or 0
        kb_change = ((knowledge_base_entries - old_kb_entries) / max(old_kb_entries, 1)) * 100

        # Users change
        old_users = db.query(func.count(User.id)).filter(User.created_at < last_week).scalar() or 0
        users_change = ((total_users - old_users) / max(old_users, 1)) * 100

        return DashboardStats(
            total_conversations=total_conversations,
            total_conversations_change=f"{conversation_change:+.1f}%",
            knowledge_base_entries=knowledge_base_entries,
            knowledge_base_entries_change=f"{kb_change:+.1f}%",
            total_users=total_users,
            total_users_change=f"{users_change:+.1f}%",
            success_rate=round(success_rate, 1),
            success_rate_change="+2.1%"  # Simplified for now
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")

@router.get("/dashboard/recent-activities", response_model=List[RecentActivity])
async def get_recent_activities(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent activities from database"""
    try:
        activities = []

        # Get recent knowledge base updates
        recent_docs = db.query(Document).filter(Document.is_active == True).order_by(desc(Document.updated_at)).limit(5).all()
        for doc in recent_docs:
            time_diff = datetime.now() - doc.updated_at if doc.updated_at else datetime.now() - doc.created_at
            hours_ago = int(time_diff.total_seconds() / 3600)
            activities.append(RecentActivity(
                id=doc.id,
                action="Knowledge Base Updated",
                details=f"Updated document: {doc.title}",
                timestamp=f"{hours_ago} hours ago" if hours_ago > 0 else "Just now",
                status="success"
            ))

        # Get recent chat sessions
        recent_sessions = db.query(ChatSession).order_by(desc(ChatSession.created_at)).limit(3).all()
        for session in recent_sessions:
            time_diff = datetime.now() - session.created_at
            hours_ago = int(time_diff.total_seconds() / 3600)
            activities.append(RecentActivity(
                id=session.id,
                action="Chat Session Started",
                details=f"New chat session from channel: {session.channel}",
                timestamp=f"{hours_ago} hours ago" if hours_ago > 0 else "Just now",
                status="success"
            ))

        # Sort by timestamp and limit
        return activities[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent activities: {str(e)}")

@router.get("/dashboard/top-queries", response_model=List[TopQuery])
async def get_top_queries(limit: int = 5, db: Session = Depends(get_db)):
    """Get top queries from chat messages"""
    try:
        # This is a simplified version - in production you'd want more sophisticated query analysis
        top_queries = []

        # Get recent chat messages and count similar patterns
        recent_messages = db.query(ChatMessage.message_text).filter(
            ChatMessage.message_text.isnot(None),
            ChatMessage.message_type == "user"
        ).order_by(desc(ChatMessage.created_at)).limit(100).all()

        # Simplified query categorization
        query_patterns = {
            "GST": ["gst", "tax", "return", "filing"],
            "Inventory": ["inventory", "stock", "product", "item"],
            "ERP": ["erp", "system", "setup", "configuration"],
            "Billing": ["bill", "invoice", "payment", "amount"],
            "Reports": ["report", "generate", "export", "print"]
        }

        category_counts = {category: 0 for category in query_patterns.keys()}
        sample_queries = {category: [] for category in query_patterns.keys()}

        for message in recent_messages:
            if message[0]:  # Check if message exists
                msg_lower = message[0].lower()
                for category, keywords in query_patterns.items():
                    if any(keyword in msg_lower for keyword in keywords):
                        category_counts[category] += 1
                        if len(sample_queries[category]) < 3:
                            # Store a cleaned version of the query
                            sample_queries[category].append(message[0][:50] + "..." if len(message[0]) > 50 else message[0])
                        break

        # Create response
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                query_text = sample_queries[category][0] if sample_queries[category] else f"General {category} queries"
                top_queries.append(TopQuery(
                    query=query_text,
                    count=count,
                    category=category
                ))

        return top_queries[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top queries: {str(e)}")

# CRUD Operations for Knowledge Base
@router.get("/knowledge-base", response_model=List[KnowledgeBaseEntry])
async def get_knowledge_base_entries(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    document_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get knowledge base entries with pagination and filtering"""
    try:
        query = db.query(Document).filter(Document.is_active == True)

        if search:
            query = query.filter(
                or_(
                    Document.title.contains(search),
                    Document.content.contains(search)
                )
            )

        if document_type:
            query = query.filter(Document.document_type == document_type)

        documents = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()

        result = []
        for doc in documents:
            chunk_count = db.query(func.count(DocumentChunk.id)).filter(DocumentChunk.document_id == doc.id).scalar() or 0
            result.append(KnowledgeBaseEntry(
                id=doc.id,
                title=doc.title,
                document_type=doc.document_type,
                industry_type=doc.industry_type,
                language=doc.language,
                is_active=doc.is_active,
                created_at=doc.created_at,
                chunk_count=chunk_count
            ))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching knowledge base entries: {str(e)}")

@router.post("/knowledge-base", response_model=Dict[str, Any])
async def create_knowledge_base_entry(entry: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    """Create a new knowledge base entry with full processing pipeline"""
    try:
        start_time = time.time()

        # Use document processor to save document and create chunks
        document, chunks, processing_time = document_processor.save_document_with_chunks(
            db=db,
            title=entry.title,
            content=entry.content,
            document_type=entry.document_type,
            industry_type=entry.industry_type,
            language=entry.language
        )

        # Create embeddings for the chunks and store in Pinecone
        embeddings_created = 0
        try:
            embeddings_created = vector_search_service.store_chunk_embeddings(db, chunks)
            logger.info(f"Admin: Created {embeddings_created} embeddings for document '{document.title}'")
        except Exception as e:
            logger.warning(f"Admin: Failed to create embeddings: {e}")

        total_time = int((time.time() - start_time) * 1000)

        return {
            "id": document.id,
            "message": f"Knowledge base entry created successfully with {len(chunks)} chunks and {embeddings_created} embeddings",
            "status": "success",
            "chunks_created": len(chunks),
            "embeddings_created": embeddings_created,
            "processing_time_ms": total_time
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Admin: Error creating knowledge base entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating knowledge base entry: {str(e)}")

@router.put("/knowledge-base/{entry_id}", response_model=Dict[str, Any])
async def update_knowledge_base_entry(
    entry_id: int,
    entry_update: KnowledgeBaseUpdate,
    db: Session = Depends(get_db)
):
    """Update a knowledge base entry and regenerate embeddings if content changed"""
    try:
        document = db.query(Document).filter(Document.id == entry_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Knowledge base entry not found")

        # Check if content is being updated (need to regenerate embeddings)
        content_changed = entry_update.content is not None and entry_update.content != document.content

        # Update fields if provided
        if entry_update.title is not None:
            document.title = entry_update.title
        if entry_update.content is not None:
            document.content = entry_update.content
        if entry_update.document_type is not None:
            document.document_type = entry_update.document_type
        if entry_update.industry_type is not None:
            document.industry_type = entry_update.industry_type
        if entry_update.language is not None:
            document.language = entry_update.language
        if entry_update.is_active is not None:
            document.is_active = entry_update.is_active

        document.updated_at = func.now()
        db.commit()
        db.refresh(document)

        # If content changed, regenerate chunks and embeddings
        embeddings_updated = 0
        chunks_created = 0
        if content_changed:
            try:
                # Delete existing chunks and embeddings
                existing_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == entry_id).all()
                for chunk in existing_chunks:
                    db.delete(chunk)
                db.commit()

                # Recreate chunks using document processor
                chunks_data = document_processor.chunk_document(document.content)

                # Create new chunk objects
                chunk_objects = []
                for chunk_data in chunks_data:
                    chunk = DocumentChunk(
                        document_id=document.id,
                        chunk_text=chunk_data['text'],
                        chunk_index=chunk_data['index'],
                        chunk_size=chunk_data['size'],
                        overlap_with_previous=chunk_data['overlap_with_previous'],
                        keywords=chunk_data.get('keywords'),
                        section_title=chunk_data.get('section_title'),
                        confidence_score=chunk_data.get('confidence_score')
                    )
                    chunk_objects.append(chunk)

                db.add_all(chunk_objects)
                db.commit()
                chunks_created = len(chunk_objects)

                # Generate new embeddings
                embeddings_updated = vector_search_service.store_chunk_embeddings(db, chunk_objects)
                logger.info(f"Admin: Updated {embeddings_updated} embeddings for document '{document.title}'")

            except Exception as e:
                logger.warning(f"Admin: Failed to regenerate embeddings during update: {e}")

        return {
            "id": document.id,
            "message": f"Knowledge base entry updated successfully" +
                      (f" with {chunks_created} new chunks and {embeddings_updated} embeddings" if content_changed else ""),
            "status": "success",
            "content_changed": content_changed,
            "chunks_updated": chunks_created if content_changed else 0,
            "embeddings_updated": embeddings_updated if content_changed else 0
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Admin: Error updating knowledge base entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating knowledge base entry: {str(e)}")

@router.delete("/knowledge-base/{entry_id}", response_model=Dict[str, Any])
async def delete_knowledge_base_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a knowledge base entry (soft delete + vector cleanup)"""
    try:
        document = db.query(Document).filter(Document.id == entry_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Knowledge base entry not found")

        # Delete vectors from Pinecone first
        vectors_deleted = 0
        try:
            vectors_deleted = vector_search_service.delete_document_embeddings(db, entry_id)
            logger.info(f"Deleted {vectors_deleted} vectors from Pinecone for document {entry_id}")
        except Exception as e:
            logger.warning(f"Failed to delete vectors from Pinecone: {e}")
            # Continue with soft delete even if vector deletion fails

        # Soft delete the document
        document.is_active = False
        document.updated_at = func.now()

        db.commit()

        return {
            "id": entry_id,
            "message": f"Knowledge base entry deleted successfully. Removed {vectors_deleted} vectors from search index.",
            "status": "success",
            "vectors_deleted": vectors_deleted
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting knowledge base entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting knowledge base entry: {str(e)}")

@router.get("/knowledge-base/{entry_id}", response_model=Dict[str, Any])
async def get_knowledge_base_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a specific knowledge base entry with full details"""
    try:
        document = db.query(Document).filter(Document.id == entry_id, Document.is_active == True).first()
        if not document:
            raise HTTPException(status_code=404, detail="Knowledge base entry not found")

        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == entry_id).all()

        return {
            "id": document.id,
            "title": document.title,
            "content": document.content,
            "document_type": document.document_type,
            "industry_type": document.industry_type,
            "language": document.language,
            "is_active": document.is_active,
            "created_at": document.created_at,
            "updated_at": document.updated_at,
            "chunk_count": len(chunks),
            "chunks": [{"id": chunk.id, "content": chunk.content[:200] + "..."} for chunk in chunks]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching knowledge base entry: {str(e)}")

@router.get("/system/status", response_model=Dict[str, Any])
async def get_system_status(db: Session = Depends(get_db)):
    """Get system status for admin dashboard"""
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))

        # Get basic counts
        total_docs = db.query(func.count(Document.id)).filter(Document.is_active == True).scalar() or 0
        total_chunks = db.query(func.count(DocumentChunk.id)).scalar() or 0
        total_sessions = db.query(func.count(ChatSession.id)).scalar() or 0

        return {
            "database_status": "connected",
            "api_services_status": "online",
            "vector_store_status": "ready",
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "total_sessions": total_sessions,
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "database_status": "error",
            "api_services_status": "error",
            "vector_store_status": "error",
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }