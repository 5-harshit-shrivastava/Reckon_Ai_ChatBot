#!/usr/bin/env python3
"""
Fix embeddings script - Create embeddings for all existing document chunks
"""
import os
import sys
sys.path.append('.')

from config.database import get_db
from models.knowledge_base import DocumentChunk
from services.vector_search import VectorSearchService
from loguru import logger

def fix_embeddings():
    """Create embeddings for all document chunks"""
    try:
        # Initialize services
        vs = VectorSearchService()
        db = next(get_db())

        # Get all chunks
        all_chunks = db.query(DocumentChunk).all()
        logger.info(f"Found {len(all_chunks)} total chunks")

        if not all_chunks:
            logger.info("No chunks found. Add documents through admin portal first.")
            return

        # Reset embedding status and recreate all
        for chunk in all_chunks:
            chunk.embedding_created = False
            chunk.embedding_id = None

        db.commit()
        logger.info("Reset embedding status for all chunks")

        # Create embeddings in batches
        batch_size = 10
        total_created = 0

        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: chunks {i+1} to {min(i+batch_size, len(all_chunks))}")

            try:
                created = vs.store_chunk_embeddings(db, batch)
                total_created += created
                logger.info(f"Created {created} embeddings in this batch")
            except Exception as e:
                logger.error(f"Error processing batch: {e}")
                continue

        # Check final status
        stats = vs.pinecone_index.describe_index_stats() if vs.pinecone_index else {}

        logger.info(f"✅ Embedding creation complete!")
        logger.info(f"Total embeddings created: {total_created}")
        logger.info(f"Pinecone vector count: {stats.get('total_vector_count', 0)}")

        db.close()

    except Exception as e:
        logger.error(f"Error in fix_embeddings: {e}")

if __name__ == "__main__":
    fix_embeddings()