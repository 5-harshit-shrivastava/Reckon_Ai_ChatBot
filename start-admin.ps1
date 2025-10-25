# Start Admin Frontend on Port 3001
Write-Host "Starting Admin Frontend on port 3001..."
Set-Location "c:\Users\hp\OneDrive\Documents\Desktop\Reckon_Ai_ChatBot\frontend\admin"
$env:PORT = "3001"
npm start
