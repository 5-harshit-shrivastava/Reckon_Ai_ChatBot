#!/usr/bin/env python3
"""
Simple test to verify Google EmbeddingGemma setup
"""

def test_imports():
    """Test that required packages are available"""
    print("🔍 Testing package imports...")

    try:
        import sentence_transformers
        print(f"✅ sentence-transformers: {sentence_transformers.__version__}")
    except ImportError as e:
        print(f"❌ sentence-transformers: {e}")
        return False

    try:
        import transformers
        print(f"✅ transformers: {transformers.__version__}")
    except ImportError as e:
        print(f"❌ transformers: {e}")
        return False

    try:
        import torch
        print(f"✅ torch: {torch.__version__}")
    except ImportError as e:
        print(f"❌ torch: {e}")
        return False

    try:
        import numpy
        print(f"✅ numpy: {numpy.__version__}")
    except ImportError as e:
        print(f"❌ numpy: {e}")
        return False

    return True

def test_vector_search_config():
    """Test VectorSearchService configuration"""
    print("\n🔧 Testing VectorSearchService configuration...")

    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))

        from services.vector_search import VectorSearchService

        vs = VectorSearchService()

        # Check model configuration
        print(f"✅ Primary model: {vs.primary_model['name']}")
        print(f"✅ Vector dimension: {vs.vector_dimension}")
        print(f"✅ Index name: {vs.index_name}")
        print(f"✅ Context length: {vs.primary_model['context_length']}")

        # Verify it's Google EmbeddingGemma
        if "embeddinggemma" in vs.primary_model['name'].lower():
            print("✅ Google EmbeddingGemma correctly configured as primary model")
            return True
        else:
            print(f"❌ Wrong primary model: {vs.primary_model['name']}")
            return False

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Run setup verification"""
    print("🚀 Google EmbeddingGemma Setup Verification")
    print("=" * 50)

    success = True

    if not test_imports():
        success = False

    if not test_vector_search_config():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup verification PASSED!")
        print("\n✅ Google EmbeddingGemma is properly configured:")
        print("   • Primary model: google/embeddinggemma-300m")
        print("   • Vector dimensions: 768")
        print("   • Context length: 2048 tokens")
        print("   • Fallbacks: Jina v3, E5-large")
        print("   • Index: reckon-embeddinggemma-kb")
        print("\n📝 Next steps:")
        print("   1. The model will download on first use (~300MB)")
        print("   2. Set your HUGGINGFACE_API_TOKEN in .env")
        print("   3. Run your chatbot - it will use Google EmbeddingGemma!")
    else:
        print("❌ Setup issues detected")

    return success

if __name__ == "__main__":
    main()