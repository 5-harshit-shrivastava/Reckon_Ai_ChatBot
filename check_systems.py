#!/usr/bin/env python3
"""
Check both Pinecone and PostgreSQL systems to see which has data
"""

import os
import sys
import json
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.vector_search import VectorSearchService

# Load environment variables
load_dotenv()

def check_pinecone():
    """Check Pinecone system"""
    print("=== CHECKING PINECONE SYSTEM ===")
    try:
        vector_service = VectorSearchService()
        
        # Get stats
        if vector_service.pinecone_index:
            stats = vector_service.pinecone_index.describe_index_stats()
            print(f"Pinecone Index: {vector_service.index_name}")
            print(f"Total vectors: {stats.total_vector_count}")
            print(f"Namespaces: {list(stats.namespaces.keys()) if stats.namespaces else 'None'}")
            
            # Try to search
            if stats.total_vector_count > 0:
                print("\nTesting Pinecone search...")
                results = vector_service.semantic_search("billing", top_k=3)
                print(f"Search results: {len(results)} documents found")
                for i, result in enumerate(results[:2]):
                    print(f"  Result {i+1}: ID={result.get('chunk_id')}, Score={result.get('score'):.3f}")
                    print(f"    Text: {result.get('text', '')[:100]}...")
        else:
            print("Pinecone not initialized")
            
    except Exception as e:
        print(f"Pinecone error: {e}")

def check_postgresql():
    """Check PostgreSQL system"""
    print("\n=== CHECKING POSTGRESQL SYSTEM ===")
    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("No DATABASE_URL found")
            return
            
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if documents table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'documents'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            # Count documents
            cursor.execute("SELECT COUNT(*) FROM documents;")
            count = cursor.fetchone()[0]
            print(f"PostgreSQL documents table exists")
            print(f"Total documents: {count}")
            
            if count > 0:
                # Show sample documents
                cursor.execute("SELECT id, title, content FROM documents LIMIT 3;")
                docs = cursor.fetchall()
                print("\nSample documents:")
                for doc in docs:
                    print(f"  ID={doc['id']}, Title='{doc['title']}'")
                    print(f"    Content: {doc['content'][:100]}...")
        else:
            print("PostgreSQL documents table does not exist")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"PostgreSQL error: {e}")

def test_embedding_service():
    """Test the embedding service"""
    print("\n=== TESTING EMBEDDING SERVICE ===")
    try:
        # Test HuggingFace API
        api_url = "https://api-inference.huggingface.co/models/BAAI/bge-large-en-v1.5"
        token = os.getenv('HUGGINGFACE_API_TOKEN', '').strip()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": "test query",
            "options": {"wait_for_model": True}
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                embedding = result[0] if isinstance(result[0], list) else result
                print(f"HuggingFace API working - Embedding dimensions: {len(embedding)}")
            else:
                print(f"Unexpected response format: {result}")
        else:
            print(f"HuggingFace API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Embedding service error: {e}")

if __name__ == "__main__":
    print("Checking both database systems...\n")
    check_pinecone()
    check_postgresql()
    test_embedding_service()