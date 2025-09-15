#!/usr/bin/env python3
"""
Show all database content - every single line
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

def main():
    """Show everything in database"""
    try:
        from config.database import get_db
        from models.knowledge_base import Document, DocumentChunk
        from sqlalchemy import func

        db = next(get_db())

        print("🔍 COMPLETE DATABASE CONTENT")
        print("=" * 80)

        # Get stats first
        total_docs = db.query(Document).count()
        total_chunks = db.query(DocumentChunk).count()
        embedded_chunks = db.query(DocumentChunk).filter(DocumentChunk.embedding_created == True).count()

        print(f"📊 SUMMARY: {total_docs} documents, {total_chunks} chunks, {embedded_chunks} embedded")
        print("=" * 80)

        # Show all documents with their chunks
        documents = db.query(Document).order_by(Document.id).all()

        for doc in documents:
            print(f"\n📄 DOCUMENT #{doc.id}")
            print(f"Title: {doc.title}")
            print(f"Type: {doc.document_type} | Industry: {doc.industry_type} | Language: {doc.language}")
            print(f"Size: {doc.file_size} chars | Created: {doc.created_at}")
            print("-" * 80)
            print("FULL DOCUMENT CONTENT:")
            print("-" * 80)
            print(doc.content)
            print("-" * 80)

            # Show chunks for this document
            chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index).all()

            print(f"\n📝 CHUNKS FOR DOCUMENT #{doc.id} ({len(chunks)} chunks):")

            for chunk in chunks:
                print(f"\n  🔹 CHUNK #{chunk.id} (Index: {chunk.chunk_index})")
                print(f"  Size: {chunk.chunk_size} chars | Overlap: {chunk.overlap_with_previous}")
                print(f"  Embedded: {'✅' if chunk.embedding_created else '❌'} | Vector ID: {chunk.embedding_id or 'None'}")
                print(f"  Keywords: {chunk.keywords}")
                print(f"  Section: {chunk.section_title}")
                print(f"  Confidence: {chunk.confidence_score}")
                print("  " + "-" * 60)
                print("  CHUNK TEXT:")
                print("  " + "-" * 60)
                # Indent each line of chunk text
                for line in chunk.chunk_text.split('\n'):
                    print(f"  {line}")
                print("  " + "-" * 60)

            print("=" * 80)

        print(f"\n✅ COMPLETE! Showed all {total_docs} documents and {total_chunks} chunks")
        print("🔗 Every single line of text stored in your database is above ☝️")

        db.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()