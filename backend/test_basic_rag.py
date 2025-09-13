#!/usr/bin/env python3
"""
Basic RAG functionality test - tests core components without external dependencies
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

def test_document_processor():
    """Test document processing functionality"""
    print("🔄 Testing document processor...")
    
    try:
        from services.document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Test content
        test_content = """
        ReckonSales Billing Guide
        
        Step 1: Creating an Invoice
        To create a new invoice in ReckonSales:
        1. Navigate to the Billing section
        2. Click on "Create New Invoice"
        3. Select the customer from dropdown
        4. Add items and quantities
        5. Apply GST rates as per regulations
        6. Save and generate the invoice
        
        Step 2: Managing Inventory
        For inventory management:
        - Access the Inventory module
        - Check stock levels regularly
        - Set low stock alerts
        - Update item prices when needed
        
        Error: "GST calculation failed"
        Solution: Check if GST rates are properly configured in settings.
        """
        
        # Test chunking
        chunks = processor.chunk_document(test_content, chunk_size=400, overlap=50)
        
        print(f"✅ Document processed into {len(chunks)} chunks")
        
        # Display chunk information
        for i, chunk in enumerate(chunks):
            print(f"   Chunk {i+1}:")
            print(f"     Length: {chunk['size']} chars")
            print(f"     Confidence: {chunk.get('confidence_score', 0):.2f}")
            if chunk.get('section_title'):
                print(f"     Section: {chunk['section_title']}")
            if chunk.get('keywords'):
                print(f"     Keywords: {chunk['keywords']}")
            print(f"     Preview: {chunk['text'][:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Document processor test failed: {e}")
        return False

def test_database_models():
    """Test database model imports and basic functionality"""
    print("🔄 Testing database models...")
    
    try:
        from models.knowledge_base import Document, DocumentChunk, KnowledgeBaseQuery
        from models.user import User
        from models.chat import ChatSession, ChatMessage
        from config.database import Base
        
        print("✅ All models imported successfully")
        
        # Test model attributes
        doc_attrs = [attr for attr in dir(Document) if not attr.startswith('_')]
        chunk_attrs = [attr for attr in dir(DocumentChunk) if not attr.startswith('_')]
        
        print(f"✅ Document model has {len(doc_attrs)} attributes")
        print(f"✅ DocumentChunk model has {len(chunk_attrs)} attributes")
        
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False

def test_rag_service_fallback():
    """Test RAG service fallback functionality"""
    print("🔄 Testing RAG service fallback responses...")
    
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        
        # Test fallback responses
        test_queries = [
            ("How do I create an invoice?", "en"),
            ("GST calculation error", "en"),
            ("What is inventory management?", "en"),
            ("बिलिंग कैसे करें?", "hi"),
        ]
        
        print("✅ RAG service initialized")
        
        for query, language in test_queries:
            try:
                fallback = rag_service._get_fallback_response(query, language)
                print(f"   Query: {query} ({language})")
                print(f"   Fallback: {fallback[:80]}...")
                print()
            except Exception as e:
                print(f"   ⚠️ Fallback failed for '{query}': {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG service test failed: {e}")
        return False

def test_api_schemas():
    """Test API schema imports"""
    print("🔄 Testing API schemas...")
    
    try:
        from app.chat_schemas import SendMessageRequest, SendMessageResponse
        from app.knowledge_schemas import DocumentCreate, DocumentSearchRequest
        from app.schemas import APIResponse
        
        print("✅ Chat schemas imported successfully")
        print("✅ Knowledge base schemas imported successfully") 
        print("✅ Base API schemas imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ API schemas test failed: {e}")
        return False

def test_configuration():
    """Test configuration and environment setup"""
    print("🔄 Testing configuration...")
    
    try:
        # Check environment variables that should be configured
        required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY", "SECRET_KEY"]
        
        print("Environment variables status:")
        for var in required_vars:
            value = os.getenv(var)
            status = "✅ Set" if value else "⚠️ Not set"
            print(f"   {var}: {status}")
        
        # Check if .env file exists
        env_file = Path(".env")
        env_example = Path(".env.example")
        
        print(f"\nConfiguration files:")
        print(f"   .env file: {'✅ Exists' if env_file.exists() else '⚠️ Missing'}")
        print(f"   .env.example: {'✅ Exists' if env_example.exists() else '❌ Missing'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🚀 Starting Basic RAG Implementation Tests\n")
    
    tests = [
        ("Document Processor", test_document_processor),
        ("Database Models", test_database_models),
        ("RAG Service Fallback", test_rag_service_fallback),
        ("API Schemas", test_api_schemas),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Summary: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All basic tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("\n📝 Next Steps:")
    print("1. Configure API keys in .env file for full functionality")
    print("2. Install missing dependencies: pip install sentence-transformers")
    print("3. Run the FastAPI server: uvicorn app.main:app --reload")
    print("4. Test the endpoints using the provided test script or API client")

if __name__ == "__main__":
    main()