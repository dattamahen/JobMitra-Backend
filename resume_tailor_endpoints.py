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
from db import db
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
        elif posted:
            try:
                pd = datetime.fromisoformat(str(posted)) if isinstance(posted, str) else posted
                age_days = (now - pd).days
                if age_days > default_expiry_days:
                    new_status = "expired"
            except Exception:
                pass

        # Also check if deadline has passed
        if new_status == "active" and deadline:
            try:
                dl = datetime.fromisoformat(str(deadline)) if isinstance(deadline, str) else deadline
                if dl < now:
                    new_status = "expired"
            except Exception:
                pass

        await db.database["jobs"].update_one(
            {"_id": job["_id"]},
            {"$set": {"status": new_status, "is_active": new_status == "active"}},
        )

    _backfill_done = True


def calculate_skill_match_score(user_skills: List[str], job_skills: List[str]) -> int:
    """Calculate skill match percentage between user and job skills."""
    if not user_skills or not job_skills:
        return 0
    
    # Normalize skills to lowercase for comparison
    normalized_user_skills = [skill.lower().strip() for skill in user_skills]
    normalized_job_skills = [skill.lower().strip() for skill in job_skills]
    
    # Count exact matches
    exact_matches = len(set(normalized_user_skills) & set(normalized_job_skills))
    
    # Count partial matches (substring matching)
    partial_matches = 0
    for user_skill in normalized_user_skills:
        for job_skill in normalized_job_skills:
            if user_skill not in normalized_job_skills:  # Don't double count exact matches
                if user_skill in job_skill or job_skill in user_skill:
                    partial_matches += 1
                    break
    
    total_matches = exact_matches + (partial_matches * 0.5)  # Partial matches count as half
    total_job_skills = len(normalized_job_skills)
    
    if total_job_skills == 0:
        return 0
    
    match_percentage = min(100, int((total_matches / total_job_skills) * 100))
    return match_percentage

@router.post("/jobs/search")
async def search_jobs_unified(search_request: JobSearchRequest, current_user: dict = Depends(get_current_user)):
    """Unified job search with skill-based filtering - at least 2 skills must match"""
    try:
        # Get user_id
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)
        
        # Get user profile and applied jobs
        user = await db.database["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        user_skills = user.get("skills", [])
        applied_jobs = set(user.get("applied_jobs", []))
        
        # If user has no skills, return empty result with message
        if not user_skills or len(user_skills) < 2:
            logger.warning(f"User {user_id} has insufficient skills ({len(user_skills)}) for skill-based matching")
            return {
                "jobs": [],
                "total": 0,
                "message": "Please add at least 2 skills to your profile to see relevant job recommendations.",
                "filters_applied": {
                    "min_skills_required": 2,
                    "user_skills_count": len(user_skills),
                    "skill_matching_enabled": True
                }
            }
        
        # Backfill legacy jobs missing status field
        await _backfill_legacy_job_status()

        # Base query - only active jobs
        query = {"status": "active"}
        
        # Apply additional filters (location, experience level)
        if search_request.location_type:
            query["location.type"] = search_request.location_type
        if search_request.experience_level:
            query["experience_level"] = search_request.experience_level
        
        # Get all active jobs first
        all_jobs = await db.database["jobs"].find(query).to_list(length=None)
        logger.info(f"Found {len(all_jobs)} active jobs before skill filtering")
        
        # Apply skill-based filtering: at least 2 skills must match
        filtered_jobs = []
        now = datetime.utcnow()
        
        for job in all_jobs:
            # Get all job skills (required + preferred)
            job_skills_required = job.get('skills_required', job.get('skills', []))
            job_skills_preferred = job.get('skills_preferred', [])
            all_job_skills = job_skills_required + job_skills_preferred
            
            if not all_job_skills:
                continue  # Skip jobs with no skills listed
            
            # Count skill matches
            normalized_user_skills = [skill.lower().strip() for skill in user_skills]
            normalized_job_skills = [skill.lower().strip() for skill in all_job_skills]
            
            # Count exact and partial matches
            exact_matches = 0
            partial_matches = 0
            matched_skills = []
            
            for user_skill in normalized_user_skills:
                # Check for exact matches first
                if user_skill in normalized_job_skills:
                    exact_matches += 1
                    matched_skills.append(user_skill)
                else:
                    # Check for partial matches (substring)
                    for job_skill in normalized_job_skills:
                        if (len(user_skill) > 3 and user_skill in job_skill) or \
                           (len(job_skill) > 3 and job_skill in user_skill):
                            partial_matches += 1
                            matched_skills.append(f"{user_skill}~{job_skill}")
                            break
            
            total_matches = exact_matches + partial_matches
            
            # SKILL FILTERING RULE: At least 2 skills must match
            if total_matches < 2:
                continue
            
            # Calculate match score
            match_score = calculate_skill_match_score(user_skills, all_job_skills)
            
            # Prepare job data with match information
            job_data = sanitize_for_json(job)
            job_data["already_applied"] = job.get("job_id") in applied_jobs
            job_data["status"] = "active"
            job_data["match_score"] = match_score  # Backend calculated score
            job_data["matched_skills_count"] = total_matches
            job_data["matched_skills"] = matched_skills[:5]  # Show top 5 matched skills
            
            # Check if user has done detailed match analysis for this job
            user_applied_jobs = user.get("overall_jobs_applied", [])
            detailed_analysis = None
            for app_record in user_applied_jobs:
                if isinstance(app_record, dict) and app_record.get("job_id") == job.get("job_id"):
                    detailed_analysis = app_record
                    break
            
            # If detailed analysis exists, use that instead of basic score
            if detailed_analysis and detailed_analysis.get("match_analysis_done"):
                job_data["match_percentage"] = detailed_analysis.get("match_percentage", match_score)
                job_data["match_analysis_done"] = True
                job_data["match_level"] = detailed_analysis.get("match_level", "unknown")
            else:
                # Use basic score as initial match percentage
                job_data["match_percentage"] = match_score
                job_data["match_analysis_done"] = False
            
            # Set tailor resume status
            if detailed_analysis and detailed_analysis.get("tailor_resume_done"):
                job_data["tailor_resume_done"] = True
            else:
                job_data["tailor_resume_done"] = False
            
            # Calculate days remaining until deadline
            deadline = job.get("application_deadline")
            if deadline:
                try:
                    dl = datetime.fromisoformat(str(deadline)) if isinstance(deadline, str) else deadline
                    job_data["days_remaining"] = max(0, (dl - now).days)
                except Exception:
                    pass

            filtered_jobs.append(job_data)
        
        # Sort by match score (highest first), then by posted date (newest first)
        filtered_jobs.sort(key=lambda x: (-x.get('match_score', 0), -x.get('posted_date', '')), reverse=False)
        
        # Apply pagination limit
        result_jobs = filtered_jobs[:search_request.limit]
        
        logger.info(f"Skill-based filtering: {len(all_jobs)} total jobs → {len(filtered_jobs)} jobs with ≥2 skill matches → {len(result_jobs)} returned")
        
        return {
            "jobs": result_jobs,
            "total": len(filtered_jobs),
            "filters_applied": {
                "min_skills_required": 2,
                "user_skills_count": len(user_skills),
                "skill_matching_enabled": True,
                "jobs_before_filtering": len(all_jobs),
                "jobs_after_skill_filtering": len(filtered_jobs)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in skill-based job search: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/jobs/{job_id}/close")
async def close_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """HR endpoint to manually close and archive a job posting."""
    try:
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)

        from archive_jobs import archive_job
        archived = await archive_job(job_id, reason="closed", archived_by=user_id)
        if archived:
            return {"success": True, "message": f"Job {job_id} closed and archived"}
        raise HTTPException(status_code=404, detail="Job not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs")
async def search_jobs_alias(request: dict, current_user: dict = Depends(get_current_user)):
    """Alias for /jobs/search - for frontend compatibility with skill-based filtering"""
    try:
        # Get user skills from request body or user profile
        user_skills = request.get("user_skills", [])
        
        # If no user skills in request, get from user profile
        if not user_skills:
            if isinstance(current_user, str):
                user_id = current_user
            else:
                user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)
            
            user = await db.database["users"].find_one({"user_id": user_id})
            user_skills = user.get("skills", []) if user else []
        
        search_req = JobSearchRequest(
            query=request.get("keywords"),
            skills=user_skills,  # Use user skills for filtering
            location_type=None,
            experience_level=None,
            limit=request.get("per_page", 20)
        )
        return await search_jobs_unified(search_req, current_user)
        
    except Exception as e:
        logger.error("Error in jobs alias endpoint: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
