# 🤖 Reckon AI RAG Chatbot

A sophisticated **Retrieval-Augmented Generation (RAG)** chatbot system with **Image Document Analysis** capabilities, featuring separate user and admin interfaces. Built with modern tech stack: FastAPI backend, React frontends, and advanced AI integration.

## ✨ Key Features

### 🤖 **Intelligent Conversational AI**
- **RAG Technology**: Context-aware responses using retrieval-augmented generation
- **Multi-language Support**: Supports multiple languages with multilingual embeddings
- **Smart Intent Detection**: Automatically detects user intents and provides relevant responses
- **Session Management**: Maintains conversation context across sessions

### 📸 **Advanced Document Analysis**
- **Image Upload & Analysis**: Upload business documents (invoices, receipts, purchase orders)
- **AI-Powered Questions**: Automatically generates relevant questions based on document content
- **Document Type Recognition**: Intelligent recognition of document types and extraction of key information
- **Vision AI Integration**: Powered by Google Gemini Vision API for accurate image analysis

### 🎯 **Dual Portal System**
- **User Portal**: Clean, intuitive chat interface for end users
- **Admin Portal**: Comprehensive data management and analytics dashboard
- **Role-Based Access**: Separate authentication and features for users and administrators

### 🔍 **Advanced Vector Search**
- **Semantic Search**: High-quality embeddings using BAAI/bge-large-en-v1.5 model
- **Pinecone Integration**: Scalable vector database for fast similarity search
- **HuggingFace API**: Modern embedding generation with fallback mechanisms
- **Hybrid Search**: Combines semantic and traditional text search for optimal results

### 📊 **Analytics & Monitoring**
- **Real-time Dashboard**: Live statistics on conversations, documents, and system health
- **Performance Metrics**: Response times, success rates, and user engagement analytics
- **Debug Tools**: Built-in debugging endpoints for troubleshooting and monitoring

## 🏗️ Architecture

### Backend (FastAPI)
- **API Framework**: FastAPI with automatic OpenAPI documentation
- **AI Integration**: Google Gemini for chat responses and vision analysis
- **Vector Database**: Pinecone for semantic search and embeddings storage
- **Document Processing**: Advanced chunking and preprocessing pipeline
- **Authentication**: JWT-based secure authentication system

### Frontend (React + TypeScript)
- **User Interface**: Modern React app with Material-UI components
- **Admin Dashboard**: Comprehensive management interface with charts and analytics
- **Responsive Design**: Mobile-first responsive design for all devices
- **Real-time Updates**: Live data updates and connection status indicators

### Data & AI Pipeline
- **Document Chunking**: Intelligent text segmentation with overlap handling
- **Embedding Generation**: High-quality vector embeddings for semantic search
- **Context Retrieval**: Relevant document chunks retrieved for each query
- **Response Generation**: AI-powered responses with retrieved context

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- Pinecone API account
- HuggingFace API token
- Google Cloud API key (for Gemini)

### 1. Clone Repository
```bash
git clone https://github.com/your-username/Reckon_Rag_Chatbot.git
cd Reckon_Rag_Chatbot
```

### 2. Setup Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your API keys:
# PINECONE_API_KEY=your_pinecone_api_key
# HUGGINGFACE_API_TOKEN=your_hf_token
# GEMINI_API_KEY=your_google_api_key

# Start backend
python app/main.py
```

### 3. Setup User Frontend
```bash
cd frontend/user

# Install dependencies
npm install

# Set environment variables
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start user app
npm start
```

### 4. Setup Admin Frontend
```bash
cd frontend/admin

# Install dependencies
npm install

# Set environment variables
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start admin app
npm start
```

### 5. Access Applications
- **User Portal**: http://localhost:3000
- **Admin Portal**: http://localhost:3001  
- **API Documentation**: http://localhost:8000/docs

## 🌐 Deployment

### Vercel Deployment (Recommended)

The project is configured for seamless deployment on Vercel with separate deployments:

#### Backend Deployment
```bash
cd backend
vercel --prod
```

#### User Frontend Deployment
```bash
cd frontend/user
# Set environment variable in Vercel dashboard:
# REACT_APP_API_URL=https://your-backend.vercel.app
vercel --prod
```

#### Admin Frontend Deployment
```bash
cd frontend/admin
# Set environment variable in Vercel dashboard:
# REACT_APP_API_URL=https://your-backend.vercel.app
vercel --prod
```

### Environment Variables for Production
Set these in your Vercel dashboard:

**Backend:**
```env
PINECONE_API_KEY=your_pinecone_api_key
HUGGINGFACE_API_TOKEN=your_hf_token
GEMINI_API_KEY=your_google_api_key
```

**Frontend Apps:**
```env
REACT_APP_API_URL=https://your-backend.vercel.app
```

## 📁 Project Structure

```
Reckon_Rag_Chatbot/
├── backend/                 # FastAPI backend
│   ├── app/                # Application configuration
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── schemas.py      # Pydantic models
│   │   └── chat_schemas.py # Chat-specific schemas
│   ├── services/           # Business logic services
│   │   ├── rag_service.py          # RAG implementation
│   │   ├── vector_search.py        # Vector search & embeddings
│   │   ├── document_processor.py   # Document chunking
│   │   ├── gemini_service.py       # Google Gemini integration
│   │   └── image_analysis_service.py # Image document analysis
│   ├── routes/             # API endpoints
│   │   ├── chat_simple.py          # User chat endpoints
│   │   ├── admin_pinecone.py       # Admin management
│   │   ├── knowledge_base_pinecone.py # Document management
│   │   └── admin_utils.py          # Utility endpoints
│   ├── models/             # Database models (if using DB)
│   ├── config/             # Configuration files
│   ├── requirements.txt    # Python dependencies
│   └── vercel.json        # Vercel deployment config
├── frontend/
│   ├── user/               # User React application
│   │   ├── src/
│   │   │   ├── pages/
│   │   │   │   ├── HomePage.tsx    # Landing page
│   │   │   │   └── ChatPage.tsx    # Chat interface
│   │   │   ├── services/
│   │   │   │   └── chatApi.ts      # API client
│   │   │   └── shared/             # Shared components
│   │   ├── package.json    # Dependencies
│   │   └── vercel.json     # Deployment config
│   ├── admin/              # Admin React application
│   │   ├── src/
│   │   │   ├── pages/
│   │   │   │   ├── DashboardPage.tsx    # Analytics dashboard
│   │   │   │   └── DataManagementPage.tsx # Knowledge base management
│   │   │   ├── services/
│   │   │   │   └── adminApi.ts          # Admin API client
│   │   │   ├── components/
│   │   │   │   └── AdminLayout.tsx      # Admin layout
│   │   │   └── shared/                  # Shared components
│   │   ├── package.json    # Dependencies  
│   │   └── vercel.json     # Deployment config
│   └── shared/             # Shared components between apps
│       ├── components/     # Common UI components
│       ├── hooks/          # Custom React hooks
│       └── theme.ts        # Material-UI theme
├── DEPLOYMENT_GUIDE.md     # Detailed deployment instructions
├── ENVIRONMENT_SETUP.md    # Environment setup guide
└── README.md              # This file
```

## 🛠️ Core Features Breakdown

### 💬 **Chat System**
- **Real-time Messaging**: Instant message exchange with typing indicators
- **Session Persistence**: Conversations saved and can be resumed
- **Context Awareness**: AI maintains context throughout conversations
- **Multi-turn Conversations**: Handles complex, multi-step interactions
- **Intent Recognition**: Automatically detects user intents (questions, requests, etc.)

### 📄 **Document Management** 
- **File Upload**: Support for various document formats
- **Auto-chunking**: Intelligent text segmentation for optimal retrieval
- **Metadata Extraction**: Automatic extraction of document properties
- **Version Control**: Track document updates and changes
- **Bulk Operations**: Upload and manage multiple documents at once

### 🔍 **Search & Retrieval**
- **Semantic Search**: Find relevant content based on meaning, not just keywords
- **Hybrid Search**: Combines vector similarity and traditional text search
- **Relevance Ranking**: Advanced scoring for result relevance
- **Filtering Options**: Filter by document type, industry, language, etc.
- **Debug Tools**: Built-in search debugging and performance monitoring

### 👥 **Admin Dashboard**
- **Analytics Overview**: Comprehensive statistics on usage and performance
- **User Management**: Monitor user sessions and interactions
- **Content Management**: Add, edit, and organize knowledge base content
- **System Monitoring**: Real-time system health and performance metrics
- **Configuration**: Adjust system settings and AI parameters

### 🖼️ **Image Document Analysis**
- **Smart Upload**: Drag-and-drop image upload interface
- **Document Recognition**: Automatically identifies document types
- **Content Extraction**: Extracts text and key information from images
- **Question Generation**: Creates relevant questions based on document content
- **Business Document Focus**: Optimized for invoices, receipts, purchase orders

### 🔧 **System Features**
- **Health Monitoring**: Built-in health checks and status endpoints
- **Error Handling**: Comprehensive error handling with helpful messages
- **Logging**: Detailed logging for debugging and monitoring
- **Rate Limiting**: API rate limiting for performance protection
- **CORS Support**: Cross-origin resource sharing for frontend integration

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **API Key Management**: Secure API key storage and rotation
- **Input Validation**: Comprehensive input validation and sanitization
- **CORS Configuration**: Proper cross-origin request handling
- **Error Messages**: Secure error messages that don't expose sensitive information

## 📈 Performance Features

- **Vector Caching**: Efficient caching of frequently accessed embeddings
- **Batch Processing**: Batch operations for bulk document processing
- **Connection Pooling**: Optimized database and API connections
- **Lazy Loading**: Efficient frontend data loading strategies
- **CDN Ready**: Static assets optimized for CDN deployment

## 🔄 API Endpoints

### User API
- `POST /api/chat/sessions/` - Create new chat session
- `POST /api/chat/messages/send` - Send message and get AI response
- `POST /api/chat/upload-image` - Upload and analyze document images

### Admin API
- `GET /api/admin/dashboard/stats` - Get dashboard statistics
- `POST /api/admin/knowledge-base` - Create knowledge base entry
- `GET /api/admin/knowledge-base` - List knowledge base entries
- `PUT /api/admin/knowledge-base/{id}` - Update knowledge base entry
- `DELETE /api/admin/knowledge-base/{id}` - Delete knowledge base entry

### System API
- `GET /api/admin/system/status` - System health status
- `GET /debug/search-status` - Search service status
- `GET /debug/test-search/{query}` - Test search functionality

## 🧪 Development & Testing

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend/user
npm test

cd frontend/admin  
npm test
```

### Debug Tools
- **Search Testing**: Built-in endpoints to test search functionality
- **Embedding Debugging**: Tools to verify embedding generation
- **Connection Status**: Real-time connection status monitoring
- **Performance Metrics**: Built-in performance tracking and reporting

## 📝 Environment Configuration

### Required API Keys

1. **Pinecone**: Get from [Pinecone Console](https://app.pinecone.io/)
2. **HuggingFace**: Get from [HuggingFace Tokens](https://huggingface.co/settings/tokens)  
3. **Google Gemini**: Get from [Google AI Studio](https://aistudio.google.com/)

### Optional Configuration
- `DATABASE_URL`: For persistent storage (defaults to Pinecone-only mode)
- `CORS_ORIGINS`: Configure allowed frontend origins
- `LOG_LEVEL`: Set logging verbosity (DEBUG, INFO, WARNING, ERROR)

## 🚀 Performance Tips

- **Chunking Strategy**: Optimize chunk size (1000-1500 characters) for your content
- **Embedding Model**: Use bge-large-en-v1.5 for best English performance
- **Pinecone Index**: Use cosine similarity for optimal semantic search
- **Response Caching**: Implement caching for frequently asked questions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)  
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) and [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
- **Issues**: Create an issue on GitHub for bug reports or feature requests
- **Discussions**: Use GitHub Discussions for questions and community support

## 🌟 Acknowledgments

- **OpenAI**: For inspiring conversational AI development
- **HuggingFace**: For providing excellent embedding models
- **Pinecone**: For scalable vector database infrastructure  
- **Google**: For Gemini AI and vision capabilities
- **React & FastAPI**: For excellent development frameworks

---

**Built with ❤️ by harshit**
