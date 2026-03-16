"""
Additional API endpoints for JobMitra Backend.
Provides comprehensive REST API for all features.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel

# Import authentication router
from auth_endpoints import auth_router

# Import database functions
from db_simple import (
    create_user_profile, get_user_profile, update_user_profile,
    search_jobs, create_job_listing,
    create_job_application, get_user_applications,
    create_mock_interview, get_user_mock_interviews,
    get_user_dashboard, update_user_dashboard,
    get_learning_resources, get_user_progress
)
from activity_tracker import log_user_activity

# Import schemas - commented out for now since using mock data
# from schemas import (
#     UserProfile, JobListing, JobApplication, MockInterviewSession,
#     LearningResource, UserDashboard, UserProgress
# )


# Router for organizing endpoints
router = APIRouter()


# Pydantic Models for API Requests/Responses
class UserProfileCreate(BaseModel):
    """Request model for creating user profile."""
    user_id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    current_job_title: Optional[str] = None
    skills: List[str] = []


class UserProfileUpdate(BaseModel):
    """Request model for updating user profile - comprehensive."""
    # Basic Information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    date_of_birth: Optional[str] = None
    
    # Professional Information
    professional_summary: Optional[str] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    overall_experience_years: Optional[int] = None
    highest_qualification: Optional[str] = None
    linkedin_link: Optional[str] = None
    github_link: Optional[str] = None
    portfolio_link: Optional[str] = None
    
    # Skills and Experience (arrays)
    skills: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    
    # Career Preferences
    desired_job_title: Optional[str] = None
    job_preferences: Optional[List[str]] = None
    employment_type: Optional[List[str]] = None
    expected_salary: Optional[float] = None
    currency: Optional[str] = None
    
    # Legacy compatibility
    full_name: Optional[str] = None
    current_job_title: Optional[str] = None


class JobSearchRequest(BaseModel):
    """Request model for job search."""
    query: Optional[str] = None
    skills: Optional[List[str]] = None
    location_type: Optional[str] = None
    experience_level: Optional[str] = None
    limit: int = 20


class JobApplicationCreate(BaseModel):
    """Request model for creating job application."""
    user_id: str
    job_id: str
    cover_letter: Optional[str] = None
    custom_answers: Dict[str, str] = {}


class MockInterviewCreate(BaseModel):
    """Request model for creating mock interview."""
    user_id: str
    skill: str
    difficulty_level: str = "intermediate"


# User Profile Endpoints
@router.post("/users", tags=["User Management"])
async def create_user(user_data: UserProfileCreate):
    """Create a new user profile with all fields initialized."""
    try:
        # Initialize complete user profile with all default values
        full_user_profile = {
            # Core Identity
            "user_id": user_data.user_id,
            "email": user_data.email,
            "password_hash": "",  # Should be set by auth system
            
            # Basic Personal Information
            "first_name": user_data.full_name.split()[0] if user_data.full_name else "",
            "last_name": " ".join(user_data.full_name.split()[1:]) if user_data.full_name and len(user_data.full_name.split()) > 1 else "",
            "date_of_birth": None,
            "phone": user_data.phone,
            "location": None,
            "city": None,
            "state": None,
            "avatar_url": None,
            
            # Professional Information
            "overall_experience_years": None,
            "highest_qualification": None,
            "professional_summary": None,
            "current_role": user_data.current_job_title,
            "current_company": None,
            
            # Skills and Experience
            "skills": user_data.skills,
            "technical_skills": [],
            "work_experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            
            # Legacy fields
            "previous_organizations": [],
            "contributions": None,
            "communication_skills": [],
            "ai_tools": [],
            
            # Additional professional fields
            "linkedin_link": None,
            "github_link": None,
            "portfolio_link": None,
            "desired_job_title": None,
            "expected_salary": None,
            "currency": "USD",
            
            # Social Links
            "social_links": None,
            
            # Job Application Tracking
            "overall_jobs_applied": [],
            
            # User Classification
            "user_type": "candidate",
            "user_status": "active",
            "user_plan": "free",
            
            # Preferences
            "job_preferences": [],
            "employment_type": [],
            
            # Timestamps
            "profile_created_on": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            
            # Analytics and Metrics
            "match_analysis_count": 0,
            "match_tailored_count": 0,
            "mock_interview_count": 0,
            "profile_completion_count": 0,
            "profile_visits": 0,
            "recent_activity": [],
            
            # Legacy Settings
            "is_active": True,
            "is_public": True,
            "email_notifications": True,
            "profile_searchable": True,
        }
        
        user_id = await create_user_profile(full_user_profile)
        
        if user_id:
            return {"message": "User created successfully", "user_id": user_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.get("/users/{user_id}", tags=["User Management"])
async def get_user(user_id: str):
    """Get user profile by ID."""
    try:
        user = await get_user_profile(user_id)
        
        if user:
            return user
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")


@router.put("/users/{user_id}", tags=["User Management"])
async def update_user(user_id: str, update_data: UserProfileUpdate):
    """Update user profile."""
    try:
        update_dict = update_data.dict(exclude_unset=True)
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No data provided for update")
        
        success = await update_user_profile(user_id, update_dict)
        
        if success:
            # Log activity
            await log_user_activity(
                user_id,
                "profile_update",
                "Updated profile information"
            )
            return {"message": "User updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found or no changes made")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


# DEPRECATED: Moved to resume_tailor_endpoints.py with already_applied flag
# @router.post("/jobs/search", tags=["Job Management"])
# async def search_jobs_endpoint(search_request: JobSearchRequest):
#     """Search for jobs based on criteria."""
#     try:
#         filters = {}
#         if search_request.skills:
#             filters["skills"] = search_request.skills
#         if search_request.location_type:
#             filters["location_type"] = search_request.location_type
#         if search_request.experience_level:
#             filters["experience_level"] = search_request.experience_level
#         
#         jobs = await search_jobs(
#             query=search_request.query or "",
#             filters=filters,
#             limit=search_request.limit
#         )
#         
#         return {
#             "jobs": jobs,
#             "count": len(jobs),
#             "query": search_request.query,
#             "filters": filters
#         }
#         
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")


@router.get("/jobs/{job_id}", tags=["Job Management"])
async def get_job(job_id: str):
    """Get specific job details."""
    try:
        # This would require implementing get_job_by_id function
        # For now, return a placeholder
        return {"message": f"Job details for {job_id} - implementation needed"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting job: {str(e)}")


# Application Management Endpoints
@router.post("/applications", tags=["Application Management"])
async def create_application(application_data: JobApplicationCreate):
    """Create a new job application."""
    try:
        # Add application ID and default status
        app_dict = application_data.dict()
        app_dict["application_id"] = f"app_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{app_dict['user_id']}"
        app_dict["current_status"] = "draft"
        
        app_id = await create_job_application(app_dict)
        
        if app_id:
            return {"message": "Application created successfully", "application_id": app_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to create application")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")


# DEPRECATED: Moved to resume_tailor_endpoints.py
# @router.get("/users/{user_id}/applications", tags=["Application Management"])
# async def get_user_applications_endpoint(user_id: str, limit: int = Query(20, ge=1, le=100)):
#     """Get all applications for a user."""
#     try:
#         applications = await get_user_applications(user_id, limit)
#         
#         return {
#             "applications": applications,
#             "count": len(applications),
#             "user_id": user_id
#         }
#         
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error getting applications: {str(e)}")


# Mock Interview Endpoints
@router.post("/mock-interviews", tags=["Mock Interviews"])
async def create_mock_interview_endpoint(interview_data: MockInterviewCreate):
    """Create a new mock interview session."""
    try:
        # Add session ID and default values
        interview_dict = interview_data.dict()
        interview_dict["session_id"] = f"mi_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{interview_dict['user_id']}"
        interview_dict["status"] = "scheduled"
        
        interview_id = await create_mock_interview(interview_dict)
        
        if interview_id:
            return {"message": "Mock interview created successfully", "session_id": interview_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to create mock interview")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating mock interview: {str(e)}")


@router.get("/users/{user_id}/mock-interviews", tags=["Mock Interviews"])
async def get_user_mock_interviews_endpoint(user_id: str, limit: int = Query(10, ge=1, le=50)):
    """Get mock interview history for a user."""
    try:
        interviews = await get_user_mock_interviews(user_id, limit)
        
        return {
            "interviews": interviews,
            "count": len(interviews),
            "user_id": user_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting mock interviews: {str(e)}")


# Dashboard Endpoints
@router.get("/users/{user_id}/dashboard", tags=["Dashboard"])
async def get_user_dashboard_endpoint(user_id: str):
    """Get user dashboard data."""
    try:
        dashboard = await get_user_dashboard(user_id)
        
        if dashboard:
            return dashboard
        else:
            raise HTTPException(status_code=404, detail="Dashboard not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard: {str(e)}")


# Learning Resources Endpoints
@router.get("/learning-resources", tags=["Learning Resources"])
async def get_learning_resources_endpoint(
    skill: Optional[str] = Query(None, description="Filter by skill"),
    level: Optional[str] = Query(None, description="Filter by difficulty level"),
    limit: int = Query(20, ge=1, le=100, description="Number of resources to return")
):
    """Get learning resources with optional filters."""
    try:
        resources = await get_learning_resources(skill=skill, level=level, limit=limit)
        
        return {
            "resources": resources,
            "count": len(resources),
            "filters": {
                "skill": skill,
                "level": level
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting learning resources: {str(e)}")


@router.get("/users/{user_id}/progress", tags=["User Progress"])
async def get_user_progress_endpoint(user_id: str):
    """Get user learning progress."""
    try:
        progress = await get_user_progress(user_id)
        
        if progress:
            return progress
        else:
            raise HTTPException(status_code=404, detail="Progress not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user progress: {str(e)}")


# Analytics Endpoints
@router.get("/analytics/summary", tags=["Analytics"])
async def get_analytics_summary():
    """Get system-wide analytics summary."""
    try:
        return {
            "total_users": 0,
            "total_jobs": 0,
            "total_applications": 0,
            "total_mock_interviews": 0,
            "message": "Analytics implementation needed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")


# Health Check for Extended APIs
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check for the extended API."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "api_version": "2.0.0",
        "features": [
            "user_management",
            "job_search",
            "applications",
            "mock_interviews",
            "learning_resources",
            "dashboard",
            "analytics",
            "resume_builder"
        ]
    }
