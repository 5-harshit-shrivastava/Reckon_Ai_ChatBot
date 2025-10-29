#!/usr/bin/env python3
"""
Test Gemini API to see available models
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    print("Available Gemini models:")
    try:
        models = genai.list_models()
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
        
    # Test common models
    test_models = [
        "models/gemini-pro",
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-flash-latest",
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]
    
    print("\nTesting models:")
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print(f"  ✅ {model_name} - Working")
            break  # Use the first working model
        except Exception as e:
            print(f"  ❌ {model_name} - {str(e)[:100]}")
else:
    print("No GEMINI_API_KEY found")