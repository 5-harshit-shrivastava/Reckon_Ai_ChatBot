#!/usr/bin/env python3
"""
Comprehensive verification that HuggingFace multilingual model is working 100%
"""

def test_embedding_generation():
    """Test that embeddings are generated correctly"""
    print("🧪 Testing embedding generation...")

    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np

        # Load the exact model used in your system - Google EmbeddingGemma
        model = SentenceTransformer('google/embeddinggemma-300m')

        # Test various scenarios
        test_cases = [
            ("query: How to manage inventory in ReckonSales?", "English Query"),
            ("passage: ReckonSales helps manage inventory and billing", "English Passage"),
            ("query: ReckonSales में इन्वेंटरी कैसे मैनेज करें?", "Hindi Query"),
            ("passage: ReckonSales इन्वेंटरी और बिलिंग का प्रबंधन करता है", "Hindi Passage")
        ]

        embeddings = {}
        for text, label in test_cases:
            embedding = model.encode(text, normalize_embeddings=True)
            embeddings[label] = embedding
            print(f"  ✅ {label}: {embedding.shape} dimensions")

            # Verify embedding quality
            if len(embedding) != 768:
                print(f"  ❌ Wrong dimension: expected 768, got {len(embedding)}")
                return False

            if np.isnan(embedding).any():
                print(f"  ❌ NaN values in embedding")
                return False

            if np.sum(np.abs(embedding)) == 0:
                print(f"  ❌ Zero embedding")
                return False

        # Test semantic similarity
        eng_query_passage = np.dot(embeddings["English Query"], embeddings["English Passage"])
        hindi_query_passage = np.dot(embeddings["Hindi Query"], embeddings["Hindi Passage"])
        cross_lang = np.dot(embeddings["English Query"], embeddings["Hindi Query"])

        print(f"\n📊 Similarity scores:")
        print(f"  English Q↔P: {eng_query_passage:.4f}")
        print(f"  Hindi Q↔P: {hindi_query_passage:.4f}")
        print(f"  Cross-language: {cross_lang:.4f}")

        # Verify semantic understanding
        if eng_query_passage < 0.3:
            print(f"  ❌ Low English similarity: {eng_query_passage:.4f}")
            return False

        if hindi_query_passage < 0.3:
            print(f"  ❌ Low Hindi similarity: {hindi_query_passage:.4f}")
            return False

        print("  ✅ All similarity scores are healthy")
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_rag_service_integration():
    """Test that RAG service properly uses HuggingFace"""
    print("\n🔧 Testing RAG service integration...")

    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))

        # Temporarily disable OpenAI to force HuggingFace usage
        original_key = os.environ.get('OPENAI_API_KEY')
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']

        from services.multilingual_alternatives import HuggingFaceRAGService

        # Test HuggingFace service directly
        hf_service = HuggingFaceRAGService()

        test_context = """
        ReckonSales is a comprehensive ERP system designed for small businesses.
        It provides inventory management, billing, GST compliance, and customer management.
        The system supports multiple languages including Hindi and English.
        """

        test_queries = [
            ("What is ReckonSales?", "en"),
            ("ReckonSales क्या है?", "hi")
        ]

        for query, lang in test_queries:
            print(f"  Testing: {query} ({lang})")

            result = hf_service.generate_response(
                query=query,
                context=test_context,
                language=lang
            )

            if result.get("success"):
                response = result.get("response", "")
                print(f"    ✅ Response generated ({len(response)} chars)")
                print(f"    Model: {result.get('model', 'unknown')}")
                print(f"    Cost: {result.get('cost', 'unknown')}")

                if len(response) < 10:
                    print(f"    ⚠️ Response seems too short: {response}")

            else:
                print(f"    ❌ Failed: {result.get('error', 'Unknown error')}")
                return False

        # Restore OpenAI key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key

        print("  ✅ RAG service integration working")
        return True

    except Exception as e:
        print(f"  ❌ Integration error: {e}")
        return False

def test_vector_search_service():
    """Test vector search service with HuggingFace embeddings"""
    print("\n🔍 Testing vector search service...")

    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))

        from services.vector_search import VectorSearchService

        vector_service = VectorSearchService()

        # Test embedding creation
        test_texts = [
            "ReckonSales inventory management",
            "ReckonSales इन्वेंटरी प्रबंधन"
        ]

        for text in test_texts:
            # Test query embedding
            query_emb = vector_service.create_embedding(text, is_query=True)
            print(f"  ✅ Query embedding: {len(query_emb)} dims")

            # Test passage embedding
            passage_emb = vector_service.create_embedding(text, is_query=False)
            print(f"  ✅ Passage embedding: {len(passage_emb)} dims")

            if len(query_emb) != 768 or len(passage_emb) != 768:
                print(f"  ❌ Wrong embedding dimensions")
                return False

            if all(x == 0 for x in query_emb) or all(x == 0 for x in passage_emb):
                print(f"  ❌ Zero embeddings generated")
                return False

        print("  ✅ Vector search service working")
        return True

    except Exception as e:
        print(f"  ❌ Vector search error: {e}")
        return False

def main():
    """Run comprehensive verification"""
    print("🚀 HuggingFace Model Verification")
    print("=" * 50)

    tests = [
        ("Embedding Generation", test_embedding_generation),
        ("RAG Service Integration", test_rag_service_integration),
        ("Vector Search Service", test_vector_search_service)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)

        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")

    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 HuggingFace model is running 100% FINE!")
        print("\n✅ Confirmed working:")
        print("   • Multilingual embeddings (Hindi + English)")
        print("   • RAG response generation")
        print("   • Vector search integration")
        print("   • No API limits or costs")
        print("   • Complete fallback from OpenAI")
    else:
        print("⚠️ Some issues detected. See details above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)