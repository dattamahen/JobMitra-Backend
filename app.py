"""
FastAPI application factory and configuration.
"""

from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

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
from resume_tailor_endpoints import router as resume_tailor_router


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

    # Global validation error handler
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Global handler for validation errors with detailed field information.
        Provides user-friendly error messages for each validation failure.
        """
        errors = []
        for error in exc.errors():
            # Extract field path (skip 'body' prefix)
            field_path = " -> ".join(str(loc) for loc in error["loc"][1:]) if len(error["loc"]) > 1 else str(error["loc"][0])
            msg = error["msg"]
            error_type = error["type"]
            ctx = error.get("ctx", {})
            
            # Create user-friendly error messages based on validation type
            if "min_length" in error_type:
                limit = ctx.get('limit_value', 'required')
                errors.append({
                    "field": field_path,
                    "message": f"Must be at least {limit} characters long",
                    "type": "min_length",
                    "limit": limit
                })
            elif "max_length" in error_type:
                limit = ctx.get('limit_value', 'allowed')
                errors.append({
                    "field": field_path,
                    "message": f"Must not exceed {limit} characters",
                    "type": "max_length",
                    "limit": limit
                })
            elif "min_items" in error_type or "too_short" in error_type:
                limit = ctx.get('limit_value', ctx.get('min_length', 'required'))
                errors.append({
                    "field": field_path,
                    "message": f"Must have at least {limit} items",
                    "type": "min_items",
                    "limit": limit
                })
            elif "max_items" in error_type or "too_long" in error_type:
                limit = ctx.get('limit_value', ctx.get('max_length', 'allowed'))
                errors.append({
                    "field": field_path,
                    "message": f"Must not exceed {limit} items",
                    "type": "max_items",
                    "limit": limit
                })
            elif "missing" in error_type:
                errors.append({
                    "field": field_path,
                    "message": "This field is required",
                    "type": "required"
                })
            elif "value_error" in error_type:
                errors.append({
                    "field": field_path,
                    "message": msg,
                    "type": "value_error"
                })
            elif "type_error" in error_type:
                expected_type = ctx.get('expected', 'valid value')
                errors.append({
                    "field": field_path,
                    "message": f"Invalid type. Expected {expected_type}",
                    "type": "type_error"
                })
            else:
                errors.append({
                    "field": field_path,
                    "message": msg,
                    "type": error_type
                })
        
        logger.error(f"Validation failed for {request.url.path}: {len(errors)} errors")
        for err in errors:
            logger.error(f"  - {err['field']}: {err['message']}")
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation failed. Please check the errors below.",
                "errors": errors,
                "error_count": len(errors)
            }
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
    app.include_router(resume_tailor_router)  # Resume tailor routes (already has /api/v1 prefix)

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
