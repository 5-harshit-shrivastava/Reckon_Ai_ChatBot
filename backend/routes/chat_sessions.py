from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
import sys
import os
import uuid
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db, create_tables
from models.chat import ChatSession, ChatMessage
from models.user import User
from app.chat_schemas import (
    ChatSessionCreate, ChatSessionResponse, ChatSessionUpdate,
    ChatConversationResponse, ChatMessageResponse, ChatSessionAnalytics
)
from app.schemas import APIResponse

router = APIRouter(
    prefix="/api/chat/sessions",
    tags=["chat-sessions"],
    responses={404: {"description": "Not found"}},
)

# Initialize database tables
create_tables()

@router.post("/", response_model=APIResponse)
async def create_chat_session(session_data: ChatSessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session"""
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == session_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check for existing active session
        existing_session = db.query(ChatSession).filter(
            ChatSession.user_id == session_data.user_id,
            ChatSession.is_active == True
        ).first()
        
        if existing_session:
            # Return existing active session
            session_response = ChatSessionResponse(
                id=existing_session.id,
                user_id=existing_session.user_id,
                session_id=existing_session.session_id,
                channel=existing_session.channel,
                language=existing_session.language,
                is_active=existing_session.is_active,
                created_at=existing_session.created_at,
                ended_at=existing_session.ended_at,
                message_count=db.query(ChatMessage).filter(
                    ChatMessage.session_id == existing_session.id
                ).count()
            )
            
            return APIResponse(
                success=True,
                message="Active session already exists",
                data={"session": session_response.dict(), "is_new": False}
            )
        
        # Create new session
        session_uuid = str(uuid.uuid4())
        db_session = ChatSession(
            user_id=session_data.user_id,
            session_id=session_uuid,
            channel=session_data.channel.value,
            language=session_data.language.value
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        # Create system welcome message
        welcome_message = ChatMessage(
            session_id=db_session.id,
            message_type="system",
            message_text=f"Welcome to Reckon Support! How can I help you today?",
            message_metadata=json.dumps({"system_event": "session_started"})
        )
        
        db.add(welcome_message)
        db.commit()
        
        session_response = ChatSessionResponse(
            id=db_session.id,
            user_id=db_session.user_id,
            session_id=db_session.session_id,
            channel=db_session.channel,
            language=db_session.language,
            is_active=db_session.is_active,
            created_at=db_session.created_at,
            ended_at=db_session.ended_at,
            message_count=1
        )
        
        return APIResponse(
            success=True,
            message="Chat session created successfully",
            data={"session": session_response.dict(), "is_new": True}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating chat session: {str(e)}"
        )

@router.get("/{session_id}", response_model=APIResponse)
async def get_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Get chat session by ID"""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        message_count = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).count()
        
        session_response = ChatSessionResponse(
            id=session.id,
            user_id=session.user_id,
            session_id=session.session_id,
            channel=session.channel,
            language=session.language,
            is_active=session.is_active,
            created_at=session.created_at,
            ended_at=session.ended_at,
            message_count=message_count
        )
        
        return APIResponse(
            success=True,
            message="Chat session retrieved successfully",
            data={"session": session_response.dict()}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat session: {str(e)}"
        )

@router.get("/", response_model=APIResponse)
async def list_chat_sessions(
    user_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    channel: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List chat sessions with optional filters"""
    try:
        query = db.query(ChatSession)
        
        # Apply filters
        if user_id is not None:
            query = query.filter(ChatSession.user_id == user_id)
        if is_active is not None:
            query = query.filter(ChatSession.is_active == is_active)
        if channel is not None:
            query = query.filter(ChatSession.channel == channel)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        sessions = query.order_by(desc(ChatSession.created_at)).offset(skip).limit(limit).all()
        
        sessions_data = []
        for session in sessions:
            message_count = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).count()
            
            session_response = ChatSessionResponse(
                id=session.id,
                user_id=session.user_id,
                session_id=session.session_id,
                channel=session.channel,
                language=session.language,
                is_active=session.is_active,
                created_at=session.created_at,
                ended_at=session.ended_at,
                message_count=message_count
            )
            sessions_data.append(session_response.dict())
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(sessions_data)} chat sessions",
            data={
                "sessions": sessions_data,
                "pagination": {
                    "total": total_count,
                    "count": len(sessions_data),
                    "skip": skip,
                    "limit": limit,
                    "has_more": (skip + len(sessions_data)) < total_count
                }
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat sessions: {str(e)}"
        )

@router.put("/{session_id}", response_model=APIResponse)
async def update_chat_session(
    session_id: int, 
    update_data: ChatSessionUpdate, 
    db: Session = Depends(get_db)
):
    """Update chat session"""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Update session fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if field == "language" and value:
                setattr(session, field, value.value)
            else:
                setattr(session, field, value)
        
        db.commit()
        db.refresh(session)
        
        return APIResponse(
            success=True,
            message="Chat session updated successfully",
            data={"session_id": session.id}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating chat session: {str(e)}"
        )

@router.post("/{session_id}/end", response_model=APIResponse)
async def end_chat_session(session_id: int, db: Session = Depends(get_db)):
    """End/close a chat session"""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        if not session.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chat session is already ended"
            )
        
        # End session
        session.is_active = False
        session.ended_at = func.now()
        
        # Add system end message
        end_message = ChatMessage(
            session_id=session.id,
            message_type="system",
            message_text="Chat session ended. Thank you for using Reckon Support!",
            message_metadata=json.dumps({"system_event": "session_ended"})
        )
        
        db.add(end_message)
        db.commit()
        
        return APIResponse(
            success=True,
            message="Chat session ended successfully",
            data={"session_id": session.id, "ended_at": session.ended_at}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ending chat session: {str(e)}"
        )

@router.get("/{session_id}/conversation", response_model=APIResponse)
async def get_full_conversation(
    session_id: int,
    include_system: bool = Query(True),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get full conversation for a chat session"""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Build message query
        messages_query = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)
        
        if not include_system:
            messages_query = messages_query.filter(ChatMessage.message_type != "system")
        
        messages = messages_query.order_by(ChatMessage.created_at).limit(limit).all()
        
        # Convert to response format
        messages_data = []
        for message in messages:
            message_response = ChatMessageResponse(
                id=message.id,
                session_id=message.session_id,
                message_type=message.message_type,
                message_text=message.message_text,
                intent=message.intent,
                confidence_score=message.confidence_score,
                escalated_to_human=message.escalated_to_human,
                response_time_ms=message.response_time_ms,
                message_metadata=message.message_metadata,
                created_at=message.created_at
            )
            messages_data.append(message_response)
        
        session_response = ChatSessionResponse(
            id=session.id,
            user_id=session.user_id,
            session_id=session.session_id,
            channel=session.channel,
            language=session.language,
            is_active=session.is_active,
            created_at=session.created_at,
            ended_at=session.ended_at,
            message_count=len(messages_data)
        )
        
        conversation = ChatConversationResponse(
            session=session_response,
            messages=messages_data,
            total_messages=len(messages_data)
        )
        
        return APIResponse(
            success=True,
            message="Conversation retrieved successfully",
            data={"conversation": conversation.dict()}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation: {str(e)}"
        )

@router.get("/{session_id}/analytics", response_model=APIResponse)
async def get_session_analytics(session_id: int, db: Session = Depends(get_db)):
    """Get analytics for a chat session"""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Calculate analytics
        messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
        
        user_messages = [m for m in messages if m.message_type == "user"]
        assistant_messages = [m for m in messages if m.message_type == "assistant"]
        
        # Calculate average response time
        response_times = [m.response_time_ms for m in assistant_messages if m.response_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else None
        
        # Calculate session duration
        session_duration = None
        if session.ended_at:
            delta = session.ended_at - session.created_at
            session_duration = delta.total_seconds() / 60  # in minutes
        
        # Extract unique intents
        intents = list(set([m.intent for m in messages if m.intent]))
        
        # Check if escalated
        escalated = any(m.escalated_to_human for m in messages)
        
        analytics = ChatSessionAnalytics(
            session_id=session_id,
            total_messages=len(messages),
            user_messages=len(user_messages),
            assistant_messages=len(assistant_messages),
            average_response_time=avg_response_time,
            session_duration_minutes=session_duration,
            intents_detected=intents,
            escalated_to_human=escalated
        )
        
        return APIResponse(
            success=True,
            message="Session analytics retrieved successfully",
            data={"analytics": analytics.dict()}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session analytics: {str(e)}"
        )