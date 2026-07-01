"""
FastAPI application factory and configuration.
"""

from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import logging.handlers
import sys
import os

from config import settings

# ── Centralized Logging Setup ────────────────────────────────
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

# Root logger configuration (applies to all modules)
_root = logging.getLogger()
_root.setLevel(_LOG_LEVEL)

# Console handler
_console = logging.StreamHandler(sys.stdout)
_console.setFormatter(logging.Formatter(_LOG_FORMAT))
_root.addHandler(_console)

# File handler with rotation (logs/ directory)
_log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(_log_dir, exist_ok=True)
_file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(_log_dir, "app.log"),
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5,
    encoding="utf-8",
)
_file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
_root.addHandler(_file_handler)

# Suppress noisy third-party loggers in production
if settings.APP_ENV != "local":
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

from db import db
from dashboard_endpoints import router as dashboard_router
from api_routes import router as api_router
from auth_endpoints import auth_router
from hr_endpoints import hr_router
from job_application_endpoints import application_router
from apply_endpoints import apply_router
from match_analysis_endpoints import match_router
from resume_endpoints import resume_router
from skill_assessment_endpoints import router as skill_assessment_router
from feature_usage_endpoints import router as feature_usage_router
from google_auth_endpoints import router as google_auth_router
from interview_prompts_endpoints import router as interview_prompts_router
from multi_agent_endpoints import router as multi_agent_router
from interview_evaluation_endpoint import router as interview_evaluation_router
from resume_tailor_endpoints import router as resume_tailor_router
from credits_endpoints import router as credits_router
from upload_endpoints import router as upload_router
from prompt_endpoints import router as prompt_router
from cv_bootstrap_endpoints import router as cv_bootstrap_router
from professional_summary_endpoints import router as professional_summary_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting JobMitra Backend API...")
    try:
        await db.connect_to_mongo()
        logger.info("Database connection established (fallback=%s)", db.fallback_mode)
        # Ensure indexes exist for optimal query performance
        if not db.fallback_mode:
            from db_indexes import ensure_indexes
            await ensure_indexes(db.database)
    except Exception as e:
        logger.error("Failed to connect to database: %s", e)

    # Initialize Redis cache
    try:
        from cache import cache
        await cache.connect()
    except Exception as e:
        logger.warning("Redis cache unavailable: %s", e)

    # Run immediate sweep on startup, then start periodic background loop
    from job_expiry_scheduler import start_expiry_scheduler
    if not db.fallback_mode:
        from job_expiry_scheduler import expire_stale_jobs
        archived = await expire_stale_jobs()
        if archived:
            logger.info("Startup sweep: archived %d stale job(s)", archived)
    start_expiry_scheduler()

    yield

    # Shutdown
    logger.info("Shutting down JobMitra Backend API...")
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

    # Add GZip compression for responses > 1KB
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add rate limiting middleware
    from rate_limiter import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

    # Add request ID for tracing
    from request_id_middleware import RequestIDMiddleware
    app.add_middleware(RequestIDMiddleware)

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
        
        logger.warning("Validation failed for %s: %d errors", request.url.path, len(errors))
        
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
    app.include_router(dashboard_router, prefix="/api/v1")  # Dashboard and profile endpoints
    app.include_router(api_router, prefix="/api/v1")  # Additional API routes
    app.include_router(auth_router, prefix="/api/v1")  # Authentication routes
    app.include_router(hr_router, prefix="/api/v1")  # HR job management routes (database-connected)
    app.include_router(application_router, prefix="/api/v1")  # Job application routes
    app.include_router(apply_router, prefix="")  # Apply for job routes (includes /api/v1 prefix)
    app.include_router(match_router, prefix="")  # Match analysis routes (includes /api/v1 prefix)
    app.include_router(resume_router, prefix="")  # Resume builder routes
    app.include_router(skill_assessment_router, prefix="")  # Skill assessment routes
    app.include_router(feature_usage_router, prefix="")  # Feature usage tracking routes
    app.include_router(google_auth_router, prefix="/api/v1/auth")  # Google authentication routes
    app.include_router(interview_prompts_router, prefix="/api/v1")  # Interview prompts routes
    app.include_router(multi_agent_router, prefix="/api/v1")  # Multi-Agent Interview routes
    app.include_router(interview_evaluation_router, prefix="/api/v1/mock-interview")  # Interview evaluation routes
    app.include_router(resume_tailor_router)  # Resume tailor routes (already has /api/v1 prefix)
    app.include_router(credits_router)  # Credits & payments routes
    app.include_router(upload_router)  # File upload routes

    # Serve uploaded files
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
    app.include_router(prompt_router)  # Prompt management routes
    app.include_router(cv_bootstrap_router)  # CV bootstrap for new users
    app.include_router(professional_summary_router, prefix="/api/v1")  # Professional summary generation

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
