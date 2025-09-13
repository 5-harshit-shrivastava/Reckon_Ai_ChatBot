"""
Alternative multilingual RAG implementations for ReckonSales
Avoiding OpenAI dependency with better Hindi support
"""

import os
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

class MultilingualRAGService(ABC):
    """Abstract base for multilingual RAG services"""
    
    @abstractmethod
    def generate_response(self, query: str, context: str, language: str) -> Dict:
        pass
    
    @abstractmethod 
    def detect_language(self, text: str) -> str:
        pass

# 1. GOOGLE GEMINI APPROACH (Best for Hindi)
class GeminiRAGService(MultilingualRAGService):
    """
    Uses Google Gemini - Excellent Hindi support, cheaper than GPT-4
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        # pip install google-generativeai
        
    def generate_response(self, query: str, context: str, language: str) -> Dict:
        """Generate response using Gemini Pro"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = self._build_prompt(query, context, language)
            response = model.generate_content(prompt)
            
            return {
                "success": True,
                "response": response.text,
                "model": "gemini-pro",
                "cost": "~50% cheaper than GPT-4"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _build_prompt(self, query: str, context: str, language: str) -> str:
        if language == "hi":
            return f"""आप ReckonSales ERP के लिए एक सहायक हैं। संदर्भ का उपयोग करके उत्तर दें:

संदर्भ: {context}

प्रश्न: {query}

कृपया हिंदी में स्पष्ट और सहायक उत्तर दें।"""
        else:
            return f"""You are a ReckonSales ERP assistant. Answer using the context:

Context: {context}

Question: {query}

Provide a clear and helpful response."""

# 2. HUGGING FACE TRANSFORMERS (Free, Local)
class HuggingFaceRAGService(MultilingualRAGService):
    """
    Uses local multilingual models - Completely free, works offline
    """
    
    def __init__(self):
        # pip install transformers torch
        self.model_name = "microsoft/DialoGPT-medium"  # Or "ai4bharat/indic-bert"
        
    def generate_response(self, query: str, context: str, language: str) -> Dict:
        """Generate response using local transformers"""
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            
            # For Hindi: Use AI4Bharat models
            if language == "hi":
                model_name = "ai4bharat/indic-bert"
            else:
                model_name = "microsoft/DialoGPT-medium"
            
            generator = pipeline('text-generation', model=model_name)
            
            prompt = f"Context: {context}\nQuestion: {query}\nAnswer:"
            response = generator(prompt, max_length=200, num_return_sequences=1)
            
            return {
                "success": True,
                "response": response[0]['generated_text'],
                "model": model_name,
                "cost": "FREE - runs locally"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# 3. OLLAMA LOCAL MODELS (Best free option)
class OllamaRAGService(MultilingualRAGService):
    """
    Uses Ollama for local LLaMA/Mistral models - Free, private, fast
    """
    
    def __init__(self):
        # Install: curl -fsSL https://ollama.ai/install.sh | sh
        # Then: ollama pull llama3:8b
        self.base_url = "http://localhost:11434"
        
    def generate_response(self, query: str, context: str, language: str) -> Dict:
        """Generate response using local Ollama"""
        try:
            import requests
            
            # Choose model based on language
            model = "llama3:8b"  # Or "mistral:7b", "codellama:7b"
            
            prompt = self._build_multilingual_prompt(query, context, language)
            
            response = requests.post(f"{self.base_url}/api/generate", json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            })
            
            result = response.json()
            
            return {
                "success": True,
                "response": result.get("response", ""),
                "model": model,
                "cost": "FREE - runs locally",
                "privacy": "100% private - no data leaves your server"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _build_multilingual_prompt(self, query: str, context: str, language: str) -> str:
        if language == "hi":
            return f"""आप एक ReckonSales ERP सिस्टम के विशेषज्ञ हैं। दिए गए संदर्भ का उपयोग करके प्रश्न का उत्तर दें।

संदर्भ जानकारी:
{context}

उपयोगकर्ता का प्रश्न: {query}

कृपया हिंदी में विस्तृत और सहायक उत्तर दें:"""
        else:
            return f"""You are a ReckonSales ERP system expert. Answer the question using the provided context.

Context Information:
{context}

User Question: {query}

Please provide a detailed and helpful answer:"""

# 4. TRANSLATION LAYER APPROACH
class TranslationRAGService(MultilingualRAGService):
    """
    Uses translation + English-only LLM - Good accuracy, moderate cost
    """
    
    def __init__(self):
        # pip install googletrans==4.0.0-rc1
        # Or use: pip install transformers sentencepiece
        pass
        
    def generate_response(self, query: str, context: str, language: str) -> Dict:
        """Translate -> Generate -> Translate back"""
        try:
            # Detect and translate to English if needed
            if language == "hi":
                query_en = self._translate_to_english(query)
                context_en = self._translate_to_english(context)
            else:
                query_en, context_en = query, context
            
            # Generate response in English (using any English LLM)
            english_response = self._generate_english_response(query_en, context_en)
            
            # Translate back to Hindi if needed
            if language == "hi":
                final_response = self._translate_to_hindi(english_response)
            else:
                final_response = english_response
            
            return {
                "success": True,
                "response": final_response,
                "approach": "translation_layer",
                "cost": "Translation API + English LLM costs"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _translate_to_english(self, text: str) -> str:
        """Translate Hindi to English"""
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, src='hi', dest='en')
            return result.text
        except:
            # Fallback to local translation
            return self._local_translate(text, "hi", "en")
    
    def _translate_to_hindi(self, text: str) -> str:
        """Translate English to Hindi"""
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, src='en', dest='hi')
            return result.text
        except:
            return self._local_translate(text, "en", "hi")
    
    def _local_translate(self, text: str, src: str, dest: str) -> str:
        """Local translation using MarianMT"""
        try:
            from transformers import MarianMTModel, MarianTokenizer
            
            if src == "hi" and dest == "en":
                model_name = "Helsinki-NLP/opus-mt-hi-en"
            else:
                model_name = "Helsinki-NLP/opus-mt-en-hi"
                
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            
            translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
            return tokenizer.decode(translated[0], skip_special_tokens=True)
        except:
            return text  # Fallback: return original

# RECOMMENDATION FOR RECKONSALES
def get_recommended_setup():
    """
    Recommended multilingual setup for ReckonSales
    """
    return {
        "primary": "OllamaRAGService",  # Free, private, fast
        "backup": "GeminiRAGService",   # Cheap, excellent Hindi
        "fallback": "TranslationRAGService",  # If others fail
        
        "setup_commands": [
            "# Install Ollama",
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "ollama pull llama3:8b",
            "",
            "# Or use Gemini",
            "pip install google-generativeai",
            "# Get free API key from https://makersuite.google.com/app/apikey"
        ],
        
        "cost_comparison": {
            "Ollama (Local)": "FREE",
            "Google Gemini": "~$0.0005/1K tokens (50% cheaper than OpenAI)",
            "OpenAI GPT-4": "~$0.03/1K tokens",
            "HuggingFace": "FREE (but needs good GPU)"
        }
    }

if __name__ == "__main__":
    recommendations = get_recommended_setup()
    print("🌐 Multilingual RAG Recommendations for ReckonSales:")
    print(f"Primary: {recommendations['primary']}")
    print(f"Backup: {recommendations['backup']}")
    print("\nCost Comparison:")
    for service, cost in recommendations['cost_comparison'].items():
        print(f"  {service}: {cost}")