# 🚀 Complete Postman API Testing Guide for ReckonSales RAG Chatbot

**Base URL**: `http://localhost:8000`

## 📋 **TESTING ORDER (Follow this sequence)**

### 1️⃣ **Health & Basic Endpoints**
### 2️⃣ **User Management**
### 3️⃣ **Knowledge Base (Documents)**
### 4️⃣ **Chat Sessions**
### 5️⃣ **Chat Messages & RAG**
### 6️⃣ **Advanced Features**

---

## 1️⃣ **HEALTH & BASIC ENDPOINTS**

### **1.1 Health Check**
```
Method: GET
URL: http://localhost:8000/health
Headers: Content-Type: application/json

Expected Response:
{
  "status": "healthy",
  "message": "Reckon ChatBot API is running",
  "version": "1.0.0"
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/health" -H "accept: application/json"
```

---

### **1.2 Root Endpoint**
```
Method: GET
URL: http://localhost:8000/
Headers: Content-Type: application/json

Expected Response:
{
  "message": "Welcome to Reckon ChatBot API",
  "version": "1.0.0",
  "status": "active"
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/" -H "accept: application/json"
```

---

### **1.3 Ping**
```
Method: GET
URL: http://localhost:8000/ping
Headers: Content-Type: application/json

Expected Response:
{
  "message": "pong"
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/ping" -H "accept: application/json"
```

---

## 2️⃣ **USER MANAGEMENT**

### **2.1 Create User**
```
Method: POST
URL: http://localhost:8000/api/users/
Headers: Content-Type: application/json

Body (JSON):
{
  "name": "John Doe",
  "email": "john.doe@reckon.com",
  "phone": "+919876543210",
  "company_name": "Reckon Pharmacy",
  "industry_type": "pharmacy",
  "reckon_user_id": "R123456"
}

Expected Response:
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "user_id": 2,
    "email": "john.doe@reckon.com"
  }
}
```

**🔹 CURL Command:**
```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@reckon.com",
    "phone": "+919876543210",
    "company_name": "Reckon Pharmacy",
    "industry_type": "pharmacy",
    "reckon_user_id": "R123456"
  }'
```

---

### **2.2 Get User by ID**
```
Method: GET
URL: http://localhost:8000/api/users/2
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "User retrieved successfully",
  "data": {
    "user": {
      "id": 2,
      "name": "John Doe",
      "email": "john.doe@reckon.com",
      // ... other user fields
    }
  }
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/api/users/2" -H "accept: application/json"
```

---

### **2.3 List All Users**
```
Method: GET
URL: http://localhost:8000/api/users/?skip=0&limit=10
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Retrieved X users",
  "data": {
    "users": [...],
    "total_count": X,
    "skip": 0,
    "limit": 10
  }
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/api/users/?skip=0&limit=10" -H "accept: application/json"
```

---

## 3️⃣ **KNOWLEDGE BASE (DOCUMENTS)**

### **3.1 Create Document (Text)**
```
Method: POST
URL: http://localhost:8000/api/knowledge/documents/
Headers: Content-Type: application/json

Body (JSON):
{
  "title": "ReckonSales Pharmacy Guide",
  "content": "Step 1: Login to ReckonSales Pharmacy module. Navigate to Medicine Inventory. Step 2: Add new medicines by clicking Add Medicine button. Enter medicine name, batch number, expiry date, and quantity. Step 3: Set pricing and GST rates. Save the medicine details. For prescription management, go to Prescription section and scan or manually enter prescription details.",
  "document_type": "guide",
  "industry_type": "pharmacy",
  "language": "en"
}

Expected Response:
{
  "success": true,
  "message": "Document 'ReckonSales Pharmacy Guide' created successfully with X chunks and Y embeddings",
  "document": {...},
  "chunks_created": X,
  "processing_time_ms": Z
}
```

**🔹 CURL Command:**
```bash
curl -X POST "http://localhost:8000/api/knowledge/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "ReckonSales Pharmacy Guide",
    "content": "Step 1: Login to ReckonSales Pharmacy module. Navigate to Medicine Inventory. Step 2: Add new medicines by clicking Add Medicine button. Enter medicine name, batch number, expiry date, and quantity. Step 3: Set pricing and GST rates. Save the medicine details. For prescription management, go to Prescription section and scan or manually enter prescription details.",
    "document_type": "guide",
    "industry_type": "pharmacy",
    "language": "en"
  }'
```

---

### **3.2 Upload Document File**
```
Method: POST
URL: http://localhost:8000/api/knowledge/documents/upload
Headers: Content-Type: multipart/form-data

Form Data:
- file: [Select a .txt file]
- title: "Auto Parts Manual"
- document_type: "manual"
- industry_type: "auto_parts"
- language: "en"
- chunk_size: 1000
- chunk_overlap: 200

Expected Response:
{
  "success": true,
  "message": "File 'filename.txt' uploaded and processed successfully with X chunks and Y embeddings",
  "document": {...},
  "chunks_created": X,
  "processing_time_ms": Z
}
```

**🔹 CURL Command:**
```bash
# Create a test file first
echo "ReckonSales Auto Parts Guide: Step 1: Access Parts Inventory. Step 2: Add new auto parts with part numbers, compatibility details, and pricing." > test_autoparts.txt

curl -X POST "http://localhost:8000/api/knowledge/documents/upload" \
  -F "file=@test_autoparts.txt" \
  -F "title=Auto Parts Manual" \
  -F "document_type=manual" \
  -F "industry_type=auto_parts" \
  -F "language=en" \
  -F "chunk_size=1000" \
  -F "chunk_overlap=200"
```

---

### **3.3 Get Document by ID**
```
Method: GET
URL: http://localhost:8000/api/knowledge/documents/1
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Document retrieved successfully",
  "data": {
    "document": {
      "id": 1,
      "title": "...",
      "content": "...",
      // ... other document fields
    }
  }
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/api/knowledge/documents/1" -H "accept: application/json"
```

---

### **3.4 List Documents with Filters**
```
Method: GET
URL: http://localhost:8000/api/knowledge/documents/?document_type=guide&industry_type=pharmacy&language=en&skip=0&limit=10
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Retrieved X documents",
  "documents": [...],
  "total_count": X
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/api/knowledge/documents/?document_type=guide&industry_type=pharmacy&language=en&skip=0&limit=10" -H "accept: application/json"
```

---

### **3.5 Get Document Chunks**
```
Method: GET
URL: http://localhost:8000/api/knowledge/documents/1/chunks?skip=0&limit=10
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Retrieved X chunks for document 1",
  "data": {
    "document_title": "...",
    "chunks": [...],
    "total_chunks": X,
    "pagination": {...}
  }
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/api/knowledge/documents/1/chunks?skip=0&limit=10" -H "accept: application/json"
```

---

### **3.6 Search Documents**
```
Method: POST
URL: http://localhost:8000/api/knowledge/search
Headers: Content-Type: application/json

Body (JSON):
{
  "query": "How to add medicine inventory",
  "document_types": ["guide", "manual"],
  "industry_types": ["pharmacy"],
  "language": "en",
  "limit": 5,
  "min_confidence": 0.3
}

Expected Response:
{
  "success": true,
  "message": "Found X relevant chunks",
  "query": "How to add medicine inventory",
  "results": [...],
  "total_results": X,
  "search_time_ms": Z
}
```

**🔹 CURL Command:**
```bash
curl -X POST "http://localhost:8000/api/knowledge/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to add medicine inventory",
    "document_types": ["guide", "manual"],
    "industry_types": ["pharmacy"],
    "language": "en",
    "limit": 5,
    "min_confidence": 0.3
  }'
```

---

### **3.7 Get Knowledge Analytics**
```
Method: GET
URL: http://localhost:8000/api/knowledge/analytics
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Knowledge base analytics retrieved successfully",
  "data": {
    "analytics": {
      "total_documents": X,
      "documents_by_type": {...},
      "documents_by_industry": {...},
      "documents_by_language": {...},
      "total_chunks": Y,
      "average_chunks_per_doc": Z
    }
  }
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/api/knowledge/analytics" -H "accept: application/json"
```

---

## 4️⃣ **CHAT SESSIONS**

### **4.1 Create Chat Session**
```
Method: POST
URL: http://localhost:8000/api/chat/sessions/
Headers: Content-Type: application/json

Body (JSON):
{
  "user_id": 2,
  "channel": "web",
  "language": "en"
}

Expected Response:
{
  "success": true,
  "message": "Chat session created successfully",
  "data": {
    "session": {
      "id": 2,
      "user_id": 2,
      "session_id": "uuid-here",
      "channel": "web",
      "language": "en",
      "is_active": true,
      // ... other fields
    },
    "is_new": true
  }
}
```

**🔹 CURL Command:**
```bash
curl -X POST "http://localhost:8000/api/chat/sessions/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "channel": "web",
    "language": "en"
  }'
```

---

### **4.2 Get Session by ID**
```
Method: GET
URL: http://localhost:8000/api/chat/sessions/2
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Session retrieved successfully",
  "data": {
    "session": {...}
  }
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/api/chat/sessions/2" -H "accept: application/json"
```

---

### **4.3 List User Sessions**
```
Method: GET
URL: http://localhost:8000/api/chat/sessions/user/2?skip=0&limit=10
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Retrieved X sessions for user 2",
  "data": {
    "sessions": [...],
    "total_count": X
  }
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/api/chat/sessions/user/2?skip=0&limit=10" -H "accept: application/json"
```

---

### **4.4 End Session**
```
Method: PUT
URL: http://localhost:8000/api/chat/sessions/2/end
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Session ended successfully",
  "data": {
    "session_id": 2,
    "ended_at": "2025-09-13T06:00:00"
  }
}
```

**🔹 CURL Command:**
```bash
curl -X PUT "http://localhost:8000/api/chat/sessions/2/end" -H "accept: application/json"
```

---

## 5️⃣ **CHAT MESSAGES & RAG**

### **5.1 Send Message (RAG-Powered)**
```
Method: POST
URL: http://localhost:8000/api/chat/messages/send
Headers: Content-Type: application/json

Body (JSON):
{
  "session_id": 2,
  "message": "How do I add medicine to inventory in pharmacy module?",
  "channel": "web",
  "language": "en"
}

Expected Response:
{
  "success": true,
  "message": "Message sent and response generated successfully",
  "data": {
    "conversation_flow": "user_message -> ai_response",
    "response_time_ms": X,
    "intent_detected": "inventory"
  },
  "user_message": {...},
  "assistant_response": {
    "message_text": "To add medicine to inventory: 1. Login to ReckonSales...",
    "confidence_score": 0.8,
    "chunks_used": 2,
    "sources": [...]
  },
  "session_info": {...}
}
```

**🔹 CURL Command:**
```bash
curl -X POST "http://localhost:8000/api/chat/messages/send" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 2,
    "message": "How do I add medicine to inventory in pharmacy module?",
    "channel": "web",
    "language": "en"
  }'
```

---

### **5.2 Direct RAG Query**
```
Method: POST
URL: http://localhost:8000/api/chat/messages/rag/query?query=How%20to%20manage%20prescriptions&industry_context=pharmacy&language=en
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "RAG query processed successfully",
  "data": {
    "query": "How to manage prescriptions",
    "response": "For prescription management...",
    "confidence": 0.85,
    "sources": [...],
    "processing_time_ms": X,
    "chunks_used": 3,
    "model_used": "gpt-3.5-turbo"
  }
}
```

**🔹 CURL Command:**
```bash
curl -X POST "http://localhost:8000/api/chat/messages/rag/query?query=How%20to%20manage%20prescriptions&industry_context=pharmacy&language=en" \
  -H "Content-Type: application/json"
```

---

### **5.3 Get Session Messages**
```
Method: GET
URL: http://localhost:8000/api/chat/messages/session/2?message_type=assistant&skip=0&limit=10
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Retrieved X messages for session 2",
  "data": {
    "session_id": 2,
    "filter": {"message_type": "assistant"}
  },
  "messages": [...],
  "pagination": {...}
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/api/chat/messages/session/2?message_type=assistant&skip=0&limit=10" -H "accept: application/json"
```

---

### **5.4 Get Message by ID**
```
Method: GET
URL: http://localhost:8000/api/chat/messages/3
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Message retrieved successfully",
  "data": {
    "message": {
      "id": 3,
      "session_id": 2,
      "message_type": "assistant",
      "message_text": "...",
      // ... other fields
    }
  }
}
```

**🔹 CURL Command:**
```bash
curl -X GET "http://localhost:8000/api/chat/messages/3" -H "accept: application/json"
```

---

### **5.5 Escalate Message to Human**
```
Method: PUT
URL: http://localhost:8000/api/chat/messages/3/escalate
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Message escalated to human successfully",
  "data": {
    "message_id": 3,
    "escalated_at": "2025-09-13T06:00:00"
  }
}
```

**🔹 CURL Command:**
```bash
curl -X PUT "http://localhost:8000/api/chat/messages/3/escalate" -H "accept: application/json"
```

---

## 6️⃣ **ADVANCED FEATURES**

### **6.1 Create Embeddings for Existing Chunks**
```
Method: POST
URL: http://localhost:8000/api/chat/messages/embeddings/create
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Created embeddings for X chunks",
  "data": {
    "processed": X,
    "total_chunks": Y
  }
}
```

**🔹 CURL Command:**
```bash
curl -X POST "http://localhost:8000/api/chat/messages/embeddings/create" -H "accept: application/json"
```

---

### **6.2 Delete Document**
```
Method: DELETE
URL: http://localhost:8000/api/knowledge/documents/1
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Document 'Document Title' and all its chunks deleted successfully",
  "data": {
    "document_id": 1
  }
}
```

**🔹 CURL Command:**
```bash
curl -X DELETE "http://localhost:8000/api/knowledge/documents/1" -H "accept: application/json"
```

---

### **6.3 Delete Message (Soft Delete)**
```
Method: DELETE
URL: http://localhost:8000/api/chat/messages/3
Headers: Content-Type: application/json

Expected Response:
{
  "success": true,
  "message": "Message deleted successfully",
  "data": {
    "message_id": 3
  }
}
```

**🔹 CURL Command:**
```bash
curl -X DELETE "http://localhost:8000/api/chat/messages/3" -H "accept: application/json"
```

---

## 🧪 **TESTING SCENARIOS**

### **Scenario 1: Complete Pharmacy Workflow**
1. Create pharmacy user
2. Upload pharmacy documents
3. Create chat session
4. Ask pharmacy-specific questions
5. Verify RAG responses use pharmacy context

### **Scenario 2: Multi-language Testing**
1. Upload Hindi content
2. Send Hindi queries
3. Verify Hindi responses

### **Scenario 3: Error Handling**
1. Test with invalid user IDs
2. Test with empty messages
3. Test with non-existent sessions

### **Scenario 4: Performance Testing**
1. Upload large documents
2. Send multiple concurrent requests
3. Monitor response times

---

## 🎯 **EXPECTED BEHAVIOR**

### **✅ Success Indicators:**
- Status codes: 200, 201
- "success": true in responses
- Proper data structure in responses
- Reasonable response times (< 10 seconds)

### **⚠️ Warning Indicators:**
- OpenAI quota exceeded (fallback responses still work)
- Zero chunks used (no relevant documents found)
- Low confidence scores (< 0.5)

### **❌ Error Indicators:**
- Status codes: 400, 404, 422, 500
- "success": false in responses
- Missing required fields
- Database connection errors

---

## 🔍 **API DOCUMENTATION**

**Interactive Docs**: http://localhost:8000/docs
**OpenAPI JSON**: http://localhost:8000/openapi.json

Use these for detailed parameter specifications and response schemas!