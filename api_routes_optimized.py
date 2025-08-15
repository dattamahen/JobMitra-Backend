"""
Optimized API routes with caching and performance improvements
"""
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional
from datetime import datetime

from auth_endpoints import get_current_user
from db_optimized import db_manager
from cache import cache
from schemas import JobSearchRequest, JobApplicationCreate
import logging

logger = logging.getLogger(__name__)
api_router = APIRouter()

@api_router.get("/users/{user_id}")
async def get_user_profile(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user profile with caching"""
    try:
        # Security check
        if current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        user = await db_manager.get_user_cached(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@api_router.put("/users/{user_id}")
async def update_user_profile(
    user_id: str, 
    update_data: dict,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile with background cache invalidation"""
    try:
        # Security check
        if current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        success = await db_manager.update_user_cached(user_id, update_data)
        if not success:
            raise HTTPException(status_code=400, detail="Update failed")
        
        # Background task to warm up cache
        background_tasks.add_task(warm_user_cache, user_id)
        
        return {"message": "Profile updated successfully"}
        
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@api_router.post("/jobs/search")
async def search_jobs(search_request: JobSearchRequest):
    """Optimized job search with caching"""
    try:
        filters = {}
        if search_request.skills:
            filters["skills"] = search_request.skills
        if search_request.location_type:
            filters["location_type"] = search_request.location_type
        if search_request.experience_level:
            filters["experience_level"] = search_request.experience_level
        
        jobs = await db_manager.search_jobs_optimized(
            query=search_request.query or "",
            filters=filters,
            limit=min(search_request.limit, 50)  # Cap at 50 for performance
        )
        
        return {
            "jobs": jobs,
            "count": len(jobs),
            "cached": True
        }
        
    except Exception as e:
        logger.error(f"Job search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@api_router.post("/applications")
async def create_application(
    application_data: JobApplicationCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create job application with optimized performance"""
    try:
        # Use authenticated user ID
        app_dict = application_data.dict()
        app_dict["user_id"] = current_user["user_id"]
        app_dict["application_id"] = f"app_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{current_user['user_id']}"
        app_dict["status"] = "applied"
        
        app_id = await db_manager.create_application_optimized(app_dict)
        if not app_id:
            raise HTTPException(status_code=400, detail="Application failed")
        
        # Background task to update job application count
        background_tasks.add_task(update_job_stats, app_dict["job_id"])
        
        return {"message": "Application submitted successfully", "application_id": app_id}
        
    except Exception as e:
        logger.error(f"Application creation error: {e}")
        raise HTTPException(status_code=500, detail="Application failed")

@api_router.get("/users/{user_id}/applications")
async def get_user_applications(
    user_id: str,
    limit: int = Query(20, le=50),
    current_user: dict = Depends(get_current_user)
):
    """Get user applications with caching"""
    try:
        # Security check
        if current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        applications = await db_manager.get_user_applications_cached(user_id, limit)
        
        return {
            "applications": applications,
            "count": len(applications)
        }
        
    except Exception as e:
        logger.error(f"Get applications error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get applications")

@api_router.get("/users/{user_id}/dashboard")
async def get_dashboard(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard data with aggressive caching"""
    try:
        # Security check
        if current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        dashboard_data = await db_manager.get_dashboard_data_cached(user_id)
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard")

@api_router.get("/analytics/summary")
async def get_analytics():
    """System analytics with caching"""
    try:
        cache_key = "analytics:summary"
        
        # Try cache first
        cached_analytics = await cache.get(cache_key)
        if cached_analytics:
            return cached_analytics
        
        # Calculate analytics (simplified for performance)
        analytics = {
            "active_users_today": await db_manager.db.users.count_documents({
                "last_active": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
            }),
            "total_jobs": await db_manager.db.jobs.estimated_document_count(),
            "applications_today": await db_manager.db.applications.count_documents({
                "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
            }),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Cache for 15 minutes
        await cache.set(cache_key, analytics, 900)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail="Analytics unavailable")

# Background tasks
async def warm_user_cache(user_id: str):
    """Warm up user-related cache after updates"""
    try:
        await db_manager.get_user_cached(user_id)
        await db_manager.get_dashboard_data_cached(user_id)
        logger.info(f"Cache warmed for user {user_id}")
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")

async def update_job_stats(job_id: str):
    """Update job application statistics"""
    try:
        await db_manager.db.jobs.update_one(
            {"job_id": job_id},
            {"$inc": {"applications_count": 1}}
        )
    except Exception as e:
        logger.error(f"Job stats update failed: {e}")