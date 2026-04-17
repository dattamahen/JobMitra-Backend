"""
Resume Tailor API endpoints using CrewAI and OpenAI
"""
import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from auth_endpoints import get_current_user
from resume_tailor_agent import run_resume_tailor
from db_simple import db
from api_contracts import (
    TailorPreviewResponse as TailorPreviewContract,
    TailorResumeResponse as TailorResumeContract,
    ApplyJobResponse as ApplyJobContract,
    OriginalResume,
    TailoredResume,
    TailorChange,
    parse_tailor_response,
)
import json
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter(prefix="/api/v1", tags=["Resume Tailor"])

# Request/Response Models (kept for backward compat, contracts are in api_contracts.py)
class TailorPreviewResponse(BaseModel):
    original_resume: Dict[str, Any]
    tailored_resume: Dict[str, Any]
    match_improvement: int
    changes: List[Dict[str, Any]]

class TailorResumeResponse(BaseModel):
    success: bool
    message: str
    tailor_done: bool
    match_percentage: int

class ApplyJobResponse(BaseModel):
    success: bool
    message: str
    application_id: str
    match_percentage: int | None = None

def sanitize_for_json(obj):
    """Recursively convert MongoDB documents to JSON-serializable format"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items() if k != '_id'}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

@router.get("/jobs/{job_id}/tailor-preview")
async def get_tailor_preview(job_id: str, current_user: dict = Depends(get_current_user)) -> TailorPreviewResponse:
    """Get preview of tailored resume changes using AI"""
    logger.debug("\n=== Tailor Preview Request ===")
    logger.debug("Job ID: %s ", job_id)
    logger.debug("Current user type: %s ", type(current_user))
    logger.debug("Current user: %s ", current_user)
    
    # Handle if current_user is a string (user_id only)
    if isinstance(current_user, str):
        user_id = current_user
    else:
        user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)
    
    logger.debug("User ID: %s ", user_id)
    
    try:
        # Fetch job details
        job = await db.database["jobs"].find_one({"job_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Fetch user profile
        user = await db.database["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Build job description from job data
        company = job.get('company', '')
        company_name = company.get('name', '') if isinstance(company, dict) else str(company)
        
        location = job.get('location', {})
        location_city = location.get('city', '') if isinstance(location, dict) else ''
        job_type = job.get('job_type', '')
        
        skills_required = job.get('skills_required', job.get('skills', []))
        skills_preferred = job.get('skills_preferred', [])
        
        job_description = f"""
Job Title: {job.get('title', '')}
Company: {company_name}
Location: {location_city} - {job_type}
Experience Level: {job.get('experience_level', '')}
Employment Type: {job.get('employment_type', '')}

Description:
{job.get('description', '')}

Required Skills:
{', '.join(skills_required)}

Preferred Skills:
{', '.join(skills_preferred)}

Requirements:
{chr(10).join([f"- {req.get('description', '') if isinstance(req, dict) else str(req)}" for req in job.get('requirements', [])])}

Responsibilities:
{chr(10).join([f"- {r.get('description', '') if isinstance(r, dict) else str(r)}" for r in job.get('responsibilities', [])])}
"""
        
        # Prepare original resume data
        original_resume = {
            "first_name": user.get('first_name', ''),
            "last_name": user.get('last_name', ''),
            "email": user.get('email', ''),
            "phone": user.get('phone', ''),
            "professional_summary": user.get('professional_summary', ''),
            "skills": user.get('skills', []),
            "work_experience": user.get('work_experience', []),
            "education": user.get('education', []),
            "projects": user.get('projects', []),
            "certifications": user.get('certifications', [])
        }
        
        # Run AI tailor agent
        logger.info("Running AI resume tailor agent...")
        ai_result = run_resume_tailor(sanitize_for_json(user), job_description)
        
        if "error" in ai_result:
            raise HTTPException(status_code=500, detail=ai_result["error"])
        
        # Parse and normalize AI output using the contract parser
        parsed = parse_tailor_response(json.dumps(ai_result) if isinstance(ai_result, dict) else str(ai_result))
        
        # Store tailored resume in cache for later use
        await db.database["users"].update_one(
            {"user_id": user_id},
            {"$set": {f"tailored_resumes.{job_id}": parsed.get("tailored_resume", {})}}
        )
        
        return TailorPreviewContract(
            original_resume=OriginalResume(**original_resume),
            tailored_resume=TailoredResume(**parsed.get("tailored_resume", {})),
            match_before=parsed.get("match_before", 0),
            match_improvement=parsed.get("match_improvement", 0),
            changes=[
                TailorChange(**c) for c in parsed.get("changes", [])
            ],
        ).model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("in tailor preview: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/tailor-resume")
async def tailor_resume(job_id: str, current_user: dict = Depends(get_current_user)) -> TailorResumeResponse:
    """Tailor resume for specific job"""
    try:
        # Handle if current_user is a string
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)
        # Get the preview (which runs the AI and caches result)
        preview = await get_tailor_preview(job_id, current_user)
        
        # Mark as tailored
        await db.database["users"].update_one(
            {"user_id": user_id},
            {"$addToSet": {"tailored_jobs": job_id}}
        )
        
        return TailorResumeContract(
            success=True,
            message="Resume tailored successfully",
            tailor_done=True,
            match_percentage=max(0, min(100, preview["match_improvement"])),
        ).model_dump()
    except Exception as e:
        logger.error("in tailor resume: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/apply")
async def apply_for_job(job_id: str, use_tailored: bool = False, current_user: dict = Depends(get_current_user)):
    """Redirect to unified apply endpoint. Kept for backward compatibility."""
    from apply_endpoints import apply_for_job as unified_apply, ApplyJobRequest
    request = ApplyJobRequest(job_id=job_id, force_apply=True, use_tailored=use_tailored)
    result = await unified_apply(request, current_user)
    # Map to the contract response format
    return ApplyJobContract(
        success=result.success,
        message=result.message,
        application_id=result.application_id or f"{current_user.get('user_id', '')}_{job_id}",
        match_percentage=result.match_percentage,
    ).model_dump()

@router.get("/users/{user_id}/applications")
async def get_user_applications(user_id: str, current_user: dict = Depends(get_current_user)):
    """Redirect to unified applications endpoint."""
    from apply_endpoints import get_user_applied_jobs
    return await get_user_applied_jobs(user_id, current_user)

class JobSearchRequest(BaseModel):
    query: str | None = None
    skills: list[str] | None = None
    location_type: str | None = None
    experience_level: str | None = None
    limit: int = 20

_backfill_done = False

async def _backfill_legacy_job_status():
    """One-time backfill: set status on legacy jobs that don't have it. Runs once per server lifecycle."""
    global _backfill_done
    if _backfill_done:
        return

    import os
    default_expiry_days = int(os.getenv("DEFAULT_JOB_EXPIRY_DAYS", "30"))
    now = datetime.utcnow()

    legacy_jobs = await db.database["jobs"].find(
        {"status": {"$exists": False}}
    ).to_list(length=None)

    for job in legacy_jobs:
        posted = job.get("posted_date")
        deadline = job.get("application_deadline")
        is_active = job.get("is_active", True)

        new_status = "active"

        if not is_active:
            new_status = "closed"
        elif deadline:
            try:
                dl = datetime.fromisoformat(str(deadline)) if isinstance(deadline, str) else deadline
                if dl < now:
                    new_status = "expired"
            except Exception:
                pass
        elif posted:
            try:
                pd = datetime.fromisoformat(str(posted)) if isinstance(posted, str) else posted
                derived_deadline = pd + timedelta(days=default_expiry_days)
                if derived_deadline < now:
                    new_status = "expired"
            except Exception:
                pass

        await db.database["jobs"].update_one(
            {"_id": job["_id"]},
            {"$set": {"status": new_status, "is_active": new_status == "active"}},
        )

    _backfill_done = True


@router.post("/jobs/search")
async def search_jobs_unified(search_request: JobSearchRequest, current_user: dict = Depends(get_current_user)):
    """Unified job search - returns only active jobs with already_applied flag"""
    try:
        # Get user_id
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)
        
        # Get user's applied jobs
        user = await db.database["users"].find_one({"user_id": user_id})
        applied_jobs = set(user.get("applied_jobs", [])) if user else set()
        
        # Backfill legacy jobs missing status field, then query only active
        await _backfill_legacy_job_status()

        query = {"status": "active"}
        if search_request.skills:
            query["skills"] = {"$in": search_request.skills}
        if search_request.location_type:
            query["location.type"] = search_request.location_type
        if search_request.experience_level:
            query["experience_level"] = search_request.experience_level
        
        # Search jobs
        jobs = await db.database["jobs"].find(query).limit(search_request.limit).to_list(length=None)
        
        # Add already_applied flag and remaining days to each job
        now = datetime.utcnow()
        result = []
        for job in jobs:
            job_data = sanitize_for_json(job)
            job_data["already_applied"] = job.get("job_id") in applied_jobs
            job_data["status"] = "active"

            # Calculate days remaining until deadline
            deadline = job.get("application_deadline")
            if deadline:
                try:
                    dl = datetime.fromisoformat(str(deadline)) if isinstance(deadline, str) else deadline
                    job_data["days_remaining"] = max(0, (dl - now).days)
                except Exception:
                    pass

            result.append(job_data)
        
        return {"jobs": result, "total": len(result)}
    except Exception as e:
        logger.error("searching jobs: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/jobs/{job_id}/close")
async def close_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """HR endpoint to manually close/deactivate a job posting."""
    try:
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)

        job = await db.database["jobs"].find_one({"job_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        result = await db.database["jobs"].update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "status": "closed",
                    "is_active": False,
                    "updated_date": datetime.utcnow().isoformat(),
                    "closed_by": user_id,
                }
            },
        )

        if result.modified_count > 0:
            return {"success": True, "message": f"Job {job_id} closed successfully"}
        return {"success": False, "message": "Job was already closed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs")
async def search_jobs_alias(request: dict, current_user: dict = Depends(get_current_user)):
    """Alias for /jobs/search - for frontend compatibility"""
    search_req = JobSearchRequest(
        query=request.get("keywords"),
        skills=request.get("user_skills", []),
        location_type=None,
        experience_level=None,
        limit=request.get("per_page", 20)
    )
    return await search_jobs_unified(search_req, current_user)
