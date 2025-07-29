"""
Mock database module for development/testing purposes.
Uses in-memory storage instead of MongoDB.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import json


class MockDatabase:
    """Mock database handler class using in-memory storage."""
    
    def __init__(self):
        self.connected = False
        # In-memory storage
        self.data = {
            "users": {},
            "jobs": {},
            "applications": {},
            "mock_interviews": {},
            "learning_resources": [],
            "user_progress": {},
            "dashboards": {},
            "query_logs": []
        }
        self._seed_sample_data()
        
    async def connect_to_mongo(self):
        """Mock connection to database."""
        print("Mock Database: Connected to in-memory storage")
        self.connected = True
        
    async def close_mongo_connection(self):
        """Mock close database connection."""
        print("Mock Database: Connection closed")
        self.connected = False
        
    def _seed_sample_data(self):
        """Add sample data for testing."""
        # Sample learning resources
        self.data["learning_resources"] = [
            {
                "resource_id": "lr_001",
                "title": "Python Programming Fundamentals",
                "description": "Learn Python basics for web development",
                "skill": "Python",
                "level": "beginner",
                "type": "course",
                "url": "https://example.com/python-course",
                "duration_minutes": 480
            },
            {
                "resource_id": "lr_002",
                "title": "React.js Complete Guide",
                "description": "Master React.js for frontend development",
                "skill": "React",
                "level": "intermediate",
                "type": "course",
                "url": "https://example.com/react-course",
                "duration_minutes": 720
            },
            {
                "resource_id": "lr_003",
                "title": "Data Structures and Algorithms",
                "description": "Essential DSA for technical interviews",
                "skill": "Algorithms",
                "level": "intermediate",
                "type": "course",
                "url": "https://example.com/dsa-course",
                "duration_minutes": 960
            }
        ]
        
        # Sample jobs
        sample_jobs = [
            {
                "job_id": "job_001",
                "title": "Frontend Developer",
                "company": "TechCorp Inc",
                "location_type": "remote",
                "experience_level": "mid",
                "skills": ["React", "JavaScript", "CSS"],
                "description": "Join our team as a Frontend Developer...",
                "posted_date": datetime.utcnow().isoformat()
            },
            {
                "job_id": "job_002", 
                "title": "Python Backend Developer",
                "company": "DataFlow Solutions",
                "location_type": "hybrid",
                "experience_level": "senior",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "description": "We're looking for a Senior Python Developer...",
                "posted_date": datetime.utcnow().isoformat()
            }
        ]
        
        for job in sample_jobs:
            self.data["jobs"][job["job_id"]] = job


# Database functions that match the original API

async def create_user_profile(user_data: Dict[str, Any]) -> Optional[str]:
    """Create a new user profile."""
    user_id = user_data.get("user_id")
    if user_id:
        db.data["users"][user_id] = user_data
        return user_id
    return None

async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile by ID."""
    return db.data["users"].get(user_id)

async def update_user_profile(user_id: str, update_data: Dict[str, Any]) -> bool:
    """Update user profile."""
    if user_id in db.data["users"]:
        db.data["users"][user_id].update(update_data)
        return True
    return False

async def search_jobs(query: str = "", filters: Dict[str, Any] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Search for jobs."""
    jobs = list(db.data["jobs"].values())
    
    # Apply basic filtering
    if filters:
        if "skills" in filters:
            filter_skills = filters["skills"]
            jobs = [job for job in jobs if any(skill in job.get("skills", []) for skill in filter_skills)]
        
        if "location_type" in filters:
            jobs = [job for job in jobs if job.get("location_type") == filters["location_type"]]
            
        if "experience_level" in filters:
            jobs = [job for job in jobs if job.get("experience_level") == filters["experience_level"]]
    
    # Apply text search
    if query:
        query_lower = query.lower()
        jobs = [job for job in jobs if 
               query_lower in job.get("title", "").lower() or 
               query_lower in job.get("description", "").lower()]
    
    return jobs[:limit]

async def create_job_listing(job_data: Dict[str, Any]) -> Optional[str]:
    """Create a new job listing."""
    job_id = job_data.get("job_id", f"job_{len(db.data['jobs']) + 1:03d}")
    job_data["job_id"] = job_id
    db.data["jobs"][job_id] = job_data
    return job_id

async def create_job_application(app_data: Dict[str, Any]) -> Optional[str]:
    """Create a job application."""
    app_id = app_data.get("application_id")
    if app_id:
        db.data["applications"][app_id] = app_data
        return app_id
    return None

async def get_user_applications(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get user applications."""
    user_apps = [app for app in db.data["applications"].values() 
                 if app.get("user_id") == user_id]
    return user_apps[:limit]

async def create_mock_interview(interview_data: Dict[str, Any]) -> Optional[str]:
    """Create a mock interview session."""
    session_id = interview_data.get("session_id")
    if session_id:
        db.data["mock_interviews"][session_id] = interview_data
        return session_id
    return None

async def get_user_mock_interviews(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get user mock interviews."""
    user_interviews = [interview for interview in db.data["mock_interviews"].values() 
                      if interview.get("user_id") == user_id]
    return user_interviews[:limit]

async def get_user_dashboard(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user dashboard data."""
    if user_id not in db.data["dashboards"]:
        # Create default dashboard
        db.data["dashboards"][user_id] = {
            "user_id": user_id,
            "total_applications": len([app for app in db.data["applications"].values() 
                                     if app.get("user_id") == user_id]),
            "total_interviews": len([interview for interview in db.data["mock_interviews"].values() 
                                   if interview.get("user_id") == user_id]),
            "profile_completion": 75,
            "recent_activity": [],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    return db.data["dashboards"][user_id]

async def update_user_dashboard(user_id: str, dashboard_data: Dict[str, Any]) -> bool:
    """Update user dashboard."""
    if user_id:
        db.data["dashboards"][user_id] = dashboard_data
        return True
    return False

async def get_learning_resources(skill: str = None, level: str = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Get learning resources with optional filters."""
    resources = db.data["learning_resources"].copy()
    
    if skill:
        resources = [r for r in resources if r.get("skill", "").lower() == skill.lower()]
        
    if level:
        resources = [r for r in resources if r.get("level", "").lower() == level.lower()]
    
    return resources[:limit]

async def get_user_progress(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user learning progress."""
    if user_id not in db.data["user_progress"]:
        # Create default progress
        db.data["user_progress"][user_id] = {
            "user_id": user_id,
            "completed_resources": [],
            "current_skills": ["Python", "JavaScript"],
            "skill_levels": {"Python": "intermediate", "JavaScript": "beginner"},
            "total_learning_hours": 25,
            "certificates_earned": 2,
            "last_activity": datetime.utcnow().isoformat()
        }
    
    return db.data["user_progress"][user_id]

async def log_to_db(query: str, response: str, metadata: Dict[str, Any] = None):
    """Log query and response to database."""
    log_entry = {
        "query": query,
        "response": response,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    db.data["query_logs"].append(log_entry)
    
    # Keep only last 100 logs to manage memory
    if len(db.data["query_logs"]) > 100:
        db.data["query_logs"] = db.data["query_logs"][-100:]

# Global database instance
db = MockDatabase()
