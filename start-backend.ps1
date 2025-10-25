# Start Reckon ChatBot Backend
Write-Host "Starting Reckon ChatBot Backend..." -ForegroundColor Green

# Navigate to backend directory
Set-Location "c:\Users\hp\OneDrive\Documents\Desktop\Reckon_Ai_ChatBot\backend"

# Set Python path
$env:PYTHONPATH = "c:\Users\hp\OneDrive\Documents\Desktop\Reckon_Ai_ChatBot\backend"

# Start backend
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Cyan
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Write-Host "Backend stopped." -ForegroundColor Yellow
