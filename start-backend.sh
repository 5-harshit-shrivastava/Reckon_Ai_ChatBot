#!/bin/bash

# Start the Reckon ChatBot Backend
echo "Starting Reckon ChatBot Backend..."

# Navigate to backend directory
cd backend

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your API keys before running the backend."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn sqlalchemy python-dotenv langchain pinecone-client openai

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
python app/main.py