# RecoverAI Windows One-Click Startup Script
# Safe environment check and launcher for RecoverAI Backend & Frontend

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "         RECOVERAI — ONE-CLICK DEVELOPMENT STARTUP          " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Check Python
Write-Host "`n[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✖ Python is not accessible in current PATH." -ForegroundColor Red
    exit 1
}

# 2. Check Node & npm
Write-Host "`n[2/6] Checking Node.js and npm..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "✓ Node.js found: $nodeVersion (npm: $npmVersion)" -ForegroundColor Green
} catch {
    Write-Host "✖ Node.js or npm is not accessible in current PATH." -ForegroundColor Red
    exit 1
}

# 3. Check Backend Dependencies
Write-Host "`n[3/6] Verifying backend dependencies..." -ForegroundColor Yellow
try {
    python -c "import fastapi, uvicorn, sqlalchemy, pydantic"
    Write-Host "✓ Backend dependencies satisfied." -ForegroundColor Green
} catch {
    Write-Host "⚠ Installing backend dependencies from backend/requirements.txt..." -ForegroundColor Yellow
    python -m pip install -r backend/requirements.txt
}

# 4. Start Backend Service
Write-Host "`n[4/6] Starting RecoverAI FastAPI Backend Server on port 8000..." -ForegroundColor Yellow
$port8000Active = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -InformationLevel Quiet
if ($port8000Active) {
    Write-Host "✓ Backend server is already running on http://127.0.0.1:8000" -ForegroundColor Green
} else {
    $backendJob = Start-Job -ScriptBlock {
        python -m uvicorn backend.app.main:app --port 8000
    }
    Start-Sleep -Seconds 3
}

# 5. Verify Backend /health
Write-Host "`n[5/6] Verifying Backend Health Check at http://127.0.0.1:8000/health..." -ForegroundColor Yellow
try {
    $healthResp = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 5
    if ($healthResp.status -eq "HEALTHY") {
        Write-Host "✓ Backend status: HEALTHY (Database: $($healthResp.dependencies.database))" -ForegroundColor Green
    } else {
        Write-Host "⚠ Backend status: $($healthResp.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✖ Backend failed to respond on http://127.0.0.1:8000/health" -ForegroundColor Red
}

# 6. Start Frontend Next.js Server
Write-Host "`n[6/6] Starting RecoverAI Next.js Frontend Server on port 3000..." -ForegroundColor Yellow
$port3000Active = Test-NetConnection -ComputerName 127.0.0.1 -Port 3000 -InformationLevel Quiet
if ($port3000Active) {
    Write-Host "✓ Frontend server is already running on http://localhost:3000" -ForegroundColor Green
} else {
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location -Path "frontend"
        npm run dev
    }
    Start-Sleep -Seconds 3
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "                  RECOVERAI IS NOW RUNNING                  " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Backend Service:   http://127.0.0.1:8000" -ForegroundColor Green
Write-Host " Health Endpoint:   http://127.0.0.1:8000/health" -ForegroundColor Green
Write-Host " Dashboard URL:     http://localhost:3000/dashboard" -ForegroundColor Green
Write-Host " Simulation URL:    http://localhost:3000/simulation" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
