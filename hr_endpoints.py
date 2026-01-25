"""
HR Job Posting API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
from db_simple import db
import logging

logger = logging.getLogger(__name__)

from job_schemas import (
    JobPostRequest, JobPostResponse, JobListing, JobUpdateRequest, 
    JobSearchFilters, JobSearchResponse, HRJobDashboard, JobApplicationStats,
    HRJobSearchResponse
)
from job_application_schemas import JobApplicationsResponse, ApplicationStatus
from job_db import job_db
from job_application_db import JobApplicationDatabase

# Initialize job application database
job_application_db = JobApplicationDatabase()
from auth_utils import verify_token
from auth_db import get_user_by_id

# Create router
hr_router = APIRouter(prefix="/hr", tags=["HR Job Management"])
security = HTTPBearer()

# Dependency to get current HR user
async def get_current_hr_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated HR user"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user has HR role
        user_type = user.get("user_type", "job_seeker")
        if user_type not in ["hire", "hr", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. HR privileges required."
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@hr_router.post("/jobs", response_model=JobPostResponse)
async def post_job(
    job_data: JobPostRequest,
    current_user: dict = Depends(get_current_hr_user)
):
    """Post a new job listing"""
    try:
        hr_user_id = current_user["user_id"]
        
        logger.info(f"HR user {hr_user_id} attempting to post job: {job_data.title}")
        
        # Create job posting
        job_id = await job_db.create_job_posting(job_data, hr_user_id)
        
        logger.info(f"Job posted successfully with ID: {job_id}")
        
        return JobPostResponse(
            message="Job posted successfully",
            job_id=job_id,
            job_url=f"/api/v1/jobs/{job_id}",
            created_at=datetime.utcnow()
        )
        
    except ValueError as e:
        logger.error(f"Validation error while posting job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error posting job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to post job: {str(e)}"
        )


@hr_router.get("/jobs", response_model=HRJobSearchResponse)
async def get_my_jobs(
    page: int = 1,
    per_page: int = 10,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get all jobs posted by the current HR user"""
    try:
        hr_user_id = current_user["user_id"]
        result = await job_db.get_jobs_by_hr(hr_user_id, page, per_page)
        
        return HRJobSearchResponse(
            jobs=result["jobs"],
            total_count=result["total_count"],
            page=result["page"],
            per_page=result["per_page"],
            total_pages=result.get("total_pages"),
            has_next=result.get("has_next"),
            has_prev=result.get("has_prev")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve jobs: {str(e)}"
        )


@hr_router.get("/jobs-with-applications")
async def get_jobs_with_applications(
    current_user: dict = Depends(get_current_hr_user)
):
    """Get all jobs posted by HR with application counts"""
    try:
        hr_email = current_user["email"]
        jobs = await job_application_db.get_hr_jobs_with_applications(hr_email)
        
        return {
            "jobs": jobs,
            "total_count": len(jobs)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve jobs with applications: {str(e)}"
        )


@hr_router.get("/jobs/{job_id}")
async def get_job_details(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get specific job details (only jobs posted by this HR)"""
    try:
        job = await job_db.get_job_by_id(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check if this HR posted the job
        if job["posted_by_hr_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only view jobs you posted."
            )
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job: {str(e)}"
        )


@hr_router.put("/jobs/{job_id}")
async def update_job(
    job_id: str,
    update_data: JobUpdateRequest,
    current_user: dict = Depends(get_current_hr_user)
):
    """Update job posting"""
    try:
        hr_user_id = current_user["user_id"]
        
        # Convert update data to dict, excluding None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        success = await job_db.update_job(job_id, update_dict, hr_user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found or you don't have permission to update it"
            )
        
        return {"message": "Job updated successfully", "job_id": job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}"
        )


@hr_router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Delete (deactivate) job posting"""
    try:
        hr_user_id = current_user["user_id"]
        success = await job_db.delete_job(job_id, hr_user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found or you don't have permission to delete it"
            )
        
        return {"message": "Job deleted successfully", "job_id": job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        )


@hr_router.get("/dashboard", response_model=HRJobDashboard)
async def get_hr_dashboard(
    current_user: dict = Depends(get_current_hr_user)
):
    """Get HR dashboard with job statistics"""
    try:
        hr_user_id = current_user["user_id"]
        dashboard = await job_db.get_hr_dashboard(hr_user_id)
        return dashboard
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard: {str(e)}"
        )


@hr_router.post("/jobs/{job_id}/toggle-status")
async def toggle_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Toggle job active/inactive status"""
    try:
        hr_user_id = current_user["user_id"]
        
        # Get current job
        job = await job_db.get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        if job["posted_by_hr_id"] != hr_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Toggle status
        new_status = not job.get("is_active", True)
        success = await job_db.update_job(job_id, {"is_active": new_status}, hr_user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update job status"
            )
        
        return {
            "message": f"Job {'activated' if new_status else 'deactivated'} successfully",
            "job_id": job_id,
            "is_active": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle job status: {str(e)}"
        )


@hr_router.get("/jobs/{job_id}/stats")
async def get_job_stats(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get statistics for a specific job"""
    try:
        hr_user_id = current_user["user_id"]
        
        job = await job_db.get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        if job["posted_by_hr_id"] != hr_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return {
            "job_id": job_id,
            "job_title": job["title"],
            "views_count": job.get("views_count", 0),
            "applications_count": job.get("applications_count", 0),
            "posted_date": job["posted_date"],
            "is_active": job.get("is_active", True),
            "days_since_posted": (datetime.utcnow() - job["posted_date"]).days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job stats: {str(e)}"
        )


@hr_router.get("/applications")
async def get_all_applications(
    job_id: Optional[str] = None,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get all applications for HR user's jobs or specific job"""
    try:
        hr_user_id = current_user["user_id"]
        
        # Get HR jobs
        if job_id:
            jobs = await db.database["jobs"].find({"job_id": job_id, "posted_by_hr_id": hr_user_id}).to_list(None)
        else:
            jobs = await db.database["jobs"].find({"posted_by_hr_id": hr_user_id}).to_list(None)
        
        all_applications = []
        
        for job in jobs:
            applications_received = job.get("applications_received", [])
            for app in applications_received:
                # Get full application details from applications collection
                full_app = await db.database["applications"].find_one({"application_id": app["application_id"]})
                
                if full_app:
                    logger.info(f"Full app data: resume_tailored={full_app.get('resume_tailored')}, has_resume_data={bool(full_app.get('resume_data'))}")
                    
                    # Use tailored resume data if available, otherwise get user data
                    if full_app.get("resume_tailored") and full_app.get("resume_data"):
                        resume_data = full_app["resume_data"]
                        skills = resume_data.get("skills_organized", resume_data.get("skills", []))
                        professional_summary = resume_data.get("professional_summary", "")
                        experience_years = resume_data.get("overall_experience_years", resume_data.get("experience_years", 0))
                        current_role = resume_data.get("current_role", "")
                        highest_qualification = resume_data.get("highest_qualification", "")
                        phone = resume_data.get("phone", "")
                        logger.info(f"Using tailored data: skills={skills[:2] if skills else []}, summary_len={len(professional_summary)}")
                    else:
                        # Get user's original data
                        user = await db.database["users"].find_one({"user_id": app["user_id"]})
                        if not user:
                            continue
                        skills = user.get("skills", [])
                        professional_summary = user.get("professional_summary", "")
                        experience_years = user.get("overall_experience_years", 0)
                        current_role = user.get("current_role", "")
                        highest_qualification = user.get("highest_qualification", "")
                        phone = user.get("phone", "")
                        logger.info(f"Using original user data")
                    
                    application_data = {
                        "application_id": app["application_id"],
                        "job_id": job["job_id"],
                        "job_title": job["title"],
                        "user_id": app["user_id"],
                        "full_name": full_app.get("candidate_name", ""),
                        "experience_years": experience_years,
                        "current_role": current_role,
                        "applied_date": app.get("applied_date", app.get("applied_at", "")),
                        "resume_tailored": full_app.get("resume_tailored", False),
                        "match_score": full_app.get("match_score"),
                        "match_percentage": app.get("match_percentage", 0),
                        "ats_score": app.get("ats_score", 0),
                        "email": full_app.get("candidate_email", ""),
                        "phone": phone,
                        "skills": skills,
                        "professional_summary": professional_summary,
                        "highest_qualification": highest_qualification
                    }
                    all_applications.append(application_data)
        
        return {
            "applications": all_applications,
            "total_count": len(all_applications)
        }
        
    except Exception as e:
        logger.error(f"Error in get_all_applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve applications: {str(e)}"
        )


@hr_router.get("/jobs/{job_id}/applications", response_model=JobApplicationsResponse)
async def get_job_applications(
    job_id: str,
    current_user: dict = Depends(get_current_hr_user)
):
    """Get all applications for a specific job"""
    try:
        hr_user_id = current_user["user_id"]
        applications = await job_application_db.get_job_applications(job_id, hr_user_id)
        return applications
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve applications: {str(e)}"
        )


@hr_router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    status: ApplicationStatus,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_hr_user)
):
    """Update application status"""
    try:
        hr_user_id = current_user["user_id"]
        success = await job_application_db.update_application_status(
            application_id, status, hr_user_id, notes
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found or access denied"
            )
        
        return {"message": "Application status updated successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application status: {str(e)}"
        )
