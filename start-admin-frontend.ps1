# Start Reckon Admin Frontend
Write-Host "Starting Reckon Admin Frontend..." -ForegroundColor Green

# Navigate to admin frontend directory
Set-Location "c:\Users\hp\OneDrive\Documents\Desktop\Reckon_Ai_ChatBot\frontend\admin"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Set environment variables for compatibility
$env:NODE_OPTIONS = "--openssl-legacy-provider"
$env:BROWSER = "none"
$env:PORT = "3000"

# Start frontend
Write-Host "Starting React app on http://localhost:3000" -ForegroundColor Cyan
npm start

Write-Host "Admin frontend stopped." -ForegroundColor Yellow
