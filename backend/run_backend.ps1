$ErrorActionPreference = "Stop"
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Starting InterviewIQ AI FastAPI Server..." -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot

$pythonPath = "C:\Users\brgoj\AppData\Local\Programs\Python\Python313\python.exe"

if (Test-Path $pythonPath) {
    & $pythonPath -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} else {
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

