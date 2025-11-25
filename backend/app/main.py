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

# Load environment variables from backend/.env file
env_path = os.path.join(backend_dir, '.env')
load_dotenv(dotenv_path=env_path, override=True)

# Try to import routes, but handle import errors gracefully for minimal deployment
import traceback
routes_available = False
import_error_message = ""

try:
    # Using Pinecone-only routes (no PostgreSQL/Neon database)
    from routes.knowledge_base_pinecone import router as knowledge_router
    from routes.admin_pinecone import router as admin_router
    from routes.chat_simple import router as chat_router
    from routes.admin_utils import router as admin_utils_router
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
    version="2.0.2"
)

# Configure CORS for production deployment
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://reckonadmin.vercel.app",
    "https://reckonadmin-wine.vercel.app",
    "https://reckonadmin-lr7tlw0c6-5-harshit-shrivastavas-projects.vercel.app",
    "https://bckreckon.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://(reckon(user|admin)(-[a-z0-9]+)*\.vercel\.app|reckon.*\.vercel\.app)",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Reckon ChatBot API v2",
        "version": "2.0.2",
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
        "backend_dir": backend_dir,
        "env_vars_available": {
            "GEMINI_API_KEY": "SET" if os.getenv("GEMINI_API_KEY") else "NOT SET",
            "PINECONE_API_KEY": "SET" if os.getenv("PINECONE_API_KEY") else "NOT SET",
            "HUGGINGFACE_API_TOKEN": "SET" if os.getenv("HUGGINGFACE_API_TOKEN") else "NOT SET"
        }
    }

@app.get("/debug/search-status")
async def debug_search_status():
    """Debug search service status"""
    try:
        # Import here to avoid startup issues
        from new_vector_search import NewVectorSearchService
        
        search_service = NewVectorSearchService()
        
        status = {
            "pinecone_connected": bool(search_service.pinecone_index),
            "hf_client_available": bool(search_service.hf_client),
            "index_name": search_service.index_name,
            "embedding_model": search_service.embedding_model,
            "vector_dimension": search_service.vector_dimension
        }
        
        # Test index stats if connected
        if search_service.pinecone_index:
            try:
                index_stats = search_service.pinecone_index.describe_index_stats()
                status["index_stats"] = {
                    "total_vector_count": index_stats.total_vector_count,
                    "namespaces": list(index_stats.namespaces.keys()) if index_stats.namespaces else [],
                    "dimension": index_stats.dimension
                }
                
                # Check our specific namespace
                if "reckon-knowledge-base" in index_stats.namespaces:
                    namespace_stats = index_stats.namespaces["reckon-knowledge-base"]
                    status["reckon_namespace"] = {
                        "vector_count": namespace_stats.vector_count
                    }
                else:
                    status["reckon_namespace"] = {"vector_count": 0, "error": "Namespace not found"}
                    
            except Exception as e:
                status["index_stats_error"] = str(e)
        
        # Test embedding creation
        try:
            test_embedding = search_service.create_embedding("test query", is_query=True)
            status["embedding_test"] = {
                "success": True,
                "dimensions": len(test_embedding) if test_embedding else 0,
                "sample_values": test_embedding[:3] if test_embedding else []
            }
        except Exception as e:
            status["embedding_test"] = {
                "success": False,
                "error": str(e)
            }
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/debug/test-search/{query}")
async def debug_test_search(query: str):
    """Test search with specific query"""
    try:
        from new_vector_search import NewVectorSearchService
        
        search_service = NewVectorSearchService()
        
        results = search_service.semantic_search(
            query=query,
            top_k=10,
            min_confidence=0.0
        )
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "chunk_text": result.get("chunk_text", "")[:200],
                "similarity_score": result.get("similarity_score", 0),
                "document_title": result.get("document_title", ""),
                "document_type": result.get("document_type", ""),
                "metadata_keys": list(result.get("metadata", {}).keys())
            })
        
        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "results": formatted_results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

# Include routers only if they were successfully imported
if routes_available:
    app.include_router(knowledge_router)
    app.include_router(admin_router)
    app.include_router(chat_router)
    app.include_router(admin_utils_router)

# For Vercel deployment
app_handler = app

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(app, host=host, port=port)