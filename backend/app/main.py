from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sys
import re

# Add backend directory to path for proper imports in Vercel
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load environment variables
load_dotenv()

# Try to import routes, but handle import errors gracefully for minimal deployment
import traceback
routes_available = False
import_error_message = ""

try:
    # Using Pinecone-only routes (no PostgreSQL/Neon database)
    from routes.knowledge_base_pinecone import router as knowledge_router
    from routes.admin_pinecone import router as admin_router
    routes_available = True
    print("✅ Routes imported successfully")
except ImportError as e:
    import_error_message = f"Import error: {str(e)}"
    print(f"❌ Warning: Could not import all routes: {e}")
    traceback.print_exc()
except Exception as e:
    import_error_message = f"Unexpected error: {str(e)}"
    print(f"❌ Unexpected error importing routes: {e}")
    traceback.print_exc()

# Create FastAPI instance
app = FastAPI(
    title="Reckon ChatBot API",
    description="RAG-based chatbot API - Pinecone Only",
    version="2.0.0"
)

# Configure CORS for production deployment

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+",
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
        "message": "Reckon ChatBot API is running - Pinecone Only",
        "version": "2.0.0",
        "storage": "pinecone_only"
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
        "import_error": import_error_message if not routes_available else None,
        "python_path": sys.path[:3],  # Show first 3 paths
        "working_directory": os.getcwd(),
        "backend_dir": backend_dir
    }

# Include routers only if they were successfully imported
if routes_available:
    app.include_router(knowledge_router)
    app.include_router(admin_router)

# For Vercel deployment
app_handler = app

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(app, host=host, port=port)