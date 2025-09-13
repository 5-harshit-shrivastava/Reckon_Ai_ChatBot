#!/usr/bin/env python3
"""
Test script for RAG implementation
Tests the basic functionality of the RAG system
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from sqlalchemy.orm import Session
from config.database import get_db, create_tables
from services.document_processor import DocumentProcessor
from services.vector_search import VectorSearchService
from services.rag_service import RAGService
from models.knowledge_base import Document, DocumentChunk
from models.user import User
from models.chat import ChatSession


def test_document_processing():
    """Test document processing and chunking"""
    print("🔄 Testing document processing...")
    
    processor = DocumentProcessor()
    
    # Test document content
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
    
    Step 3: Order Processing
    Order processing workflow:
    1. Receive order from customer
    2. Check inventory availability
    3. Generate delivery note
    4. Update stock levels
    5. Create invoice after delivery
    
    Troubleshooting Common Issues
    
    Error: "GST calculation failed"
    Solution: Check if GST rates are properly configured in settings.
    
    Error: "Inventory not found"
    Solution: Ensure all items are properly added to the inventory master.
    """
    
    # Test chunking
    chunks = processor.chunk_document(test_content, chunk_size=500, overlap=100)
    
    print(f"✅ Document processed into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i+1}: {len(chunk['text'])} chars, confidence: {chunk.get('confidence_score', 0):.2f}")
        if chunk.get('section_title'):
            print(f"      Section: {chunk['section_title']}")
        if chunk.get('keywords'):
            print(f"      Keywords: {chunk['keywords']}")
    
    return chunks


def test_vector_search():
    """Test vector search functionality"""
    print("\n🔄 Testing vector search service...")
    
    vector_service = VectorSearchService()
    
    # Test embedding creation
    test_text = "How to create an invoice in ReckonSales billing module?"
    try:
        embedding = vector_service.create_embedding(test_text, use_openai=False)  # Use local model for testing
        print(f"✅ Created embedding with {len(embedding)} dimensions")
    except Exception as e:
        print(f"⚠️ Embedding creation failed (expected if no API keys): {e}")
        return False
    
    return True


def test_database_operations():
    """Test database operations"""
    print("\n🔄 Testing database operations...")
    
    # Create tables
    create_tables()
    print("✅ Database tables created/verified")
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Test document creation
        processor = DocumentProcessor()
        
        test_doc_content = """
        ReckonSales Quick Start Guide
        
        Welcome to ReckonSales! This guide will help you get started.
        
        Setting up your account:
        1. Log in to your dashboard
        2. Configure company details
        3. Set up GST preferences
        4. Add initial inventory items
        
        Creating your first invoice:
        - Go to Billing → New Invoice
        - Select customer
        - Add items and quantities
        - Review and save
        """
        
        document, chunks, processing_time = processor.save_document_with_chunks(
            db=db,
            title="ReckonSales Quick Start Guide",
            content=test_doc_content,
            document_type="guide",
            industry_type="general",
            language="en"
        )
        
        print(f"✅ Document saved with ID: {document.id}")
        print(f"✅ Created {len(chunks)} chunks in {processing_time}ms")
        
        # Test chunk retrieval
        saved_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).all()
        print(f"✅ Retrieved {len(saved_chunks)} chunks from database")
        
        return document, chunks
        
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        return None, None
    finally:
        db.close()


def test_rag_service():
    """Test RAG service functionality"""
    print("\n🔄 Testing RAG service...")
    
    rag_service = RAGService()
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Test queries
        test_queries = [
            "How do I create an invoice?",
            "What should I do if GST calculation fails?",
            "How to manage inventory?",
            "ReckonSales setup steps"
        ]
        
        for query in test_queries:
            print(f"\n   Query: {query}")
            
            try:
                response = rag_service.generate_rag_response(
                    db=db,
                    user_query=query,
                    industry_context="general",
                    language="en"
                )
                
                print(f"   ✅ Response generated: {response.get('success', False)}")
                print(f"   📊 Confidence: {response.get('confidence', 0):.2f}")
                print(f"   ⏱️ Time: {response.get('processing_time_ms', 0)}ms")
                print(f"   📄 Chunks used: {response.get('chunks_used', 0)}")
                
                if response.get('response'):
                    preview = response['response'][:150] + "..." if len(response['response']) > 150 else response['response']
                    print(f"   💬 Response preview: {preview}")
                
            except Exception as e:
                print(f"   ⚠️ Query failed (expected if no API keys): {e}")
    
    except Exception as e:
        print(f"❌ RAG service test failed: {e}")
    finally:
        db.close()


def test_fallback_responses():
    """Test fallback responses when AI services are unavailable"""
    print("\n🔄 Testing fallback responses...")
    
    rag_service = RAGService()
    
    # Test fallback response generation
    test_queries = [
        ("How do I create an invoice?", "en"),
        ("GST calculation error", "en"),
        ("इनवॉइस कैसे बनाएं?", "hi"),
        ("inventory management", "en")
    ]
    
    for query, language in test_queries:
        fallback = rag_service._get_fallback_response(query, language)
        print(f"   Query: {query} ({language})")
        print(f"   Fallback: {fallback[:100]}...")


def main():
    """Run all tests"""
    print("🚀 Starting RAG Implementation Tests\n")
    
    # Test 1: Document Processing
    chunks = test_document_processing()
    
    # Test 2: Vector Search (will use fallback if no API keys)
    test_vector_search()
    
    # Test 3: Database Operations
    document, db_chunks = test_database_operations()
    
    # Test 4: RAG Service
    test_rag_service()
    
    # Test 5: Fallback Responses
    test_fallback_responses()
    
    print("\n🎉 All tests completed!")
    print("\n📝 Notes:")
    print("   - If you see API key warnings, that's expected for testing")
    print("   - Configure OpenAI and Pinecone API keys in .env for full functionality")
    print("   - The system will use fallback responses when AI services are unavailable")
    print("   - Vector search will use sentence transformers as fallback")


if __name__ == "__main__":
    # Set environment to avoid API key requirements for basic testing
    os.environ["TESTING"] = "true"
    main()