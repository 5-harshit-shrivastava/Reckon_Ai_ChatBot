#!/usr/bin/env python3
"""
Database setup script for RAG system
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

def setup_database():
    """Create all database tables"""
    print("🔄 Setting up database...")
    
    try:
        from config.database import engine, create_tables
        from models.knowledge_base import Document, DocumentChunk, KnowledgeBaseQuery
        from models.user import User
        from models.chat import ChatSession, ChatMessage
        
        # Create all tables
        create_tables()
        
        print("✅ Database tables created successfully")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'users', 'documents', 'document_chunks', 'kb_queries',
            'chat_sessions', 'chat_messages'
        ]
        
        print(f"📊 Found {len(tables)} tables: {tables}")
        
        missing_tables = [t for t in expected_tables if t not in tables]
        if missing_tables:
            print(f"⚠️ Missing tables: {missing_tables}")
        else:
            print("✅ All expected tables are present")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_database_operations():
    """Test basic database operations"""
    print("\n🔄 Testing database operations...")
    
    try:
        from config.database import get_db
        from models.user import User
        from models.knowledge_base import Document
        
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            # Test user creation
            test_user = User(
                name="Test User",
                email="test@reckon.com",
                company_name="Test Company",
                industry_type="general"
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"✅ Created test user with ID: {test_user.id}")
            
            # Test document creation
            test_doc = Document(
                title="Test Document",
                content="This is a test document for the RAG system.",
                document_type="guide",
                industry_type="general",
                language="en",
                file_size=len("This is a test document for the RAG system.")
            )
            
            db.add(test_doc)
            db.commit()
            db.refresh(test_doc)
            
            print(f"✅ Created test document with ID: {test_doc.id}")
            
            # Clean up test data
            db.delete(test_doc)
            db.delete(test_user)
            db.commit()
            
            print("✅ Test data cleaned up")
            
            return True
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def main():
    """Run database setup and tests"""
    print("🚀 Database Setup for RAG System\n")
    
    # Setup database
    if setup_database():
        print("\n" + "="*50)
        
        # Test operations
        test_database_operations()
        
        print("\n" + "="*50)
        print("✅ Database setup completed successfully!")
        print("\n📝 Next Steps:")
        print("1. Run the Pinecone test: python test_pinecone_connection.py")
        print("2. Start the FastAPI server: uvicorn app.main:app --reload")
        print("3. Upload documents and test the RAG functionality")
        print("4. Optional: Configure OpenAI API key for enhanced responses")
    else:
        print("\n❌ Database setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()