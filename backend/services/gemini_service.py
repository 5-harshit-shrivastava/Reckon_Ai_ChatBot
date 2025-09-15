import os
import time
from typing import Dict, Optional
import google.generativeai as genai
from loguru import logger


class GeminiService:
    """Google Gemini Pro service for text generation"""

    def __init__(self):
        self.client = None
        self.model_name = "gemini-1.5-flash"  # Updated model name
        self.initialize_service()

    def initialize_service(self):
        """Initialize Google Gemini Pro service"""
        try:
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

            if not api_key:
                logger.error("Google Gemini API key not found")
                return

            # Configure Gemini
            genai.configure(api_key=api_key)

            # Initialize model with updated name
            self.client = genai.GenerativeModel(self.model_name)

            logger.info("Google Gemini Pro service initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Gemini service: {e}")

    def generate_response(
        self,
        user_query: str,
        context: str,
        industry_context: Optional[str] = None,
        language: str = "en",
        session_id: Optional[int] = None
    ) -> Dict:
        """
        Generate response using Google Gemini Pro

        Args:
            user_query: User's question
            context: Retrieved context from knowledge base
            industry_context: Industry type for specialized responses
            language: Response language (en/hi)
            session_id: Chat session ID

        Returns:
            Dict with response data
        """
        try:
            if not self.client:
                return {
                    "success": False,
                    "response": "Gemini service not available",
                    "confidence": 0.0,
                    "model_used": "none"
                }

            # Build system prompt
            system_prompt = self._build_system_prompt(industry_context, language)

            # Build user prompt with context
            user_prompt = self._build_user_prompt(user_query, context, language)

            # Combine prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            # Generate response
            start_time = time.time()

            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800,
                    top_p=0.9,
                    top_k=40
                )
            )

            generation_time = int((time.time() - start_time) * 1000)

            if response and response.text:
                ai_response = response.text.strip()

                # Calculate confidence
                confidence = self._calculate_response_confidence(ai_response, context)

                logger.info(f"Gemini response generated in {generation_time}ms")

                return {
                    "success": True,
                    "response": ai_response,
                    "confidence": confidence,
                    "model_used": self.model_name,
                    "generation_time_ms": generation_time
                }
            else:
                return {
                    "success": False,
                    "response": "No response generated",
                    "confidence": 0.0,
                    "model_used": self.model_name
                }

        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return {
                "success": False,
                "response": f"Error generating response: {str(e)}",
                "confidence": 0.0,
                "model_used": self.model_name,
                "error": str(e)
            }

    def _build_system_prompt(self, industry_context: Optional[str] = None, language: str = "en") -> str:
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
6. Use step-by-step instructions when explaining procedures
7. Focus on practical, actionable advice"""

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

    def _calculate_response_confidence(self, response: str, context: str) -> float:
        """Calculate confidence score for the generated response"""
        base_confidence = 0.8  # Gemini is generally reliable

        # Boost confidence if response references specific context
        if context and any(word in response.lower() for word in ["according to", "based on", "as mentioned"]):
            base_confidence += 0.1

        # Reduce confidence if response indicates uncertainty
        uncertainty_phrases = ["i don't know", "not sure", "cannot find", "unclear", "नहीं पता", "अस्पष्ट"]
        if any(phrase in response.lower() for phrase in uncertainty_phrases):
            base_confidence -= 0.2

        # Boost confidence for structured responses (steps, lists)
        if any(indicator in response for indicator in ["1.", "•", "Step", "First", "Next", "पहले", "फिर"]):
            base_confidence += 0.05

        return max(0.3, min(0.95, base_confidence))

    def test_connection(self) -> bool:
        """Test Gemini API connection"""
        try:
            if not self.client:
                return False

            response = self.client.generate_content("Hello")
            return response and response.text is not None

        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False