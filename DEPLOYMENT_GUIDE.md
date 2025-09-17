# Reckon RAG Chatbot - Deployment Guide

## Project Structure for Deployment

This project consists of 3 separate deployments:

1. **Backend API** (FastAPI) - `/backend`
2. **User Frontend** (React) - `/frontend/user`
3. **Admin Frontend** (React) - `/frontend/admin`

## Deployment Steps

### 1. Backend Deployment (Vercel)

Deploy the backend first as the frontends depend on it.

```bash
cd backend
vercel --prod
```

**Important Notes:**
- The backend will be deployed to: `https://reckon-rag-chatbot-backend.vercel.app`
- Make sure all environment variables are set in Vercel dashboard
- Database file `reckon_chatbot.db` will be included in deployment

### 2. User Frontend Deployment (Vercel)

```bash
cd frontend/user
vercel --prod
```

**Environment Variables needed:**
- `REACT_APP_API_URL=https://reckon-rag-chatbot-backend.vercel.app`

### 3. Admin Frontend Deployment (Vercel)

```bash
cd frontend/admin
vercel --prod
```

**Environment Variables needed:**
- `REACT_APP_API_URL=https://reckon-rag-chatbot-backend.vercel.app`

## Expected URLs

After deployment, you should have:

- **Backend API**: `https://reckon-rag-chatbot-backend.vercel.app`
- **User Frontend**: `https://reckon-rag-chatbot-user.vercel.app`
- **Admin Frontend**: `https://reckon-rag-chatbot-admin.vercel.app`

## Important Configuration

### Backend CORS Configuration
The backend is already configured to accept requests from the expected frontend URLs:
- `https://reckon-rag-chatbot-user.vercel.app`
- `https://reckon-rag-chatbot-admin.vercel.app`
- `http://localhost:3000` (development)
- `http://localhost:3001` (development)

### Frontend API Configuration
Both frontends automatically use the production API URL when deployed, falling back to localhost for development.

## Files Ready for Deployment

### Backend Files:
- ✅ `vercel.json` - Vercel configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `app/main.py` - Modified for Vercel with CORS configuration

### User Frontend Files:
- ✅ `vercel.json` - Vercel configuration
- ✅ `.env.production` - Production environment variables
- ✅ `package.json` - Build scripts
- ✅ Updated API endpoints to use environment variables

### Admin Frontend Files:
- ✅ `vercel.json` - Vercel configuration
- ✅ `.env.production` - Production environment variables
- ✅ `package.json` - Build scripts
- ✅ Updated API endpoints to use environment variables

## Deployment Commands

1. **Push to GitHub first:**
```bash
git add .
git commit -m "Production deployment ready"
git push origin main
```

2. **Deploy each service:**
```bash
# Backend
cd backend && vercel --prod

# User Frontend
cd ../frontend/user && vercel --prod

# Admin Frontend
cd ../frontend/admin && vercel --prod
```

3. **Verify deployments:**
- Test the backend health check: `https://your-backend-url.vercel.app/health`
- Test user frontend functionality
- Test admin frontend functionality

## Clean Project Structure

Removed unnecessary files:
- All test files and documentation
- Development scripts and database utilities
- Unused assets and configurations
- Virtual environments and cache files

The project is now optimized for production deployment on Vercel.