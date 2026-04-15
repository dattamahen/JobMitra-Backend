"""
Configuration settings for JobMitra Backend
Loads environment-specific .env file based on APP_ENV variable.

Usage:
  Local:  APP_ENV=local python main.py   (or just python main.py, defaults to local)
  Dev:    APP_ENV=dev python main.py
  Prod:   APP_ENV=prod python main.py
"""
import os
from dotenv import load_dotenv

# Determine which .env file to load
# Priority: APP_ENV env var > default "local"
app_env = os.getenv("APP_ENV", "local")

# Load the environment-specific .env file
env_file = f".env.{app_env}"
if os.path.exists(env_file):
    load_dotenv(env_file, override=True)
    print(f"✅ Loaded environment: {env_file}")
elif os.path.exists(".env"):
    load_dotenv(".env", override=True)
    print(f"⚠️  .env.{app_env} not found, loaded fallback .env")
else:
    print(f"❌ No .env file found for environment: {app_env}")


class Settings:
    # App Info
    APP_NAME = "JobMitra Backend API"
    DESCRIPTION = "AI-powered job search and career development platform"
    VERSION = "1.0.0"
    APP_ENV = os.getenv("APP_ENV", "local")

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    RELOAD = APP_ENV == "local"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

    # CORS
    _cors_raw = os.getenv("CORS_ORIGINS", "http://localhost:4200")
    CORS_ORIGINS = [origin.strip() for origin in _cors_raw.split(",")]

    # Frontend
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")

    # Database
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmitra")
    MONGO_MAX_POOL_SIZE = 100
    MONGO_MIN_POOL_SIZE = 10

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL = 300
    SESSION_TTL = 86400

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "local-jwt-secret-key-change-this-in-production-12345")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    RATE_LIMIT_BURST = 200

    # AI API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

    # Email
    EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "")
    APP_NAME_EMAIL = os.getenv("APP_NAME", "JobMouka")

    # Workers
    MAX_WORKERS = 4
    KEEP_ALIVE_TIMEOUT = 5
    ENABLE_METRICS = True

    # Deprecated - kept for backward compat
    SECRET_KEY = JWT_SECRET_KEY
    missing_env_vars = []


settings = Settings()
