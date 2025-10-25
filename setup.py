#!/usr/bin/env python3
"""
Setup script for Reckon AI ChatBot
This script helps configure the environment and test the system
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def create_env_file():
    """Create .env file with template values"""
    env_path = Path("backend/.env")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return
    
    env_content = """# Database Configuration
DATABASE_URL=sqlite:///./reckon_chatbot.db

# API Keys (Required for full functionality)
# Get these from:
# - Pinecone: https://app.pinecone.io/
# - HuggingFace: https://huggingface.co/settings/tokens
# - Google: https://console.cloud.google.com/
PINECONE_API_KEY=your_pinecone_api_key_here
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
GOOGLE_API_KEY=your_google_api_key_here

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001", "https://*.vercel.app"]
"""
    
    try:
        env_path.write_text(env_content)
        print("✅ Created .env file template")
        print("⚠️  Please edit backend/.env and add your actual API keys")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    # Check Python packages
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "pinecone-client", 
        "requests", "python-dotenv", "loguru"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_backend_connection():
    """Test if backend is accessible"""
    print("\n🌐 Testing backend connection...")
    
    urls_to_test = [
        "http://localhost:8000/health",
        "https://bckreckon.vercel.app/health"
    ]
    
    for url in urls_to_test:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Backend accessible at: {url}")
                return url
        except:
            print(f"❌ Backend not accessible at: {url}")
    
    return None

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting backend server...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Change to backend directory and start server
        os.chdir(backend_dir)
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Backend server stopped")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 Reckon AI ChatBot Setup")
    print("=" * 40)
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    # Test backend connection
    backend_url = test_backend_connection()
    
    if not backend_url:
        print("\n🚀 Backend not running. Starting it now...")
        print("   Press Ctrl+C to stop the server")
        start_backend()
    else:
        print(f"\n✅ Backend is already running at: {backend_url}")
        print("   You can now test the system with: python test_system.py")

if __name__ == "__main__":
    main()
