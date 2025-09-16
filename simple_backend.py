#!/usr/bin/env python3
"""
Simple backend server to demonstrate frontend-backend connection
This version runs without AI/ML dependencies for quick testing
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import time

# Create FastAPI instance
app = FastAPI(
    title="Reckon ChatBot API (Simple)",
    description="Simplified RAG-based chatbot API for testing frontend connection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data models
class SendMessageRequest(BaseModel):
    session_id: int
    message: str
    user_id: Optional[int] = 1
    channel: Optional[str] = "web"
    language: Optional[str] = "en"

class ChatMessage(BaseModel):
    id: int
    session_id: int
    message_text: str
    message_type: str
    escalated_to_human: bool = False
    response_time_ms: Optional[int] = None
    created_at: str

class ChatSession(BaseModel):
    id: int
    user_id: int
    session_id: str
    channel: str
    language: str
    is_active: bool
    created_at: str
    ended_at: Optional[str] = None
    message_count: Optional[int] = 0

class SendMessageResponse(BaseModel):
    success: bool
    message: str
    data: dict
    user_message: ChatMessage
    assistant_response: Optional[ChatMessage] = None
    session_info: ChatSession

class CreateSessionRequest(BaseModel):
    user_id: int
    channel: Optional[str] = "web"
    language: Optional[str] = "en"

# In-memory storage for demo
sessions = {}
messages = {}
session_counter = 1
message_counter = 1

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Reckon ChatBot API (Simple)",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Reckon ChatBot API is running",
        "version": "1.0.0"
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint for testing"""
    return {"message": "pong"}

@app.post("/api/chat/sessions", response_model=ChatSession)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session"""
    global session_counter

    session = ChatSession(
        id=session_counter,
        user_id=request.user_id,
        session_id=f"session-{session_counter}-{int(time.time())}",
        channel=request.channel,
        language=request.language,
        is_active=True,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        message_count=0
    )

    sessions[session_counter] = session
    session_counter += 1

    return session

@app.post("/api/chat/messages/send", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest):
    """Send a message and get AI response"""
    global message_counter

    # Check if session exists
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")

    session = sessions[request.session_id]

    # Create user message
    user_message = ChatMessage(
        id=message_counter,
        session_id=request.session_id,
        message_text=request.message,
        message_type="user",
        escalated_to_human=False,
        response_time_ms=100,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    messages[message_counter] = user_message
    message_counter += 1

    # Generate simple AI response
    ai_response_text = generate_simple_response(request.message)

    # Create assistant message
    assistant_message = ChatMessage(
        id=message_counter,
        session_id=request.session_id,
        message_text=ai_response_text,
        message_type="assistant",
        escalated_to_human=False,
        response_time_ms=500,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    messages[message_counter] = assistant_message
    message_counter += 1

    # Update session message count
    session.message_count += 2

    return SendMessageResponse(
        success=True,
        message="Message sent successfully",
        data={"processing_time": 500, "model": "simple-mock"},
        user_message=user_message,
        assistant_response=assistant_message,
        session_info=session
    )

def generate_simple_response(user_message: str) -> str:
    """Generate a simple response based on keywords"""
    message_lower = user_message.lower()

    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'namaste']):
        return "Hello! Welcome to Reckon Support. How can I help you today?"

    elif any(word in message_lower for word in ['erp', 'advantage', 'benefit']):
        return "Reckon ERP offers many advantages including:\n• Integrated billing and inventory\n• Real-time GST compliance\n• Multi-location support\n• Automated reporting\n• Cloud accessibility\n\nWould you like to know more about any specific feature?"

    elif any(word in message_lower for word in ['gst', 'tax', 'compliance']):
        return "For GST compliance, Reckon helps with:\n• Automatic GST calculation\n• GSTR-1, GSTR-3B filing\n• Input tax credit management\n• E-way bill generation\n• Compliance reports\n\nWhat specific GST help do you need?"

    elif any(word in message_lower for word in ['inventory', 'stock', 'warehouse']):
        return "Reckon's inventory management includes:\n• Real-time stock tracking\n• Low stock alerts\n• Batch/serial tracking\n• Multi-warehouse management\n• Purchase-sales integration\n\nWhich inventory feature interests you?"

    elif any(word in message_lower for word in ['billing', 'invoice', 'payment']):
        return "Our billing system offers:\n• Professional invoice templates\n• Automatic tax calculations\n• Payment tracking\n• Recurring billing\n• Payment gateway integration\n\nHow can I assist with billing?"

    elif any(word in message_lower for word in ['price', 'cost', 'plan', 'pricing']):
        return "Reckon offers flexible pricing plans:\n• Starter Plan: ₹999/month\n• Professional: ₹1,999/month\n• Enterprise: Custom pricing\n\nAll plans include GST compliance and support. Would you like a detailed comparison?"

    elif any(word in message_lower for word in ['demo', 'trial', 'test']):
        return "Great! I can arrange a free demo for you:\n• 30-minute personalized demo\n• See all features in action\n• Ask questions to our experts\n• Free 15-day trial\n\nShall I schedule a demo for you?"

    elif any(word in message_lower for word in ['support', 'help', 'contact']):
        return "Our support team is here to help:\n• 24/7 phone support: +91-522-XXXXXX\n• Email: support@reckonsales.in\n• Live chat on website\n• Video call support\n• Knowledge base\n\nWhat kind of support do you need?"

    else:
        return f"Thank you for your question about '{user_message}'. I'm here to help with all Reckon-related queries.\n\nI can assist you with:\n• ERP and billing solutions\n• GST compliance\n• Inventory management\n• Pricing and demos\n• Technical support\n\nCould you please provide more specific details?"

# Admin endpoints for dashboard
@app.get("/api/admin/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return {
        "total_conversations": len(sessions),
        "total_conversations_change": "+12%",
        "knowledge_base_entries": 150,
        "knowledge_base_entries_change": "+5%",
        "total_users": 45,
        "total_users_change": "+8%",
        "success_rate": 94.5,
        "success_rate_change": "+2.1%"
    }

@app.get("/api/admin/dashboard/recent-activities")
async def get_recent_activities():
    """Get recent activities"""
    return [
        {
            "id": 1,
            "action": "New chat session created",
            "details": "User started conversation about GST compliance",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "success"
        },
        {
            "id": 2,
            "action": "Knowledge base updated",
            "details": "Added new billing documentation",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "success"
        }
    ]

@app.get("/api/admin/dashboard/top-queries")
async def get_top_queries():
    """Get top queries"""
    return [
        {"query": "GST compliance", "count": 45, "category": "Tax"},
        {"query": "Inventory management", "count": 32, "category": "Operations"},
        {"query": "Billing setup", "count": 28, "category": "Finance"},
        {"query": "ERP benefits", "count": 22, "category": "General"},
        {"query": "Pricing plans", "count": 18, "category": "Sales"}
    ]

if __name__ == "__main__":
    print("Starting Reckon ChatBot API (Simple Version)")
    print("This version runs without AI/ML dependencies for testing")
    print("Backend will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )