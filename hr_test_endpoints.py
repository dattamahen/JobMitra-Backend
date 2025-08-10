"""
Simple HR endpoints for testing
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# Create a simple test router
test_hr_router = APIRouter(prefix="/hr", tags=["HR Test"])

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
