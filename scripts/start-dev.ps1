# Guardian Angel Systems (GAS) - Local Development Runner (Windows PowerShell)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   GUARDIAN ANGEL SYSTEMS (GAS) - LOCAL DEV STARTUP       " -ForegroundColor Cyan
Write-Host "   TECHgium 2026 | L&T Technology Services (LTTS)         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Check Python and Node
Write-Host "`n[+] Verifying Runtimes..." -ForegroundColor Yellow
python --version
node --version
npm --version

Write-Host "`n[+] Starting Backend Service on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\backend'; `$env:PYTHONPATH='.'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "[+] Starting Frontend Service on http://localhost:5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\frontend'; npm run dev"

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " Services Initialized!" -ForegroundColor Green
Write-Host "   • Frontend:          http://localhost:5173" -ForegroundColor White
Write-Host "   • Backend API:       http://localhost:8000" -ForegroundColor White
Write-Host "   • API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Health Check:      http://localhost:8000/api/v1/health" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
