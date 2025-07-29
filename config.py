"""
Configuration settings for JobMitra Backend.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    # API Configuration
    APP_NAME: str = "JobMitra Backend API"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = """
    A comprehensive REST API for JobMitra that processes user queries using AI agents powered by CrewAI.
    
    Features:
    - AI-powered query processing
    - User profile management
    - Job search and application tracking
    - Mock interview system
    - Learning resources and progress tracking
    - Dashboard analytics
    - MongoDB integration for data persistence
    - OpenAI integration via CrewAI
    """
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    LOG_LEVEL: str = "info"
    
    # CORS Configuration
    CORS_ORIGINS: list = [
        "http://localhost:4200",  # Angular default port
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:4200",  # Alternative localhost format
        "http://127.0.0.1:3000",  # Alternative localhost format
    ]
    
    # Environment Variables
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MONGO_URI: str = os.getenv("MONGO_URI", "")
    
    @property
    def required_env_vars(self) -> list:
        """List of required environment variables."""
        return ["OPENAI_API_KEY", "MONGO_URI"]
    
    @property
    def missing_env_vars(self) -> list:
        """List of missing environment variables."""
        return [var for var in self.required_env_vars if not os.getenv(var)]


# Create settings instance
settings = Settings()
