# Reckon AI ChatBot - Production Setup

## Project Structure
```
Reckon_Ai_ChatBot/
├── backend/           # FastAPI backend
├── frontend/
│   ├── user/         # User interface
│   └── admin/        # Admin interface
└── README.md         # Project documentation
```

## Production Deployment

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
# User Interface
cd frontend/user
npm install
npm run build

# Admin Interface
cd frontend/admin
npm install
npm run build
```

### Environment Variables
Create `.env` file in backend directory:
```
DATABASE_URL=your_database_url
OPENAI_API_KEY=your_openai_key
CORS_ORIGINS=["http://localhost:3000"]
```

### Production Checklist
- [ ] Set production environment variables
- [ ] Configure database connections
- [ ] Set up SSL certificates
- [ ] Configure CORS origins
- [ ] Set up monitoring and logging
- [ ] Configure backup systems

## API Endpoints
- Chat API: `http://localhost:8000/api/chat/`
- Knowledge Base: `http://localhost:8000/api/knowledge/`
- Admin Dashboard: `http://localhost:8000/admin/`

For detailed API documentation, visit `/docs` endpoint when server is running.