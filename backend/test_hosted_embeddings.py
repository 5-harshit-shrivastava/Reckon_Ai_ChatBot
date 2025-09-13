#!/usr/bin/env python3
"""
Test script to create and test Pinecone index with hosted embeddings
"""

import os
import sys
import time
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_hosted_embeddings_index():
    """Test creating a new index with hosted embeddings"""
    print("🔄 Testing Pinecone hosted embeddings index creation...")
    
    try:
        from pinecone import Pinecone, ServerlessSpec
        
        # Get API key from environment
        api_key = os.getenv("PINECONE_API_KEY")
        
        if not api_key:
            print("❌ PINECONE_API_KEY not found in environment")
            return False
        
        print(f"✅ Found Pinecone API key: {api_key[:10]}...")
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        
        # Test index name with hosted embeddings
        index_name = "reckon-multilingual-test"
        
        # List existing indexes
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        print(f"✅ Found {len(index_names)} existing indexes: {index_names}")
        
        # Delete test index if it exists
        if index_name in index_names:
            print(f"🗑️ Deleting existing test index: {index_name}")
            pc.delete_index(index_name)
            time.sleep(10)
        
        # Create index with hosted embeddings
        print(f"🔄 Creating new index with hosted embeddings: {index_name}")
        
        # Try different approaches to enable hosted embeddings
        try:
            # Approach 1: Using model parameter
            pc.create_index(
                name=index_name,
                dimension=1024,  # multilingual-e5-large dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                ),
                model="multilingual-e5-large"  # Specify hosted model
            )
            print("✅ Index created with model parameter")
        except Exception as e:
            print(f"⚠️ Approach 1 failed: {e}")
            
            # Approach 2: Try without model parameter (check if inference is auto-enabled)
            try:
                pc.create_index(
                    name=index_name,
                    dimension=1024,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print("✅ Index created without model parameter")
            except Exception as e2:
                print(f"❌ Approach 2 also failed: {e2}")
                return False
        
        # Wait for index to be ready
        print("⏳ Waiting for index to be ready...")
        time.sleep(15)
        
        # Connect to the index
        index = pc.Index(index_name)
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"✅ Index stats: {stats}")
        
        # Test upsert with text (hosted embeddings)
        print("🔄 Testing upsert with hosted embeddings...")
        
        test_record = {
            "id": "test-1",
            "text": "This is a test document for ReckonSales invoice creation",
            "metadata": {
                "title": "Test Document",
                "type": "test"
            }
        }
        
        try:
            # Use upsert_records for hosted embeddings
            index.upsert_records(
                namespace="test",
                records=[test_record]
            )
            print("✅ Successfully upserted record with hosted embeddings")
            
            # Wait a moment for indexing
            time.sleep(5)
            
            # Test search with text
            search_response = index.query(
                namespace="test",
                text="invoice creation guide",
                top_k=1,
                include_metadata=True
            )
            
            print(f"✅ Search completed, found {len(search_response.matches)} results")
            if search_response.matches:
                match = search_response.matches[0]
                print(f"   Score: {match.score:.3f}")
                print(f"   Metadata: {match.metadata}")
            
        except Exception as e:
            print(f"❌ Hosted embeddings test failed: {e}")
            return False
        
        print("🎉 Hosted embeddings test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run hosted embeddings test"""
    print("🚀 Starting Pinecone Hosted Embeddings Test\n")
    
    if test_hosted_embeddings_index():
        print("\n✅ Hosted embeddings are working!")
        print("📝 You can now use the updated vector search service.")
    else:
        print("\n❌ Hosted embeddings test failed.")
        print("🔧 Check Pinecone account settings and billing.")

if __name__ == "__main__":
    main()