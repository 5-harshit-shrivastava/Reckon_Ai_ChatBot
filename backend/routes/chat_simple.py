"""
Simple chat routes for user portal - Pinecone only, no database
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import sys
import os
from loguru import logger

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag_service import RAGService
from services.image_analysis_service import ImageAnalysisService

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)

# Initialize RAG service
rag_service = RAGService()


# Request/Response Models
class CreateSessionRequest(BaseModel):
    user_id: int
    channel: str = "web"
    language: str = "en"


class SendMessageRequest(BaseModel):
    session_id: int
    message: str
    user_id: Optional[int] = 1
    channel: Optional[str] = "web"
    language: Optional[str] = "en"


class SessionResponse(BaseModel):
    id: int
    user_id: int
    session_id: str
    channel: str
    language: str
    is_active: bool


class MessageResponse(BaseModel):
    id: int
    session_id: int
    message_text: str
    message_type: str
    confidence_score: Optional[float] = None
    response_time_ms: Optional[int] = None


class SendMessageResponse(BaseModel):
    success: bool
    message: str
    user_message: MessageResponse
    assistant_response: Optional[MessageResponse] = None


@router.post("/sessions/")
async def create_session(request: CreateSessionRequest):
    """
    Create a new chat session (simplified - no database storage)
    """
    try:
        import time
        session_id = int(time.time() * 1000)  # Use timestamp as session ID

        return {
            "success": True,
            "message": "Session created successfully",
            "data": {
                "session": {
                    "id": session_id,
                    "user_id": request.user_id,
                    "session_id": str(session_id),
                    "channel": request.channel,
                    "language": request.language,
                    "is_active": True,
                    "created_at": None,
                    "message_count": 0
                }
            }
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/send")
async def send_message(request: SendMessageRequest):
    """
    Send a message and get AI response (using Pinecone + RAG)
    """
    try:
        import time
        import uuid

        # Generate response using RAG
        rag_result = rag_service.generate_rag_response(
            db=None,  # No database
            user_query=request.message,
            session_id=request.session_id,
            user_id=request.user_id,
            industry_context=None,
            language=request.language
        )

        # Create user message
        user_message = MessageResponse(
            id=int(time.time() * 1000),
            session_id=request.session_id,
            message_text=request.message,
            message_type="user"
        )

        # Create assistant message
        assistant_message = MessageResponse(
            id=int(time.time() * 1000) + 1,
            session_id=request.session_id,
            message_text=rag_result.get("response", "Sorry, I couldn't generate a response."),
            message_type="assistant",
            confidence_score=rag_result.get("confidence", 0.7),
            response_time_ms=rag_result.get("processing_time_ms", 0)
        )

        return {
            "success": True,
            "message": "Message sent successfully",
            "data": {
                "sources": rag_result.get("sources", []),
                "chunks_used": rag_result.get("chunks_used", 0)
            },
            "user_message": user_message.dict(),
            "assistant_response": assistant_message.dict(),
            "session_info": {
                "id": request.session_id,
                "is_active": True
            }
        }

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Image Analysis Endpoints

@router.post("/analyze-image")
async def analyze_uploaded_image(image: UploadFile = File(...)):
    """
    Analyze uploaded image and generate relevant business questions
    
    This endpoint:
    1. Accepts image upload from frontend
    2. Uses Gemini Vision to analyze the business document
    3. Generates relevant questions user might ask
    4. Returns questions for interactive chat suggestions
    """
    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Expected image, got: {image.content_type}"
            )
        
        # Check file size (limit to 10MB)
        if image.size and image.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        logger.info(f"Analyzing uploaded image: {image.filename} ({image.content_type})")
        
        # Read image data
        image_data = await image.read()
        
        if not image_data:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Initialize image analysis service
        image_service = ImageAnalysisService()
        
        # Analyze image and generate questions
        result = await image_service.analyze_image_and_generate_questions(
            image_data=image_data,
            filename=image.filename or "uploaded_document"
        )
        
        if result["success"]:
            logger.info(f"Successfully analyzed {image.filename}: {len(result['questions'])} questions generated")
            
            return {
                "success": True,
                "message": f"Found {len(result['questions'])} relevant questions from your {result['document_type']}",
                "questions": result["questions"],
                "document_info": {
                    "type": result["document_type"],
                    "filename": result["filename"],
                    "key_information": result["key_information"]
                },
                "analysis_method": result["analysis_method"]
            }
        else:
            logger.error(f"Image analysis failed for {image.filename}: {result.get('error', 'Unknown error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to analyze image: {result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error analyzing image {image.filename if image else 'unknown'}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing image: {str(e)}"
        )


@router.get("/test-vision")
async def test_vision_capabilities():
    """
    Test endpoint to verify Gemini Vision API is working
    """
    try:
        image_service = ImageAnalysisService()
        is_working = image_service.test_connection()
        
        return {
            "vision_api_available": is_working,
            "service": "gemini_vision",
            "status": "ready" if is_working else "error"
        }
        
    except Exception as e:
        logger.error(f"Vision test failed: {e}")
        return {
            "vision_api_available": False,
            "service": "gemini_vision", 
            "status": "error",
            "error": str(e)
        }
