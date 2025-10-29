#!/usr/bin/env python3
"""
Debug what similarity scores are being returned
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

# Add backend to path
sys.path.append('backend')

def debug_search_results():
    """Debug search result structure"""
    print("=== DEBUGGING SEARCH RESULTS ===")
    try:
        from services.vector_search import VectorSearchService
        
        vector_service = VectorSearchService()
        
        if vector_service.pinecone_index:
            # Test search
            results = vector_service.semantic_search("billing setup", top_k=3)
            
            print(f"Search results: {len(results)}")
            for i, result in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"  Keys: {list(result.keys())}")
                for key, value in result.items():
                    if key == 'chunk_text':
                        print(f"  {key}: {str(value)[:100]}...")
                    else:
                        print(f"  {key}: {value}")
                        
        else:
            print("❌ Pinecone index not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_search_results()