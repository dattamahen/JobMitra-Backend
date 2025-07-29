"""
FastAPI application factory and configuration.
"""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from db_simple import db
from endpoints import router as core_router
from dashboard_endpoints import router as dashboard_router
from api_routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup: Initialize database connection
    print("Starting JobMitra Backend API...")
    
    try:
        await db.connect_to_mongo()
        print("Database connection established successfully")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        # You might want to exit here in production
        
    yield
    
    # Shutdown: Close database connection
    print("Shutting down JobMitra Backend API...")
    await db.close_mongo_connection()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    
    # Initialize FastAPI application with metadata
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )

    # Include routers with prefixes
    app.include_router(core_router, prefix="")  # Core endpoints (ask, resume-enhance, logs)
    app.include_router(dashboard_router, prefix="/api/v1")  # Dashboard and profile endpoints
    app.include_router(api_router, prefix="/api/v1")  # Additional API routes

    # Health check endpoint
    @app.get("/", tags=["Health"])
    async def root():
        """
        Root endpoint for health checking.
        
        Returns:
            dict: API status and information
        """
        return {
            "message": f"{settings.APP_NAME} is running",
            "version": settings.VERSION,
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "cors_enabled": True
        }

    # CORS test endpoint
    @app.get("/cors-test", tags=["Health"])
    async def cors_test():
        """
        Simple endpoint to test CORS configuration.
        """
        return {
            "message": "CORS is working!",
            "timestamp": datetime.utcnow(),
            "access_from": "Angular frontend should be able to access this"
        }

    return app
