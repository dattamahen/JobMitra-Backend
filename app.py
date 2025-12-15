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
from auth_endpoints import auth_router
from hr_endpoints import hr_router
from hr_test_endpoints import test_hr_router
from job_application_endpoints import application_router
from apply_endpoints import apply_router
from match_analysis_endpoints import match_router
from resume_endpoints import resume_router
from skill_assessment_endpoints import router as skill_assessment_router
from mock_interview_api import router as mock_interview_router
from feature_usage_endpoints import router as feature_usage_router
from google_auth_endpoints import router as google_auth_router
from interview_prompts_endpoints import router as interview_prompts_router
from simple_ai_endpoints import router as simple_ai_router
from multi_agent_endpoints import router as multi_agent_router
from interview_evaluation_endpoint import router as interview_evaluation_router


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
        print(f"Database object: {db.database}")
        print(f"Fallback mode: {db.fallback_mode}")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        print(f"Database object after error: {db.database}")
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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers with prefixes
    app.include_router(core_router, prefix="")  # Core endpoints (ask, resume-enhance, logs)
    app.include_router(dashboard_router, prefix="/api/v1")  # Dashboard and profile endpoints
    app.include_router(api_router, prefix="/api/v1")  # Additional API routes
    app.include_router(auth_router, prefix="/api/v1")  # Authentication routes
    app.include_router(hr_router, prefix="/api/v1")  # HR job management routes (database-connected)
    app.include_router(application_router, prefix="/api/v1")  # Job application routes
    app.include_router(apply_router, prefix="")  # Apply for job routes (includes /api/v1 prefix)
    app.include_router(match_router, prefix="")  # Match analysis routes (includes /api/v1 prefix)
    app.include_router(resume_router, prefix="")  # Resume builder routes
    app.include_router(skill_assessment_router, prefix="")  # Skill assessment routes
    app.include_router(mock_interview_router, prefix="")  # Mock interview routes
    app.include_router(feature_usage_router, prefix="")  # Feature usage tracking routes
    app.include_router(google_auth_router, prefix="/api/v1/auth")  # Google authentication routes
    app.include_router(interview_prompts_router, prefix="/api/v1")  # Interview prompts routes
    app.include_router(simple_ai_router, prefix="/api/v1")  # AI Interview routes
    app.include_router(multi_agent_router, prefix="/api/v1")  # Multi-Agent Interview routes
    app.include_router(interview_evaluation_router, prefix="/api/v1/mock-interview")  # Interview evaluation routes

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
