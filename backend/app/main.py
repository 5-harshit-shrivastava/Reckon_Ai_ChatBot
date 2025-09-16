from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import routes
from routes.users import router as users_router
from routes.chat_sessions import router as chat_sessions_router
from routes.chat_messages import router as chat_messages_router
from routes.knowledge_base import router as knowledge_router
from routes.test_endpoints import router as test_router
from routes.admin import router as admin_router

# Create FastAPI instance
app = FastAPI(
    title="Reckon ChatBot API",
    description="RAG-based chatbot API for ReckonSales ERP platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Reckon ChatBot API",
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

# Include routers
app.include_router(users_router)
app.include_router(chat_sessions_router)
app.include_router(chat_messages_router)
app.include_router(knowledge_router)
app.include_router(test_router)
app.include_router(admin_router)

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)