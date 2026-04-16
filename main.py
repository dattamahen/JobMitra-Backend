"""
FastAPI main application entry point for JobMitra Backend.
"""

# config.py handles environment loading based on APP_ENV
import logging
import uvicorn

from config import settings
from app import create_app

logger = logging.getLogger(__name__)

# Create the app instance for uvicorn
app = create_app()

def main():
    """
    Main entry point for the application.
    """
    if settings.missing_env_vars:
        logger.warning("Missing environment variables: %s", settings.missing_env_vars)

    logger.info("Starting %s server on %s:%s", settings.APP_NAME, settings.HOST, settings.PORT)
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )


# Run the application
if __name__ == "__main__":
    main()
