#!/usr/bin/env python3
"""
Test the complete chatbot with real queries
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

# Add backend to path
sys.path.append('backend')

def test_chat_queries():
    """Test chat with real user queries"""
    print("=== TESTING CHAT QUERIES ===")
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        
        test_queries = [
            "Setup pharmacy billing system",
            "harry potter",
            "omozing",
            "billing setup"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            print("-" * 50)
            
            response = rag_service.generate_rag_response(
                db=None,  # No database needed for Pinecone-only mode
                user_query=query,
                language="en"
            )
            
            answer = response.get('response', 'No response')
            sources = response.get('sources', [])
            confidence = response.get('confidence', 0)
            
            print(f"Answer: {answer[:200]}...")
            print(f"Sources: {len(sources)} documents")
            print(f"Confidence: {confidence:.1%}")
            
            if sources:
                print("Document sources:")
                for i, source in enumerate(sources[:2]):
                    if isinstance(source, dict):
                        title = source.get('title', 'Unknown')
                        score = source.get('similarity_score', 0)
                        print(f"  {i+1}. {title} (Score: {score:.3f})")
                    else:
                        print(f"  {i+1}. {source}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chat test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing chatbot with real queries...\n")
    test_chat_queries()