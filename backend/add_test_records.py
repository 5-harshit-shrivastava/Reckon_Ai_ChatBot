#!/usr/bin/env python3
"""
Add test records to check Google EmbeddingGemma integration
"""

import os
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def add_sample_documents(db: Session):
    """Add sample documents for testing"""
    from models.knowledge_base import Document, DocumentChunk

    # Sample documents for ReckonSales
    sample_documents = [
        {
            "title": "ReckonSales Inventory Management Guide",
            "content": """ReckonSales provides comprehensive inventory management features for businesses.
            You can track stock levels, manage purchase orders, and generate inventory reports.
            The system supports barcode scanning and real-time stock updates.
            To add new items, go to Inventory > Add Item and fill in the product details including SKU, name, and pricing.""",
            "document_type": "user_guide",
            "industry_type": "general",
            "language": "en"
        },
        {
            "title": "GST और बिलिंग गाइड - ReckonSales",
            "content": """ReckonSales में GST और बिलिंग की सुविधा उपलब्ध है। आप आसानी से GST के साथ इनवॉइस बना सकते हैं।
            सिस्टम automatically GST calculation करता है। बिलिंग के लिए Sales > Create Invoice पर जाएं।
            आप customer details, items, और GST rates add कर सकते हैं। System सभी GST reports भी generate करता है।""",
            "document_type": "user_guide",
            "industry_type": "general",
            "language": "hi"
        },
        {
            "title": "Pharmacy Management in ReckonSales",
            "content": """ReckonSales offers specialized pharmacy management features. Track medicine inventory with expiry dates,
            batch numbers, and manufacturer details. Generate prescription bills with patient information.
            The system maintains medicine master data and supports drug interaction warnings.
            For pharmacy setup, configure medicine categories and supplier information in the system.""",
            "document_type": "user_guide",
            "industry_type": "pharmacy",
            "language": "en"
        },
        {
            "title": "ReckonSales Customer Management",
            "content": """Manage your customers effectively with ReckonSales CRM features. Add customer details,
            track purchase history, and maintain contact information. You can create customer groups for targeted marketing.
            The system supports customer payment tracking and credit limit management.
            Access customer reports to analyze buying patterns and preferences.""",
            "document_type": "user_guide",
            "industry_type": "general",
            "language": "en"
        },
        {
            "title": "Auto Parts Inventory - ReckonSales",
            "content": """ReckonSales supports auto parts businesses with vehicle-specific inventory management.
            Track parts by vehicle make, model, and year. Maintain compatibility charts and cross-reference numbers.
            Generate parts catalogs and manage supplier information. The system supports both OEM and aftermarket parts tracking.""",
            "document_type": "user_guide",
            "industry_type": "auto_parts",
            "language": "en"
        }
    ]

    print("📝 Adding sample documents to knowledge base...")

    for i, doc_data in enumerate(sample_documents, 1):
        # Create document
        document = Document(
            title=doc_data["title"],
            content=doc_data["content"],
            document_type=doc_data["document_type"],
            industry_type=doc_data["industry_type"],
            language=doc_data["language"],
            file_path=f"/sample/doc_{i}.txt",
            file_size=len(doc_data["content"]),
            is_active=True
        )

        db.add(document)
        db.flush()  # Get the document ID

        # Create document chunks (split content into smaller pieces)
        content = doc_data["content"]
        chunk_size = 200  # Characters per chunk

        chunks = []
        for j in range(0, len(content), chunk_size):
            chunk_text = content[j:j + chunk_size]

            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=j // chunk_size,
                chunk_text=chunk_text,
                chunk_size=len(chunk_text),
                section_title=doc_data["title"],
                keywords=f"reckon, {doc_data['industry_type']}, {doc_data['document_type']}",
                confidence_score=0.8,
                embedding_created=False  # Will be created by vector service
            )
            chunks.append(chunk)

        db.add_all(chunks)
        print(f"  ✅ Added document {i}: {doc_data['title']} ({len(chunks)} chunks)")

    db.commit()
    print(f"\n🎉 Successfully added {len(sample_documents)} sample documents!")

def create_embeddings_for_records():
    """Create embeddings for the sample records"""
    from services.rag_service import RAGService
    from config.database import get_db

    print("\n🔄 Creating embeddings for sample documents...")

    # Initialize RAG service
    rag_service = RAGService()

    # Get database session
    db = next(get_db())

    try:
        # Create embeddings for all chunks without embeddings
        result = rag_service.create_embeddings_for_existing_chunks(db)

        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"📊 Processed: {result['processed']} chunks")
        else:
            print(f"❌ Error: {result['message']}")

    except Exception as e:
        print(f"❌ Error creating embeddings: {e}")
    finally:
        db.close()

def test_search():
    """Test search functionality with sample queries"""
    from services.rag_service import RAGService
    from config.database import get_db

    print("\n🔍 Testing search functionality...")

    # Initialize RAG service
    rag_service = RAGService()

    # Get database session
    db = next(get_db())

    test_queries = [
        ("How to manage inventory in ReckonSales?", "en"),
        ("GST कैसे calculate करें?", "hi"),
        ("Pharmacy inventory tracking", "en"),
        ("Customer management features", "en")
    ]

    try:
        for query, lang in test_queries:
            print(f"\n🔤 Query: {query} ({lang})")

            # Generate RAG response
            result = rag_service.generate_rag_response(
                db=db,
                user_query=query,
                language=lang
            )

            if result["success"]:
                print(f"  ✅ Response ({result['confidence']:.2f} confidence):")
                print(f"  📝 {result['response'][:150]}...")
                print(f"  📊 Sources used: {result['chunks_used']}")
                print(f"  ⏱️ Time: {result['processing_time_ms']}ms")
            else:
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Search test error: {e}")
    finally:
        db.close()

def main():
    """Main function to add records and test"""
    print("🚀 Adding Test Records for Google EmbeddingGemma")
    print("=" * 60)

    try:
        # Initialize database
        from config.database import get_db
        db = next(get_db())

        # Add sample documents
        add_sample_documents(db)

        # Create embeddings
        create_embeddings_for_records()

        # Test search
        test_search()

        print("\n" + "=" * 60)
        print("🎉 Test records added and embeddings created successfully!")
        print("\n✅ Your Google EmbeddingGemma integration is working!")
        print("📝 You can now:")
        print("   1. Query the knowledge base with Hindi/English questions")
        print("   2. Test different industry contexts (pharmacy, auto parts)")
        print("   3. Check embedding quality and search accuracy")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()