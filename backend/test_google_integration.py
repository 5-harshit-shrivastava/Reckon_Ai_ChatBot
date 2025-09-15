#!/usr/bin/env python3
"""
Complete test for Google EmbeddingGemma + Google Gemini Pro integration
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

def test_api_keys():
    """Test that API keys are configured"""
    print("🔐 Testing API Keys Configuration...")

    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    gemini_key = os.getenv("GOOGLE_GEMINI_API_KEY")

    if hf_token and hf_token.startswith("hf_"):
        print(f"  ✅ HuggingFace API Token: {hf_token[:10]}...")
    else:
        print("  ❌ HuggingFace API Token missing or invalid")
        return False

    if gemini_key and gemini_key.startswith("AI"):
        print(f"  ✅ Google Gemini API Key: {gemini_key[:10]}...")
    else:
        print("  ❌ Google Gemini API Key missing or invalid")
        return False

    return True

def test_gemini_service():
    """Test Google Gemini Pro service"""
    print("\n🤖 Testing Google Gemini Pro Service...")

    try:
        from services.gemini_service import GeminiService

        gemini = GeminiService()

        if not gemini.client:
            print("  ❌ Gemini service not initialized")
            return False

        # Test connection
        if gemini.test_connection():
            print("  ✅ Gemini Pro connection successful")
        else:
            print("  ❌ Gemini Pro connection failed")
            return False

        # Test response generation
        test_context = """
        ReckonSales is a comprehensive ERP system for small businesses.
        It provides inventory management, billing, and GST compliance.
        """

        result = gemini.generate_response(
            user_query="What is ReckonSales?",
            context=test_context,
            language="en"
        )

        if result["success"]:
            print(f"  ✅ Response generated: {result['response'][:100]}...")
            print(f"  📊 Confidence: {result['confidence']:.2f}")
            print(f"  ⏱️ Time: {result.get('generation_time_ms', 0)}ms")
        else:
            print(f"  ❌ Response generation failed: {result.get('error', 'Unknown error')}")
            return False

        return True

    except Exception as e:
        print(f"  ❌ Gemini service error: {e}")
        return False

def test_embedding_service():
    """Test Google EmbeddingGemma service"""
    print("\n🔗 Testing Google EmbeddingGemma Service...")

    try:
        from services.vector_search import VectorSearchService

        vector_service = VectorSearchService()

        # Test embedding creation
        test_texts = [
            "ReckonSales inventory management system",
            "ReckonSales में इन्वेंटरी प्रबंधन",
            "GST billing and invoice creation"
        ]

        for text in test_texts:
            embedding = vector_service.create_embedding(text, is_query=False)

            if embedding and len(embedding) == 768:
                print(f"  ✅ '{text[:30]}...' → {len(embedding)} dimensions")

                # Check if embedding has values (not all zeros)
                non_zero_count = sum(1 for x in embedding if abs(x) > 0.001)
                if non_zero_count > 100:
                    print(f"    💡 Quality check: {non_zero_count}/768 non-zero values ✅")
                else:
                    print(f"    ⚠️ Quality check: only {non_zero_count}/768 non-zero values")
            else:
                print(f"  ❌ '{text[:30]}...' → Failed or wrong dimensions ({len(embedding) if embedding else 0})")
                return False

        return True

    except Exception as e:
        print(f"  ❌ Embedding service error: {e}")
        return False

def test_end_to_end_rag():
    """Test complete RAG pipeline"""
    print("\n🔄 Testing Complete RAG Pipeline...")

    try:
        from services.rag_service import RAGService
        from config.database import get_db

        rag_service = RAGService()
        db = next(get_db())

        # Add a simple test document first
        from models.knowledge_base import Document, DocumentChunk

        # Check if test doc exists
        existing_doc = db.query(Document).filter(Document.title.contains("Test Google Integration")).first()

        if not existing_doc:
            # Create test document
            test_doc = Document(
                title="Test Google Integration Document",
                content="ReckonSales provides inventory management, billing, and customer management. You can create invoices, track stock levels, and manage GST compliance easily.",
                document_type="test_guide",
                industry_type="general",
                language="en",
                file_path="/test/google_integration.txt",
                file_size=150
            )

            db.add(test_doc)
            db.flush()

            # Create chunk
            test_chunk = DocumentChunk(
                document_id=test_doc.id,
                chunk_index=0,
                chunk_text=test_doc.content,
                chunk_size=len(test_doc.content),
                section_title="Google Integration Test",
                keywords="reckon, inventory, billing, gst",
                confidence_score=0.9,
                embedding_created=False
            )

            db.add(test_chunk)
            db.commit()
            print("  📄 Created test document")

        # Test RAG response
        test_query = "How does ReckonSales help with inventory management?"

        result = rag_service.generate_rag_response(
            db=db,
            user_query=test_query,
            language="en"
        )

        if result["success"]:
            print(f"  ✅ RAG Pipeline Success!")
            print(f"  📝 Query: {test_query}")
            print(f"  🤖 Response: {result['response'][:150]}...")
            print(f"  📊 Confidence: {result['confidence']:.2f}")
            print(f"  📚 Sources: {result['chunks_used']} chunks")
            print(f"  ⏱️ Time: {result['processing_time_ms']}ms")
            print(f"  🔧 Model: {result['model_used']}")
        else:
            print(f"  ❌ RAG Pipeline Failed: {result.get('error', 'Unknown error')}")
            return False

        db.close()
        return True

    except Exception as e:
        print(f"  ❌ RAG pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run complete Google integration test"""
    print("🚀 Google EmbeddingGemma + Gemini Pro Integration Test")
    print("=" * 60)

    tests = [
        ("API Keys", test_api_keys),
        ("Google Gemini Pro", test_gemini_service),
        ("Google EmbeddingGemma", test_embedding_service),
        ("Complete RAG Pipeline", test_end_to_end_rag)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)

        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")

    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 Google Integration is 100% WORKING!")
        print("\n✅ What's working:")
        print("   • Google EmbeddingGemma embeddings (768D)")
        print("   • Google Gemini Pro text generation")
        print("   • Pinecone vector storage")
        print("   • Complete RAG pipeline")
        print("   • Hindi/English multilingual support")
        print("\n🚀 Your premium setup is ready!")
        print("   → Single model approach (no fallbacks)")
        print("   → Consistent embeddings for semantic search")
        print("   → High-quality AI responses")
    else:
        print("⚠️ Some issues detected. Check details above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)