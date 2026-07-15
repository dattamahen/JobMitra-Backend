#!/bin/bash
echo "Installing JobMitra Backend dependencies..."

# Core FastAPI packages
pip install fastapi uvicorn python-dotenv

# MongoDB packages
pip install motor pymongo

# Additional packages
pip install pydantic typing-extensions

echo "✅ Installation complete!"
echo "You can now start the server with: python main.py"
