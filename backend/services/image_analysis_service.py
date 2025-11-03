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
            
            # Generate questions using Gemini Vision
            questions = await self._generate_questions_from_image(image)
            
            # Extract key information
            key_info = await self._extract_key_information(image)
            
            # Get document type analysis
            doc_type = await self._analyze_document_type(image)
            
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
    
    async def _generate_questions_from_image(self, image: Image.Image) -> List[str]:
        """Generate relevant questions from business document image"""
        
        prompt = """
        You are a business analyst. Examine this document/screen carefully and generate 4-6 specific, actionable questions.

        STEP 1: Identify what type of document this is:
        - Invoice/Bill (amounts, due dates, vendor info)
        - Purchase Order (items, quantities, suppliers)
        - Software Screen (error messages, data entry, installation)
        - Financial Report (calculations, totals, analysis)
        - Inventory/Stock (product codes, quantities, warnings)

        STEP 2: Create specific questions based on what you see:
        - Reference actual numbers, dates, names visible in the image
        - Ask about decisions that need to be made
        - Focus on potential problems or verification needs
        - Use business terminology for the document type

        EXAMPLES:
        For Purchase Orders: "Should we approve 40 units of ESOGARD at ₹141.43 each?"
        For Error Screens: "How do we resolve the Database Engine recovery error?"
        For Invoices: "Is the tax calculation of ₹200 correct on this ₹2000 total?"
        For Stock Screens: "Why is item 200513 showing a stock warning?"

        Return 4-6 questions, one per line, without numbering.
        Be specific to what you actually see in this image.
        """
        
        try:
            response = self.model.generate_content([prompt, image])
            
            if response and response.text:
                # Parse questions from response
                lines = response.text.strip().split('\n')
                questions = []
                
                for line in lines:
                    line = line.strip()
                    # Clean up common prefixes and ensure it's a question
                    line = line.lstrip('•-*123456789. ')
                    if line and '?' in line and len(line) > 15:  # Increased minimum length for specificity
                        questions.append(line)
                
                # Limit to 6 questions maximum
                return questions[:6]
            
            return []
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return []
    
    async def _extract_key_information(self, image: Image.Image) -> str:
        """Extract key textual information from the image"""
        
        prompt = """
        Extract the most important information from this business document/screen.

        Focus on:
        - Important numbers (amounts, quantities, dates)
        - Company/vendor names
        - Product/item details
        - Error messages or warnings
        - Status information

        Provide a brief summary of what this document shows and the key details visible.
        Include specific numbers, names, and important facts.
        Keep it concise but informative (2-3 sentences).
        """
        
        try:
            response = self.model.generate_content([prompt, image])
            return response.text.strip() if response and response.text else ""
        except Exception as e:
            logger.error(f"Error extracting key information: {str(e)}")
            return ""
    
    async def _analyze_document_type(self, image: Image.Image) -> str:
        """Identify the type of business document"""
        
        prompt = """
        Look at this business document/screen and identify what it is.

        Common types:
        - Invoice (billing document)
        - Purchase Order (ordering items)
        - Error Screen (system errors)
        - Installation Screen (software setup)
        - Stock Report (inventory levels)
        - Financial Report (accounting data)
        - Data Entry Form (input screens)

        Return only the specific document type you see (1-3 words).
        Be precise about what you observe.
        """
        
        try:
            response = self.model.generate_content([prompt, image])
            doc_type = response.text.strip() if response and response.text else "document"
            
            # Clean up the response
            doc_type = doc_type.replace('"', '').replace("'", "")
            if len(doc_type) > 50:  # If too long, truncate
                doc_type = doc_type[:50]
            return doc_type if doc_type else "business document"
            
        except Exception as e:
            logger.error(f"Error analyzing document type: {str(e)}")
            return "document"
    
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