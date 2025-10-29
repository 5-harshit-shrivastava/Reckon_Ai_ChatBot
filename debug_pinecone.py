#!/usr/bin/env python3
"""
Debug what's actually stored in Pinecone
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

# Add backend to path
sys.path.append('backend')

def debug_pinecone_data():
    """Debug what's in Pinecone"""
    print("=== DEBUGGING PINECONE DATA ===")
    try:
        from services.vector_search import VectorSearchService
        
        vector_service = VectorSearchService()
        
        if vector_service.pinecone_index:
            # Get stats
            stats = vector_service.pinecone_index.describe_index_stats()
            print(f"Total vectors: {stats.total_vector_count}")
            print(f"Namespaces: {list(stats.namespaces.keys())}")
            
            # Query a few vectors to see their structure
            query_response = vector_service.pinecone_index.query(
                namespace="reckon-knowledge-base",
                vector=[0.0] * 1024,  # Dummy vector
                top_k=3,
                include_metadata=True
            )
            
            print(f"\nFound {len(query_response.matches)} vectors:")
            for i, match in enumerate(query_response.matches):
                print(f"\nVector {i+1}:")
                print(f"  ID: {match.id} (type: {type(match.id)})")
                print(f"  Score: {match.score}")
                print(f"  Metadata keys: {list(match.metadata.keys())}")
                print(f"  chunk_id: {match.metadata.get('chunk_id')} (type: {type(match.metadata.get('chunk_id'))})")
                print(f"  document_id: {match.metadata.get('document_id')} (type: {type(match.metadata.get('document_id'))})")
                text = match.metadata.get('chunk_text', '')
                print(f"  Text preview: {text[:100]}...")
                
        else:
            print("❌ Pinecone index not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pinecone_data()