"""
Unified Apply for Job endpoint.
Single entry point for all apply flows (direct + tailored).
Stores in: users.overall_jobs_applied[] + jobs.applications_received[]
No separate applications collection.
"""

import logging
logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import random

from db import db
from auth_endpoints import get_current_user
from job_db import job_db
from activity_tracker import log_user_activity
from schemas import JobApplicationRecord

apply_router = APIRouter(prefix="/api/v1", tags=["Job Applications"])


class ApplyJobRequest(BaseModel):
    job_id: str
    force_apply: bool = False
    use_tailored: bool = False


class ApplyJobResponse(BaseModel):
    message: str
    success: bool
    show_match_prompt: bool = False
    match_percentage: Optional[int] = None
    application_id: Optional[str] = None


class ApplicationsResponse(BaseModel):
    applications: List[dict]
    total_count: int
    page: int
    per_page: int
    total_pages: int


class UserAppliedJobsResponse(BaseModel):
    applied_jobs: list
    total_count: int


@apply_router.post("/apply-job", response_model=ApplyJobResponse)
async def apply_for_job(
    request: ApplyJobRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Unified apply endpoint.
    - Direct apply: { job_id, force_apply: true }
    - Tailored apply: { job_id, force_apply: true, use_tailored: true }
    - First click (show prompt): { job_id } → returns show_match_prompt: true
    """
    try:
        user_id = current_user["user_id"]
        job_id = request.job_id

        # Check if job exists and is still active
        job = await job_db.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.get("status") in ("expired", "closed", "filled") or not job.get("is_active", True):
            raise HTTPException(status_code=410, detail="This job is no longer accepting applications")

        # Get user and check for existing application
        user = await db.database["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        applied_jobs_records = user.get("overall_jobs_applied", [])
        existing_index = -1
        existing_record = None
        for i, app in enumerate(applied_jobs_records):
            # Handle both dict records and legacy string entries
            if isinstance(app, dict) and app.get("job_id") == job_id:
                if app.get("is_applied", False):
                    raise HTTPException(status_code=400, detail="You have already applied for this job")
                existing_index = i
                existing_record = app
                break
            elif isinstance(app, str) and app == job_id:
                raise HTTPException(status_code=400, detail="You have already applied for this job")

        # First click — show confirmation prompt
        if not request.force_apply:
            return ApplyJobResponse(
                message="Apply without matching your CV with actual job description?",
                success=False,
                show_match_prompt=True
            )

        # Determine match percentage
        match_percentage = None
        if existing_record and existing_record.get("match_percentage"):
            match_percentage = existing_record["match_percentage"]
        else:
            match_percentage = random.randint(20, 59)

        application_id = f"{user_id}_{job_id}"

        # --- Write 1: users.overall_jobs_applied[] ---
        if existing_record:
            existing_record["status"] = "applied"
            existing_record["is_applied"] = True
            existing_record["match_analysis_done"] = True
            existing_record["tailor_resume_done"] = existing_record.get("tailor_resume_done", False) or request.use_tailored
            existing_record["match_percentage"] = match_percentage
            existing_record["last_updated"] = datetime.utcnow()
            await db.database["users"].update_one(
                {"user_id": user_id},
                {"$set": {f"overall_jobs_applied.{existing_index}": existing_record}}
            )
        else:
            new_record = JobApplicationRecord(
                job_id=job_id,
                application_id=application_id,
                status="applied",
                match_analysis_done=True,
                match_percentage=match_percentage,
                tailor_resume_done=request.use_tailored,
                is_applied=True
            )
            await db.database["users"].update_one(
                {"user_id": user_id},
                {"$push": {"overall_jobs_applied": new_record.dict()}}
            )

        # --- Write 2: jobs.applications_received[] ---
        await db.database["jobs"].update_one(
            {"job_id": job_id},
            {"$addToSet": {
                "applications_received": {
                    "user_id": user_id,
                    "application_id": application_id,
                    "user_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                    "user_email": user.get('email', ''),
                    "applied_date": datetime.utcnow(),
                    "match_percentage": match_percentage,
                    "status": "applied",
                    "resume_tailored": request.use_tailored
                }
            }}
        )

        # Log activity
        await log_user_activity(
            user_id,
            "job_application",
            f"Applied for {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}",
            {"job_id": job_id, "company": job.get('company'), "position": job.get('title'), "tailored": request.use_tailored}
        )

        message = "Applied with tailored resume" if request.use_tailored else "Successfully applied for the job"

        return ApplyJobResponse(
            message=message,
            success=True,
            application_id=application_id,
            match_percentage=match_percentage
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to apply for job: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to apply: {str(e)}")


@apply_router.get("/applications", response_model=ApplicationsResponse)
async def get_applications(
    page: int = 1,
    per_page: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get user's job applications from users.overall_jobs_applied"""
    try:
        user_id = current_user["user_id"]
        user = await db.database["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Only show actually applied records
        all_records = [
            app for app in user.get("overall_jobs_applied", [])
            if isinstance(app, dict) and app.get("is_applied", False) and app.get("job_id")
        ]

        if not all_records:
            return ApplicationsResponse(applications=[], total_count=0, page=page, per_page=per_page, total_pages=0)

        # Filter to only jobs still in the jobs collection (archived ones are gone)
        all_job_ids = [app["job_id"] for app in all_records]
        existing_job_ids = set()
        async for job in db.database["jobs"].find({"job_id": {"$in": all_job_ids}}, {"job_id": 1}):
            existing_job_ids.add(job["job_id"])
        all_records = [app for app in all_records if app["job_id"] in existing_job_ids]

        total_count = len(all_records)

        if not all_records:
            return ApplicationsResponse(applications=[], total_count=0, page=page, per_page=per_page, total_pages=0)

        # Paginate
        start = (page - 1) * per_page
        paginated = all_records[start:start + per_page]
        job_ids = [app.get("job_id") for app in paginated]

        # Fetch job details (archived jobs won't exist, so missing = archived)
        jobs_cursor = db.database["jobs"].find({"job_id": {"$in": job_ids}})
        jobs_map = {}
        async for job in jobs_cursor:
            job["_id"] = str(job["_id"])
            jobs_map[job.get("job_id")] = job

        applications = []
        for app_record in paginated:
            job = jobs_map.get(app_record.get("job_id"))
            if not job:
                continue
            job.update({
                "application_id": app_record.get("application_id"),
                "status": app_record.get("status", "applied"),
                "applied_date": app_record.get("applied_date"),
                "last_updated": app_record.get("last_updated"),
                "match_percentage": app_record.get("match_percentage"),
                "tailor_resume_done": app_record.get("tailor_resume_done", False)
            })
            applications.append(job)

        return ApplicationsResponse(
            applications=applications,
            total_count=total_count,
            page=page,
            per_page=per_page,
            total_pages=(total_count + per_page - 1) // per_page
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get applications: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@apply_router.get("/users/{user_id}/applied-jobs", response_model=UserAppliedJobsResponse)
async def get_user_applied_jobs(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all jobs applied by a user"""
    try:
        if current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        user = await db.database["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        applied_records = [
            app for app in user.get("overall_jobs_applied", [])
            if isinstance(app, dict) and app.get("is_applied", False)
        ]

        if not applied_records:
            return UserAppliedJobsResponse(applied_jobs=[], total_count=0)

        job_ids = [app.get("job_id") for app in applied_records]
        jobs_cursor = db.database["jobs"].find({"job_id": {"$in": job_ids}})
        applied_jobs = []

        async for job in jobs_cursor:
            job["_id"] = str(job["_id"])
            app_record = next((a for a in applied_records if a.get("job_id") == job.get("job_id")), None)
            if app_record:
                job.update({
                    "application_id": app_record.get("application_id"),
                    "status": app_record.get("status", "applied"),
                    "applied_date": app_record.get("applied_date"),
                    "last_updated": app_record.get("last_updated"),
                    "match_percentage": app_record.get("match_percentage")
                })
            applied_jobs.append(job)

        return UserAppliedJobsResponse(applied_jobs=applied_jobs, total_count=len(applied_jobs))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get applied jobs: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
