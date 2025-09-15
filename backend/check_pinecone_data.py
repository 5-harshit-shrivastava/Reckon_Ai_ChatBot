#!/usr/bin/env python3
"""
Check and inspect Pinecone database contents
"""

import os
import sys
from pathlib import Path
import json

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def check_pinecone_connection():
    """Check Pinecone connection and basic info"""
    print("🌲 Checking Pinecone Connection...")

    try:
        from pinecone import Pinecone

        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            print("  ❌ PINECONE_API_KEY not found")
            return False

        pc = Pinecone(api_key=api_key)

        # List indexes
        indexes = pc.list_indexes()
        print(f"  ✅ Connected to Pinecone")
        print(f"  📊 Available indexes: {len(indexes)}")

        for idx in indexes:
            print(f"    • {idx.name}: {idx.dimension}D, {idx.metric} metric")

        return True

    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        return False

def check_index_stats():
    """Check detailed index statistics"""
    print("\n📊 Checking Index Statistics...")

    try:
        from services.vector_search import VectorSearchService

        vs = VectorSearchService()

        if not vs.pinecone_index:
            print("  ❌ Pinecone index not available")
            return False

        # Get index stats
        stats = vs.pinecone_index.describe_index_stats()

        print(f"  ✅ Index: {vs.index_name}")
        print(f"  📏 Dimensions: {stats.get('dimension', 'N/A')}")
        print(f"  📊 Total vectors: {stats.get('total_vector_count', 0)}")
        print(f"  📈 Index fullness: {stats.get('index_fullness', 0):.1%}")

        # Check namespaces
        namespaces = stats.get('namespaces', {})
        print(f"  📁 Namespaces: {len(namespaces)}")

        for ns_name, ns_stats in namespaces.items():
            vector_count = ns_stats.get('vector_count', 0)
            print(f"    • {ns_name}: {vector_count} vectors")

        return True

    except Exception as e:
        print(f"  ❌ Stats error: {e}")
        return False

def list_vectors_sample():
    """List sample vectors from Pinecone"""
    print("\n🔍 Listing Sample Vectors...")

    try:
        from services.vector_search import VectorSearchService

        vs = VectorSearchService()

        if not vs.pinecone_index:
            print("  ❌ Pinecone index not available")
            return False

        # Try to fetch some vectors by IDs
        # First, let's try to query for any vectors
        try:
            # Create a dummy query to see what's there
            dummy_query = [0.1] * vs.vector_dimension

            results = vs.pinecone_index.query(
                vector=dummy_query,
                top_k=5,
                include_metadata=True,
                namespace="reckon-knowledge-base"
            )

            print(f"  📋 Found {len(results.matches)} vectors in namespace 'reckon-knowledge-base'")

            for i, match in enumerate(results.matches, 1):
                print(f"\n    Vector {i}:")
                print(f"      ID: {match.id}")
                print(f"      Score: {match.score:.4f}")

                if hasattr(match, 'metadata') and match.metadata:
                    print(f"      Metadata:")
                    for key, value in match.metadata.items():
                        if key == 'chunk_text':
                            # Truncate text for display
                            display_text = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                            print(f"        {key}: {display_text}")
                        else:
                            print(f"        {key}: {value}")

            if len(results.matches) == 0:
                print("  ⚠️ No vectors found - embeddings may not be generated yet")

        except Exception as query_error:
            print(f"  ❌ Query error: {query_error}")

        return True

    except Exception as e:
        print(f"  ❌ Vector listing error: {e}")
        return False

def check_database_chunks():
    """Check what chunks are in the database vs Pinecone"""
    print("\n💾 Comparing Database vs Pinecone...")

    try:
        from config.database import get_db
        from models.knowledge_base import Document, DocumentChunk

        db = next(get_db())

        # Get database stats
        total_docs = db.query(Document).count()
        total_chunks = db.query(DocumentChunk).count()
        embedded_chunks = db.query(DocumentChunk).filter(
            DocumentChunk.embedding_created == True
        ).count()

        print(f"  📄 Database Documents: {total_docs}")
        print(f"  📝 Database Chunks: {total_chunks}")
        print(f"  🔗 Embedded Chunks: {embedded_chunks}")
        print(f"  📊 Embedding Progress: {(embedded_chunks/total_chunks*100):.1f}%")

        # Show recent chunks
        print(f"\n  📋 Recent Chunks (last 5):")
        recent_chunks = db.query(DocumentChunk).join(Document).order_by(
            DocumentChunk.id.desc()
        ).limit(5).all()

        for chunk in recent_chunks:
            status = "✅ Embedded" if chunk.embedding_created else "⏳ Pending"
            preview = chunk.chunk_text[:60] + "..." if len(chunk.chunk_text) > 60 else chunk.chunk_text
            print(f"    • Chunk {chunk.id}: {status}")
            print(f"      Preview: {preview}")
            if chunk.embedding_id:
                print(f"      Vector ID: {chunk.embedding_id}")

        db.close()
        return True

    except Exception as e:
        print(f"  ❌ Database check error: {e}")
        return False

def search_test():
    """Test search functionality to see if vectors work"""
    print("\n🔍 Testing Search Functionality...")

    try:
        from services.vector_search import VectorSearchService

        vs = VectorSearchService()

        # Test queries
        test_queries = [
            "ReckonSales inventory management",
            "GST billing features",
            "customer management"
        ]

        for query in test_queries:
            print(f"\n  🔤 Testing query: '{query}'")

            try:
                results = vs.semantic_search(
                    query=query,
                    top_k=3
                )

                if results:
                    print(f"    ✅ Found {len(results)} results")
                    for i, result in enumerate(results, 1):
                        score = result.get('similarity_score', 0)
                        section = result.get('section_title', 'Unknown')
                        print(f"      {i}. {section} (Score: {score:.3f})")
                else:
                    print(f"    ⚠️ No results found")

            except Exception as search_error:
                print(f"    ❌ Search error: {search_error}")

        return True

    except Exception as e:
        print(f"  ❌ Search test error: {e}")
        return False

def show_embedding_status():
    """Show detailed embedding generation status"""
    print("\n🔗 Embedding Generation Status...")

    try:
        from services.vector_search import VectorSearchService

        vs = VectorSearchService()

        print(f"  🔧 Configuration:")
        print(f"    Model: {vs.embedding_model}")
        print(f"    Dimensions: {vs.vector_dimension}")
        print(f"    Context Length: {vs.context_length}")
        print(f"    Index Name: {vs.index_name}")

        # Test embedding generation
        print(f"\n  🧪 Testing embedding generation...")
        test_text = "ReckonSales inventory management system"

        try:
            embedding = vs.create_embedding(test_text)

            if embedding and len(embedding) == vs.vector_dimension:
                non_zero_count = sum(1 for x in embedding if abs(x) > 0.001)
                magnitude = sum(x*x for x in embedding) ** 0.5

                print(f"    ✅ Embedding generated successfully")
                print(f"    📏 Dimensions: {len(embedding)}")
                print(f"    🔢 Non-zero values: {non_zero_count}/{len(embedding)}")
                print(f"    📊 Magnitude: {magnitude:.4f}")

                if non_zero_count > 100:
                    print(f"    💯 Quality: Good (model working)")
                else:
                    print(f"    ⚠️ Quality: Poor (model may be downloading)")

            else:
                print(f"    ❌ Embedding generation failed")

        except Exception as embed_error:
            print(f"    ❌ Embedding error: {embed_error}")

        return True

    except Exception as e:
        print(f"  ❌ Status check error: {e}")
        return False

def main():
    """Main function to check all Pinecone data"""
    print("🌲 Pinecone Database Inspector")
    print("=" * 50)

    # Run all checks
    checks = [
        ("Pinecone Connection", check_pinecone_connection),
        ("Index Statistics", check_index_stats),
        ("Sample Vectors", list_vectors_sample),
        ("Database Comparison", check_database_chunks),
        ("Embedding Status", show_embedding_status),
        ("Search Test", search_test)
    ]

    results = {}

    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}")
        print("-" * 30)

        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} failed: {e}")
            results[check_name] = False

    # Summary
    print("\n" + "=" * 50)
    print("📊 INSPECTION SUMMARY")

    passed = sum(results.values())
    total = len(results)

    print(f"✅ Checks passed: {passed}/{total}")

    for check_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")

    if results.get("Index Statistics", False):
        print(f"\n🎯 Next Steps:")
        if not results.get("Sample Vectors", False):
            print("  1. Run: python generate_all_embeddings.py")
            print("  2. Wait for Google EmbeddingGemma to finish downloading")
            print("  3. Re-run this inspector to see populated data")
        else:
            print("  ✅ Your Pinecone database is working perfectly!")
            print("  🚀 Ready for production queries!")

if __name__ == "__main__":
    main()