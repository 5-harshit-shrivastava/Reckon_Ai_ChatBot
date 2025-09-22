#!/usr/bin/env python3
"""
Test single embedding creation to verify the pipeline
"""
import os
import sys
sys.path.append('.')

from config.database import get_db
from models.knowledge_base import DocumentChunk
from services.vector_search import VectorSearchService
from loguru import logger

def test_single_embedding():
    """Test creating a single embedding"""
    try:
        vs = VectorSearchService()
        db = next(get_db())

        # Get one chunk for testing
        chunk = db.query(DocumentChunk).first()

        if not chunk:
            logger.error("No chunks found")
            return

        logger.info(f"Testing with chunk ID {chunk.id}: {chunk.chunk_text[:100]}...")

        # Reset its embedding status
        chunk.embedding_created = False
        chunk.embedding_id = None
        db.commit()

        # Create embedding
        logger.info("Creating embedding...")
        created = vs.store_chunk_embeddings(db, [chunk])
        logger.info(f"Created: {created}")

        # Check Pinecone
        if vs.pinecone_index:
            stats = vs.pinecone_index.describe_index_stats()
            logger.info(f"Pinecone stats: {stats}")

            # Test search
            if stats.get('total_vector_count', 0) > 0:
                logger.info("Testing search...")
                results = vs.semantic_search('invoice', top_k=1)
                logger.info(f"Search results: {len(results)}")
                if results:
                    logger.info(f"Result: {results[0]}")

        db.close()

    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    test_single_embedding()