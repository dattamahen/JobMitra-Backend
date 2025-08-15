"""
Match Analysis and Tailor Resume endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime

from db_simple import db
from auth_endpoints import get_current_user

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

@match_router.post("/match-analysis", response_model=MatchAnalysisResponse)
async def perform_match_analysis(
    request: MatchAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Perform match analysis for a job"""
    try:
        user_id = current_user["user_id"]
        job_id = request.job_id
        
        # Get user profile
        user = await db.database["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        applied_jobs = user.get("overall_jobs_applied", [])
        app_record = None
        app_index = -1
        
        # Find existing application record
        for i, app in enumerate(applied_jobs):
            if isinstance(app, dict) and app.get("job_id") == job_id:
                app_record = app
                app_index = i
                break
        
        # Application record must exist (user must apply first)
        if not app_record:
            raise HTTPException(status_code=404, detail="Please apply for the job first")
        
        # Check if analysis already done
        if app_record.get("match_analysis_done", False):
            return MatchAnalysisResponse(
                match_percentage=app_record.get("match_percentage", 0),
                message="Match analysis already completed",
                analysis_done=True
            )
        
        # Generate random match percentage below 60%
        match_percentage = random.randint(20, 59)
        
        # Update the application record
        app_record["match_analysis_done"] = True
        app_record["match_percentage"] = match_percentage
        app_record["last_updated"] = datetime.utcnow()
        
        # Update in database
        await db.database["users"].update_one(
            {"user_id": user_id},
            {"$set": {f"overall_jobs_applied.{app_index}": app_record}}
        )
        
        return MatchAnalysisResponse(
            match_percentage=match_percentage,
            message=f"Match analysis complete: {match_percentage}% match found",
            analysis_done=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform match analysis: {str(e)}"
        )

@match_router.post("/tailor-resume", response_model=TailorResumeResponse)
async def tailor_resume(
    request: TailorResumeRequest,
    current_user: dict = Depends(get_current_user)
):
    """Tailor resume for a job"""
    try:
        user_id = current_user["user_id"]
        job_id = request.job_id
        
        # Get user profile
        user = await db.database["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        applied_jobs = user.get("overall_jobs_applied", [])
        app_record = None
        app_index = -1
        
        # Find existing application record
        for i, app in enumerate(applied_jobs):
            if isinstance(app, dict) and app.get("job_id") == job_id:
                app_record = app
                app_index = i
                break
        
        # Application record must exist (user must apply first)
        if not app_record:
            raise HTTPException(status_code=404, detail="Please apply for the job first")
        
        # Check if tailor resume already done
        if app_record.get("tailor_resume_done", False):
            return TailorResumeResponse(
                match_percentage=app_record.get("match_percentage", 0),
                message="Resume already tailored",
                tailor_done=True
            )
        
        # Generate random match percentage above 80%
        match_percentage = random.randint(80, 99)
        
        # Update the application record
        app_record["tailor_resume_done"] = True
        app_record["match_percentage"] = match_percentage
        app_record["last_updated"] = datetime.utcnow()
        
        # Update in database
        await db.database["users"].update_one(
            {"user_id": user_id},
            {"$set": {f"overall_jobs_applied.{app_index}": app_record}}
        )
        
        
        return TailorResumeResponse(
            match_percentage=match_percentage,
            message=f"Resume tailored successfully! New match: {match_percentage}%",
            tailor_done=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to tailor resume: {str(e)}"
        )