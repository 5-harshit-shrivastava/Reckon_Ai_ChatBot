#!/usr/bin/env python3
"""
Test different queries to see their similarity scores
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

# Add backend to path
sys.path.append('backend')

def test_query_similarities():
    """Test various queries to see their similarity scores"""
    print("=== TESTING QUERY SIMILARITIES ===")
    try:
        from services.vector_search import VectorSearchService
        
        vector_service = VectorSearchService()
        
        if vector_service.pinecone_index:
            test_queries = [
                "billing setup",
                "harry potter",
                "omozing", 
                "pharmacy billing",
                "contact management",
                "sales pipeline",
                "ReckonSales features",
                "random nonsense words",
                "xyz abc def",
                "recipe for pizza",
                "weather forecast",
                "cryptocurrency bitcoin"
            ]
            
            for query in test_queries:
                print(f"\n🔍 Query: '{query}'")
                results = vector_service.semantic_search(query, top_k=3)
                
                if results:
                    max_score = max(r.get('similarity_score', 0) for r in results)
                    min_score = min(r.get('similarity_score', 0) for r in results)
                    avg_score = sum(r.get('similarity_score', 0) for r in results) / len(results)
                    
                    print(f"  Scores: Max={max_score:.3f}, Min={min_score:.3f}, Avg={avg_score:.3f}")
                    
                    # Show top result
                    top_result = results[0]
                    text_preview = top_result.get('chunk_text', '')[:80]
                    print(f"  Top match: {text_preview}...")
                else:
                    print("  No results found")
                        
        else:
            print("❌ Pinecone index not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query_similarities()