"""
Optimized FastAPI application for 10K+ daily users
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config import settings
from cache import cache
from db_optimized import db_manager
from rate_limiter import RateLimitMiddleware
from auth_endpoints import auth_router
from api_routes_optimized import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting JobMitra Backend...")
    
    # Initialize connections
    await cache.connect()
    await db_manager.connect()
    
    logger.info("All services initialized successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down JobMitra Backend...")

# Create FastAPI app with optimized settings
app = FastAPI(
    title="JobMitra Backend API",
    description="High-performance job search and career development API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.LOG_LEVEL == "DEBUG" else None,
    redoc_url="/redoc" if settings.LOG_LEVEL == "DEBUG" else None
)

# Add middleware for performance and security
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "Please try again later"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for load balancer"""
    try:
        # Quick health checks
        redis_status = "ok" if cache.redis_client else "error"
        mongo_status = "ok" if db_manager.client else "error"
        
        return {
            "status": "healthy",
            "services": {
                "redis": redis_status,
                "mongodb": mongo_status
            },
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

# Include routers
app.include_router(auth_router)
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "JobMitra Backend API v2.0",
        "status": "running",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_optimized:app",
        host="0.0.0.0",
        port=8000,
        workers=settings.MAX_WORKERS,
        loop="uvloop",
        http="httptools",
        access_log=False,
        keep_alive_timeout=settings.KEEP_ALIVE_TIMEOUT
    )