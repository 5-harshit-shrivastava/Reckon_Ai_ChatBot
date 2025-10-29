#!/usr/bin/env python3
"""
Quick test to check if Pinecone system is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

# Add backend to path
sys.path.append('backend')

def test_pinecone_system():
    """Test Pinecone system"""
    print("=== TESTING PINECONE SYSTEM ===")
    try:
        from services.vector_search import VectorSearchService
        
        vector_service = VectorSearchService()
        
        if vector_service.pinecone_index:
            # Get stats
            stats = vector_service.pinecone_index.describe_index_stats()
            print(f"✅ Pinecone connected successfully")
            print(f"Index: {vector_service.index_name}")
            print(f"Total vectors: {stats.total_vector_count}")
            
            if stats.total_vector_count > 0:
                print("\n🔍 Testing search...")
                results = vector_service.semantic_search("billing setup", top_k=3)
                print(f"Search results: {len(results)} documents found")
                
                for i, result in enumerate(results[:2]):
                    chunk_id = result.get('chunk_id', 'Unknown')
                    score = result.get('score', 0)
                    text = result.get('text', '')[:100]
                    print(f"  Result {i+1}: ID={chunk_id}, Score={score:.3f}")
                    print(f"    Text: {text}...")
                    
                return True
            else:
                print("❌ No documents found in Pinecone")
                return False
        else:
            print("❌ Pinecone index not available")
            return False
            
    except Exception as e:
        print(f"❌ Pinecone error: {e}")
        return False

def test_rag_service():
    """Test RAG service"""
    print("\n=== TESTING RAG SERVICE ===")
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        
        # Test with a billing question
        response = rag_service.generate_rag_response(
            db=None,  # No database needed for Pinecone-only mode
            user_query="Setup pharmacy billing system",
            language="en"
        )
        
        print(f"✅ RAG service working")
        print(f"Response: {response.get('response', 'No response')[:200]}...")
        print(f"Sources: {len(response.get('sources', []))} documents used")
        print(f"Confidence: {response.get('confidence', 0):.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG service error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Reckon AI systems...\n")
    
    # Test environment variables
    print("Environment variables:")
    print(f"  PINECONE_API_KEY: {'✅' if os.getenv('PINECONE_API_KEY') else '❌'}")
    print(f"  HUGGINGFACE_API_TOKEN: {'✅' if os.getenv('HUGGINGFACE_API_TOKEN') else '❌'}")
    print(f"  GEMINI_API_KEY: {'✅' if os.getenv('GEMINI_API_KEY') else '❌'}\n")
    
    # Test systems
    pinecone_ok = test_pinecone_system()
    
    if pinecone_ok:
        rag_ok = test_rag_service()
        
        if rag_ok:
            print("\n🎉 ALL SYSTEMS WORKING! Your chatbot should work properly.")
        else:
            print("\n⚠️  Pinecone works but RAG service has issues.")
    else:
        print("\n❌ Pinecone system not working. Check API keys and documents.")