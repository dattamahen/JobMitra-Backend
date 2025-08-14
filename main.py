"""
FastAPI main application entry point for JobMitra Backend.
"""

import uvicorn

from app import create_app
from config import settings

# Create the app instance for uvicorn
app = create_app()

def main():
    """
    Main entry point for the application.
    """
    # Check if required environment variables are set
    if settings.missing_env_vars:
        print(f"Warning: Missing environment variables: {settings.missing_env_vars}")
        print("Please check your .env file")
    
    # Start the server
    print(f"Starting {settings.APP_NAME} server...")
    uvicorn.run(
        "app:create_app",
        factory=True,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )


# Run the application
if __name__ == "__main__":
    main()
