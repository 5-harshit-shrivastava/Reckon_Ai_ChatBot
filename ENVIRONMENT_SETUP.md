# Reckon AI ChatBot - Environment Setup Guide

## Required Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./reckon_chatbot.db

# API Keys (Required for full functionality)
PINECONE_API_KEY=your_pinecone_api_key_here
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: For production database
# DATABASE_URL=postgresql://user:password@localhost/dbname

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001", "https://*.vercel.app"]
```

## How to Get API Keys

### 1. Pinecone API Key
1. Go to [Pinecone Console](https://app.pinecone.io/)
2. Sign up/Login
3. Go to API Keys section
4. Copy your API key

### 2. HuggingFace API Token
1. Go to [HuggingFace](https://huggingface.co/)
2. Sign up/Login
3. Go to Settings > Access Tokens
4. Create a new token
5. Copy the token

### 3. Google API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Gemini API
3. Create credentials (API Key)
4. Copy the API key

## Current Issues Found

1. **Missing API Keys**: The system cannot create embeddings or generate responses without these keys
2. **Backend URL**: Frontend is pointing to `https://bckreckon.vercel.app` - verify this is correct
3. **Environment Setup**: No `.env` file exists in the backend directory

## Quick Fix for Testing

If you want to test the system without API keys, the system will:
- Save documents to database ✅
- Show documents in admin panel ✅
- Return fallback responses in chat ❌ (no AI responses)

## Next Steps

1. Create the `.env` file with your API keys
2. Restart the backend server
3. Test the admin panel to save documents
4. Test the user chat to verify responses
