#!/usr/bin/env python3
"""
View every single line stored in the database
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

def view_all_documents():
    """Show every document in detail"""
    try:
        from config.database import get_db
        from models.knowledge_base import Document

        db = next(get_db())
        documents = db.query(Document).order_by(Document.id).all()

        print("📄 ALL DOCUMENTS IN DATABASE")
        print("=" * 80)

        for doc in documents:
            print(f"\n🔸 DOCUMENT ID: {doc.id}")
            print(f"📝 Title: {doc.title}")
            print(f"🏭 Industry: {doc.industry_type}")
            print(f"📂 Type: {doc.document_type}")
            print(f"🌐 Language: {doc.language}")
            print(f"📏 Size: {doc.file_size} characters")
            print(f"📁 Path: {doc.file_path}")
            print(f"📅 Created: {doc.created_at}")
            print("-" * 80)
            print("FULL CONTENT:")
            print("-" * 80)
            print(doc.content)
            print("=" * 80)

        db.close()
        return len(documents)

    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

def view_all_chunks():
    """Show every chunk in detail"""
    try:
        from config.database import get_db
        from models.knowledge_base import DocumentChunk, Document

        db = next(get_db())

        # Get all chunks with their document info
        chunks = db.query(DocumentChunk, Document).join(Document).order_by(DocumentChunk.id).all()

        print("\n📝 ALL CHUNKS IN DATABASE")
        print("=" * 80)

        for chunk, document in chunks:
            print(f"\n🔹 CHUNK ID: {chunk.id}")
            print(f"📄 Document: {document.title}")
            print(f"🔢 Chunk Index: {chunk.chunk_index}")
            print(f"📏 Size: {chunk.chunk_size} characters")
            print(f"📊 Overlap: {chunk.overlap_with_previous} chars")
            print(f"📑 Section: {chunk.section_title}")
            print(f"🏷️ Keywords: {chunk.keywords}")
            print(f"📈 Confidence: {chunk.confidence_score}")
            print(f"🔗 Embedded: {'✅ Yes' if chunk.embedding_created else '❌ No'}")
            if chunk.embedding_id:
                print(f"🆔 Vector ID: {chunk.embedding_id}")
            print(f"📅 Created: {chunk.created_at}")
            print("-" * 80)
            print("CHUNK TEXT:")
            print("-" * 80)
            print(chunk.chunk_text)
            print("=" * 80)

        db.close()
        return len(chunks)

    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

def view_summary_stats():
    """Show summary statistics"""
    try:
        from config.database import get_db
        from models.knowledge_base import Document, DocumentChunk

        db = next(get_db())

        # Count everything
        total_docs = db.query(Document).count()
        total_chunks = db.query(DocumentChunk).count()
        embedded_chunks = db.query(DocumentChunk).filter(DocumentChunk.embedding_created == True).count()

        # Group by language
        en_docs = db.query(Document).filter(Document.language == 'en').count()
        hi_docs = db.query(Document).filter(Document.language == 'hi').count()

        # Group by industry
        industries = db.query(Document.industry_type, db.func.count(Document.id)).group_by(Document.industry_type).all()

        # Calculate sizes
        total_chars = db.query(db.func.sum(Document.file_size)).scalar() or 0
        avg_chunk_size = db.query(db.func.avg(DocumentChunk.chunk_size)).scalar() or 0

        print("📊 DATABASE SUMMARY STATISTICS")
        print("=" * 50)
        print(f"📄 Total Documents: {total_docs}")
        print(f"📝 Total Chunks: {total_chunks}")
        print(f"🔗 Embedded Chunks: {embedded_chunks}")
        print(f"📊 Embedding Progress: {(embedded_chunks/total_chunks*100):.1f}%")
        print(f"\n🌐 By Language:")
        print(f"  🇺🇸 English: {en_docs}")
        print(f"  🇮🇳 Hindi: {hi_docs}")
        print(f"\n🏭 By Industry:")
        for industry, count in industries:
            print(f"  • {industry}: {count}")
        print(f"\n📏 Size Statistics:")
        print(f"  Total Characters: {total_chars:,}")
        print(f"  Average Chunk Size: {avg_chunk_size:.0f} characters")

        db.close()

    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function to show everything"""
    print("🔍 COMPLETE DATABASE CONTENT VIEWER")
    print("=" * 60)

    # Show summary first
    view_summary_stats()

    # Ask user what they want to see
    print("\n" + "=" * 60)
    print("📋 WHAT DO YOU WANT TO VIEW?")
    print("=" * 60)

    choice = input("""
Choose what to display:
1. All Documents (full content)
2. All Chunks (every piece)
3. Both Documents and Chunks
4. Just the summary above

Enter choice (1-4): """).strip()

    if choice == "1":
        doc_count = view_all_documents()
        print(f"\n✅ Displayed {doc_count} documents with full content")

    elif choice == "2":
        chunk_count = view_all_chunks()
        print(f"\n✅ Displayed {chunk_count} chunks with full text")

    elif choice == "3":
        doc_count = view_all_documents()
        chunk_count = view_all_chunks()
        print(f"\n✅ Displayed {doc_count} documents and {chunk_count} chunks")

    elif choice == "4":
        print("\n✅ Summary displayed above")

    else:
        print("\n❌ Invalid choice. Run script again.")

if __name__ == "__main__":
    main()