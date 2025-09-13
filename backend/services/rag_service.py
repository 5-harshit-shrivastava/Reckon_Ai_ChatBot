import os
import time
import json
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from openai import OpenAI
from services.vector_search import VectorSearchService
from services.multilingual_alternatives import HuggingFaceRAGService, get_recommended_setup
from models.knowledge_base import Document, DocumentChunk, KnowledgeBaseQuery
from models.chat import ChatSession
from models.user import User
from loguru import logger


class RAGService:
    """
    Retrieval-Augmented Generation service for ReckonSales chatbot
    Combines vector search with GPT-4 to generate contextual responses
    """
    
    def __init__(self):
        self.vector_search = VectorSearchService()
        self.openai_client = None
        self.huggingface_service = None
        self.model_name = "gpt-3.5-turbo"  # More accessible model
        self.max_context_tokens = 8000  # Leave room for response
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize OpenAI and HuggingFace services"""
        try:
            # Try to initialize OpenAI first
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                self.openai_client = OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized for RAG service")
            else:
                logger.warning("OpenAI API key not found, will use HuggingFace as fallback")

            # Initialize HuggingFace service as fallback
            try:
                self.huggingface_service = HuggingFaceRAGService()
                logger.info("HuggingFace multilingual service initialized as fallback")
            except Exception as hf_error:
                logger.warning(f"HuggingFace service initialization failed: {hf_error}")

        except Exception as e:
            logger.error(f"Error initializing services: {e}")
    
    def generate_rag_response(
        self,
        db: Session,
        user_query: str,
        session_id: int = None,
        user_id: int = None,
        industry_context: str = None,
        language: str = "en"
    ) -> Dict:
        """
        Generate RAG-powered response for user query
        
        Args:
            db: Database session
            user_query: User's question
            session_id: Chat session ID
            user_id: User ID for personalization
            industry_context: Industry type for filtering
            language: Response language
            
        Returns:
            Dict with response, sources, and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Retrieve relevant documents
            search_results = self._retrieve_relevant_docs(
                db=db,
                query=user_query,
                industry_context=industry_context,
                user_id=user_id
            )
            
            # Step 2: Build context from retrieved documents
            context = self._build_context(search_results)
            
            # Step 3: Generate response using GPT-4
            response_data = self._generate_response(
                user_query=user_query,
                context=context,
                industry_context=industry_context,
                language=language,
                session_id=session_id,
                db=db
            )
            
            # Step 4: Log the query for analytics
            processing_time = int((time.time() - start_time) * 1000)
            self._log_rag_query(
                db=db,
                user_id=user_id,
                session_id=session_id,
                query=user_query,
                chunks_retrieved=len(search_results),
                chunk_ids=[r.get("chunk_id") for r in search_results],
                processing_time=processing_time,
                response_generated=response_data.get("success", False)
            )
            
            return {
                "success": True,
                "response": response_data.get("response", ""),
                "confidence": response_data.get("confidence", 0.7),
                "sources": self._format_sources(search_results),
                "processing_time_ms": processing_time,
                "chunks_used": len(search_results),
                "model_used": self.model_name,
                "industry_context": industry_context,
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Error in RAG response generation: {e}")
            return {
                "success": False,
                "response": self._get_fallback_response(user_query, language),
                "confidence": 0.3,
                "sources": [],
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "chunks_used": 0,
                "error": str(e)
            }
    
    def _retrieve_relevant_docs(
        self,
        db: Session,
        query: str,
        industry_context: str = None,
        user_id: int = None,
        top_k: int = 5
    ) -> List[Dict]:
        """Retrieve relevant document chunks using vector search"""
        try:
            # Determine document types and industry filters
            document_types = None
            industry_types = [industry_context] if industry_context else None
            
            # Use hybrid search for better results
            search_results = self.vector_search.hybrid_search(
                db=db,
                query=query,
                top_k=top_k,
                document_types=document_types,
                industry_types=industry_types
            )
            
            logger.info(f"Retrieved {len(search_results)} relevant chunks for query")
            return search_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def _build_context(self, search_results: List[Dict], max_tokens: int = 6000) -> str:
        """
        Build context string from search results
        
        Args:
            search_results: List of search result dictionaries
            max_tokens: Maximum tokens for context (approximate)
            
        Returns:
            Formatted context string
        """
        if not search_results:
            return ""
        
        context_parts = []
        current_length = 0
        max_chars = max_tokens * 4  # Rough approximation: 1 token ≈ 4 chars
        
        for i, result in enumerate(search_results):
            chunk_text = result.get("chunk_text", "")
            section_title = result.get("section_title", "")
            confidence = result.get("confidence_score", 0.5)
            
            # Format the chunk with metadata
            chunk_context = f"\n--- Source {i+1} ---"
            if section_title:
                chunk_context += f"\nSection: {section_title}"
            chunk_context += f"\nConfidence: {confidence:.2f}"
            chunk_context += f"\nContent: {chunk_text}\n"
            
            # Check if adding this chunk would exceed the limit
            if current_length + len(chunk_context) > max_chars:
                break
            
            context_parts.append(chunk_context)
            current_length += len(chunk_context)
        
        context = "\n".join(context_parts)
        logger.debug(f"Built context with {len(context_parts)} chunks, {current_length} characters")
        
        return context
    
    def _generate_response(
        self,
        user_query: str,
        context: str,
        industry_context: str = None,
        language: str = "en",
        session_id: int = None,
        db: Session = None
    ) -> Dict:
        """Generate response using OpenAI GPT-4 or HuggingFace with ReckonSales context"""

        # Try OpenAI first
        if self.openai_client:
            return self._generate_openai_response(user_query, context, industry_context, language, session_id, db)

        # Fall back to HuggingFace if OpenAI is not available
        elif self.huggingface_service:
            return self._generate_huggingface_response(user_query, context, language)

        # If neither service is available
        else:
            return {
                "success": False,
                "response": self._get_fallback_response(user_query, language),
                "confidence": 0.3,
                "model_used": "fallback_text"
            }

    def _generate_openai_response(
        self,
        user_query: str,
        context: str,
        industry_context: str = None,
        language: str = "en",
        session_id: int = None,
        db: Session = None
    ) -> Dict:
        """Generate response using OpenAI GPT"""
        try:
            # Build the system prompt
            system_prompt = self._build_system_prompt(industry_context, language)

            # Build the user prompt with context
            user_prompt = self._build_user_prompt(user_query, context, language)

            # Get conversation history for better context
            conversation_history = self._get_conversation_history(db, session_id) if session_id else []

            # Build messages array
            messages = [{"role": "system", "content": system_prompt}]

            # Add recent conversation history
            messages.extend(conversation_history[-4:])  # Last 4 messages for context

            # Add current query
            messages.append({"role": "user", "content": user_prompt})

            # Generate response
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )

            ai_response = response.choices[0].message.content.strip()

            # Calculate confidence based on response quality
            confidence = self._calculate_response_confidence(ai_response, context)

            return {
                "success": True,
                "response": ai_response,
                "confidence": confidence,
                "tokens_used": response.usage.total_tokens,
                "model_used": self.model_name
            }

        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            # Try HuggingFace as fallback
            if self.huggingface_service:
                logger.info("Falling back to HuggingFace due to OpenAI error")
                return self._generate_huggingface_response(user_query, context, language)
            else:
                return {
                    "success": False,
                    "response": self._get_fallback_response(user_query, language),
                    "confidence": 0.3,
                    "model_used": "fallback_text"
                }

    def _generate_huggingface_response(
        self,
        user_query: str,
        context: str,
        language: str = "en"
    ) -> Dict:
        """Generate response using HuggingFace local models"""
        try:
            logger.info("Using HuggingFace multilingual model for response generation")

            # Use the HuggingFace service
            hf_result = self.huggingface_service.generate_response(
                query=user_query,
                context=context,
                language=language
            )

            if hf_result.get("success"):
                # Calculate confidence based on response quality
                confidence = self._calculate_response_confidence(hf_result.get("response", ""), context)

                return {
                    "success": True,
                    "response": hf_result.get("response", ""),
                    "confidence": confidence,
                    "model_used": hf_result.get("model", "huggingface-local"),
                    "cost": hf_result.get("cost", "FREE")
                }
            else:
                return {
                    "success": False,
                    "response": self._get_fallback_response(user_query, language),
                    "confidence": 0.3,
                    "model_used": "fallback_text",
                    "error": hf_result.get("error", "HuggingFace generation failed")
                }

        except Exception as e:
            logger.error(f"Error generating HuggingFace response: {e}")
            return {
                "success": False,
                "response": self._get_fallback_response(user_query, language),
                "confidence": 0.3,
                "model_used": "fallback_text",
                "error": str(e)
            }
    
    def _build_system_prompt(self, industry_context: str = None, language: str = "en") -> str:
        """Build system prompt for ReckonSales chatbot"""
        
        base_prompt = """You are a helpful AI assistant for ReckonSales ERP platform. You help users with:
- Billing, invoicing, and GST management
- Inventory and stock management
- Order processing and customer management
- Technical support and troubleshooting
- Platform setup and configuration

Guidelines:
1. Provide accurate, helpful responses based on the provided context
2. If you don't have enough information, say so clearly
3. Always prioritize user safety and data security
4. Suggest escalation to human support for complex technical issues
5. Be concise but thorough in your explanations
6. Use step-by-step instructions when explaining procedures"""

        # Add industry-specific context
        if industry_context:
            industry_prompts = {
                "pharmacy": "\nYou specialize in pharmacy management including prescription handling, medicine inventory, patient records, and regulatory compliance.",
                "auto_parts": "\nYou specialize in auto parts inventory, vehicle compatibility, spare parts management, and garage operations.",
                "fmcg": "\nYou specialize in FMCG retail including grocery inventory, supermarket operations, and consumer goods management.",
                "restaurant": "\nYou specialize in restaurant management including menu planning, kitchen operations, table management, and food service."
            }
            base_prompt += industry_prompts.get(industry_context, "")
        
        # Add language instruction
        if language == "hi":
            base_prompt += "\n\nPlease respond in Hindi (हिंदी) when appropriate, but keep technical terms in English for clarity."
        
        return base_prompt
    
    def _build_user_prompt(self, user_query: str, context: str, language: str = "en") -> str:
        """Build user prompt with context and query"""
        
        if language == "hi":
            prompt_template = """संदर्भ जानकारी (Context Information):
{context}

उपयोगकर्ता का प्रश्न (User Question): {query}

कृपया उपरोक्त संदर्भ का उपयोग करके उपयोगकर्ता के प्रश्न का उत्तर दें। यदि संदर्भ में जानकारी नहीं है, तो कृपया स्पष्ट रूप से बताएं।"""
        else:
            prompt_template = """Context Information:
{context}

User Question: {query}

Please answer the user's question based on the context provided above. If the information is not available in the context, please state that clearly."""
        
        return prompt_template.format(context=context, query=user_query)
    
    def _get_conversation_history(self, db: Session, session_id: int) -> List[Dict]:
        """Get recent conversation history for context"""
        try:
            from models.chat import ChatMessage
            
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.desc()).limit(8).all()
            
            history = []
            for msg in reversed(messages):  # Reverse to get chronological order
                role = "user" if msg.message_type == "user" else "assistant"
                history.append({
                    "role": role,
                    "content": msg.message_text[:500]  # Truncate long messages
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def _calculate_response_confidence(self, response: str, context: str) -> float:
        """Calculate confidence score for the generated response"""
        base_confidence = 0.7
        
        # Boost confidence if response references specific context
        if context and any(word in response.lower() for word in ["according to", "based on", "as mentioned"]):
            base_confidence += 0.1
        
        # Reduce confidence if response indicates uncertainty
        uncertainty_phrases = ["i don't know", "not sure", "cannot find", "unclear"]
        if any(phrase in response.lower() for phrase in uncertainty_phrases):
            base_confidence -= 0.2
        
        # Boost confidence for structured responses (steps, lists)
        if any(indicator in response for indicator in ["1.", "•", "Step", "First", "Next"]):
            base_confidence += 0.05
        
        return max(0.3, min(0.95, base_confidence))
    
    def _format_sources(self, search_results: List[Dict]) -> List[Dict]:
        """Format search results as source references"""
        sources = []
        
        for i, result in enumerate(search_results):
            source = {
                "id": i + 1,
                "chunk_id": result.get("chunk_id"),
                "document_id": result.get("document_id"),
                "section_title": result.get("section_title"),
                "confidence": result.get("confidence_score", 0.5),
                "similarity": result.get("similarity_score", 0.5),
                "preview": result.get("chunk_text", "")[:200] + "..." if len(result.get("chunk_text", "")) > 200 else result.get("chunk_text", "")
            }
            sources.append(source)
        
        return sources
    
    def _get_fallback_response(self, query: str, language: str = "en") -> str:
        """Generate fallback response when AI is not available"""
        
        fallback_responses = {
            "en": {
                "general": "I apologize, but I'm currently unable to process your request. Please contact our support team for assistance with your ReckonSales query.",
                "billing": "For billing and invoice queries, please check your ReckonSales dashboard under the Billing section or contact support.",
                "inventory": "For inventory-related questions, please access the Inventory module in your ReckonSales dashboard.",
                "technical": "For technical issues, please try restarting the application or contact our technical support team."
            },
            "hi": {
                "general": "खुशी है, मैं वर्तमान में आपके अनुरोध को प्रोसेस करने में असमर्थ हूं। कृपया अपने ReckonSales प्रश्न के लिए हमारी सहायता टीम से संपर्क करें।",
                "billing": "बिलिंग और इनवॉइस प्रश्नों के लिए, कृपया बिलिंग सेक्शन के तहत अपने ReckonSales डैशबोर्ड की जांच करें या सहायता से संपर्क करें।",
                "inventory": "इन्वेंट्री संबंधी प्रश्नों के लिए, कृपया अपने ReckonSales डैशबोर्ड में इन्वेंट्री मॉड्यूल का उपयोग करें।",
                "technical": "तकनीकी समस्याओं के लिए, कृपया एप्लिकेशन को पुनः आरंभ करने का प्रयास करें या हमारी तकनीकी सहायता टीम से संपर्क करें।"
            }
        }
        
        # Simple intent detection for fallback
        query_lower = query.lower()
        if any(word in query_lower for word in ["bill", "invoice", "payment", "gst"]):
            intent = "billing"
        elif any(word in query_lower for word in ["inventory", "stock", "item"]):
            intent = "inventory"
        elif any(word in query_lower for word in ["error", "bug", "problem", "issue"]):
            intent = "technical"
        else:
            intent = "general"
        
        return fallback_responses.get(language, fallback_responses["en"]).get(intent, fallback_responses[language]["general"])
    
    def _log_rag_query(
        self,
        db: Session,
        user_id: int,
        session_id: int,
        query: str,
        chunks_retrieved: int,
        chunk_ids: List[int],
        processing_time: int,
        response_generated: bool
    ):
        """Log RAG query for analytics"""
        try:
            # Update the existing query log
            self.vector_search.log_search_query(
                db=db,
                user_id=user_id,
                session_id=session_id,
                query_text=query,
                chunks_retrieved=chunks_retrieved,
                chunk_ids=chunk_ids,
                search_time_ms=processing_time
            )
            
            # Update the last query record with response info
            last_query = db.query(KnowledgeBaseQuery).filter(
                KnowledgeBaseQuery.session_id == session_id
            ).order_by(KnowledgeBaseQuery.created_at.desc()).first()
            
            if last_query:
                last_query.response_generated = response_generated
                last_query.response_time_ms = processing_time
                db.commit()
                
        except Exception as e:
            logger.error(f"Error logging RAG query: {e}")
    
    def create_embeddings_for_existing_chunks(self, db: Session) -> Dict:
        """Create embeddings for existing chunks that don't have them"""
        try:
            # Find chunks without embeddings
            chunks_without_embeddings = db.query(DocumentChunk).filter(
                DocumentChunk.embedding_created == False
            ).all()
            
            if not chunks_without_embeddings:
                return {
                    "success": True,
                    "message": "All chunks already have embeddings",
                    "processed": 0
                }
            
            # Process in batches
            batch_size = 50
            total_processed = 0
            
            for i in range(0, len(chunks_without_embeddings), batch_size):
                batch = chunks_without_embeddings[i:i + batch_size]
                processed = self.vector_search.store_chunk_embeddings(db, batch)
                total_processed += processed
                
                logger.info(f"Processed batch {i//batch_size + 1}: {processed} embeddings created")
            
            return {
                "success": True,
                "message": f"Created embeddings for {total_processed} chunks",
                "processed": total_processed,
                "total_chunks": len(chunks_without_embeddings)
            }
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return {
                "success": False,
                "message": f"Error creating embeddings: {str(e)}",
                "processed": 0
            }