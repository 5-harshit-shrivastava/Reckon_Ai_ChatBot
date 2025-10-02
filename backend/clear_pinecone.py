"""
Script to clear old Pinecone vectors
Run this: python clear_pinecone.py YOUR_PINECONE_API_KEY
"""

import sys

def clear_pinecone_index(api_key):
    """Clear all vectors from Pinecone index"""
    try:
        from pinecone import Pinecone

        if not api_key:
            print("❌ Please provide Pinecone API key as argument")
            print("Usage: python clear_pinecone.py YOUR_API_KEY")
            return

        pc = Pinecone(api_key=api_key)
        index_name = "reckon-bge-large-kb"
        index = pc.Index(index_name)

        # Get stats before deletion
        stats_before = index.describe_index_stats()
        print(f"\n📊 Before deletion:")
        print(f"   Total vectors: {stats_before.total_vector_count}")
        print(f"   Namespaces: {stats_before.namespaces}")

        # Delete all vectors in the namespace
        namespace = "reckon-knowledge-base"

        print(f"\n🗑️  Deleting all vectors from namespace: {namespace}")
        index.delete(delete_all=True, namespace=namespace)

        # Get stats after deletion
        import time
        time.sleep(2)  # Wait for deletion to propagate
        stats_after = index.describe_index_stats()
        print(f"\n✅ After deletion:")
        print(f"   Total vectors: {stats_after.total_vector_count}")
        print(f"   Namespaces: {stats_after.namespaces}")

        print(f"\n🎉 Successfully cleared Pinecone index!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Please provide Pinecone API key")
        print("Usage: python clear_pinecone.py YOUR_API_KEY")
        sys.exit(1)

    api_key = sys.argv[1]
    print("⚠️  WARNING: This will delete ALL vectors from Pinecone!")
    confirm = input("Type 'yes' to continue: ")
    if confirm.lower() == 'yes':
        clear_pinecone_index(api_key)
    else:
        print("Cancelled.")
