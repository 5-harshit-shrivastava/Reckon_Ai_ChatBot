import os
import time
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from pinecone import Pinecone, ServerlessSpec
import json
from loguru import logger
from dotenv import load_dotenv

# Load environment variables at module level
load_dotenv()


class NewVectorSearchService:
    """NEW Service for vector-based semantic search using HuggingFace Hub API"""
    
    def __init__(self):
        self.pinecone_client = None
        self.pinecone_index = None
        self.hf_client = None
        # Use BAAI/bge-large-en-v1.5 with new HuggingFace Hub API
        self.embedding_model = "BAAI/bge-large-en-v1.5"
        self.vector_dimension = 1024  # bge-large-en-v1.5 dimensions
        self.context_length = 8000  # Model context length
        self.model_description = "BAAI/bge-large-en-v1.5 via HuggingFace Hub API - High-quality multilingual embeddings"
        self.index_name = "reckon-knowledge-base"
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize Pinecone and HuggingFace Hub client"""
        logger.info("=== STARTING NEW VECTOR SEARCH INITIALIZATION ===")
        
        # Initialize hf_client to None by default
        self.hf_client = None
        
        try:
            # Initialize HuggingFace Hub client
            logger.info("Initializing HuggingFace Hub client...")
            try:
                from huggingface_hub import InferenceClient
                logger.info("huggingface_hub imported successfully")
                
                hf_token = os.getenv("HUGGINGFACE_API_TOKEN") or os.getenv("HF_TOKEN")
                logger.info(f"Token found: {bool(hf_token)}")
                
                if hf_token:
                    self.hf_client = InferenceClient(token=hf_token)
                    logger.info("🎉 HuggingFace Hub client initialized successfully!")
                else:
                    logger.warning("No HuggingFace token found - will use mathematical fallback")
                    self.hf_client = None
            except ImportError as e:
                logger.warning(f"huggingface_hub not available: {e} - will use mathematical fallback")
                self.hf_client = None
            except Exception as e:
                logger.warning(f"Failed to initialize HuggingFace client: {e} - will use mathematical fallback")
                self.hf_client = None
            
            # Initialize Pinecone
            logger.info("Initializing Pinecone...")
            pinecone_api_key = os.getenv("PINECONE_API_KEY")
            
            if pinecone_api_key:
                self.pinecone_client = Pinecone(api_key=pinecone_api_key)
                
                # Check if index exists
                existing_indexes = self.pinecone_client.list_indexes()
                index_names = [idx.name for idx in existing_indexes]
                
                if self.index_name not in index_names:
                    logger.info(f"Creating Pinecone index: {self.index_name}")
                    
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
                    logger.info(f"Created index: {self.index_name}")
                
                # Connect to the index
                self.pinecone_index = self.pinecone_client.Index(self.index_name)
                logger.info("Pinecone index connected")
                
                # Test index stats
                try:
                    stats = self.pinecone_index.describe_index_stats()
                    logger.info(f"Index stats: {stats}")
                except Exception as e:
                    logger.warning(f"Could not get index stats: {e}")
                
            else:
                logger.error("Pinecone API key not found - vector search will not work")
                
        except Exception as e:
            logger.error(f"Error initializing services: {e}")
            
        logger.info("=== NEW VECTOR SEARCH INITIALIZATION COMPLETE ===")

    def create_embedding(self, text: str, is_query: bool = False) -> List[float]:
        """
        Create embedding using BAAI/bge-large-en-v1.5 via HuggingFace Hub API

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

            logger.info(f"Creating embedding with {self.embedding_model}")

            # Try HuggingFace Hub API
            try:
                embedding = self._create_embedding_with_api(text, self.embedding_model, is_query)
                if embedding and len(embedding) == self.vector_dimension:
                    logger.info(f"✅ HuggingFace Hub API success - {len(embedding)} dimensions")
                    return embedding
                else:
                    raise Exception(f"API returned wrong dimensions: expected {self.vector_dimension}, got {len(embedding) if embedding else 0}")
                    
            except Exception as api_error:
                logger.warning(f"HuggingFace Hub API failed: {api_error}, using mathematical fallback")
                
                # Fallback to mathematical embedding
                embedding = self._create_mathematical_embedding(text)
                if embedding:
                    return embedding
                else:
                    raise Exception("All embedding methods failed")

        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            # Don't return zero vector - raise error to be handled by caller
            raise Exception(f"Embedding generation failed: {str(e)}")

    def _create_embedding_with_api(self, text: str, model_name: str, is_query: bool = False) -> List[float]:
        """Create embedding via new HuggingFace Hub API"""
        if not self.hf_client:
            raise Exception("HuggingFace Hub client not available")

        try:
            # bge models use query/passage prefixes for better performance
            if is_query:
                formatted_text = f"query: {text}"
            else:
                formatted_text = f"passage: {text}"

            # Use the new HuggingFace Hub client
            logger.info(f"Creating embedding with {model_name}")
            embeddings = self.hf_client.feature_extraction(formatted_text, model=model_name)
            
            # Handle numpy array response
            if hasattr(embeddings, 'tolist'):
                embedding = embeddings.tolist()
            else:
                embedding = list(embeddings)
            
            if embedding and len(embedding) == self.vector_dimension:
                # Normalize the embedding
                import numpy as np
                embedding_array = np.array(embedding)
                norm = np.linalg.norm(embedding_array)
                if norm > 0:
                    embedding_array = embedding_array / norm
                
                logger.info(f"✅ HuggingFace Hub API success - {len(embedding)} dimensions")
                return embedding_array.tolist()
            else:
                raise Exception(f"Wrong dimensions: expected {self.vector_dimension}, got {len(embedding) if embedding else 0}")
                
        except Exception as e:
            logger.error(f"HuggingFace Hub API failed: {e}")
            raise e

    def _create_mathematical_embedding(self, text: str) -> List[float]:
        """Create a simple mathematical embedding as fallback when API fails"""
        import hashlib
        import numpy as np
        
        # Create a deterministic hash-based embedding
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to numeric values
        hash_ints = [int(text_hash[i:i+2], 16) for i in range(0, len(text_hash), 2)]
        
        # Extend to required dimensions
        while len(hash_ints) < self.vector_dimension:
            hash_ints.extend(hash_ints)
        
        # Take only required dimensions
        hash_ints = hash_ints[:self.vector_dimension]
        
        # Normalize to [-1, 1] range
        embedding = np.array(hash_ints, dtype=float)
        embedding = (embedding - 127.5) / 127.5
        
        # Add some text-based features
        text_lower = text.lower()
        char_counts = np.zeros(26)
        for char in text_lower:
            if 'a' <= char <= 'z':
                char_counts[ord(char) - ord('a')] += 1
        
        # Mix in character frequency features (first 26 dimensions)
        if len(char_counts) <= self.vector_dimension:
            embedding[:len(char_counts)] = (embedding[:len(char_counts)] + char_counts[:self.vector_dimension]) / 2
        
        # Normalize the final embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        logger.info(f"✅ Mathematical fallback embedding created - {len(embedding)} dimensions")
        return embedding.tolist()

    def search_similar_chunks(self, query: str, top_k: int = 5, namespace: str = None) -> List[Dict[str, Any]]:
        """
        Search for similar document chunks using vector similarity
        
        Args:
            query: Search query text
            top_k: Number of results to return
            namespace: Pinecone namespace to search in
            
        Returns:
            List of matching chunks with metadata and scores
        """
        try:
            if not self.pinecone_index:
                logger.error("Pinecone index not available")
                return []
            
            # Create query embedding
            query_embedding = self.create_embedding(query, is_query=True)
            
            # Search in Pinecone
            search_response = self.pinecone_index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=namespace or "reckon-knowledge-base"
            )
            
            results = []
            for match in search_response.matches:
                result = {
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "document_title": match.metadata.get("document_title", "Unknown"),
                    "chunk_index": match.metadata.get("chunk_index", 0),
                    "metadata": match.metadata
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} similar chunks for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {e}")
            return []

    def semantic_search(
        self, 
        query: str, 
        top_k: int = 5,
        document_types: List[str] = None,
        industry_types: List[str] = None,
        min_confidence: float = 0.0
    ) -> List[Dict]:
        """
        Perform semantic search using Pinecone with new HuggingFace embeddings
        
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
            if not self.pinecone_index:
                logger.error("Pinecone index not available")
                return []
            
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

            # Search in our namespace
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
                # Get chunk text from metadata
                chunk_text = match.metadata.get("text", match.metadata.get("chunk_text", ""))
                
                # Get IDs from metadata
                chunk_id = match.metadata.get("chunk_id")
                document_id = match.metadata.get("document_id")
                
                # If chunk_id is None, extract from vector ID
                if chunk_id is None and match.id:
                    try:
                        if "_chunk_" in match.id:
                            chunk_index = match.id.split("_chunk_")[-1]
                            chunk_id = f"{document_id}_chunk_{chunk_index}"
                    except:
                        chunk_id = match.id
                
                # Convert chunk_id to int if possible
                if chunk_id is not None:
                    try:
                        chunk_id = int(float(chunk_id))
                    except (ValueError, TypeError):
                        chunk_id = str(chunk_id)
                
                result = {
                    "id": match.id,
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "similarity_score": float(match.score),
                    "confidence_score": float(match.score),  # Added for compatibility
                    "chunk_text": chunk_text,  # Changed from 'text' to 'chunk_text'
                    "text": chunk_text,  # Keep both for backward compatibility
                    "document_title": match.metadata.get("document_title", "Unknown"),
                    "document_type": match.metadata.get("document_type", "Unknown"),
                    "industry_type": match.metadata.get("industry_type", "Unknown"),
                    "chunk_index": match.metadata.get("chunk_index", 0),
                    "section_title": match.metadata.get("section_title", ""),  # Added for RAG service
                    "metadata": match.metadata
                }
                results.append(result)
            
            logger.info(f"Semantic search returned {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
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
            # Get semantic search results with new embeddings
            semantic_results = self.semantic_search(
                query=query,
                top_k=top_k * 2,  # Get more results for reranking
                document_types=document_types,
                industry_types=industry_types
            )
            
            # For now, just use semantic results since we have proper embeddings
            # Text search can be added later if needed
            logger.info(f"Hybrid search returning {len(semantic_results[:top_k])} results for query: {query[:50]}...")
            return semantic_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []