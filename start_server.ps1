# JobMitra Backend Server Startup Script
Write-Host "🚀 Starting JobMitra Backend API..." -ForegroundColor Green
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Error: main.py not found. Make sure you're in the JobMitra-Backend directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found. Please ensure Python is installed and in PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required packages are installed
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow

try {
    python -c "import uvicorn, fastapi, motor, pymongo; print('✅ All dependencies available')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "📦 Installing missing dependencies..." -ForegroundColor Yellow
        pip install fastapi uvicorn motor pymongo python-dotenv
    }
} catch {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    pip install fastapi uvicorn motor pymongo python-dotenv
}

# Check MongoDB connection
Write-Host "🔍 Checking MongoDB connection..." -ForegroundColor Yellow
try {
    python -c "import pymongo; pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000).admin.command('ping'); print('✅ MongoDB connection successful')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MongoDB is running and accessible" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MongoDB connection failed - will use fallback mode" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  MongoDB connection test failed - will use fallback mode" -ForegroundColor Yellow
}

# Start the server
Write-Host ""
Write-Host "🌐 Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔍 Health Check: http://localhost:8000/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

try {
    python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0
} catch {
    Write-Host ""
    Write-Host "❌ Server stopped or failed to start" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Server shutdown complete." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
