#!/usr/bin/env python3
"""
Guide to setup HuggingFace authentication for Google EmbeddingGemma
"""

def show_huggingface_setup():
    """Show how to set up HuggingFace authentication"""
    print("🔐 HuggingFace Authentication Setup Guide")
    print("=" * 50)

    print("\n📋 Steps to access Google EmbeddingGemma:")
    print("1. Go to: https://huggingface.co/google/embeddinggemma-300m")
    print("2. Click 'Request Access' and accept Google's license")
    print("3. Create HuggingFace account/login if needed")
    print("4. Go to: https://huggingface.co/settings/tokens")
    print("5. Create a new token (Read access is enough)")
    print("6. Copy the token")

    print("\n🔧 Add token to your .env file:")
    print("HUGGINGFACE_API_TOKEN=hf_your_token_here")

    print("\n💡 Alternative: Use command line:")
    print("source venv/bin/activate")
    print("huggingface-cli login")
    print("# Then paste your token when prompted")

def create_fallback_test():
    """Create test using free, unrestricted model"""
    print("\n🔄 Creating fallback test with free model...")

    # Update vector search to use unrestricted model for testing
    test_code = '''
from sentence_transformers import SentenceTransformer
import numpy as np

# Use free, unrestricted model for testing
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# Test texts
texts = [
    "ReckonSales inventory management",
    "GST billing in ReckonSales",
    "Customer management features",
    "ReckonSales इन्वेंटरी प्रबंधन"
]

print("🧪 Testing with free multilingual model...")
for text in texts:
    embedding = model.encode(text, normalize_embeddings=True)
    print(f"✅ {text[:30]}... -> {len(embedding)} dimensions")

print("\\n🎉 Free model working! You can use this while setting up EmbeddingGemma access.")
'''

    with open('/home/harshit/Reckon_Rag_Chatbot/Reckon_Ai_ChatBot/backend/test_free_model.py', 'w') as f:
        f.write(test_code)

    print("📝 Created test_free_model.py for immediate testing")

def main():
    show_huggingface_setup()
    create_fallback_test()

    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Set up HuggingFace authentication (steps above)")
    print("2. Or run: python3 test_free_model.py (immediate testing)")
    print("3. Once authenticated, your Google EmbeddingGemma will work!")

if __name__ == "__main__":
    main()