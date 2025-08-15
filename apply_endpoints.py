"""
Apply for job endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import random

from db_simple import db
from auth_utils import verify_token
from auth_db import get_user_by_id
from job_db import job_db
from activity_tracker import log_user_activity
from schemas import JobApplicationRecord

# Create router
apply_router = APIRouter(prefix="/api/v1", tags=["Job Applications"])
security = HTTPBearer()

class ApplyJobRequest(BaseModel):
    job_id: str
    force_apply: bool = False  # Skip match analysis prompt

class ApplyJobResponse(BaseModel):
    message: str
    success: bool
    show_match_prompt: bool = False
    match_percentage: Optional[int] = None

class UserAppliedJobsResponse(BaseModel):
    applied_jobs: list
    total_count: int

class ApplicationsResponse(BaseModel):
    applications: List[dict]
    total_count: int
    page: int
    per_page: int
    total_pages: int

# Dependency to get current authenticated user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = await get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@apply_router.post("/apply-job", response_model=ApplyJobResponse)
async def apply_for_job(
    request: ApplyJobRequest,
    current_user: dict = Depends(get_current_user)
):
    """Apply for a job"""
    try:
        user_id = current_user["user_id"]  # Use authenticated user's ID
        job_id = request.job_id
        
        # Check if job exists
        job = await job_db.get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check user's overall_jobs_applied for existing application with is_applied=True
        user = await get_user_by_id(user_id)
        if user:
            applied_jobs_records = user.get("overall_jobs_applied", [])
            for app in applied_jobs_records:
                if isinstance(app, dict) and app.get("job_id") == job_id and app.get("is_applied", False):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="You have already applied for this job"
                    )
        
        # Add user to job's applications_count array (skip this step for now)
        # The job applications are tracked in user's overall_jobs_applied
        
        # Check if user wants to skip match analysis prompt
        if not request.force_apply:
            # Show apply confirmation modal
            return ApplyJobResponse(
                message="Apply without matching your CV with actual job description?",
                success=False,
                show_match_prompt=True
            )
        
        # Generate dummy match analysis report (20-59%)
        dummy_match_percentage = random.randint(20, 59)
        
        # Create application record with is_applied=True and disabled states
        application_record = JobApplicationRecord(
            job_id=job_id,
            application_id=f"{user_id}_{job_id}",
            status="applied",
            match_analysis_done=True,  # Disabled forever
            match_percentage=dummy_match_percentage,
            tailor_resume_done=True,  # Disabled forever
            is_applied=True
        )
        
        # Add application record to user's overall_jobs_applied array
        result = await db.database["users"].update_one(
            {"user_id": user_id},
            {"$push": {"overall_jobs_applied": application_record.dict()}}
        )
        
        # Get user details for applications_received
        user_details = await db.database["users"].find_one({"user_id": user_id})
        
        # Add user to job's applications_received with dummy match report and user details
        await db.database["jobs"].update_one(
            {"job_id": job_id},
            {"$addToSet": {
                "applications_received": {
                    "user_id": user_id,
                    "user_name": f"{user_details.get('first_name', '')} {user_details.get('last_name', '')}".strip(),
                    "user_email": user_details.get('email', ''),
                    "applied_date": datetime.utcnow(),
                    "match_percentage": dummy_match_percentage,
                    "ats_score": dummy_match_percentage,
                    "status": "applied",
                    "match_analysis_details": {
                        "skills_matched": random.randint(3, 8),
                        "experience_match": "Partial",
                        "qualification_match": "Good",
                        "overall_fit": "Average"
                    }
                }
            }}
        )
        
        # Log activity
        await log_user_activity(
            user_id, 
            "job_application", 
            f"Applied for {job.get('title', 'Unknown Position')} at {job.get('company', 'Unknown Company')}",
            {"job_id": job_id, "company": job.get('company'), "position": job.get('title')}
        )
        
        return ApplyJobResponse(
            message="Successfully applied for the job",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply for job: {str(e)}"
        )

@apply_router.get("/applications", response_model=ApplicationsResponse)
async def get_applications(
    page: int = 1,
    per_page: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get user's job applications with pagination"""
    try:
        user_id = current_user["user_id"]
        
        # Get user's applied job IDs
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        applied_jobs_records = user.get("overall_jobs_applied", [])
        total_count = len(applied_jobs_records)
        
        if not applied_jobs_records:
            return ApplicationsResponse(
                applications=[],
                total_count=0,
                page=page,
                per_page=per_page,
                total_pages=0
            )
        
        # Apply pagination to application records
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_records = applied_jobs_records[start_idx:end_idx]
        
        # Get job IDs from paginated records
        paginated_job_ids = [app.get("job_id") for app in paginated_records]
        
        # Get job details for paginated applied jobs
        jobs_cursor = db.database["jobs"].find({"job_id": {"$in": paginated_job_ids}})
        applications = []
        
        async for job in jobs_cursor:
            if "_id" in job:
                job["_id"] = str(job["_id"])
            
            # Find corresponding application record
            app_record = next((app for app in paginated_records if app.get("job_id") == job.get("job_id")), None)
            if app_record:
                # Merge job and application data
                job.update({
                    "application_id": app_record.get("application_id"),
                    "status": app_record.get("status", "applied"),
                    "applied_date": app_record.get("applied_date"),
                    "last_updated": app_record.get("last_updated"),
                    "notes": app_record.get("notes")
                })
            applications.append(job)
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return ApplicationsResponse(
            applications=applications,
            total_count=total_count,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get applications: {str(e)}"
        )

@apply_router.get("/users/{user_id}/applied-jobs", response_model=UserAppliedJobsResponse)
async def get_user_applied_jobs(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all jobs applied by a user"""
    try:
        # Verify the authenticated user matches the request user_id
        if current_user["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access another user's applied jobs"
            )
        
        # Get user's applied job IDs
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        applied_jobs_records = user.get("overall_jobs_applied", [])
        
        if not applied_jobs_records:
            return UserAppliedJobsResponse(
                applied_jobs=[],
                total_count=0
            )
        
        # Get job IDs from application records
        applied_job_ids = [app.get("job_id") for app in applied_jobs_records]
        
        # Get job details for applied jobs
        jobs_cursor = db.database["jobs"].find({"job_id": {"$in": applied_job_ids}})
        applied_jobs = []
        
        async for job in jobs_cursor:
            # Convert ObjectId to string for JSON serialization
            if "_id" in job:
                job["_id"] = str(job["_id"])
            
            # Find corresponding application record
            app_record = next((app for app in applied_jobs_records if app.get("job_id") == job.get("job_id")), None)
            if app_record:
                # Merge job and application data
                job.update({
                    "application_id": app_record.get("application_id"),
                    "status": app_record.get("status", "applied"),
                    "applied_date": app_record.get("applied_date"),
                    "last_updated": app_record.get("last_updated"),
                    "notes": app_record.get("notes")
                })
            applied_jobs.append(job)
        
        return UserAppliedJobsResponse(
            applied_jobs=applied_jobs,
            total_count=len(applied_jobs)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get applied jobs: {str(e)}"
        )