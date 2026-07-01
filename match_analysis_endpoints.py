"""
Match Analysis and Tailor Resume endpoints with enhanced skill-based matching
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from db import db
from auth_endpoints import get_current_user
from resume_tailor_endpoints import calculate_skill_match_score

logger = logging.getLogger(__name__)

# Create router
match_router = APIRouter(prefix="/api/v1", tags=["Match Analysis"])

class MatchAnalysisRequest(BaseModel):
    job_id: str

class MatchAnalysisResponse(BaseModel):
    match_percentage: int
    message: str
    analysis_done: bool

class TailorResumeRequest(BaseModel):
    job_id: str

class TailorResumeResponse(BaseModel):
    match_percentage: int
    message: str
    tailor_done: bool

def perform_detailed_skill_analysis(user_skills: list, job_skills_required: list, job_skills_preferred: list) -> dict:
    """Perform detailed skill-based match analysis."""
    if not user_skills:
        return {
            "match_percentage": 0,
            "skill_matches": [],
            "missing_skills": job_skills_required + job_skills_preferred,
            "match_level": "poor",
            "recommendations": ["Add skills to your profile to improve job matching"]
        }
    
    # Combine all job skills
    all_job_skills = job_skills_required + job_skills_preferred
    
    # Calculate match score using our existing function
    match_percentage = calculate_skill_match_score(user_skills, all_job_skills)
    
    # Analyze skill matches in detail
    normalized_user = [skill.lower().strip() for skill in user_skills]
    normalized_required = [skill.lower().strip() for skill in job_skills_required]
    normalized_preferred = [skill.lower().strip() for skill in job_skills_preferred]
    
    # Find exact matches
    required_matches = list(set(normalized_user) & set(normalized_required))
    preferred_matches = list(set(normalized_user) & set(normalized_preferred))
    
    # Find missing skills
    missing_required = [skill for skill in job_skills_required 
                       if skill.lower().strip() not in normalized_user]
    missing_preferred = [skill for skill in job_skills_preferred 
                        if skill.lower().strip() not in normalized_user]
    
    # Determine match level and recommendations
    total_required = len(job_skills_required)
    required_match_rate = len(required_matches) / total_required if total_required > 0 else 0
    
    if required_match_rate >= 0.8:
        match_level = "excellent"
        recommendations = ["Great match! You have most required skills."]
    elif required_match_rate >= 0.6:
        match_level = "good"
        recommendations = [f"Good match! Consider learning: {', '.join(missing_required[:3])}"]
    elif required_match_rate >= 0.4:
        match_level = "fair"
        recommendations = [f"Fair match. Focus on: {', '.join(missing_required[:3])}"]
    else:
        match_level = "poor"
        recommendations = [f"Low match. You need: {', '.join(missing_required[:5])}"]
    
    return {
        "match_percentage": match_percentage,
        "skill_matches": required_matches + preferred_matches,
        "missing_required": missing_required,
        "missing_preferred": missing_preferred,
        "match_level": match_level,
        "recommendations": recommendations
    }

@match_router.post("/match-analysis", response_model=MatchAnalysisResponse)
async def perform_match_analysis(
    request: MatchAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Perform enhanced skill-based match analysis for a job"""
    try:
        user_id = current_user["user_id"]
        job_id = request.job_id
        
        # Get user profile
        user = await db.database["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get job details
        job = await db.database["jobs"].find_one({"job_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.get("status") in ("expired", "closed", "filled") or not job.get("is_active", True):
            raise HTTPException(status_code=410, detail="This job is no longer active")
        
        # Get user skills and job requirements
        user_skills = user.get("skills", [])
        job_skills_required = job.get("skills_required", job.get("skills", []))
        job_skills_preferred = job.get("skills_preferred", [])
        
        applied_jobs = user.get("overall_jobs_applied", [])
        app_record = None
        app_index = -1
        
        # Find existing application record
        for i, app in enumerate(applied_jobs):
            if isinstance(app, dict) and app.get("job_id") == job_id:
                app_record = app
                app_index = i
                break
        
        # Check if analysis already done on existing record
        if app_record and app_record.get("match_analysis_done", False):
            return MatchAnalysisResponse(
                match_percentage=app_record.get("match_percentage", 0),
                message=f"Match analysis already completed: {app_record.get('match_percentage', 0)}% match",
                analysis_done=True
            )
        
        # Perform enhanced skill-based analysis
        analysis_result = perform_detailed_skill_analysis(
            user_skills, job_skills_required, job_skills_preferred
        )
        
        match_percentage = analysis_result["match_percentage"]
        match_level = analysis_result["match_level"]
        recommendations = analysis_result["recommendations"]
        
        # Create detailed message
        message = f"Analysis complete: {match_percentage}% match ({match_level}). {recommendations[0] if recommendations else ''}"
        
        # Log the analysis for debugging
        logger.info(f"Match analysis for user {user_id}, job {job_id}: {match_percentage}% ({match_level})")
        logger.debug(f"User skills: {user_skills}")
        logger.debug(f"Job skills required: {job_skills_required}")
        logger.debug(f"Job skills preferred: {job_skills_preferred}")
        
        if app_record:
            # Update existing application record with detailed analysis
            app_record["match_analysis_done"] = True
            app_record["match_percentage"] = match_percentage
            app_record["match_level"] = match_level
            app_record["skill_matches"] = analysis_result["skill_matches"]
            app_record["missing_skills"] = analysis_result["missing_required"]
            app_record["recommendations"] = recommendations
            app_record["last_updated"] = datetime.utcnow()
            
            await db.database["users"].update_one(
                {"user_id": user_id},
                {"$set": {f"overall_jobs_applied.{app_index}": app_record}}
            )
        else:
            # Create a new application record for pre-apply analysis
            new_record = {
                "job_id": job_id,
                "application_id": f"{user_id}_{job_id}",
                "status": "analyzing",
                "match_analysis_done": True,
                "match_percentage": match_percentage,
                "match_level": match_level,
                "skill_matches": analysis_result["skill_matches"],
                "missing_skills": analysis_result["missing_required"],
                "recommendations": recommendations,
                "tailor_resume_done": False,
                "is_applied": False,
                "applied_date": datetime.utcnow(),
                "last_updated": datetime.utcnow()
            }
            await db.database["users"].update_one(
                {"user_id": user_id},
                {"$push": {"overall_jobs_applied": new_record}}
            )
        
        return MatchAnalysisResponse(
            match_percentage=match_percentage,
            message=message,
            analysis_done=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in match analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform match analysis: {str(e)}"
        )

@match_router.post("/tailor-resume", response_model=TailorResumeResponse)
async def tailor_resume(
    request: TailorResumeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Tailor resume for a job with enhanced skill-based analysis"""
    try:
        user_id = current_user["user_id"]
        job_id = request.job_id
        
        # Get user profile and job details
        user = await db.database["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        job = await db.database["jobs"].find_one({"job_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        applied_jobs = user.get("overall_jobs_applied", [])
        app_record = None
        app_index = -1
        
        # Find existing application record
        for i, app in enumerate(applied_jobs):
            if isinstance(app, dict) and app.get("job_id") == job_id:
                app_record = app
                app_index = i
                break
        
        # Check if tailor resume already done on existing record
        if app_record and app_record.get("tailor_resume_done", False):
            return TailorResumeResponse(
                match_percentage=app_record.get("match_percentage", 0),
                message="Resume already tailored",
                tailor_done=True
            )
        
        # Get skill-based analysis first
        user_skills = user.get("skills", [])
        job_skills_required = job.get("skills_required", job.get("skills", []))
        job_skills_preferred = job.get("skills_preferred", [])
        
        analysis_result = perform_detailed_skill_analysis(
            user_skills, job_skills_required, job_skills_preferred
        )
        
        # After tailoring, improve match percentage by 15-25 points
        base_match = analysis_result["match_percentage"]
        improvement = min(25, max(15, 100 - base_match))  # Don't exceed 100%
        match_percentage = min(99, base_match + improvement)
        
        logger.info(f"Resume tailoring for user {user_id}, job {job_id}: {base_match}% -> {match_percentage}%")
        
        if app_record:
            # Update existing application record with tailoring improvements
            app_record["tailor_resume_done"] = True
            app_record["match_percentage"] = match_percentage
            app_record["match_improvement"] = improvement
            app_record["last_updated"] = datetime.utcnow()
            
            await db.database["users"].update_one(
                {"user_id": user_id},
                {"$set": {f"overall_jobs_applied.{app_index}": app_record}}
            )
        else:
            # Create a new application record for pre-apply tailoring
            new_record = {
                "job_id": job_id,
                "application_id": f"{user_id}_{job_id}",
                "status": "tailored",
                "match_analysis_done": False,
                "match_percentage": match_percentage,
                "match_improvement": improvement,
                "tailor_resume_done": True,
                "is_applied": False,
                "applied_date": datetime.utcnow(),
                "last_updated": datetime.utcnow()
            }
            await db.database["users"].update_one(
                {"user_id": user_id},
                {"$push": {"overall_jobs_applied": new_record}}
            )
        
        
        return TailorResumeResponse(
            match_percentage=match_percentage,
            message=f"Resume tailored successfully! Match improved by {improvement}% to {match_percentage}%",
            tailor_done=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in resume tailoring: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to tailor resume: {str(e)}"
        )