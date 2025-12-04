import os
import io
import google.generativeai as genai
from PIL import Image
from typing import Dict, List
from loguru import logger


class ImageAnalysisService:
    """
    Service for extracting text from uploaded images
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("Gemini API key is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        try:
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            logger.info("Image Analysis Service initialized with Gemini 2.5 Flash")
        except Exception as e:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Image Analysis Service initialized with Gemini Pro")
            except Exception as e2:
                logger.error(f"Failed to initialize any Gemini model: {e}, {e2}")
                raise Exception(f"Could not initialize Gemini vision model: {e}")
                
    
    async def analyze_image_and_generate_questions(self, image_data: bytes, filename: str = "document") -> Dict:
        """
        Extract text from uploaded image
        
        Args:
            image_data: Raw image bytes
            filename: Original filename for context
            
        Returns:
            Dict with extracted text
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Optimize image if too large
            if image.width > 1024 or image.height > 1024:
                image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {image.width}x{image.height}")
            
            # Extract text from image
            extracted_text = await self._extract_text_from_image(image)
            
            logger.info(f"Successfully extracted text from: {filename}")
            
            return {
                "success": True,
                "questions": [extracted_text],  # Return text as question for compatibility
                "key_information": extracted_text,
                "document_type": "Document",
                "analysis_method": "gemini_vision",
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "questions": ["Text extraction failed"],
                "key_information": "Text extraction failed",
                "document_type": "unknown",
                "filename": filename
            }
    
    async def _extract_text_from_image(self, image: Image.Image) -> str:
        """Extract exact text from image"""
        
        prompt = """Read all the text in this image and return it exactly as written.
        
        Rules:
        - Extract every single word, number, symbol you can see
        - Copy text word-for-word exactly as it appears
        - Keep original formatting and line breaks
        - Do not interpret, summarize or add anything
        - Just extract the raw text content
        
        Return only the text content:"""
        
        try:
            response = self.model.generate_content([prompt, image])
            
            if not response or not hasattr(response, 'text') or not response.text:
                return "No text found in image"
            
            result = response.text.strip()
            return result if result else "No readable text"
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return "Text extraction failed"
    
    def test_connection(self) -> bool:
        """Test if the Gemini Vision API is working"""
        try:
            test_image = Image.new('RGB', (100, 100), color='white')
            response = self.model.generate_content([
                "What text do you see?",
                test_image
            ])
            return response and response.text is not None
            
        except Exception as e:
            logger.error(f"Vision API connection test failed: {e}")
            return False