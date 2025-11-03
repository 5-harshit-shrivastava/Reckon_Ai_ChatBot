import os
import io
import google.generativeai as genai
from PIL import Image
from typing import Dict, List
from loguru import logger


class ImageAnalysisService:
    """
    Service for analyzing uploaded images and generating relevant questions
    using Google Gemini Vision capabilities
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("Gemini API key is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        # Use the working model from gemini_service but check if it supports vision
        try:
            # Try the model that works in the main service
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            logger.info("Image Analysis Service initialized with Gemini 2.5 Flash")
        except Exception as e:
            try:
                # Fallback to another known model
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("Image Analysis Service initialized with Gemini Pro")
            except Exception as e2:
                logger.error(f"Failed to initialize any Gemini model: {e}, {e2}")
                raise Exception(f"Could not initialize Gemini vision model: {e}")
                
    
    async def analyze_image_and_generate_questions(self, image_data: bytes, filename: str = "document") -> Dict:
        """
        Analyze uploaded image and generate relevant business questions
        
        Args:
            image_data: Raw image bytes
            filename: Original filename for context
            
        Returns:
            Dict with success status, questions, and extracted insights
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Optimize image if too large
            if image.width > 1024 or image.height > 1024:
                image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {image.width}x{image.height} to fit within 1024x1024")
            
            # Get document type analysis first
            doc_type = await self._analyze_document_type(image)
            
            # Generate questions using Gemini Vision (context-aware)
            questions = await self._generate_questions_from_image(image, doc_type)
            
            # Extract key information
            key_info = await self._extract_key_information(image)
            
            logger.info(f"Successfully analyzed image: {filename}, found {len(questions)} questions")
            
            return {
                "success": True,
                "questions": questions,
                "key_information": key_info,
                "document_type": doc_type,
                "analysis_method": "gemini_vision",
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image {filename}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "questions": [],
                "key_information": "",
                "document_type": "unknown",
                "filename": filename
            }
    
    async def _generate_questions_from_image(self, image: Image.Image, doc_type: str = "") -> List[str]:
        """Generate relevant questions from business document image"""
        
        # For error screens, extract exact error text
        if "error" in doc_type.lower():
            prompt = """
            Extract ONLY the main error message from this screen.
            
            Ignore:
            - Button text like "OK", "Cancel"
            - Window titles
            - Extra UI elements
            
            Return ONLY the core error message text that describes the problem.
            """
        else:
            prompt = """
            Look at this document and generate 2-3 relevant questions based on what you see.
            Keep questions under 12 words. Be specific to what you see.
            """
        
        try:
            response = self.model.generate_content([prompt, image])
            
            # Better error handling for empty responses
            if not response or not hasattr(response, 'text') or not response.text:
                logger.warning("Empty response from Gemini for question generation")
                return [
                    "What action should be taken for this document?",
                    "Does this require immediate attention?",
                    "Who should handle this issue?"
                ]
            
            # For error screens, return exact error text
            if "error" in doc_type.lower():
                # Extract exact error text and clean it
                error_text = response.text.strip()
                # Remove common UI elements
                lines = error_text.split('\n')
                cleaned_lines = []
                
                for line in lines:
                    line = line.strip()
                    # Skip common UI elements
                    if line.lower() in ['ok', 'cancel', 'error', 'x', 'close']:
                        continue
                    if line and len(line) > 3:  # Keep meaningful text
                        cleaned_lines.append(line)
                
                cleaned_error = '\n'.join(cleaned_lines)
                return [cleaned_error] if cleaned_error else ["Error message not readable"]
            
            # For other documents, parse as questions
            lines = response.text.strip().split('\n')
            questions = []
            
            for line in lines:
                line = line.strip()
                # Clean up common prefixes and ensure it's a question
                line = line.lstrip('•-*123456789. ')
                if line and '?' in line and len(line) > 10:
                    questions.append(line)
            
            # Return fallback questions based on document type
            if not questions:
                return [
                    "What needs to be done?",
                    "Who should handle this?"
                ]
            
            # Limit to 3 questions maximum
            return questions[:3]
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            # Return simple fallback
            if "error" in doc_type.lower():
                return ["Error text could not be extracted"]
            else:
                return ["Document analysis failed"]
    
    async def _extract_key_information(self, image: Image.Image) -> str:
        """Extract key textual information from the image"""
        
        prompt = """
        Extract all visible text from this image exactly as it appears.
        
        Read every line of text you can see.
        Copy it word-for-word exactly.
        Do not interpret or summarize.
        """
        
        try:
            response = self.model.generate_content([prompt, image])
            
            # Better error handling
            if not response or not hasattr(response, 'text') or not response.text:
                return "Business document - details not extractable"
            
            result = response.text.strip()
            # Return exact text, don't limit length for error extraction
            return result if result else "Text not readable"
            
        except Exception as e:
            logger.error(f"Error extracting key information: {str(e)}")
            return "Text extraction failed"
    
    async def _analyze_document_type(self, image: Image.Image) -> str:
        """Identify the type of business document"""
        
        prompt = """
        Document type in 1-2 words:
        Invoice | Purchase Order | Error Screen | Installation | Stock Report | Data Entry
        """
        
        try:
            response = self.model.generate_content([prompt, image])
            
            if not response or not hasattr(response, 'text') or not response.text:
                return "Document"
            
            doc_type = response.text.strip()
            # Clean up the response
            doc_type = doc_type.replace('"', '').replace("'", "")
            if len(doc_type) > 30:  # If too long, truncate
                doc_type = doc_type[:30]
            return doc_type if doc_type else "Business Document"
            
        except Exception as e:
            logger.error(f"Error analyzing document type: {str(e)}")
            return "Document"
    
    def test_connection(self) -> bool:
        """Test if the Gemini Vision API is working"""
        try:
            # Create a simple test image
            test_image = Image.new('RGB', (100, 100), color='white')
            
            response = self.model.generate_content([
                "What do you see in this image?",
                test_image
            ])
            
            return response and response.text is not None
            
        except Exception as e:
            logger.error(f"Vision API connection test failed: {e}")
            return False