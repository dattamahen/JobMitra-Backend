"""
Configuration settings for JobMitra Backend
Optimized for 10K+ daily users
"""
import os
from typing import Optional
class Settings:
    APP_NAME = "JobMitra Backend API"
    DESCRIPTION = "AI-powered job search and career development platform"
    VERSION = "1.0.0"
    CORS_ORIGINS = ["http://localhost:4200", "*"]
    HOST = "localhost"
    PORT = 8000
    RELOAD = True
    LOG_LEVEL = "info"
    missing_env_vars = []
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmitra")
    MONGO_MAX_POOL_SIZE = 100
    MONGO_MIN_POOL_SIZE = 10
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL = 300
    SESSION_TTL = 86400
    RATE_LIMIT_PER_MINUTE = 100
    RATE_LIMIT_BURST = 200
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    MAX_WORKERS = 4
    KEEP_ALIVE_TIMEOUT = 5
    ENABLE_METRICS = True

settings = Settings()