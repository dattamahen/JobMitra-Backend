@echo off
echo Starting JobMitra Backend API...
echo Current directory: %cd%
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo Error: main.py not found. Make sure you're in the JobMitra-Backend directory.
    pause
    exit /b 1
)

REM Check Python installation
python --version
if %errorlevel% neq 0 (
    echo Error: Python not found. Please ensure Python is installed and in PATH.
    pause
    exit /b 1
)

REM Check if uvicorn is installed
python -c "import uvicorn; print('✅ Uvicorn available')" 2>nul
if %errorlevel% neq 0 (
    echo Installing uvicorn...
    pip install uvicorn
)

REM Start the server
echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0

pause
