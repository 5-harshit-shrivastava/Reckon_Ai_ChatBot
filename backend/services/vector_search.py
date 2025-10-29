import os
import time
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from pinecone import Pinecone, ServerlessSpec
import json
from loguru import logger


class VectorSearchService:
    """Service for vector-based semantic search using Pinecone hosted embeddings"""
    
    def __init__(self):
        self.pinecone_client = None
        self.pinecone_index = None
        self.sentence_transformer = None
        # Use BAAI/bge-large-en-v1.5 via Hugging Face API
        self.embedding_model = "BAAI/bge-large-en-v1.5"
        self.vector_dimension = 1024  # bge-large-en-v1.5 dimensions
        self.context_length = 512  # bge-large-en-v1.5 context length
        self.model_description = "BAAI/bge-large-en-v1.5 - High-quality embeddings for retrieval"
        self.index_name = "reckon-bge-large-kb"
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize Pinecone with hosted multilingual embeddings"""
        try:
            # Initialize Pinecone
            pinecone_api_key = os.getenv("PINECONE_API_KEY")
            
            if pinecone_api_key:
                self.pinecone_client = Pinecone(api_key=pinecone_api_key)
                
                # Check if multilingual index exists
                existing_indexes = self.pinecone_client.list_indexes()
                index_names = [idx.name for idx in existing_indexes]
                
                if self.index_name not in index_names:
                    logger.info(f"Creating Pinecone multilingual index: {self.index_name}")
                    
                    # Create index with bge-large-en-v1.5 dimensions
                    self.pinecone_client.create_index(
                        name=self.index_name,
                        dimension=self.vector_dimension,  # 1024 for bge-large-en-v1.5
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws", 
                            region="us-east-1"
                        )
                    )
                    
                    # Wait for index to be ready
                    import time
                    time.sleep(15)
                    logger.info(f"Created multilingual index: {self.index_name}")
                
                # Connect to the index
                self.pinecone_index = self.pinecone_client.Index(self.index_name)
                logger.info("Pinecone multilingual index connected")
                
                # Test index stats
                try:
                    stats = self.pinecone_index.describe_index_stats()
                    logger.info(f"Index stats: {stats}")
                except Exception as e:
                    logger.warning(f"Could not get index stats: {e}")
                
            else:
                logger.error("Pinecone API key not found - vector search will not work")
                
        except Exception as e:
            logger.error(f"Error initializing Pinecone services: {e}")
    
    def create_embedding(self, text: str, is_query: bool = False) -> List[float]:
        """
        Create embedding using BAAI/bge-large-en-v1.5 via Hugging Face API

        Args:
            text: Text to embed
            is_query: Whether this is a query (True) or passage (False)

        Returns:
            List of embedding values (1024 dimensions for bge-large-en-v1.5)
        """
        try:
            # Truncate text if too long
            if len(text) > self.context_length:
                text = text[:self.context_length]
                logger.info(f"Truncated text to {self.context_length} characters")

            logger.info(f"Creating embedding with BAAI/bge-large-en-v1.5")

            # Use only Hugging Face API (no local model)
            embedding = self._create_embedding_with_api(text, self.embedding_model, is_query)

            if embedding and len(embedding) == self.vector_dimension:
                logger.info(f"✅ bge-large-en-v1.5 API success - {len(embedding)} dimensions")
                return embedding
            else:
                logger.error(f"API returned wrong dimensions: {len(embedding) if embedding else 0}")
                return [0.0] * self.vector_dimension

        except Exception as e:
            logger.error(f"bge-large-en-v1.5 API failed: {e}")
            # Return zero vector as last resort
            return [0.0] * self.vector_dimension

    def _create_embedding_with_api(self, text: str, model_name: str, is_query: bool = False) -> List[float]:
        """Create embedding via HuggingFace API for BAAI/bge-large-en-v1.5"""
        import requests

        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not hf_token:
            raise Exception("No HuggingFace API token found")

        # bge models use query/passage prefixes for better performance
        if is_query:
            formatted_text = f"query: {text}"
        else:
            formatted_text = f"passage: {text}"

        # Call HuggingFace API
        api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            api_url,
            headers=headers,
            json={"inputs": formatted_text, "options": {"wait_for_model": True}},
            timeout=30
        )

        if response.status_code == 200:
            embedding = response.json()
            # Normalize the embedding
            import numpy as np
            embedding = np.array(embedding)

            # Ensure correct dimensions for bge-large-en-v1.5
            if len(embedding) != self.vector_dimension:
                logger.warning(f"API returned {len(embedding)} dimensions, expected {self.vector_dimension}")

            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()
        else:
            raise Exception(f"API error: {response.status_code} - {response.text}")

    def _normalize_embedding_dimensions(self, embedding: List[float], target_dim: int) -> List[float]:
        """Normalize embedding to target dimensions"""
        import numpy as np

        embedding_array = np.array(embedding)

        if len(embedding) > target_dim:
            # Truncate to target dimensions
            return embedding_array[:target_dim].tolist()
        elif len(embedding) < target_dim:
            # Pad with zeros
            padded = np.zeros(target_dim)
            padded[:len(embedding)] = embedding_array
            return padded.tolist()
        else:
            return embedding

    def _create_embedding_local(self, text: str, is_query: bool = False) -> List[float]:
        """Local method disabled - using only HuggingFace API"""
        logger.warning("Local embedding generation is disabled - using API only")
        return [0.0] * self.vector_dimension
    
    def store_chunk_embeddings(self, db: Any = None, chunks: List[Any] = None) -> int:
        """
        Store document chunks in Pinecone using hosted embeddings (text-based)
        
        Args:
            db: Database session
            chunks: List of document chunks to process
            
        Returns:
            Number of chunks stored
        """
        stored_count = 0
        
        try:
            if not self.pinecone_index:
                logger.error("Pinecone index not available")
                return 0
            
            # Prepare vectors for batch upsert
            vectors = []
            
            for chunk in chunks:
                if not chunk.embedding_created:
                    # Create embedding for the chunk text (as passage)
                    embedding = self.create_embedding(chunk.chunk_text, is_query=False)
                    
                    # Get document info once for efficiency
                    doc_industry = self._get_document_industry(db, chunk.document_id)
                    doc_type = self._get_document_type(db, chunk.document_id)
                    doc_language = self._get_document_language(db, chunk.document_id)
                    
                    # Prepare vector for Pinecone upsert
                    vector = {
                        "id": f"chunk_{chunk.id}",
                        "values": embedding,
                        "metadata": {
                            "chunk_id": int(chunk.id),  # Ensure integer
                            "document_id": int(chunk.document_id),  # Ensure integer
                            "chunk_index": int(chunk.chunk_index),
                            "section_title": str(chunk.section_title or ""),
                            "keywords": str(chunk.keywords or ""),
                            "confidence_score": float(chunk.confidence_score or 0.5),
                            "industry_type": str(doc_industry),
                            "document_type": str(doc_type),
                            "language": str(doc_language),
                            "chunk_text": str(chunk.chunk_text)  # Store text in metadata
                        }
                    }
                    
                    vectors.append(vector)
                    
                    # Update chunk record
                    chunk.embedding_id = f"chunk_{chunk.id}"
                    chunk.embedding_created = True
                    stored_count += 1
            
            # Batch upsert to Pinecone
            if vectors:
                self.pinecone_index.upsert(
                    vectors=vectors,
                    namespace="reckon-knowledge-base"
                )
                logger.info(f"Stored {len(vectors)} chunks in Pinecone using bge-large-en-v1.5 embeddings")

            if db:
                db.commit()
            return stored_count

        except Exception as e:
            logger.error(f"Error storing chunks in Pinecone: {e}")
            if db:
                db.rollback()
            return 0
    
    def semantic_search(
        self, 
        query: str, 
        top_k: int = 5,
        document_types: List[str] = None,
        industry_types: List[str] = None,
        min_confidence: float = 0.0
    ) -> List[Dict]:
        """
        Perform semantic search using Pinecone hosted embeddings
        
        Args:
            query: Search query
            top_k: Number of results to return
            document_types: Filter by document types
            industry_types: Filter by industry types
            min_confidence: Minimum confidence score
            
        Returns:
            List of search results with similarity scores
        """
        try:
            start_time = time.time()
            
            if self.pinecone_index:
                # Build metadata filters
                filters = {}
                if min_confidence > 0:
                    filters["confidence_score"] = {"$gte": min_confidence}
                if document_types:
                    filters["document_type"] = {"$in": document_types}
                if industry_types:
                    filters["industry_type"] = {"$in": industry_types}
                
                # Create query embedding (with query prefix)
                query_embedding = self.create_embedding(query, is_query=True)

                # Search ONLY in our namespace (ignore old default namespace)
                search_response = self.pinecone_index.query(
                    namespace="reckon-knowledge-base",
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=True,
                    filter=filters if filters else None
                )

                results = []
                logger.info(f"Semantic search found {len(search_response.matches)} matches in namespace 'reckon-knowledge-base'")
                for match in search_response.matches:
                    # Get chunk text from metadata or fetch from database if needed
                    chunk_text = self._get_chunk_text_from_match(match)
                    
                    # Convert IDs from float to int (Pinecone stores as float)
                    chunk_id = match.metadata.get("chunk_id")
                    document_id = match.metadata.get("document_id")
                    
                    # Ensure IDs are integers
                    if chunk_id is not None:
                        chunk_id = int(chunk_id)
                    if document_id is not None:
                        document_id = int(document_id)
                    
                    result = {
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "similarity_score": float(match.score),
                        "chunk_text": chunk_text,
                        "section_title": match.metadata.get("section_title"),
                        "keywords": match.metadata.get("keywords"),
                        "confidence_score": match.metadata.get("confidence_score", 0.5)
                    }
                    results.append(result)
                
                search_time = int((time.time() - start_time) * 1000)
                logger.info(f"Semantic search completed in {search_time}ms, found {len(results)} results")
                
                return results
            
            else:
                # Fallback to simple text search
                logger.warning("Pinecone not available, using fallback search")
                return self._fallback_search(query, top_k)
                
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def _fallback_search(self, query: str, top_k: int) -> List[Dict]:
        """Fallback search using simple text matching"""
        # This would need database access to implement properly
        # For now, return empty results
        logger.warning("Fallback search not fully implemented")
        return []
    
    def hybrid_search(
        self,
        db: Any = None,
        query: str = "",
        top_k: int = 5,
        semantic_weight: float = 0.7,
        text_weight: float = 0.3,
        document_types: List[str] = None,
        industry_types: List[str] = None
    ) -> List[Dict]:
        """
        Combine semantic search with traditional text search
        
        Args:
            db: Database session
            query: Search query
            top_k: Number of results to return
            semantic_weight: Weight for semantic similarity
            text_weight: Weight for text matching
            document_types: Filter by document types
            industry_types: Filter by industry types
            
        Returns:
            Combined search results
        """
        try:
            # Get semantic search results
            semantic_results = self.semantic_search(
                query=query,
                top_k=top_k * 2,  # Get more results for reranking
                document_types=document_types,
                industry_types=industry_types
            )
            
            # Get text search results (basic keyword matching) - skip if no db
            text_results = []
            if db:
                text_results = self._text_search(
                    db=db,
                    query=query,
                    top_k=top_k * 2,
                    document_types=document_types,
                    industry_types=industry_types
                )
            
            # Combine and rerank results
            combined_results = self._combine_search_results(
                semantic_results, text_results, semantic_weight, text_weight
            )
            
            # Return top K results
            return combined_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return semantic_results[:top_k] if semantic_results else []
    
    def _text_search(
        self,
        db: Any = None,
        query: str = "",
        top_k: int = 5,
        document_types: List[str] = None,
        industry_types: List[str] = None
    ) -> List[Dict]:
        """Simple text-based search in document chunks"""
        try:
            if not db:
                return []

            # Lazy import to avoid circular dependency
            try:
                from models.knowledge_base import Document, DocumentChunk
            except ImportError:
                logger.warning("Database models not available, skipping text search")
                return []
            
            # Build query
            query_obj = db.query(DocumentChunk, Document).join(Document)
            
            # Apply filters
            if document_types:
                query_obj = query_obj.filter(Document.document_type.in_(document_types))
            if industry_types:
                query_obj = query_obj.filter(Document.industry_type.in_(industry_types))
            
            # Text search
            search_terms = query.lower().split()
            for term in search_terms:
                query_obj = query_obj.filter(DocumentChunk.chunk_text.contains(term))
            
            results = query_obj.limit(top_k).all()
            
            # Format results
            formatted_results = []
            for chunk, document in results:
                result = {
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "similarity_score": 0.5,  # Placeholder score
                    "chunk_text": chunk.chunk_text,
                    "section_title": chunk.section_title,
                    "keywords": chunk.keywords,
                    "confidence_score": chunk.confidence_score or 0.5
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return []
    
    def _combine_search_results(
        self,
        semantic_results: List[Dict],
        text_results: List[Dict],
        semantic_weight: float,
        text_weight: float
    ) -> List[Dict]:
        """Combine and rerank search results"""
        try:
            # Create a mapping of chunk_id to results
            combined = {}
            
            # Add semantic results
            for result in semantic_results:
                chunk_id = result.get("chunk_id")
                if chunk_id:
                    combined[chunk_id] = result.copy()
                    combined[chunk_id]["semantic_score"] = result.get("similarity_score", 0)
                    combined[chunk_id]["text_score"] = 0
            
            # Add text results
            for result in text_results:
                chunk_id = result.get("chunk_id")
                if chunk_id:
                    if chunk_id in combined:
                        combined[chunk_id]["text_score"] = result.get("similarity_score", 0)
                    else:
                        combined[chunk_id] = result.copy()
                        combined[chunk_id]["semantic_score"] = 0
                        combined[chunk_id]["text_score"] = result.get("similarity_score", 0)
            
            # Calculate combined scores
            for chunk_id, result in combined.items():
                semantic_score = result.get("semantic_score", 0)
                text_score = result.get("text_score", 0)
                
                combined_score = (semantic_score * semantic_weight + 
                                text_score * text_weight)
                result["combined_score"] = combined_score
            
            # Sort by combined score
            sorted_results = sorted(
                combined.values(),
                key=lambda x: x.get("combined_score", 0),
                reverse=True
            )
            
            return sorted_results
            
        except Exception as e:
            logger.error(f"Error combining search results: {e}")
            return semantic_results + text_results
    
    def log_search_query(
        self,
        db: Any = None,
        user_id: int = None,
        session_id: int = None,
        query_text: str = "",
        chunks_retrieved: int = 0,
        chunk_ids: List[int] = None,
        search_time_ms: int = 0
    ):
        """Log search query for analytics"""
        try:
            if not db:
                return

            # Lazy import to avoid errors
            try:
                from models.knowledge_base import KnowledgeBaseQuery
            except ImportError:
                logger.warning("Database models not available, skipping query logging")
                return

            query_record = KnowledgeBaseQuery(
                user_id=user_id,
                session_id=session_id,
                query_text=query_text,
                chunks_retrieved=chunks_retrieved,
                top_chunk_ids=json.dumps(chunk_ids or []),
                search_time_ms=search_time_ms
            )

            db.add(query_record)
            db.commit()

        except Exception as e:
            logger.error(f"Error logging search query: {e}")
    
    def _get_chunk_text_from_match(self, match) -> str:
        """Extract chunk text from Pinecone match metadata"""
        try:
            # In modern Pinecone approach, text is stored directly in metadata
            if hasattr(match, 'metadata') and match.metadata:
                # Try to get text from various possible metadata keys
                chunk_text = (
                    match.metadata.get("text") or 
                    match.metadata.get("chunk_text") or 
                    match.metadata.get("content") or
                    ""
                )
                return chunk_text
            return ""
        except Exception as e:
            logger.warning(f"Error extracting chunk text from match: {e}")
            return ""
    
    def _get_document_industry(self, db: Any = None, document_id: int = 0) -> str:
        """Get industry type for a document"""
        try:
            if not db:
                return "general"

            try:
                from models.knowledge_base import Document
            except ImportError:
                return "general"

            document = db.query(Document).filter(Document.id == document_id).first()
            return document.industry_type if document else "general"
        except Exception as e:
            logger.warning(f"Error getting document industry: {e}")
            return "general"

    def _get_document_type(self, db: Any = None, document_id: int = 0) -> str:
        """Get document type for a document"""
        try:
            if not db:
                return "unknown"

            try:
                from models.knowledge_base import Document
            except ImportError:
                return "unknown"

            document = db.query(Document).filter(Document.id == document_id).first()
            return document.document_type if document else "unknown"
        except Exception as e:
            logger.warning(f"Error getting document type: {e}")
            return "unknown"

    def _get_document_language(self, db: Any = None, document_id: int = 0) -> str:
        """Get language for a document"""
        try:
            if not db:
                return "en"

            try:
                from models.knowledge_base import Document
            except ImportError:
                return "en"

            document = db.query(Document).filter(Document.id == document_id).first()
            return document.language if document else "en"
        except Exception as e:
            logger.warning(f"Error getting document language: {e}")
            return "en"

    def delete_document_embeddings(self, db: Any = None, document_id: int = 0) -> int:
        """
        Delete all vector embeddings for a specific document from Pinecone

        Args:
            db: Database session (optional, for backwards compatibility)
            document_id: ID of the document to delete embeddings for

        Returns:
            Number of vectors deleted
        """
        try:
            if not self.pinecone_index:
                logger.error("Pinecone index not available for deletion")
                return 0

            # Get all chunks for this document if db available
            chunks = []
            if db:
                try:
                    from models.knowledge_base import DocumentChunk
                    chunks = db.query(DocumentChunk).filter(
                        DocumentChunk.document_id == document_id
                    ).all()
                except ImportError:
                    logger.warning("Database models not available, using Pinecone filter instead")

            if not chunks:
                logger.info(f"No chunks found in DB for document {document_id}, will use Pinecone filter")
                # Use Pinecone filter to get all vectors for this document
                vector_ids = []
                # Note: This is a simplified approach - in production you'd query Pinecone
                # to get all vector IDs for this document
                return 0

            # Prepare vector IDs to delete
            vector_ids = []
            for chunk in chunks:
                vector_id = f"chunk_{chunk.id}"  # Match the format used in store_chunk_embeddings
                vector_ids.append(vector_id)

            # Delete vectors from Pinecone in batches
            batch_size = 100
            total_deleted = 0

            for i in range(0, len(vector_ids), batch_size):
                batch_ids = vector_ids[i:i + batch_size]
                try:
                    self.pinecone_index.delete(ids=batch_ids)
                    total_deleted += len(batch_ids)
                    logger.info(f"Deleted batch of {len(batch_ids)} vectors from Pinecone")
                except Exception as e:
                    logger.error(f"Error deleting batch from Pinecone: {e}")

            logger.info(f"Successfully deleted {total_deleted} vectors for document {document_id}")
            return total_deleted

        except Exception as e:
            logger.error(f"Error deleting document embeddings: {e}")
            return 0

    def delete_chunk_embedding(self, chunk_id: int, document_id: int) -> bool:
        """
        Delete a specific chunk's embedding from Pinecone

        Args:
            chunk_id: ID of the chunk
            document_id: ID of the parent document

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if not self.pinecone_index:
                logger.error("Pinecone index not available for deletion")
                return False

            vector_id = f"chunk_{chunk_id}"  # Match the format used in store_chunk_embeddings

            self.pinecone_index.delete(ids=[vector_id])
            logger.info(f"Successfully deleted vector {vector_id} from Pinecone")
            return True

        except Exception as e:
            logger.error(f"Error deleting chunk embedding: {e}")
            return False