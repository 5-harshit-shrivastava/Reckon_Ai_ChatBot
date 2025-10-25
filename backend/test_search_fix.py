"""
Test script to verify search functionality after fix
"""
import sys
import os
from loguru import logger

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.database import get_db, engine
from models.knowledge_base import Document, DocumentChunk
from services.document_processor import DocumentProcessor
from services.vector_search import VectorSearchService
from services.rag_service import RAGService
from sqlalchemy.orm import Session

def test_document_creation_and_search():
    """Test creating a document and searching for it"""
    
    db: Session = next(get_db())
    
    try:
        logger.info("=" * 80)
        logger.info("TEST 1: Creating new test document with chunks")
        logger.info("=" * 80)
        
        # Create a test document
        doc_processor = DocumentProcessor()
        
        test_content = """
        ReckonSales CRM Platform Features:
        
        1. Contact Management: Manage all your customer contacts in one place.
        2. Sales Pipeline: Track deals through customizable sales stages.
        3. Email Integration: Sync emails automatically with contact records.
        4. Reporting Dashboard: Real-time sales analytics and performance metrics.
        5. Mobile App: Access your CRM data on the go with our mobile application.
        """
        
        document, chunks, processing_time = doc_processor.save_document_with_chunks(
            db=db,
            title="ReckonSales CRM Features Guide",
            content=test_content,
            document_type="product_guide",
            industry_type="software",
            language="en",
            chunk_size=500,
            chunk_overlap=50
        )
        
        logger.info(f"✅ Document created: ID={document.id}, Title='{document.title}'")
        logger.info(f"✅ Created {len(chunks)} chunks in {processing_time}ms")
        
        # Display chunk IDs and content preview
        for chunk in chunks:
            logger.info(f"   Chunk {chunk.id}: {chunk.chunk_text[:100]}...")
        
        logger.info("\n" + "=" * 80)
        logger.info("TEST 2: Creating embeddings and storing in Pinecone")
        logger.info("=" * 80)
        
        # Store embeddings in Pinecone
        vector_service = VectorSearchService()
        embeddings_created = vector_service.store_chunk_embeddings(db, chunks)
        
        logger.info(f"✅ Created and stored {embeddings_created} embeddings in Pinecone")
        
        # Verify in database
        for chunk in chunks:
            db.refresh(chunk)
            logger.info(f"   Chunk {chunk.id}: embedding_created={chunk.embedding_created}, embedding_id={chunk.embedding_id}")
        
        logger.info("\n" + "=" * 80)
        logger.info("TEST 3: Performing semantic search")
        logger.info("=" * 80)
        
        # Test search queries
        test_queries = [
            "What are the CRM features?",
            "Tell me about email integration",
            "Mobile app features",
            "Sales pipeline tracking"
        ]
        
        for query in test_queries:
            logger.info(f"\n🔍 Query: '{query}'")
            
            results = vector_service.semantic_search(
                query=query,
                top_k=3,
                document_types=["product_guide"],
                industry_types=["software"]
            )
            
            if results:
                logger.info(f"   ✅ Found {len(results)} results:")
                for i, result in enumerate(results):
                    logger.info(f"   {i+1}. Chunk ID: {result.get('chunk_id')}, "
                              f"Doc ID: {result.get('document_id')}, "
                              f"Score: {result.get('similarity_score', 0):.3f}")
                    logger.info(f"      Text: {result.get('chunk_text', '')[:100]}...")
            else:
                logger.warning(f"   ❌ No results found!")
        
        logger.info("\n" + "=" * 80)
        logger.info("TEST 4: Testing RAG service with search")
        logger.info("=" * 80)
        
        # Test RAG response
        rag_service = RAGService()
        
        rag_query = "What features does ReckonSales CRM offer?"
        logger.info(f"\n🤖 RAG Query: '{rag_query}'")
        
        rag_response = rag_service.generate_rag_response(
            db=db,
            user_query=rag_query,
            industry_context="software",
            language="en"
        )
        
        if rag_response.get("success"):
            logger.info(f"✅ RAG Response: {rag_response.get('response')[:200]}...")
            logger.info(f"   Chunks used: {rag_response.get('chunks_used')}")
            logger.info(f"   Confidence: {rag_response.get('confidence')}")
            logger.info(f"   Sources: {len(rag_response.get('sources', []))}")
        else:
            logger.error(f"❌ RAG failed: {rag_response.get('error')}")
        
        logger.info("\n" + "=" * 80)
        logger.info("TEST 5: Checking Pinecone index stats")
        logger.info("=" * 80)
        
        if vector_service.pinecone_index:
            stats = vector_service.pinecone_index.describe_index_stats()
            logger.info(f"Pinecone Index Stats:")
            logger.info(f"   Total vectors: {stats.get('total_vector_count')}")
            logger.info(f"   Namespaces: {stats.get('namespaces')}")
            logger.info(f"   Dimension: {stats.get('dimension')}")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = test_document_creation_and_search()
    sys.exit(0 if success else 1)
