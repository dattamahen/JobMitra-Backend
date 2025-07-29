"""
Dashboard and Profile API endpoints.
"""

from datetime import datetime
from fastapi import APIRouter


# Create router for dashboard and profile endpoints
router = APIRouter()


@router.get("/dashboard", tags=["Dashboard"])
async def get_dashboard():
    """Dashboard endpoint that returns data compatible with Angular frontend."""
    
    return {
        "stats": [
            {
                "id": "applications",
                "label": "Applications Sent",
                "value": 12,
                "icon": "send",
                "color": "primary",
                "trend": {
                    "direction": "up",
                    "percentage": 15,
                    "period": "this week"
                }
            },
            {
                "id": "interviews",
                "label": "Interviews Scheduled", 
                "value": 3,
                "icon": "event",
                "color": "accent",
                "trend": {
                    "direction": "up",
                    "percentage": 50,
                    "period": "this week"
                }
            },
            {
                "id": "total-jobs",
                "label": "Total Jobs Available",
                "value": 150,
                "icon": "work",
                "color": "info",
                "trend": {
                    "direction": "neutral",
                    "percentage": 0,
                    "period": "this week"
                }
            },
            {
                "id": "profile-completion",
                "label": "Profile Completion",
                "value": "85%",
                "icon": "account_circle",
                "color": "success",
                "trend": {
                    "direction": "up",
                    "percentage": 10,
                    "period": "this week"
                }
            }
        ],
        "recentActivities": [
            {
                "id": "1",
                "title": "Applied to Software Engineer position at TechCorp",
                "icon": "send",
                "timestamp": datetime.now().isoformat(),
                "type": "application",
                "status": "pending"
            },
            {
                "id": "2", 
                "title": "Completed mock interview for Backend Developer role",
                "icon": "quiz",
                "timestamp": datetime.now().isoformat(),
                "type": "interview",
                "status": "completed"
            },
            {
                "id": "3",
                "title": "Updated resume with new skills",
                "icon": "description",
                "timestamp": datetime.now().isoformat(), 
                "type": "resume",
                "status": "completed"
            }
        ],
        "lastUpdated": datetime.now().isoformat()
    }


@router.get("/profile/current", tags=["User Management"])
async def get_current_user_profile():
    """Get current user profile - returns dummy Indian profile data."""
    return {
        "user_id": "usr_001",
        "email": "priya.sharma@example.com",
        "full_name": "Priya Sharma",
        "phone": "+91 98765 43210",
        "current_job_title": "Senior Software Engineer",
        "desired_job_title": "Technical Lead",
        "experience_years": "4-5",
        "skills": [
            "JavaScript", "React", "Node.js", "Python", "MongoDB", 
            "AWS", "Docker", "Git", "TypeScript", "Express.js"
        ],
        "professional_summary": "Experienced software engineer with a passion for building scalable web applications. Skilled in full-stack development with expertise in modern JavaScript frameworks and cloud technologies. Looking to transition into a technical leadership role.",
        "certifications": [
            "AWS Certified Developer Associate",
            "Google Cloud Professional Developer",
            "Certified Kubernetes Administrator"
        ],
        "area_of_expertise": [
            "Full Stack Development",
            "Cloud Architecture", 
            "DevOps",
            "Team Leadership"
        ],
        "key_contributions": "Led the development of a microservices architecture that improved system performance by 40%. Mentored 3 junior developers and established coding standards for the team. Implemented CI/CD pipelines reducing deployment time by 60%.",
        "preferred_work_types": ["remote", "hybrid"],
        "preferred_employment_types": ["full-time"],
        "social_links": {
            "github": "https://github.com/priyasharma",
            "portfolio": "https://priyasharma.dev",
            "youtube": "https://youtube.com/@priyatech"
        },
        "location": {
            "city": "Bangalore, Karnataka",
            "country": "India",
            "type": "hybrid"
        },
        "expected_salary": {
            "min": 18,
            "max": 25,
            "currency": "INR",
            "period": "yearly"
        },
        "profile_completion_percentage": 92,
        "profile_views": 156,
        "last_active": "2024-07-29T14:22:00Z",
        "is_active": True,
        "is_public": True,
        "email_notifications": True,
        "profile_searchable": True,
        "preferred_locations": ["Bangalore", "Mumbai", "Remote"],
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-07-29T14:22:00Z"
    }
