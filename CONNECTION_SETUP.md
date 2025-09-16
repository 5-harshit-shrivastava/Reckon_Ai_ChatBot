# Backend-Frontend Connection Setup

This guide explains how to connect and run the Reckon AI ChatBot backend with the frontend applications.

## Quick Start

### 1. Start Backend (Required)
```bash
./start-backend.sh
```
The backend will run on `http://localhost:8000`

### 2. Start Frontend(s)
```bash
# Start both user and admin frontends
./start-frontend.sh

# OR start individually
./start-frontend.sh user    # User frontend on port 3000
./start-frontend.sh admin   # Admin frontend on port 3001
```

## Manual Setup

### Backend Setup
1. Navigate to `backend/` directory
2. Create `.env` file from `.env.example`
3. Configure your API keys in `.env`
4. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn sqlalchemy python-dotenv
   ```
5. Start the server:
   ```bash
   python app/main.py
   ```

### Frontend Setup

#### User Frontend (Port 3000)
1. Navigate to `frontend/user/`
2. Install dependencies: `npm install`
3. Start: `npm start`

#### Admin Frontend (Port 3001)
1. Navigate to `frontend/admin/`
2. Install dependencies: `npm install`
3. Start: `npm start`

## API Connections

### Backend API Endpoints
- **Base URL**: `http://localhost:8000`
- **Health Check**: `GET /health`
- **Chat Messages**: `POST /api/chat/messages/send`
- **Chat Sessions**: `POST /api/chat/sessions`
- **Admin Dashboard**: `GET /api/admin/dashboard/stats`

### Frontend API Configuration

#### User Frontend
- API service: `src/services/chatApi.ts`
- Connects to: `http://localhost:8000`
- Main features: Chat messaging, session management

#### Admin Frontend
- API service: `src/services/adminApi.ts`
- Connects to: `http://localhost:8000`
- Main features: Dashboard stats, knowledge base management

## Connection Status

✅ **Backend API**: FastAPI server with proper CORS configuration
✅ **User Frontend**: React app with chat API integration
✅ **Admin Frontend**: React app with admin API integration
✅ **API Types**: TypeScript interfaces match backend schemas

## Troubleshooting

### Common Issues
1. **Backend not starting**: Check `.env` file exists and has required variables
2. **Frontend connection errors**: Ensure backend is running on port 8000
3. **CORS errors**: Backend is configured to allow all origins for development
4. **Session errors**: User frontend now creates sessions automatically

### Testing Connection
1. Start backend first
2. Visit `http://localhost:8000/health` - should return healthy status
3. Start frontend
4. User frontend should connect and create a chat session automatically
5. Admin frontend should load dashboard data

## Environment Variables

Required in `backend/.env`:
```env
DATABASE_URL=sqlite:///./reckon_chatbot.db
OPENAI_API_KEY=your_key_here
HUGGINGFACE_API_TOKEN=your_token_here
HOST=0.0.0.0
PORT=8000
```

## Development Notes

- Backend runs on port 8000 (configurable via .env)
- User frontend runs on port 3000
- Admin frontend runs on port 3001
- Both frontends are configured to call `localhost:8000` API
- Sessions are created automatically for user frontend
- Fallback to mock responses if backend is unavailable