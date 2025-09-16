#!/usr/bin/env python3
"""
Simple Data Pusher - Just like your Neon database experience but for Pinecone
Give it data -> It converts to embeddings -> Pushes to Pinecone
No questions asked!
"""
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import uuid

# Install required packages if not present
try:
    from pinecone import Pinecone
    from sentence_transformers import SentenceTransformer
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("Run: pip install pinecone-client sentence-transformers python-dotenv")
    exit(1)

# Load environment variables
load_dotenv()

class SimplePineconeUploader:
    def __init__(self):
        """Initialize Pinecone connection and embedding model"""

        # Get API key
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            print("❌ PINECONE_API_KEY not found in .env file!")
            exit(1)

        # Initialize Pinecone
        try:
            self.pc = Pinecone(api_key=api_key)
            print("✅ Connected to Pinecone")
        except Exception as e:
            print(f"❌ Failed to connect to Pinecone: {e}")
            exit(1)

        # Initialize embedding model
        print("🔄 Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, good quality
        print("✅ Embedding model loaded")

        # Index name
        self.index_name = "reckon-knowledge"
        self.index = None

        # Connect to or create index
        self.setup_index()

    def setup_index(self):
        """Setup Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]

            if self.index_name not in existing_indexes:
                print(f"🔄 Creating index '{self.index_name}'...")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric='cosine',
                    spec={
                        'serverless': {
                            'cloud': 'aws',
                            'region': 'us-east-1'
                        }
                    }
                )
                # Wait for index to be ready
                time.sleep(10)

            # Connect to index
            self.index = self.pc.Index(self.index_name)
            print(f"✅ Connected to index '{self.index_name}'")

        except Exception as e:
            print(f"❌ Error setting up index: {e}")
            exit(1)

    def push_data(self, title: str, content: str, metadata: Dict = None):
        """
        Push data to Pinecone - Just like Neon database!

        Args:
            title: Document title
            content: Document content
            metadata: Additional metadata (optional)
        """
        try:
            # Create unique ID
            doc_id = str(uuid.uuid4())

            # Get current timestamp
            created_at = datetime.now().isoformat()

            # Generate embedding
            print(f"🔄 Creating embedding for: {title[:50]}...")
            embedding = self.model.encode(content).tolist()

            # Prepare metadata (similar to your Neon columns)
            vector_metadata = {
                "title": title,
                "content": content,
                "created_at": created_at
            }

            # Add custom metadata if provided
            if metadata:
                vector_metadata.update(metadata)

            # Upsert to Pinecone
            self.index.upsert(vectors=[(doc_id, embedding, vector_metadata)])

            print(f"✅ Pushed: {title}")
            print(f"   ID: {doc_id}")
            print(f"   Content length: {len(content)} chars")
            print(f"   Created: {created_at}")

            return doc_id

        except Exception as e:
            print(f"❌ Error pushing data: {e}")
            return None

    def push_bulk_data(self, data_list: List[Dict]):
        """
        Push multiple documents at once

        Args:
            data_list: List of dicts with 'title', 'content', and optional 'metadata'
        """
        print(f"🔄 Pushing {len(data_list)} documents...")

        successful = 0
        failed = 0

        for i, data in enumerate(data_list, 1):
            print(f"\n📄 Processing {i}/{len(data_list)}")

            title = data.get('title', f'Document {i}')
            content = data.get('content', '')
            metadata = data.get('metadata', {})

            if self.push_data(title, content, metadata):
                successful += 1
            else:
                failed += 1

        print(f"\n📊 Bulk upload completed:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")

    def view_data(self, limit: int = 10):
        """View what's in your database - like browsing Neon tables"""
        try:
            # Get index stats
            stats = self.index.describe_index_stats()
            total_vectors = stats.total_vector_count

            print(f"📊 Database Stats:")
            print(f"   Total documents: {total_vectors}")
            print(f"   Index name: {self.index_name}")

            if total_vectors == 0:
                print("   Database is empty!")
                return

            # Query to get some random vectors
            dummy_vector = [0.0] * 384
            results = self.index.query(
                vector=dummy_vector,
                top_k=min(limit, total_vectors),
                include_metadata=True
            )

            print(f"\n📝 Recent documents (showing {len(results.matches)}):")
            print("=" * 80)

            for i, match in enumerate(results.matches, 1):
                metadata = match.metadata or {}
                title = metadata.get('title', 'No title')
                content = metadata.get('content', 'No content')
                created_at = metadata.get('created_at', 'Unknown date')

                print(f"{i}. ID: {match.id}")
                print(f"   Title: {title}")
                print(f"   Content: {content[:100]}{'...' if len(content) > 100 else ''}")
                print(f"   Created: {created_at}")
                print(f"   Score: {match.score:.4f}")
                print("-" * 40)

        except Exception as e:
            print(f"❌ Error viewing data: {e}")

    def search_data(self, query: str, top_k: int = 5):
        """Search your data"""
        try:
            print(f"🔍 Searching for: '{query}'")

            # Create query embedding
            query_embedding = self.model.encode(query).tolist()

            # Search
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )

            print(f"Found {len(results.matches)} results:")
            print("=" * 60)

            for i, match in enumerate(results.matches, 1):
                metadata = match.metadata or {}
                title = metadata.get('title', 'No title')
                content = metadata.get('content', 'No content')

                print(f"{i}. {title} (Score: {match.score:.4f})")
                print(f"   {content[:150]}...")
                print()

        except Exception as e:
            print(f"❌ Error searching: {e}")

    def clear_all_data(self):
        """Clear all data from index"""
        try:
            # Delete the index
            self.pc.delete_index(self.index_name)
            print(f"✅ Cleared all data from '{self.index_name}'")

            # Recreate empty index
            time.sleep(5)
            self.setup_index()

        except Exception as e:
            print(f"❌ Error clearing data: {e}")

def main():
    print("🚀 Simple Pinecone Data Pusher")
    print("Just like your Neon database - but with Pinecone!")
    print("=" * 50)

    # Initialize uploader
    uploader = SimplePineconeUploader()

    # Example usage
    print("\n📖 Example Usage:")
    print("1. Push single document:")
    print("   uploader.push_data('My Title', 'My content here')")

    print("\n2. Push with metadata:")
    print("   uploader.push_data('Title', 'Content', {'category': 'billing', 'author': 'admin'})")

    print("\n3. View your data:")
    print("   uploader.view_data()")

    print("\n4. Search your data:")
    print("   uploader.search_data('billing questions')")

    # Sample data push (uncomment to use)
    print("\n🔄 Pushing sample data...")

    sample_data = [
        {
            "title": "GST Compliance Guide",
            "content": "Complete guide to GST compliance in India. Covers GSTR-1, GSTR-3B filings, input tax credit management, and penalty avoidance.",
            "metadata": {"category": "tax", "type": "guide"}
        },
        {
            "title": "Inventory Management Best Practices",
            "content": "Best practices for managing inventory in ERP systems. Includes stock tracking, reorder points, and multi-warehouse management.",
            "metadata": {"category": "inventory", "type": "guide"}
        },
        {
            "title": "Billing System Setup",
            "content": "Step-by-step guide to set up billing system. Covers invoice templates, payment tracking, and integration with accounting software.",
            "metadata": {"category": "billing", "type": "setup"}
        }
    ]

    uploader.push_bulk_data(sample_data)

    print("\n👀 Viewing uploaded data:")
    uploader.view_data()

    print("\n🔍 Testing search:")
    uploader.search_data("GST filing")

if __name__ == "__main__":
    main()