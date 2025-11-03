"""
Pinecone-only document management service
All document storage, retrieval, and management through Pinecone metadata
No PostgreSQL/Neon database required
"""

import os
import time
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from pinecone import Pinecone
from loguru import logger
from services.vector_search import VectorSearchService
from services.document_processor import DocumentProcessor


class PineconeDocumentService:
    """
    Manage documents entirely through Pinecone using metadata
    Document structure in Pinecone:
    - id: unique document ID (doc_{uuid})
    - values: embedding vector
    - metadata: {
        document_id: str,
        document_title: str,
        document_type: str,
        industry_type: str,
        language: str,
        chunk_index: int,
        chunk_text: str,
        section_title: str,
        keywords: str,
        created_at: str (ISO format),
        updated_at: str (ISO format),
        is_active: bool
      }
    """

    def __init__(self):
        self.vector_service = VectorSearchService()
        self.document_processor = DocumentProcessor()
        self.pinecone_index = self.vector_service.pinecone_index
        self.namespace = "reckon-knowledge-base"

    def create_document(
        self,
        title: str,
        content: str,
        document_type: str,
        industry_type: Optional[str] = None,
        language: str = "en",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> Dict[str, Any]:
        """
        Create a new document and store in Pinecone

        Returns:
            Dict with document_id, chunks_created, processing_time_ms
        """
        try:
            start_time = time.time()

            # Generate unique document ID
            document_id = str(uuid.uuid4())
            created_at = datetime.utcnow().isoformat()

            # Chunk the document
            chunks_data = self.document_processor.chunk_document(
                text=content,
                chunk_size=chunk_size,
                overlap=chunk_overlap
            )

            # Prepare vectors for Pinecone
            vectors = []
            for chunk_data in chunks_data:
                # Create embedding for chunk
                embedding = self.vector_service.create_embedding(
                    text=chunk_data['text'],
                    is_query=False
                )

                # Create unique vector ID
                vector_id = f"doc_{document_id}_chunk_{chunk_data['index']}"

                # Prepare metadata
                metadata = {
                    "document_id": document_id,
                    "document_title": title,
                    "document_type": document_type,
                    "industry_type": industry_type or "general",
                    "language": language,
                    "chunk_index": chunk_data['index'],
                    "chunk_text": chunk_data['text'],
                    "section_title": chunk_data.get('section_title', ''),
                    "keywords": chunk_data.get('keywords', ''),
                    "chunk_size": chunk_data['size'],
                    "created_at": created_at,
                    "updated_at": created_at,
                    "is_active": True
                }

                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })

            # Upsert to Pinecone
            if vectors:
                self.pinecone_index.upsert(
                    vectors=vectors,
                    namespace=self.namespace
                )
                logger.info(f"Created document '{title}' with {len(vectors)} chunks in Pinecone")

            processing_time = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "document_id": document_id,
                "title": title,
                "chunks_created": len(vectors),
                "processing_time_ms": processing_time,
                "created_at": created_at
            }

        except Exception as e:
            logger.error(f"Error creating document in Pinecone: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_id": None,
                "chunks_created": 0
            }

    def list_documents(
        self,
        document_type: Optional[str] = None,
        industry_type: Optional[str] = None,
        language: Optional[str] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        List documents from Pinecone metadata

        Returns:
            Dict with documents list and total_count
        """
        try:
            # Build filter
            filter_dict = {}
            if document_type:
                filter_dict["document_type"] = {"$eq": document_type}
            if industry_type:
                filter_dict["industry_type"] = {"$eq": industry_type}
            if language:
                filter_dict["language"] = {"$eq": language}
            if is_active is not None:
                filter_dict["is_active"] = {"$eq": is_active}

            # Query Pinecone to get all matching vectors
            # We'll use a dummy vector for filtering purposes
            dummy_vector = [0.0] * 1024  # bge-large-en-v1.5 dimensions

            query_response = self.pinecone_index.query(
                namespace=self.namespace,
                vector=dummy_vector,
                top_k=10000,  # Get many results
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )

            # Extract unique documents from results
            documents_map = {}
            for match in query_response.matches:
                metadata = match.metadata
                doc_id = metadata.get("document_id")

                if doc_id not in documents_map:
                    documents_map[doc_id] = {
                        "id": doc_id,
                        "title": metadata.get("document_title"),
                        "document_type": metadata.get("document_type"),
                        "industry_type": metadata.get("industry_type"),
                        "language": metadata.get("language"),
                        "is_active": metadata.get("is_active", True),
                        "created_at": metadata.get("created_at"),
                        "updated_at": metadata.get("updated_at"),
                        "chunk_count": 0
                    }

                documents_map[doc_id]["chunk_count"] += 1

            # Convert to list
            documents_list = list(documents_map.values())

            # Sort by created_at (newest first)
            documents_list.sort(
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )

            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                documents_list = [
                    doc for doc in documents_list
                    if search_lower in doc.get("title", "").lower()
                ]

            # Apply pagination
            total_count = len(documents_list)
            documents_list = documents_list[skip:skip + limit]

            return {
                "success": True,
                "documents": documents_list,
                "total_count": total_count,
                "skip": skip,
                "limit": limit
            }

        except Exception as e:
            logger.error(f"Error listing documents from Pinecone: {e}")
            return {
                "success": False,
                "documents": [],
                "total_count": 0,
                "error": str(e)
            }

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get a specific document by ID

        Returns:
            Dict with document details and chunks
        """
        try:
            # Fetch all vectors for this document
            filter_dict = {"document_id": {"$eq": document_id}}
            dummy_vector = [0.0] * 1024  # bge-large-en-v1.5 dimensions

            query_response = self.pinecone_index.query(
                namespace=self.namespace,
                vector=dummy_vector,
                top_k=10000,
                include_metadata=True,
                filter=filter_dict
            )

            if not query_response.matches:
                return {
                    "success": False,
                    "error": "Document not found",
                    "document": None
                }

            # Extract document info and chunks
            chunks = []
            doc_metadata = None

            for match in query_response.matches:
                metadata = match.metadata

                if not doc_metadata:
                    doc_metadata = {
                        "id": metadata.get("document_id"),
                        "title": metadata.get("document_title"),
                        "document_type": metadata.get("document_type"),
                        "industry_type": metadata.get("industry_type"),
                        "language": metadata.get("language"),
                        "is_active": metadata.get("is_active", True),
                        "created_at": metadata.get("created_at"),
                        "updated_at": metadata.get("updated_at")
                    }

                chunks.append({
                    "chunk_index": metadata.get("chunk_index"),
                    "chunk_text": metadata.get("chunk_text"),
                    "section_title": metadata.get("section_title"),
                    "keywords": metadata.get("keywords")
                })

            # Sort chunks by index
            chunks.sort(key=lambda x: x.get("chunk_index", 0))

            return {
                "success": True,
                "document": doc_metadata,
                "chunks": chunks,
                "chunk_count": len(chunks)
            }

        except Exception as e:
            logger.error(f"Error getting document from Pinecone: {e}")
            return {
                "success": False,
                "error": str(e),
                "document": None
            }

    def update_document(
        self,
        document_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        document_type: Optional[str] = None,
        industry_type: Optional[str] = None,
        language: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update a document in Pinecone
        If content is updated, regenerate chunks and embeddings
        """
        try:
            # Get existing document
            doc_result = self.get_document(document_id)
            if not doc_result["success"]:
                return doc_result

            existing_doc = doc_result["document"]
            updated_at = datetime.utcnow().isoformat()

            # If content changed, regenerate everything
            if content is not None:
                # Delete old vectors
                self.delete_document(document_id)

                # Create new document with updated content
                return self.create_document(
                    title=title or existing_doc["title"],
                    content=content,
                    document_type=document_type or existing_doc["document_type"],
                    industry_type=industry_type or existing_doc["industry_type"],
                    language=language or existing_doc["language"]
                )

            # If only metadata changed, update all vectors
            else:
                filter_dict = {"document_id": {"$eq": document_id}}
                # Use hardcoded dimension to avoid dimension mismatch
                dummy_vector = [0.0] * 1024  # bge-large-en-v1.5 dimensions

                query_response = self.pinecone_index.query(
                    namespace=self.namespace,
                    vector=dummy_vector,
                    top_k=10000,
                    include_metadata=True,
                    include_values=True,  # Need to include values for upsert
                    filter=filter_dict
                )

                # Update metadata for all vectors
                updates = []
                for match in query_response.matches:
                    updated_metadata = match.metadata.copy()

                    if title is not None:
                        updated_metadata["document_title"] = title
                    if document_type is not None:
                        updated_metadata["document_type"] = document_type
                    if industry_type is not None:
                        updated_metadata["industry_type"] = industry_type
                    if language is not None:
                        updated_metadata["language"] = language
                    if is_active is not None:
                        updated_metadata["is_active"] = is_active

                    updated_metadata["updated_at"] = updated_at

                    updates.append({
                        "id": match.id,
                        "values": match.values,
                        "metadata": updated_metadata
                    })

                # Upsert updated vectors
                if updates:
                    self.pinecone_index.upsert(
                        vectors=updates,
                        namespace=self.namespace
                    )

                return {
                    "success": True,
                    "document_id": document_id,
                    "chunks_updated": len(updates),
                    "message": "Document metadata updated successfully"
                }

        except Exception as e:
            logger.error(f"Error updating document in Pinecone: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def delete_document(self, document_id: str, soft_delete: bool = True) -> Dict[str, Any]:
        """
        Delete a document from Pinecone

        Args:
            document_id: Document ID to delete
            soft_delete: If True, just mark as inactive; if False, actually delete vectors
        """
        try:
            if soft_delete:
                # Just mark as inactive
                return self.update_document(
                    document_id=document_id,
                    is_active=False
                )
            else:
                # Actually delete vectors
                filter_dict = {"document_id": {"$eq": document_id}}
                dummy_vector = [0.0] * 1024  # bge-large-en-v1.5 dimensions

                query_response = self.pinecone_index.query(
                    namespace=self.namespace,
                    vector=dummy_vector,
                    top_k=10000,
                    include_metadata=True,
                    filter=filter_dict
                )

                # Delete all matching vectors
                vector_ids = [match.id for match in query_response.matches]

                if vector_ids:
                    self.pinecone_index.delete(
                        ids=vector_ids,
                        namespace=self.namespace
                    )

                return {
                    "success": True,
                    "document_id": document_id,
                    "vectors_deleted": len(vector_ids),
                    "message": f"Document deleted permanently ({len(vector_ids)} vectors removed)"
                }

        except Exception as e:
            logger.error(f"Error deleting document from Pinecone: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about documents in Pinecone
        """
        try:
            # Get index stats
            stats = self.pinecone_index.describe_index_stats()

            # Query to get all active documents
            dummy_vector = [0.0] * 1024  # bge-large-en-v1.5 dimensions
            query_response = self.pinecone_index.query(
                namespace=self.namespace,
                vector=dummy_vector,
                top_k=10000,
                include_metadata=True,
                filter={"is_active": {"$eq": True}}
            )

            # Analyze documents
            documents_by_type = {}
            documents_by_industry = {}
            documents_by_language = {}
            unique_docs = set()
            total_chunks = 0

            for match in query_response.matches:
                metadata = match.metadata
                doc_id = metadata.get("document_id")
                unique_docs.add(doc_id)
                total_chunks += 1

                # Count by type
                doc_type = metadata.get("document_type", "unknown")
                documents_by_type[doc_type] = documents_by_type.get(doc_type, 0) + 1

                # Count by industry
                industry = metadata.get("industry_type", "general")
                documents_by_industry[industry] = documents_by_industry.get(industry, 0) + 1

                # Count by language
                lang = metadata.get("language", "en")
                documents_by_language[lang] = documents_by_language.get(lang, 0) + 1

            total_docs = len(unique_docs)
            avg_chunks = total_chunks / total_docs if total_docs > 0 else 0

            return {
                "success": True,
                "total_documents": total_docs,
                "total_chunks": total_chunks,
                "average_chunks_per_doc": round(avg_chunks, 2),
                "documents_by_type": documents_by_type,
                "documents_by_industry": documents_by_industry,
                "documents_by_language": documents_by_language,
                "index_stats": {
                    "total_vector_count": stats.total_vector_count,
                    "dimension": stats.dimension
                }
            }

        except Exception as e:
            logger.error(f"Error getting analytics from Pinecone: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def search_documents(
        self,
        query: str,
        top_k: int = 5,
        document_types: Optional[List[str]] = None,
        industry_types: Optional[List[str]] = None,
        min_confidence: float = 0.0
    ) -> Dict[str, Any]:
        """
        Search documents using semantic search
        """
        try:
            start_time = time.time()

            # Use vector search service
            results = self.vector_service.semantic_search(
                query=query,
                top_k=top_k,
                document_types=document_types,
                industry_types=industry_types,
                min_confidence=min_confidence
            )

            search_time = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "query": query,
                "results": results,
                "total_results": len(results),
                "search_time_ms": search_time
            }

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
