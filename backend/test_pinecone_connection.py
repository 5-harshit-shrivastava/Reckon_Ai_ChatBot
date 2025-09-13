#!/usr/bin/env python3
"""
Test Pinecone connection and RAG functionality
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_pinecone_connection():
    """Test Pinecone connection and index creation"""
    print("🔄 Testing Pinecone connection...")
    
    try:
        from pinecone import Pinecone, ServerlessSpec
        
        # Get API key from environment
        api_key = os.getenv("PINECONE_API_KEY")
        
        if not api_key:
            print("❌ PINECONE_API_KEY not found in environment")
            return False
        
        print(f"✅ Found Pinecone API key: {api_key[:10]}...")
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        
        print("✅ Pinecone initialized successfully")
        
        # List existing indexes
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        print(f"✅ Found {len(index_names)} existing indexes: {index_names}")
        
        # Check if our index exists
        index_name = "reckon-chatbot"
        
        if index_name not in index_names:
            print(f"🔄 Creating new index: {index_name}")
            
            # Create index with appropriate dimensions for OpenAI embeddings
            pc.create_index(
                name=index_name,
                dimension=1536,  # OpenAI ada-002 embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            
            print(f"✅ Index '{index_name}' created successfully")
            
            # Wait for index to be ready
            import time
            time.sleep(10)
        else:
            print(f"✅ Index '{index_name}' already exists")
        
        # Connect to the index
        index = pc.Index(index_name)
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"✅ Index stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

def test_vector_search_service():
    """Test the VectorSearchService with Pinecone"""
    print("\n🔄 Testing VectorSearchService...")
    
    try:
        from services.vector_search import VectorSearchService
        
        # Initialize service
        vector_service = VectorSearchService()
        
        if not vector_service.pinecone_index:
            print("❌ Pinecone index not initialized in VectorSearchService")
            return False
        
        print("✅ VectorSearchService initialized with Pinecone")
        
        # Test embedding creation (using local model for now)
        test_text = "How to create an invoice in ReckonSales billing module"
        
        try:
            # Try with local sentence transformers (fallback only)
            embedding = vector_service.create_embedding(test_text)
            print(f"✅ Created fallback embedding with {len(embedding)} dimensions (local)")
        except Exception as e:
            print(f"⚠️ Local embedding failed: {e}")
            return False
        
        # Test basic search (will be empty initially)
        try:
            search_results = vector_service.semantic_search(
                query="invoice creation",
                top_k=3
            )
            print(f"✅ Search completed, found {len(search_results)} results")
        except Exception as e:
            print(f"⚠️ Search failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ VectorSearchService test failed: {e}")
        return False

def test_rag_service():
    """Test the RAG service functionality"""
    print("\n🔄 Testing RAG Service...")
    
    try:
        from services.rag_service import RAGService
        from config.database import get_db
        
        # Initialize RAG service
        rag_service = RAGService()
        print("✅ RAG Service initialized")
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        # Test RAG response generation (will use fallback since no docs yet)
        test_query = "How do I create an invoice in ReckonSales?"
        
        try:
            response = rag_service.generate_rag_response(
                db=db,
                user_query=test_query,
                industry_context="general",
                language="en"
            )
            
            print(f"✅ RAG response generated:")
            print(f"   Success: {response.get('success')}")
            print(f"   Confidence: {response.get('confidence', 0):.2f}")
            print(f"   Processing time: {response.get('processing_time_ms', 0)}ms")
            print(f"   Chunks used: {response.get('chunks_used', 0)}")
            
            if response.get('response'):
                preview = response['response'][:150] + "..." if len(response['response']) > 150 else response['response']
                print(f"   Response: {preview}")
            
            return True
            
        except Exception as e:
            print(f"⚠️ RAG response generation failed: {e}")
            return False
        
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ RAG Service test failed: {e}")
        return False

def test_document_upload_with_embeddings():
    """Test document upload and embedding creation"""
    print("\n🔄 Testing document upload with embeddings...")
    
    try:
        from services.document_processor import DocumentProcessor
        from services.vector_search import VectorSearchService
        from config.database import get_db
        
        # Initialize services
        doc_processor = DocumentProcessor()
        vector_service = VectorSearchService()
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        # Test document content
        test_content = """
        ReckonSales Invoice Creation Guide
        
        Step 1: Login to ReckonSales
        Access your ReckonSales dashboard using your credentials.
        
        Step 2: Navigate to Billing Module
        Click on the "Billing" section in the main navigation menu.
        
        Step 3: Create New Invoice
        1. Click "Create New Invoice" button
        2. Select customer from the dropdown
        3. Add items and quantities
        4. Apply appropriate GST rates
        5. Review and save the invoice
        
        Troubleshooting:
        If you encounter "GST calculation failed" error, check your GST settings in the configuration section.
        """
        
        # Create document and chunks
        document, chunks, processing_time = doc_processor.save_document_with_chunks(
            db=db,
            title="ReckonSales Invoice Guide",
            content=test_content,
            document_type="guide",
            industry_type="general",
            language="en"
        )
        
        print(f"✅ Document created with {len(chunks)} chunks in {processing_time}ms")
        
        # Create embeddings
        embeddings_created = vector_service.store_chunk_embeddings(db, chunks)
        print(f"✅ Created {embeddings_created} embeddings")
        
        # Test search with the new content
        search_results = vector_service.semantic_search(
            query="How to create invoice?",
            top_k=3
        )
        
        print(f"✅ Search found {len(search_results)} results")
        for i, result in enumerate(search_results):
            print(f"   Result {i+1}:")
            print(f"     Similarity: {result.get('similarity_score', 0):.3f}")
            print(f"     Preview: {result.get('chunk_text', '')[:100]}...")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Document upload test failed: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def main():
    """Run all Pinecone and RAG tests"""
    print("🚀 Starting Pinecone and RAG Integration Tests\n")
    
    tests = [
        ("Pinecone Connection", test_pinecone_connection),
        ("Vector Search Service", test_vector_search_service),
        ("RAG Service", test_rag_service),
        ("Document Upload with Embeddings", test_document_upload_with_embeddings)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Testing: {test_name}")
        print('='*60)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - FAILED with exception: {e}")
    
    print(f"\n{'='*60}")
    print(f"Test Summary: {passed}/{total} tests passed")
    print('='*60)
    
    if passed == total:
        print("🎉 All tests passed! Your RAG system is ready to use!")
        print("\n📝 Next Steps:")
        print("1. Start the FastAPI server: uvicorn app.main:app --reload")
        print("2. Upload more documents via API or web interface")
        print("3. Test the chat functionality with real queries")
        print("4. Configure OpenAI API key for enhanced responses")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("\n🔧 Troubleshooting:")
        print("1. Verify Pinecone API key is correct")
        print("2. Check internet connection")
        print("3. Ensure all dependencies are installed")

if __name__ == "__main__":
    main()