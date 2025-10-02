"""
Admin utility routes for cleaning up Pinecone
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from loguru import logger
import os
from pinecone import Pinecone

router = APIRouter(
    prefix="/api/admin/utils",
    tags=["admin-utils"],
)


@router.post("/clear-pinecone-index")
async def clear_pinecone_index() -> Dict[str, Any]:
    """
    DANGER: Clear all vectors from Pinecone index
    Use this to remove old documents
    """
    try:
        # Initialize Pinecone
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            raise HTTPException(status_code=500, detail="Pinecone API key not found")

        pc = Pinecone(api_key=pinecone_api_key)
        index_name = "reckon-bge-large-kb"
        index = pc.Index(index_name)

        # Get stats before deletion
        stats_before = index.describe_index_stats()
        total_vectors_before = stats_before.total_vector_count

        # Delete all vectors in the namespace
        namespace = "reckon-knowledge-base"

        # Pinecone requires you to delete by ID or delete all
        # We'll delete all in the namespace
        index.delete(delete_all=True, namespace=namespace)

        logger.info(f"Cleared {total_vectors_before} vectors from Pinecone namespace: {namespace}")

        return {
            "success": True,
            "message": f"Cleared all vectors from Pinecone index",
            "vectors_deleted": total_vectors_before,
            "namespace": namespace
        }

    except Exception as e:
        logger.error(f"Error clearing Pinecone index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pinecone-stats")
async def get_pinecone_stats() -> Dict[str, Any]:
    """
    Get Pinecone index statistics
    """
    try:
        # Initialize Pinecone
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            raise HTTPException(status_code=500, detail="Pinecone API key not found")

        pc = Pinecone(api_key=pinecone_api_key)
        index_name = "reckon-bge-large-kb"
        index = pc.Index(index_name)

        # Get stats
        stats = index.describe_index_stats()

        return {
            "success": True,
            "index_name": index_name,
            "total_vector_count": stats.total_vector_count,
            "dimension": stats.dimension,
            "namespaces": stats.namespaces
        }

    except Exception as e:
        logger.error(f"Error getting Pinecone stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
