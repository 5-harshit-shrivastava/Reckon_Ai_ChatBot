#!/usr/bin/env python3
"""
Test specific queries to see their exact matching
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

# Add backend to path
sys.path.append('backend')

def test_specific_queries():
    """Test harry potter and other queries"""
    print("=== TESTING SPECIFIC QUERIES ===")
    try:
        from services.vector_search import VectorSearchService
        
        vector_service = VectorSearchService()
        
        test_queries = ["harry potter", "omozing", "rishi upadhay"]
        
        for query in test_queries:
            print(f"\n🔍 Testing: '{query}'")
            results = vector_service.semantic_search(query, top_k=6)
            
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results):
                score = result.get('similarity_score', 0)
                text = result.get('chunk_text', '')[:100]
                print(f"  {i+1}. Score: {score:.3f} - Text: {text}...")
                
        print(f"\n📝 Checking if documents contain specific terms:")
        # Query all vectors to see content
        query_response = vector_service.pinecone_index.query(
            namespace="reckon-knowledge-base",
            vector=[0.0] * 1024,  # Dummy vector
            top_k=10,
            include_metadata=True
        )
        
        for i, match in enumerate(query_response.matches):
            text = match.metadata.get('chunk_text', '')
            print(f"\nDocument {i+1}: {text[:200]}...")
            
            # Check for specific terms
            terms_to_check = ['harry potter', 'omozing', 'rishi', 'brahnman']
            found_terms = [term for term in terms_to_check if term.lower() in text.lower()]
            if found_terms:
                print(f"  → Contains: {found_terms}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_queries()