@echo off
echo Installing JobMitra Backend dependencies...

REM Core FastAPI packages
pip install fastapi uvicorn python-dotenv

REM MongoDB packages  
pip install motor pymongo

REM Additional packages
pip install pydantic typing-extensions

echo.
echo ✅ Installation complete!
echo You can now start the server with: python main.py
pause
