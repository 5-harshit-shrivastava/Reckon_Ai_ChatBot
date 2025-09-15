
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

print("\n🎉 Free model working! You can use this while setting up EmbeddingGemma access.")
