from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sys

# Add backend directory to path for proper imports in Vercel
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load environment variables
load_dotenv()

# Try to import routes, but handle import errors gracefully for minimal deployment
try:
    from routes.users import router as users_router
    from routes.chat_sessions import router as chat_sessions_router
    from routes.chat_messages import router as chat_messages_router
    from routes.knowledge_base import router as knowledge_router
    from routes.admin import router as admin_router
    routes_available = True
except ImportError as e:
    print(f"Warning: Could not import all routes: {e}")
    routes_available = False

# Create FastAPI instance
app = FastAPI(
    title="Reckon ChatBot API",
    description="RAG-based chatbot API for ReckonSales ERP platform",
    version="1.0.0"
)

# Configure CORS for production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://reckon-user.vercel.app",
        "https://reckon-admin.vercel.app",
        "https://reckon-rag-chatbot-user.vercel.app",
        "https://reckon-rag-chatbot-admin.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

@app.get("/debug")
async def debug():
    """Debug endpoint to check deployment status"""
    return {
        "status": "deployed",
        "routes_available": routes_available,
        "python_path": sys.path[:3],  # Show first 3 paths
        "working_directory": os.getcwd(),
        "backend_dir": backend_dir
    }

# Include routers only if they were successfully imported
if routes_available:
    app.include_router(users_router)
    app.include_router(chat_sessions_router)
    app.include_router(chat_messages_router)
    app.include_router(knowledge_router)
    app.include_router(admin_router)

# For Vercel deployment
app_handler = app

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(app, host=host, port=port)