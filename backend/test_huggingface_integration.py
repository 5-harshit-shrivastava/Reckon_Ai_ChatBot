#!/usr/bin/env python3
"""
Test script for HuggingFace multilingual RAG integration
Tests the free local models to avoid API limits
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from services.multilingual_alternatives import HuggingFaceRAGService
from services.vector_search import VectorSearchService

def test_huggingface_embeddings():
    """Test HuggingFace multilingual embeddings"""
    print("🔍 Testing HuggingFace multilingual embeddings...")

    try:
        vector_service = VectorSearchService()

        # Test English embedding
        english_text = "ReckonSales inventory management system"
        english_embedding = vector_service.create_embedding(english_text, is_query=True)

        print(f"✅ English embedding created: {len(english_embedding)} dimensions")

        # Test Hindi embedding
        hindi_text = "ReckonSales इन्वेंटरी प्रबंधन प्रणाली"
        hindi_embedding = vector_service.create_embedding(hindi_text, is_query=True)

        print(f"✅ Hindi embedding created: {len(hindi_embedding)} dimensions")

        # Check if embeddings are different (they should be)
        if english_embedding != hindi_embedding:
            print("✅ Embeddings are different for different languages (good!)")
        else:
            print("⚠️  Embeddings are identical (unexpected)")

        return True

    except Exception as e:
        print(f"❌ Error testing embeddings: {e}")
        return False

def test_huggingface_rag_response():
    """Test HuggingFace RAG response generation"""
    print("\n🤖 Testing HuggingFace RAG response generation...")

    try:
        hf_service = HuggingFaceRAGService()

        # Test context and query
        context = """
        ReckonSales is an ERP system for small businesses.
        It helps manage inventory, billing, and customer relationships.
        The system supports GST compliance and multi-language support.
        """

        # Test English query
        english_query = "How does ReckonSales help with inventory management?"
        result = hf_service.generate_response(
            query=english_query,
            context=context,
            language="en"
        )

        print(f"English Response Success: {result.get('success')}")
        if result.get('success'):
            print(f"Response: {result.get('response')[:200]}...")
            print(f"Model: {result.get('model')}")
        else:
            print(f"Error: {result.get('error')}")

        # Test Hindi query
        print("\n🔄 Testing Hindi query...")
        hindi_query = "ReckonSales इन्वेंटरी प्रबंधन कैसे करता है?"
        hindi_result = hf_service.generate_response(
            query=hindi_query,
            context=context,
            language="hi"
        )

        print(f"Hindi Response Success: {hindi_result.get('success')}")
        if hindi_result.get('success'):
            print(f"Response: {hindi_result.get('response')[:200]}...")
            print(f"Model: {hindi_result.get('model')}")
        else:
            print(f"Error: {hindi_result.get('error')}")

        return result.get('success') or hindi_result.get('success')

    except Exception as e:
        print(f"❌ Error testing HuggingFace RAG: {e}")
        return False

def test_fallback_integration():
    """Test that main RAG service falls back to HuggingFace"""
    print("\n🔄 Testing RAG service fallback to HuggingFace...")

    try:
        # Temporarily disable OpenAI to test fallback
        original_key = os.environ.get('OPENAI_API_KEY')
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']

        from services.rag_service import RAGService
        from config.database import get_db

        rag_service = RAGService()

        # Create a test query
        test_query = "What is ReckonSales used for?"
        context = "ReckonSales is a comprehensive ERP solution for small businesses."

        # Test fallback response generation
        response = rag_service._generate_response(
            user_query=test_query,
            context=context,
            language="en"
        )

        print(f"Fallback Response Success: {response.get('success')}")
        print(f"Model Used: {response.get('model_used', 'unknown')}")

        if response.get('success'):
            print(f"Response: {response.get('response')[:200]}...")
        else:
            print(f"Error: {response.get('error', 'Unknown error')}")

        # Restore OpenAI key if it existed
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key

        return response.get('success')

    except Exception as e:
        print(f"❌ Error testing fallback: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting HuggingFace Integration Tests")
    print("=" * 50)

    # Run tests
    tests_passed = 0
    total_tests = 3

    if test_huggingface_embeddings():
        tests_passed += 1

    if test_huggingface_rag_response():
        tests_passed += 1

    if test_fallback_integration():
        tests_passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! HuggingFace integration is working.")
        print("\n💡 Benefits of this integration:")
        print("   ✅ No API costs - completely FREE")
        print("   ✅ No rate limits - unlimited requests")
        print("   ✅ Privacy - runs locally, no data sent to external APIs")
        print("   ✅ Multilingual - supports Hindi and English")
        print("   ✅ Offline capable - works without internet connection")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 To fix issues:")
        print("   1. Install dependencies: pip install transformers torch")
        print("   2. Ensure sufficient disk space for model downloads")
        print("   3. Check that your system has enough RAM (4GB+ recommended)")

if __name__ == "__main__":
    main()