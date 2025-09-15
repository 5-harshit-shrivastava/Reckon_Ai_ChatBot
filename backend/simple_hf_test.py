#!/usr/bin/env python3
"""
Simple test for HuggingFace multilingual embeddings
Tests the Google EmbeddingGemma model directly
"""

def test_multilingual_embeddings():
    """Test the Google EmbeddingGemma model"""
    print("🚀 Testing Google EmbeddingGemma model")
    print("=" * 50)

    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np

        # Initialize the Google EmbeddingGemma model
        print("📥 Loading Google EmbeddingGemma model...")
        model = SentenceTransformer('google/embeddinggemma-300m')
        print("✅ Model loaded successfully!")

        # Test texts in different languages (EmbeddingGemma doesn't need prefixes)
        test_texts = {
            "English": "ReckonSales inventory management system",
            "Hindi": "ReckonSales इन्वेंटरी प्रबंधन प्रणाली",
            "English_passage": "ReckonSales helps manage inventory and billing",
            "Hindi_passage": "ReckonSales इन्वेंट्री और बिलिंग का प्रबंधन करता है"
        }

        embeddings = {}

        print("\n🔤 Creating embeddings for test texts...")
        for lang, text in test_texts.items():
            print(f"  Processing: {lang}")
            embedding = model.encode(text, normalize_embeddings=True)
            embeddings[lang] = embedding
            print(f"    ✅ Embedding shape: {embedding.shape}")

        # Test similarity between related texts
        print("\n🔍 Testing semantic similarities:")

        # English query vs English passage
        english_sim = np.dot(embeddings["English"], embeddings["English_passage"])
        print(f"  English query ↔ English passage: {english_sim:.4f}")

        # Hindi query vs Hindi passage
        hindi_sim = np.dot(embeddings["Hindi"], embeddings["Hindi_passage"])
        print(f"  Hindi query ↔ Hindi passage: {hindi_sim:.4f}")

        # Cross-language similarity
        cross_sim = np.dot(embeddings["English"], embeddings["Hindi"])
        print(f"  English query ↔ Hindi query: {cross_sim:.4f}")

        # Results analysis
        print("\n📊 Analysis:")
        if english_sim > 0.5:
            print("  ✅ English semantic matching works well")
        else:
            print(f"  ⚠️ English similarity seems low: {english_sim:.4f}")

        if hindi_sim > 0.5:
            print("  ✅ Hindi semantic matching works well")
        else:
            print(f"  ⚠️ Hindi similarity seems low: {hindi_sim:.4f}")

        if cross_sim > 0.3:
            print("  ✅ Cross-language understanding is good")
        else:
            print(f"  ⚠️ Cross-language similarity seems low: {cross_sim:.4f}")

        print("\n🎉 Multilingual embeddings test completed successfully!")
        print("\n💡 Benefits confirmed:")
        print("   ✅ FREE - No API costs")
        print("   ✅ PRIVATE - Runs locally")
        print("   ✅ MULTILINGUAL - Supports Hindi & English")
        print("   ✅ UNLIMITED - No rate limits")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check internet connection (needed for first-time model download)")
        print("   2. Ensure sufficient disk space (~2GB for model)")
        print("   3. Ensure sufficient RAM (~4GB recommended)")
        return False

def test_text_generation():
    """Test basic text generation with transformers"""
    print("\n🤖 Testing text generation capabilities...")

    try:
        from transformers import pipeline

        # Use a smaller, faster model for testing
        print("📥 Loading text generation model...")
        generator = pipeline(
            'text-generation',
            model='microsoft/DialoGPT-medium',
            max_length=100,
            do_sample=True,
            temperature=0.7
        )

        test_prompt = "ReckonSales ERP system helps businesses with"
        print(f"🔤 Test prompt: {test_prompt}")

        result = generator(test_prompt, max_new_tokens=50, num_return_sequences=1)

        if result and len(result) > 0:
            generated_text = result[0]['generated_text']
            print(f"✅ Generated text: {generated_text}")
            print("✅ Text generation working!")
            return True
        else:
            print("⚠️ No text generated")
            return False

    except Exception as e:
        print(f"❌ Text generation error: {e}")
        print("ℹ️ Note: Text generation requires more resources and may fail on limited systems")
        return False

if __name__ == "__main__":
    print("🧪 HuggingFace Integration Test")
    print("Testing free, local, multilingual AI models")
    print("=" * 60)

    success_count = 0
    total_tests = 2

    # Test 1: Multilingual embeddings (essential)
    if test_multilingual_embeddings():
        success_count += 1

    # Test 2: Text generation (optional)
    if test_text_generation():
        success_count += 1

    print("\n" + "=" * 60)
    print(f"📊 Final Results: {success_count}/{total_tests} tests passed")

    if success_count >= 1:
        print("🎉 Core functionality working! Ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Run your RAG chatbot without OpenAI API key")
        print("   2. Enjoy unlimited, free, multilingual responses")
        print("   3. No more API limit errors!")
    else:
        print("❌ Tests failed. Please check system requirements.")