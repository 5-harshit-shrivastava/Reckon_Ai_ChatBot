#!/usr/bin/env python3
"""
Test script to verify the Reckon AI ChatBot system is working end-to-end
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_backend_health():
    """Test if backend is running"""
    try:
        # Try local first
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running locally")
            return "http://localhost:8000"
    except:
        pass
    
    try:
        # Try production URL
        response = requests.get("https://bckreckon.vercel.app/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is running on production")
            return "https://bckreckon.vercel.app"
    except:
        pass
    
    print("❌ Backend is not accessible")
    return None

def test_admin_endpoints(base_url):
    """Test admin endpoints"""
    print("\n🔍 Testing Admin Endpoints...")
    
    # Test system status
    try:
        response = requests.get(f"{base_url}/api/admin/system/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System Status: {data.get('database_status', 'unknown')}")
            print(f"   Documents: {data.get('total_documents', 0)}")
            print(f"   Chunks: {data.get('total_chunks', 0)}")
        else:
            print(f"❌ System Status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ System Status error: {e}")
    
    # Test knowledge base
    try:
        response = requests.get(f"{base_url}/api/admin/knowledge-base", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Knowledge Base: {len(data)} entries")
        else:
            print(f"❌ Knowledge Base failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Knowledge Base error: {e}")

def test_chat_endpoints(base_url):
    """Test chat endpoints"""
    print("\n💬 Testing Chat Endpoints...")
    
    # Test creating a user first
    user_data = {
        "name": "Test User",
        "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "industry_type": "general"
    }
    
    try:
        response = requests.post(f"{base_url}/api/users/", json=user_data, timeout=10)
        if response.status_code == 200:
            user_id = response.json()["data"]["user"]["id"]
            print(f"✅ Created test user: {user_id}")
            
            # Test creating session
            session_data = {
                "user_id": user_id,
                "channel": "web",
                "language": "en"
            }
            
            response = requests.post(f"{base_url}/api/chat/sessions/", json=session_data, timeout=10)
            if response.status_code == 200:
                session_id = response.json()["data"]["session"]["id"]
                print(f"✅ Created chat session: {session_id}")
                
                # Test sending message
                message_data = {
                    "session_id": session_id,
                    "message": "Hello, can you help me with billing?",
                    "channel": "web",
                    "language": "en"
                }
                
                response = requests.post(f"{base_url}/api/chat/messages/send", json=message_data, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Chat message sent successfully")
                    print(f"   Response: {data.get('assistant_response', {}).get('message_text', 'No response')[:100]}...")
                else:
                    print(f"❌ Chat message failed: {response.status_code}")
                    print(f"   Error: {response.text}")
            else:
                print(f"❌ Session creation failed: {response.status_code}")
        else:
            print(f"❌ User creation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat test error: {e}")

def test_knowledge_base_creation(base_url):
    """Test creating knowledge base entry"""
    print("\n📚 Testing Knowledge Base Creation...")
    
    test_document = {
        "title": "Test Document for End-to-End Testing",
        "content": "This is a test document about billing and invoicing. It contains information about GST calculations, invoice generation, and payment processing. This document should be searchable and retrievable through the chat system.",
        "document_type": "manual",
        "industry_type": "general",
        "language": "en"
    }
    
    try:
        response = requests.post(f"{base_url}/api/admin/knowledge-base", json=test_document, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Knowledge base entry created")
            print(f"   Document ID: {data.get('id')}")
            print(f"   Chunks: {data.get('chunks_created', 0)}")
            print(f"   Embeddings: {data.get('embeddings_created', 0)}")
            return data.get('id')
        else:
            print(f"❌ Knowledge base creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Knowledge base creation error: {e}")
    
    return None

def main():
    """Main test function"""
    print("🚀 Reckon AI ChatBot - End-to-End Test")
    print("=" * 50)
    
    # Test backend health
    base_url = test_backend_health()
    if not base_url:
        print("\n❌ Cannot proceed without backend access")
        return
    
    # Test admin endpoints
    test_admin_endpoints(base_url)
    
    # Test knowledge base creation
    doc_id = test_knowledge_base_creation(base_url)
    
    # Test chat endpoints
    test_chat_endpoints(base_url)
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    
    if doc_id:
        print(f"\n📝 Test document created with ID: {doc_id}")
        print("   You can now test the chat system with queries about billing/invoicing")

if __name__ == "__main__":
    main()
