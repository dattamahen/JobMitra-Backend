"""
Simple HR endpoints for testing
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# Create a simple test router
test_hr_router = APIRouter(prefix="/hr", tags=["HR Test"])

# Pydantic models for job posting
class JobLocation(BaseModel):
    city: str
    state: str
    country: str
    is_remote: bool
    timezone: str

class JobSalary(BaseModel):
    min: int
    max: int
    currency: str
    period: str
    is_negotiable: bool

class CompanyInfo(BaseModel):
    company_size: str
    industry: str
    website: Optional[str] = None
    description: Optional[str] = None

class HRContact(BaseModel):
    name: str
    email: str
    phone: str
    title: str
    department: str

class JobPostingRequest(BaseModel):
    title: str
    company: str
    location: JobLocation
    employment_type: str
    experience_level: str
    salary: JobSalary
    description: str
    requirements: List[str]
    responsibilities: List[str]
    skills_required: List[str]
    skills_preferred: List[str]
    benefits: List[str]
    application_deadline: Optional[str] = None
    company_info: CompanyInfo
    job_type: str
    is_active: bool
    application_instructions: Optional[str] = None
    external_apply_url: Optional[str] = None
    hr_contact: HRContact
    tags: List[str]

class JobPostingResponse(BaseModel):
    id: str
    job_id: str
    title: str
    company: str
    location: JobLocation
    employment_type: str
    experience_level: str
    salary: JobSalary
    description: str
    requirements: List[str]
    responsibilities: List[str]
    skills_required: List[str]
    skills_preferred: List[str]
    benefits: List[str]
    application_deadline: Optional[str] = None
    company_info: CompanyInfo
    job_type: str
    is_active: bool
    application_instructions: Optional[str] = None
    external_apply_url: Optional[str] = None
    hr_contact: HRContact
    tags: List[str]
    posted_date: str
    updated_date: str
    views_count: int = 0
    applications_count: int = 0

# In-memory storage for demo (replace with database in production)
posted_jobs: List[JobPostingResponse] = []

@test_hr_router.get("/test")
async def test_hr_endpoint():
    """Test HR endpoint to verify routing is working"""
    return {"message": "HR endpoints are working!", "status": "success"}

@test_hr_router.get("/me")
async def get_current_hr_user_test():
    """Mock HR user endpoint for testing"""
    return {
        "id": "hr_001",
        "email": "hr@example.com",
        "company_name": "Test Company",
        "full_name": "HR Manager",
        "role": "hr",
        "is_active": True
    }

@test_hr_router.get("/dashboard")
async def get_hr_dashboard_test():
    """Mock HR dashboard with consistent format matching job seeker dashboard"""
    return {
        "stats": [
            {
                "id": "total-jobs",
                "label": "Total Jobs Posted",
                "value": 5,
                "icon": "work",
                "color": "primary",
                "trend": {
                    "direction": "up",
                    "percentage": 25,
                    "period": "this month"
                }
            },
            {
                "id": "active-jobs",
                "label": "Active Jobs",
                "value": 3,
                "icon": "visibility",
                "color": "success",
                "trend": {
                    "direction": "neutral",
                    "percentage": 0,
                    "period": "this month"
                }
            },
            {
                "id": "total-applications",
                "label": "Total Applications",
                "value": 25,
                "icon": "people",
                "color": "info",
                "trend": {
                    "direction": "up",
                    "percentage": 15,
                    "period": "this week"
                }
            },
            {
                "id": "recent-applications",
                "label": "Recent Applications",
                "value": 8,
                "icon": "new_releases",
                "color": "accent",
                "trend": {
                    "direction": "up",
                    "percentage": 33,
                    "period": "this week"
                }
            }
        ],
        "recentActivities": [
            {
                "id": "1",
                "title": "New application for Senior Software Engineer position",
                "icon": "person_add",
                "timestamp": datetime.now().isoformat(),
                "type": "application",
                "status": "new"
            },
            {
                "id": "2",
                "title": "Job posting 'Full Stack Developer' published successfully",
                "icon": "publish",
                "timestamp": datetime.now().isoformat(),
                "type": "job_posting",
                "status": "published"
            },
            {
                "id": "3",
                "title": "Interview scheduled for Product Manager role",
                "icon": "event",
                "timestamp": datetime.now().isoformat(),
                "type": "interview",
                "status": "scheduled"
            }
        ],
        "lastUpdated": datetime.now().isoformat()
    }

@test_hr_router.post("/jobs", response_model=JobPostingResponse)
async def create_job_posting(job_data: JobPostingRequest):
    """Create a new job posting"""
    try:
        # Generate unique job ID
        job_id = f"{job_data.title.lower().replace(' ', '-')}-{job_data.company.lower().replace(' ', '-')}-{len(posted_jobs) + 1}"
        
        # Create job posting response
        job_posting = JobPostingResponse(
            id=str(len(posted_jobs) + 1),
            job_id=job_id,
            title=job_data.title,
            company=job_data.company,
            location=job_data.location,
            employment_type=job_data.employment_type,
            experience_level=job_data.experience_level,
            salary=job_data.salary,
            description=job_data.description,
            requirements=job_data.requirements,
            responsibilities=job_data.responsibilities,
            skills_required=job_data.skills_required,
            skills_preferred=job_data.skills_preferred,
            benefits=job_data.benefits,
            application_deadline=job_data.application_deadline,
            company_info=job_data.company_info,
            job_type=job_data.job_type,
            is_active=job_data.is_active,
            application_instructions=job_data.application_instructions,
            external_apply_url=job_data.external_apply_url,
            hr_contact=job_data.hr_contact,
            tags=job_data.tags,
            posted_date=datetime.now().isoformat(),
            updated_date=datetime.now().isoformat(),
            views_count=0,
            applications_count=0
        )
        
        # Store the job posting
        posted_jobs.append(job_posting)
        
        return job_posting
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create job posting: {str(e)}")

@test_hr_router.get("/jobs")
async def get_hr_jobs():
    """Get all job postings for the current HR user"""
    return {
        "jobs": posted_jobs,
        "total_count": len(posted_jobs)
    }

@test_hr_router.get("/jobs/{job_id}")
async def get_job_by_id(job_id: str):
    """Get a specific job posting by ID"""
    for job in posted_jobs:
        if job.job_id == job_id or job.id == job_id:
            return job
    
    raise HTTPException(status_code=404, detail="Job not found")

@test_hr_router.put("/jobs/{job_id}")
async def update_job_posting(job_id: str, job_data: JobPostingRequest):
    """Update an existing job posting"""
    for i, job in enumerate(posted_jobs):
        if job.job_id == job_id or job.id == job_id:
            # Update the job posting
            updated_job = JobPostingResponse(
                id=job.id,
                job_id=job.job_id,
                title=job_data.title,
                company=job_data.company,
                location=job_data.location,
                employment_type=job_data.employment_type,
                experience_level=job_data.experience_level,
                salary=job_data.salary,
                description=job_data.description,
                requirements=job_data.requirements,
                responsibilities=job_data.responsibilities,
                skills_required=job_data.skills_required,
                skills_preferred=job_data.skills_preferred,
                benefits=job_data.benefits,
                application_deadline=job_data.application_deadline,
                company_info=job_data.company_info,
                job_type=job_data.job_type,
                is_active=job_data.is_active,
                application_instructions=job_data.application_instructions,
                external_apply_url=job_data.external_apply_url,
                hr_contact=job_data.hr_contact,
                tags=job_data.tags,
                posted_date=job.posted_date,
                updated_date=datetime.now().isoformat(),
                views_count=job.views_count,
                applications_count=job.applications_count
            )
            
            posted_jobs[i] = updated_job
            return updated_job
    
    raise HTTPException(status_code=404, detail="Job not found")

@test_hr_router.delete("/jobs/{job_id}")
async def delete_job_posting(job_id: str):
    """Delete a job posting"""
    for i, job in enumerate(posted_jobs):
        if job.job_id == job_id or job.id == job_id:
            deleted_job = posted_jobs.pop(i)
            return {"message": "Job deleted successfully", "job": deleted_job}
    
    raise HTTPException(status_code=404, detail="Job not found")

@test_hr_router.get("/jobs")
async def get_hr_jobs_test():
    """Mock HR jobs list for testing"""
    return {
        "jobs": [
            {
                "id": "job_001",
                "title": "Senior Software Engineer",
                "company": "Test Company",
                "location": "Remote",
                "description": "Great opportunity for a senior developer",
                "requirements": ["5+ years experience", "Python expertise"],
                "skills": ["Python", "FastAPI", "MongoDB"],
                "experience_level": "senior",
                "employment_type": "full_time",
                "job_type": "remote",
                "is_active": True,
                "created_at": "2025-01-01T10:00:00Z",
                "updated_at": "2025-01-01T10:00:00Z"
            }
        ]
    }
