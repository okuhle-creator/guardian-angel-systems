# Guardian Angel Systems (GAS) - Automated Test Suite Runner (Windows PowerShell)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   GUARDIAN ANGEL SYSTEMS (GAS) - TEST VERIFICATION       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Run Backend Pytest Suite
Write-Host "`n[1/2] Running Backend Pytest Engine & API Integration Tests..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\..\backend"
$env:PYTHONPATH = "."
python -m pytest -v

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nBackend tests failed! Please inspect output above." -ForegroundColor Red
    Exit 1
}

# 2. Run Frontend Production TypeScript Build
Write-Host "`n[2/2] Running Frontend TypeScript Typecheck & Production Build..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\..\frontend"
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nFrontend build failed! Please inspect output above." -ForegroundColor Red
    Exit 1
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "   ALL TESTS & PRODUCTION BUILDS PASSED WITH ZERO ERRORS  " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
