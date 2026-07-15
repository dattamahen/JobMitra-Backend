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

    run_kwargs = {
        "app": "main:app",
        "host": settings.HOST,
        "port": settings.PORT,
        "log_level": settings.LOG_LEVEL,
    }

    if settings.APP_ENV == "local":
        run_kwargs["reload"] = True
    else:
        run_kwargs["workers"] = settings.MAX_WORKERS
        run_kwargs["access_log"] = False
        run_kwargs["keep_alive_timeout"] = settings.KEEP_ALIVE_TIMEOUT

    uvicorn.run(**run_kwargs)


# Run the application
if __name__ == "__main__":
    main()
