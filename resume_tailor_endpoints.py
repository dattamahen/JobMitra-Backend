"""
Resume Tailor API endpoints using CrewAI and OpenAI
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from auth_endpoints import get_current_user
from resume_tailor_agent import run_resume_tailor
from db_simple import db
import json
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/v1", tags=["Resume Tailor"])

# Request/Response Models
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
    print(f"\n=== Tailor Preview Request ===")
    print(f"Job ID: {job_id}")
    print(f"Current user type: {type(current_user)}")
    print(f"Current user: {current_user}")
    
    # Handle if current_user is a string (user_id only)
    if isinstance(current_user, str):
        user_id = current_user
    else:
        user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)
    
    print(f"User ID: {user_id}")
    
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
        company = job.get('company', {})
        company_name = company.get('name', '') if isinstance(company, dict) else str(company)
        
        location = job.get('location', {})
        location_city = location.get('city', '') if isinstance(location, dict) else ''
        location_type = location.get('type', '') if isinstance(location, dict) else ''
        
        job_description = f"""
Job Title: {job.get('title', '')}
Company: {company_name}
Location: {location_city} - {location_type}
Experience Level: {job.get('experience_level', '')}

Description:
{job.get('description', '')}

Required Skills:
{', '.join(job.get('skills', []))}

Requirements:
{chr(10).join([f"- {req.get('description', '') if isinstance(req, dict) else str(req)}" for req in job.get('requirements', [])])}
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
        print("Running AI resume tailor agent...")
        ai_result = run_resume_tailor(sanitize_for_json(user), job_description)
        
        if "error" in ai_result:
            raise HTTPException(status_code=500, detail=ai_result["error"])
        
        # Store tailored resume in cache for later use
        await db.database["users"].update_one(
            {"user_id": user_id},
            {"$set": {f"tailored_resumes.{job_id}": ai_result["tailored_resume"]}}
        )
        
        return {
            "original_resume": original_resume,
            "tailored_resume": ai_result.get("tailored_resume", {}),
            "match_improvement": ai_result.get("match_improvement", 0),
            "changes": ai_result.get("changes", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in tailor preview: {e}")
        import traceback
        traceback.print_exc()
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
        
        return {
            "success": True,
            "message": "Resume tailored successfully",
            "tailor_done": True,
            "match_percentage": preview["match_improvement"]
        }
    except Exception as e:
        print(f"Error in tailor resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/apply")
async def apply_for_job(job_id: str, use_tailored: bool = False, current_user: dict = Depends(get_current_user)) -> ApplyJobResponse:
    """Apply for job with or without tailored resume"""
    try:
        # Handle if current_user is a string
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)
        
        print(f"\n=== Apply Request ===")
        print(f"Job ID: {job_id}")
        print(f"Use Tailored: {use_tailored}")
        print(f"User ID: {user_id}")
        
        # Always fetch user data
        user = await db.database["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if use_tailored:
            # Get cached tailored resume or generate new one
            tailored_resumes = user.get("tailored_resumes", {})
            
            if job_id in tailored_resumes:
                resume_data = tailored_resumes[job_id]
                match_score = resume_data.get("match_improvement", 85)
            else:
                # Generate new tailored resume
                preview = await get_tailor_preview(job_id, current_user)
                resume_data = preview["tailored_resume"]
                match_score = preview["match_improvement"]
        else:
            # Get user's original resume
            resume_data = sanitize_for_json(user)
            match_score = None
        
        # Create application ID
        application_id = f"app_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        # Create application document
        application = {
            "application_id": application_id,
            "job_id": job_id,
            "user_id": user_id,
            "candidate_name": f"{user.get('first_name', '')} {user.get('last_name', '')}",
            "candidate_email": user.get('email', ''),
            "resume_tailored": use_tailored,
            "resume_data": resume_data,
            "match_score": match_score,
            "applied_at": datetime.utcnow().isoformat(),
            "applied_date": datetime.utcnow().isoformat(),
            "status": "applied"
        }
        
        # Insert application
        await db.database["applications"].insert_one(application)
        
        # Update user's applied jobs list (both fields for compatibility)
        await db.database["users"].update_one(
            {"user_id": user_id},
            {
                "$addToSet": {
                    "applied_jobs": job_id,
                    "overall_jobs_applied": job_id
                }
            }
        )
        
        # Update job applications
        await db.database["jobs"].update_one(
            {"job_id": job_id},
            {
                "$push": {
                    "applications_received": {
                        "application_id": application_id,
                        "user_id": user_id,
                        "candidate_name": application["candidate_name"],
                        "applied_at": application["applied_at"],
                        "status": "applied",
                        "resume_tailored": use_tailored,
                        "match_score": match_score
                    }
                }
            }
        )
        
        message = "Application submitted with tailored resume" if use_tailored else "Application submitted"
        
        return {
            "success": True,
            "message": message,
            "application_id": application_id,
            "match_percentage": match_score
        }
    except Exception as e:
        print(f"Error in apply: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/applications")
async def get_user_applications(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get all applications for a user - DEPRECATED: Use /jobs/search with already_applied filter in frontend"""
    try:
        # Verify user access
        if isinstance(current_user, str):
            current_user_id = current_user
        else:
            current_user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)
        
        if current_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all applications for this user
        applications = await db.database["applications"].find({"user_id": user_id}).to_list(length=None)
        
        # Get job details for each application
        result = []
        for app in applications:
            job = await db.database["jobs"].find_one({"job_id": app["job_id"]})
            if job:
                result.append({
                    "application_id": app["application_id"],
                    "job_id": app["job_id"],
                    "job_title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", {}),
                    "status": app["status"],
                    "applied_at": app["applied_at"],
                    "resume_tailored": app.get("resume_tailored", False),
                    "match_score": app.get("match_score")
                })
        
        return {"applications": result, "total_count": len(result)}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting applications: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class JobSearchRequest(BaseModel):
    query: str | None = None
    skills: list[str] | None = None
    location_type: str | None = None
    experience_level: str | None = None
    limit: int = 20

@router.post("/jobs/search")
async def search_jobs_unified(search_request: JobSearchRequest, current_user: dict = Depends(get_current_user)):
    """Unified job search - returns all jobs with already_applied flag"""
    try:
        # Get user_id
        if isinstance(current_user, str):
            user_id = current_user
        else:
            user_id = current_user.get('user_id') if isinstance(current_user, dict) else str(current_user)
        
        # Get user's applied jobs
        user = await db.database["users"].find_one({"user_id": user_id})
        applied_jobs = set(user.get("applied_jobs", [])) if user else set()
        
        # Build query
        query = {}
        if search_request.skills:
            query["skills"] = {"$in": search_request.skills}
        if search_request.location_type:
            query["location.type"] = search_request.location_type
        if search_request.experience_level:
            query["experience_level"] = search_request.experience_level
        
        # Search jobs
        jobs = await db.database["jobs"].find(query).limit(search_request.limit).to_list(length=None)
        
        # Add already_applied flag to each job
        result = []
        for job in jobs:
            job_data = sanitize_for_json(job)
            job_data["already_applied"] = job.get("job_id") in applied_jobs
            result.append(job_data)
        
        return {"jobs": result, "total": len(result)}
    except Exception as e:
        print(f"Error searching jobs: {e}")
        import traceback
        traceback.print_exc()
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
