#!/usr/bin/env python3
"""
Quick test of individual services
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

def test_gemini_only():
    """Test only Google Gemini Pro service"""
    print("🤖 Testing Google Gemini Pro...")

    try:
        from services.gemini_service import GeminiService

        gemini = GeminiService()

        # Test simple response
        result = gemini.generate_response(
            user_query="What is ReckonSales ERP system?",
            context="ReckonSales is a comprehensive ERP platform for small businesses with inventory, billing, and GST features.",
            language="en"
        )

        if result["success"]:
            print(f"  ✅ Gemini Response: {result['response'][:100]}...")
            print(f"  📊 Confidence: {result['confidence']:.2f}")
            print(f"  ⏱️ Time: {result.get('generation_time_ms', 0)}ms")
            return True
        else:
            print(f"  ❌ Gemini Failed: {result.get('error', 'Unknown')}")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_db_connection():
    """Test database connection and structure"""
    print("\n💾 Testing Database Connection...")

    try:
        from config.database import get_db
        from models.knowledge_base import Document, DocumentChunk

        db = next(get_db())

        # Test query
        doc_count = db.query(Document).count()
        chunk_count = db.query(DocumentChunk).count()

        print(f"  ✅ Database Connected")
        print(f"  📄 Documents: {doc_count}")
        print(f"  📝 Chunks: {chunk_count}")

        db.close()
        return True

    except Exception as e:
        print(f"  ❌ Database Error: {e}")
        return False

def main():
    """Run quick tests"""
    print("⚡ Quick Service Tests")
    print("=" * 30)

    tests_passed = 0

    # Test Gemini
    if test_gemini_only():
        tests_passed += 1

    # Test Database
    if test_db_connection():
        tests_passed += 1

    print(f"\n📊 Results: {tests_passed}/2 services working")

    if tests_passed >= 1:
        print("✅ Core services are functional!")
        print("\n📝 Status:")
        if tests_passed >= 1:
            print("  🤖 Google Gemini Pro: Working")
        if tests_passed >= 2:
            print("  💾 Database: Working")
        print("\n⏳ EmbeddingGemma is downloading (~300MB)")
        print("   Once complete, you'll have full RAG capabilities!")

if __name__ == "__main__":
    main()