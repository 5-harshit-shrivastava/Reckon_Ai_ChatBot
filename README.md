<!-- kardia change -->

# Reckon AI ChatBot

A sophisticated RAG (Retrieval-Augmented Generation) chatbot system with **Image Upload & Analysis** capabilities, featuring separate user and admin interfaces, built with FastAPI backend and React frontends.

## ✨ Key Features

- 🤖 **AI-Powered Chat**: Advanced conversational AI with contextual responses
- 📸 **Image Document Analysis**: Upload business documents (invoices, receipts, purchase orders) and get AI-generated questions
- 🎯 **Smart Question Generation**: Context-aware questions based on document type and content
- 👥 **Dual Interface**: Separate user and admin portals
- 🔍 **RAG Technology**: Retrieval-Augmented Generation for accurate responses
- 🌐 **Multi-language Support**: Supports multiple languages with multilingual embeddings

## 🏗️ Architecture

- **Backend**: FastAPI with Python, Google Gemini Vision API for image analysis
- **User Frontend**: React TypeScript app for chat interactions and image uploads
- **Admin Frontend**: React TypeScript app for data management and configuration
- **Database**: SQLAlchemy with vector embeddings support
- **AI Integration**: Google Gemini, Pinecone for RAG functionality, Gemini Vision for document analysis
- **Document Processing**: PIL for image processing, intelligent document type recognition

## 🚀 Quick Start

### Local Development

1. **Backend Setup**:

   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**:

   ```bash
   # User App
   cd frontend/user
   npm install && npm start

   # Admin App
   cd frontend/admin
   npm install && npm start
   ```

## 🌐 Deployment

This project is configured for deployment on Vercel with separate deployments for each component:

### Deploy to Vercel

1. **Backend API**: Deploy from `/backend` directory
2. **User App**: Deploy from `/frontend/user` directory
3. **Admin App**: Deploy from `/frontend/admin` directory

Each directory contains its own `vercel.json` configuration file for seamless deployment.

### Environment Variables

Set up the following environment variables in your deployment:

```env
# Database
DATABASE_URL=your_database_url

# AI Services
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env

# Authentication
SECRET_KEY=your_secret_key
```

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   ├── models/             # Database models
│   ├── services/           # Business logic
│   └── vercel.json         # Vercel config
├── frontend/
│   ├── admin/              # Admin React app
│   ├── user/               # User React app
│   └── shared/             # Shared components
└── README.md
```

## 🛠️ Features

- **Intelligent Chat**: RAG-powered conversations with context awareness
- **Document Management**: Upload and manage knowledge base documents
- **Multi-language Support**: Supports various languages for global accessibility
- **Admin Dashboard**: Comprehensive data management interface
- **Real-time Chat**: Responsive chat interface with typing indicators
- **Secure Authentication**: JWT-based authentication system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
