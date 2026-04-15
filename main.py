"""
FastAPI main application entry point for JobMitra Backend.
"""

# config.py handles environment loading based on APP_ENV
import uvicorn

from config import settings
from app import create_app
from db_simple import db

# Create the app instance for uvicorn
app = create_app()

@app.on_event("startup")
async def startup_event():
    """Connect to database on startup"""
    print("Connecting to database...")
    await db.connect_to_mongo()
    print(f"Database connected: {db.database is not None}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await db.close_mongo_connection()

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
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL
    )


# Run the application
if __name__ == "__main__":
    main()
