from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
import sys
import os
import json
import time
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db, create_tables
from models.chat import ChatSession, ChatMessage
from models.user import User
from app.chat_schemas import (
    ChatMessageCreate, ChatMessageResponse, SendMessageRequest, 
    SendMessageResponse, BulkMessageResponse, MessageType
)
from app.schemas import APIResponse
from services.rag_service import RAGService

router = APIRouter(
    prefix="/api/chat/messages",
    tags=["chat-messages"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
rag_service = RAGService()

# Initialize database tables
create_tables()

@router.post("/", response_model=APIResponse)
async def create_message(message_data: ChatMessageCreate, db: Session = Depends(get_db)):
    """Create a new chat message"""
    try:
        # Verify session exists
        session = db.query(ChatSession).filter(ChatSession.id == message_data.session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        if not session.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add message to inactive session"
            )
        
        # Create message
        metadata_str = None
        if message_data.metadata:
            metadata_str = message_data.metadata if isinstance(message_data.metadata, str) else json.dumps(message_data.metadata)
        
        db_message = ChatMessage(
            session_id=message_data.session_id,
            message_type=message_data.message_type.value,
            message_text=message_data.message_text,
            intent=message_data.intent,
            message_metadata=metadata_str
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        message_response = ChatMessageResponse(
            id=db_message.id,
            session_id=db_message.session_id,
            message_type=db_message.message_type,
            message_text=db_message.message_text,
            intent=db_message.intent,
            confidence_score=db_message.confidence_score,
            escalated_to_human=db_message.escalated_to_human,
            response_time_ms=db_message.response_time_ms,
            message_metadata=db_message.message_metadata,
            created_at=db_message.created_at
        )
        
        return APIResponse(
            success=True,
            message="Message created successfully",
            data={"message": message_response.dict()}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating message: {str(e)}"
        )

@router.post("/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest, db: Session = Depends(get_db)):
    """Send a message and get AI response (simplified for now)"""
    try:
        start_time = time.time()
        
        # Verify session exists and is active
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        if not session.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send message to inactive session"
            )
        
        # Create user message
        user_message_metadata = {
            "channel": request.channel.value,
            "language": request.language.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        user_message = ChatMessage(
            session_id=request.session_id,
            message_type=MessageType.USER.value,
            message_text=request.message,
            message_metadata=json.dumps(user_message_metadata)
        )
        
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Get user info for personalization
        user = None
        industry_context = None
        if session.user_id:
            user = db.query(User).filter(User.id == session.user_id).first()
            if user:
                industry_context = user.industry_type
        
        # Generate RAG-powered response
        rag_response = rag_service.generate_rag_response(
            db=db,
            user_query=request.message,
            session_id=request.session_id,
            user_id=session.user_id,
            industry_context=industry_context,
            language=request.language.value
        )
        
        # Extract response data
        ai_response_text = rag_response.get("response", "I'm sorry, I couldn't generate a response.")
        detected_intent = detect_simple_intent(request.message)  # Keep for backward compatibility
        response_time = rag_response.get("processing_time_ms", int((time.time() - start_time) * 1000))
        confidence_score = rag_response.get("confidence", 0.7)
        
        # Create assistant response message metadata
        assistant_message_metadata = {
            "intent_detected": detected_intent,
            "response_method": "rag_powered" if rag_response.get("success") else "fallback",
            "language": request.language.value,
            "processing_time_ms": response_time,
            "confidence": confidence_score,
            "chunks_used": rag_response.get("chunks_used", 0),
            "model_used": rag_response.get("model_used"),
            "sources": rag_response.get("sources", [])[:3]  # Include top 3 sources
        }
        
        assistant_message = ChatMessage(
            session_id=request.session_id,
            message_type=MessageType.ASSISTANT.value,
            message_text=ai_response_text,
            intent=detected_intent,
            confidence_score=confidence_score,
            response_time_ms=response_time,
            message_metadata=json.dumps(assistant_message_metadata)
        )
        
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        # Prepare responses
        user_msg_response = ChatMessageResponse(
            id=user_message.id,
            session_id=user_message.session_id,
            message_type=user_message.message_type,
            message_text=user_message.message_text,
            intent=user_message.intent,
            confidence_score=user_message.confidence_score,
            escalated_to_human=user_message.escalated_to_human,
            response_time_ms=user_message.response_time_ms,
            message_metadata=user_message.message_metadata,
            created_at=user_message.created_at
        )
        
        assistant_msg_response = ChatMessageResponse(
            id=assistant_message.id,
            session_id=assistant_message.session_id,
            message_type=assistant_message.message_type,
            message_text=assistant_message.message_text,
            intent=assistant_message.intent,
            confidence_score=assistant_message.confidence_score,
            escalated_to_human=assistant_message.escalated_to_human,
            response_time_ms=assistant_message.response_time_ms,
            message_metadata=assistant_message.message_metadata,
            created_at=assistant_message.created_at
        )
        
        # Get updated session info
        message_count = db.query(ChatMessage).filter(ChatMessage.session_id == request.session_id).count()
        from app.chat_schemas import ChatSessionResponse
        session_info = ChatSessionResponse(
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
        
        return SendMessageResponse(
            success=True,
            message="Message sent and response generated successfully",
            data={
                "conversation_flow": "user_message -> ai_response",
                "response_time_ms": response_time,
                "intent_detected": detected_intent
            },
            user_message=user_msg_response,
            assistant_response=assistant_msg_response,
            session_info=session_info
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending message: {str(e)}"
        )

@router.get("/session/{session_id}", response_model=BulkMessageResponse)
async def get_messages_by_session(
    session_id: int,
    message_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get messages for a specific session"""
    try:
        # Verify session exists
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        query = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)
        
        if message_type:
            query = query.filter(ChatMessage.message_type == message_type)
        
        total_count = query.count()
        messages = query.order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
        
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
        
        return BulkMessageResponse(
            success=True,
            message=f"Retrieved {len(messages_data)} messages for session {session_id}",
            data={
                "session_id": session_id,
                "filter": {"message_type": message_type} if message_type else None
            },
            messages=messages_data,
            pagination={
                "total": total_count,
                "count": len(messages_data),
                "skip": skip,
                "limit": limit,
                "has_more": (skip + len(messages_data)) < total_count
            }
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving messages: {str(e)}"
        )

@router.get("/{message_id}", response_model=APIResponse)
async def get_message(message_id: int, db: Session = Depends(get_db)):
    """Get a specific message by ID"""
    try:
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
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
        
        return APIResponse(
            success=True,
            message="Message retrieved successfully",
            data={"message": message_response.dict()}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving message: {str(e)}"
        )

@router.put("/{message_id}/escalate", response_model=APIResponse)
async def escalate_message(message_id: int, db: Session = Depends(get_db)):
    """Mark message as escalated to human"""
    try:
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        message.escalated_to_human = True
        
        # Update metadata
        current_metadata = {}
        if message.message_metadata:
            try:
                current_metadata = json.loads(message.message_metadata)
            except json.JSONDecodeError:
                pass
        
        current_metadata.update({
            "escalated_at": datetime.utcnow().isoformat(),
            "escalation_reason": "manual_escalation"
        })
        
        message.message_metadata = json.dumps(current_metadata)
        
        db.commit()
        
        # Create system message for escalation
        escalation_message = ChatMessage(
            session_id=message.session_id,
            message_type=MessageType.SYSTEM.value,
            message_text="This conversation has been escalated to a human agent. You will be connected shortly.",
            message_metadata=json.dumps({
                "system_event": "escalation",
                "original_message_id": message_id
            })
        )
        
        db.add(escalation_message)
        db.commit()
        
        return APIResponse(
            success=True,
            message="Message escalated to human successfully",
            data={
                "message_id": message_id,
                "escalated_at": datetime.utcnow().isoformat()
            }
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error escalating message: {str(e)}"
        )

@router.delete("/{message_id}", response_model=APIResponse)
async def delete_message(message_id: int, db: Session = Depends(get_db)):
    """Delete a message (soft delete - for admin use)"""
    try:
        message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Soft delete by updating metadata
        current_metadata = {}
        if message.message_metadata:
            try:
                current_metadata = json.loads(message.message_metadata)
            except json.JSONDecodeError:
                pass
        
        current_metadata.update({
            "deleted_at": datetime.utcnow().isoformat(),
            "deleted": True
        })
        
        message.message_metadata = json.dumps(current_metadata)
        message.message_text = "[Message deleted]"
        
        db.commit()
        
        return APIResponse(
            success=True,
            message="Message deleted successfully",
            data={"message_id": message_id}
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting message: {str(e)}"
        )

@router.post("/rag/query", response_model=APIResponse)
async def query_rag_directly(
    query: str,
    session_id: Optional[int] = None,
    industry_context: Optional[str] = None,
    language: str = "en",
    db: Session = Depends(get_db)
):
    """Direct RAG query endpoint for testing and advanced usage"""
    try:
        # Get user info if session is provided
        user_id = None
        if session_id:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                user_id = session.user_id
                if not industry_context and session.user_id:
                    user = db.query(User).filter(User.id == session.user_id).first()
                    if user:
                        industry_context = user.industry_type
        
        # Generate RAG response
        rag_response = rag_service.generate_rag_response(
            db=db,
            user_query=query,
            session_id=session_id,
            user_id=user_id,
            industry_context=industry_context,
            language=language
        )
        
        return APIResponse(
            success=True,
            message="RAG query processed successfully",
            data={
                "query": query,
                "response": rag_response.get("response"),
                "confidence": rag_response.get("confidence"),
                "sources": rag_response.get("sources", []),
                "processing_time_ms": rag_response.get("processing_time_ms"),
                "chunks_used": rag_response.get("chunks_used"),
                "model_used": rag_response.get("model_used"),
                "industry_context": industry_context,
                "success": rag_response.get("success")
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing RAG query: {str(e)}"
        )

@router.post("/embeddings/create", response_model=APIResponse)
async def create_embeddings(db: Session = Depends(get_db)):
    """Create embeddings for existing document chunks"""
    try:
        result = rag_service.create_embeddings_for_existing_chunks(db)
        
        return APIResponse(
            success=result.get("success", False),
            message=result.get("message"),
            data={
                "processed": result.get("processed", 0),
                "total_chunks": result.get("total_chunks", 0)
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating embeddings: {str(e)}"
        )

# Helper functions for simple AI responses (will be replaced with real AI later)
def detect_simple_intent(message: str) -> str:
    """Simple rule-based intent detection"""
    message_lower = message.lower()
    
    # Reckon-specific intents
    if any(word in message_lower for word in ["order", "status", "track", "delivery"]):
        return "order_status"
    elif any(word in message_lower for word in ["bill", "invoice", "payment", "gst"]):
        return "billing"
    elif any(word in message_lower for word in ["inventory", "stock", "item", "product"]):
        return "inventory"
    elif any(word in message_lower for word in ["error", "bug", "problem", "issue", "not working"]):
        return "technical_support"
    elif any(word in message_lower for word in ["help", "how", "guide", "tutorial"]):
        return "help_request"
    elif any(word in message_lower for word in ["demo", "trial", "pricing", "plan"]):
        return "sales_inquiry"
    elif any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good evening"]):
        return "greeting"
    else:
        return "general_query"

def generate_simple_response(message: str, intent: str, language) -> str:
    """Generate simple rule-based responses"""
    
    responses = {
        "en": {
            "greeting": "Hello! Welcome to Reckon Support. How can I assist you today?",
            "order_status": "I can help you track your order. Please provide your order number or email address.",
            "billing": "I can assist with billing queries. What specific billing information do you need?",
            "inventory": "For inventory queries, I can help you check stock levels or product information. What would you like to know?",
            "technical_support": "I understand you're experiencing a technical issue. Can you provide more details about the problem?",
            "help_request": "I'm here to help! What specific topic would you like assistance with?",
            "sales_inquiry": "Thank you for your interest in Reckon! I can provide information about our plans and features. What would you like to know?",
            "general_query": "I'm here to help with your Reckon-related questions. Can you please provide more details about what you need assistance with?"
        },
        "hi": {
            "greeting": "नमस्ते! Reckon Support में आपका स्वागत है। आज मैं आपकी कैसे सहायता कर सकता हूँ?",
            "order_status": "मैं आपके ऑर्डर को ट्रैक करने में मदद कर सकता हूँ। कृपया अपना ऑर्डर नंबर या ईमेल पता प्रदान करें।",
            "billing": "मैं बिलिंग प्रश्नों में सहायता कर सकता हूँ। आपको किस विशिष्ट बिलिंग जानकारी की आवश्यकता है?",
            "inventory": "इन्वेंट्री प्रश्नों के लिए, मैं स्टॉक स्तर या उत्पाद जानकारी की जांच में आपकी सहायता कर सकता हूँ। आप क्या जानना चाहते हैं?",
            "technical_support": "मैं समझता हूँ कि आपको तकनीकी समस्या हो रही है। क्या आप समस्या के बारे में और विवरण दे सकते हैं?",
            "help_request": "मैं यहाँ मदद के लिए हूँ! आप किस विशिष्ट विषय पर सहायता चाहते हैं?",
            "sales_inquiry": "Reckon में आपकी रुचि के लिए धन्यवाद! मैं हमारे प्लान और सुविधाओं के बारे में जानकारी प्रदान कर सकता हूँ। आप क्या जानना चाहते हैं?",
            "general_query": "मैं आपके Reckon-संबंधी प्रश्नों में मदद के लिए यहाँ हूँ। कृपया बताएं कि आपको किस चीज़ में सहायता चाहिए?"
        }
    }
    
    lang = language.value if hasattr(language, 'value') else str(language)
    return responses.get(lang, responses["en"]).get(intent, responses[lang]["general_query"])