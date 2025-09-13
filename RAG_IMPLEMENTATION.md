# RAG Response Generation Implementation

## Overview

This implementation provides a complete **Retrieval-Augmented Generation (RAG)** system for the ReckonSales chatbot. The system combines document retrieval with GPT-4 to generate contextual, domain-specific responses.

## Architecture

```
User Query → Vector Search → Context Building → GPT-4 → Response
     ↓              ↓              ↓             ↓
  Intent    →  Relevant Docs  →  Formatted   →  Domain-specific
Detection      from Knowledge     Context        Response
               Base
```

## Key Components

### 1. Vector Search Service (`services/vector_search.py`)
- **Embeddings**: Creates vector embeddings using OpenAI or sentence-transformers
- **Pinecone Integration**: Stores and searches vectors in Pinecone cloud
- **Hybrid Search**: Combines semantic search with traditional text search
- **Fallback Support**: Works without API keys using local models

### 2. RAG Service (`services/rag_service.py`)
- **Context Building**: Assembles relevant document chunks into context
- **GPT-4 Integration**: Generates responses using OpenAI's GPT-4
- **Industry Context**: Provides industry-specific responses (pharmacy, auto-parts, etc.)
- **Multi-language**: Supports English and Hindi responses
- **Confidence Scoring**: Calculates response confidence based on context quality

### 3. Enhanced Chat Routes (`routes/chat_messages.py`)
- **RAG-Powered Responses**: Updated `/send` endpoint uses RAG by default
- **Direct RAG Query**: New `/rag/query` endpoint for testing
- **Embedding Creation**: New `/embeddings/create` endpoint for setup
- **Source Attribution**: Responses include source document references

### 4. Enhanced Knowledge Base (`routes/knowledge_base.py`)
- **Auto-Embedding**: Document uploads automatically create embeddings
- **Improved Search**: Better document search with vector similarity
- **Chunk Management**: Enhanced chunk processing and storage

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install openai sentence-transformers pinecone-client
```

### 2. Configure Environment Variables

Update `.env` file:

```env
# Required for full RAG functionality
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment

# Existing configuration
DATABASE_URL=sqlite:///./reckon_chatbot.db
SECRET_KEY=your_super_secret_key_here
```

### 3. Initialize Database and Embeddings

```bash
# Run the test to verify setup
python test_basic_rag.py

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Create Embeddings for Existing Documents

```bash
# POST request to create embeddings
curl -X POST "http://localhost:8000/api/chat/messages/embeddings/create"
```

## API Endpoints

### Chat with RAG

**POST** `/api/chat/messages/send`

Enhanced endpoint now uses RAG by default:

```json
{
  "session_id": 1,
  "message": "How do I create an invoice in ReckonSales?",
  "channel": "web",
  "language": "en"
}
```

Response includes:
- AI-generated response
- Confidence score
- Source documents used
- Processing time
- Number of chunks retrieved

### Direct RAG Query

**POST** `/api/chat/messages/rag/query`

For testing and advanced usage:

```json
{
  "query": "What should I do if GST calculation fails?",
  "industry_context": "pharmacy",
  "language": "en"
}
```

### Upload Documents with Auto-Embedding

**POST** `/api/knowledge/documents/upload`

Uploads now automatically create embeddings:

```bash
curl -X POST "http://localhost:8000/api/knowledge/documents/upload" \
  -F "file=@reckon_guide.txt" \
  -F "title=ReckonSales User Guide" \
  -F "document_type=guide" \
  -F "industry_type=general"
```

## Configuration Options

### Industry-Specific Responses

The system provides specialized responses for different industries:

- **pharmacy**: Medicine management, prescriptions, regulatory compliance
- **auto_parts**: Vehicle compatibility, spare parts, garage operations
- **fmcg**: Grocery inventory, retail operations, consumer goods
- **restaurant**: Menu planning, kitchen operations, table management

### Language Support

- **English (`en`)**: Default language with full functionality
- **Hindi (`hi`)**: Bilingual responses with Hindi explanations

### Response Quality Controls

- **Confidence Scoring**: 0.3-0.95 based on context quality and certainty
- **Source Attribution**: All responses include references to source documents
- **Fallback Responses**: Graceful degradation when AI services are unavailable

## Testing

### Basic Functionality Test

```bash
python test_basic_rag.py
```

### Full Integration Test

```bash
python test_rag_implementation.py
```

### Manual Testing

1. **Upload a document**:
   ```bash
   curl -X POST "http://localhost:8000/api/knowledge/documents/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test Guide",
       "content": "Step 1: Login to ReckonSales. Step 2: Navigate to billing.",
       "document_type": "guide",
       "language": "en"
     }'
   ```

2. **Query the system**:
   ```bash
   curl -X POST "http://localhost:8000/api/chat/messages/rag/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "How do I login?",
       "language": "en"
     }'
   ```

## Performance Optimization

### Vector Search
- Uses Pinecone for fast similarity search
- Implements hybrid search (semantic + keyword)
- Caches embeddings to avoid recomputation

### Response Generation
- Limits context size to prevent token overflow
- Uses streaming responses for better UX
- Implements timeout handling

### Cost Management
- Configurable embedding models (OpenAI vs local)
- Adjustable chunk sizes and overlap
- Rate limiting for API calls

## Monitoring and Analytics

### Query Logging
All RAG queries are logged with:
- User ID and session
- Query text and language
- Retrieved chunks and processing time
- Response generation success/failure

### Performance Metrics
- Response time tracking
- Confidence score distribution
- Source document usage statistics
- Embedding creation success rates

## Troubleshooting

### Common Issues

1. **"No module named 'openai'"**
   - Install: `pip install openai`

2. **"No module named 'sentence_transformers'"**
   - Install: `pip install sentence-transformers`

3. **"Pinecone API key not found"**
   - Add to `.env`: `PINECONE_API_KEY=your_key`
   - System will fallback to local embeddings

4. **"No relevant documents found"**
   - Upload more documents to the knowledge base
   - Check document processing and chunking
   - Verify embeddings are created

5. **Low confidence responses**
   - Add more relevant documents
   - Improve document quality and structure
   - Adjust chunk size and overlap parameters

### Fallback Behavior

The system gracefully handles missing services:
- **No OpenAI**: Uses sentence-transformers for embeddings
- **No Pinecone**: Uses simple text search
- **No AI response**: Returns rule-based fallback responses

## Next Steps

1. **Add more documents** to the knowledge base
2. **Configure API keys** for full functionality
3. **Train custom embeddings** for domain-specific terms
4. **Implement feedback loops** for response quality improvement
5. **Add conversation memory** for multi-turn interactions

## API Documentation

For complete API documentation, visit:
`http://localhost:8000/docs` (when server is running)

The system maintains backward compatibility with existing endpoints while adding powerful RAG capabilities.