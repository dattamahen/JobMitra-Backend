"""
Dashboard and Profile API endpoints.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging
from job_db import JobDatabase

logger = logging.getLogger(__name__)
from auth_endpoints import get_current_user
from db import (
    db, get_user_profile, get_user_applications, get_user_mock_interviews,
    get_learning_resources,
    get_user_progress
)
from activity_tracker import log_user_activity

# Create router for dashboard and profile endpoints
router = APIRouter()

# Initialize job database
job_db = JobDatabase()


class JobSearchRequest(BaseModel):
    """Request body schema for job search with user skills."""
    page: int = 1
    per_page: int = 10
    keywords: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    job_type: Optional[str] = None
    user_skills: List[str] = []
    user_certifications: List[str] = []
    user_experience_keywords: List[str] = []


@router.get("/dashboard", tags=["Dashboard"])
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    """Dashboard endpoint that returns real data from MongoDB for authenticated user."""
    
    try:
        user_id = current_user["user_id"]
        user_type = current_user.get("user_type", "candidate")
        
        # Get user data directly from users collection
        user_profile = await db.database["users"].find_one({"user_id": user_id})
        
        # Calculate profile completion dynamically
        def calculate_profile_completion(profile):
            if not profile:
                return 0
            
            completion_score = 0
            total_fields = 10  # Total weighted fields
            
            # Basic info (20%)
            if profile.get("first_name") and profile.get("last_name"):
                completion_score += 2
            if profile.get("email"):
                completion_score += 1
            if profile.get("phone"):
                completion_score += 1
            
            # Professional info (40%)
            if profile.get("skills") and len(profile.get("skills", [])) > 0:
                completion_score += 2
            if profile.get("overall_experience_years") is not None:
                completion_score += 1
            if profile.get("highest_qualification"):
                completion_score += 1
            
            # Additional details (40%)
            prof_info = profile.get("professional_info", {})
            if prof_info.get("current_role"):
                completion_score += 1
            if prof_info.get("professional_summary"):
                completion_score += 1
            # Check certifications (filter out invalid entries)
            certs = profile.get("certifications", [])
            valid_certs = []
            for cert in certs:
                if isinstance(cert, dict) and cert.get("name") and cert.get("name") != "[object Object]":
                    valid_certs.append(cert)
                elif isinstance(cert, str) and cert and cert != "[object Object]":
                    valid_certs.append(cert)
            if valid_certs:
                completion_score += 1
            
            return min(int((completion_score / total_fields) * 100), 100)
        
        profile_completion = calculate_profile_completion(user_profile)
        
        # Get applications count from user's overall_jobs_applied field (only is_applied=True)
        overall_jobs_applied = user_profile.get("overall_jobs_applied", []) if user_profile else []
        total_applications = sum(1 for app in overall_jobs_applied if isinstance(app, dict) and app.get("is_applied", False))
        
        # Get user mock interviews from database
        user_interviews = await get_user_mock_interviews(user_id, limit=20)
        
        # Calculate interviews scheduled (from mock interviews)
        interviews_scheduled = len(user_interviews)
        
        # Calculate trend percentages (simplified since we're using overall_jobs_applied)
        apps_trend = min(total_applications, 5) if total_applications > 0 else 0
        
        # Get total job count from database (uses same query logic as job search)
        total_jobs = await job_db.get_active_job_count()
        active_jobs = total_jobs
        
        # Build stats based on user type
        if user_type in ["candidate", "job_seeker"]:
            stats = [
                {
                    "id": "applications",
                    "label": "Applications Sent",
                    "value": total_applications,
                    "icon": "send",
                    "color": "primary",
                    "trend": {
                        "direction": "up" if apps_trend > 0 else "neutral",
                        "percentage": min(apps_trend * 10, 100),  # Scale trend
                        "period": "this week"
                    }
                },
                {
                    "id": "interviews",
                    "label": "Mock Interview", 
                    "value": interviews_scheduled,
                    "icon": "record_voice_over",
                    "color": "accent",
                    "trend": {
                        "direction": "up" if interviews_scheduled > 0 else "neutral",
                        "percentage": min(interviews_scheduled * 20, 100),
                        "period": "this week"
                    }
                },
                {
                    "id": "matching-jobs",
                    "label": "Total Jobs Available",
                    "value": total_jobs,
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
                    "value": f"{profile_completion}%",
                    "icon": "account_circle",
                    "color": "success",
                    "trend": {
                        "direction": "up" if profile_completion > 50 else "neutral",
                        "percentage": 5,
                        "period": "this week"
                    }
                }
            ]
        else:  # HR user
            # Get HR-specific metrics from database using aggregation (not loading all docs)
            try:
                hr_jobs_count = await db.database["jobs"].count_documents({"posted_by_hr_id": user_id})
                hr_active_jobs = await db.database["jobs"].count_documents({"posted_by_hr_id": user_id, "is_active": True})
                # Use aggregation to count applications without loading all jobs into memory
                pipeline = [
                    {"$match": {"posted_by_hr_id": user_id}},
                    {"$project": {"app_count": {"$size": {"$ifNull": ["$applications_received", []]}}}},
                    {"$group": {"_id": None, "total": {"$sum": "$app_count"}}}
                ]
                agg_result = await db.database["jobs"].aggregate(pipeline).to_list(1)
                hr_applications_received = agg_result[0]["total"] if agg_result else 0
            except Exception:
                hr_jobs_count = 0
                hr_active_jobs = 0
                hr_applications_received = 0
            
            stats = [
                {
                    "id": "jobs-posted",
                    "label": "Jobs Posted",
                    "value": hr_jobs_count,
                    "icon": "work_add",
                    "color": "primary",
                    "trend": {
                        "direction": "up" if hr_jobs_count > 0 else "neutral",
                        "percentage": 10,
                        "period": "this week"
                    }
                },
                {
                    "id": "applications-received",
                    "label": "Applications Received",
                    "value": hr_applications_received,
                    "icon": "inbox",
                    "color": "accent",
                    "trend": {
                        "direction": "up" if hr_applications_received > 0 else "neutral",
                        "percentage": 15,
                        "period": "this week"
                    }
                },
                {
                    "id": "active-jobs",
                    "label": "Active Job Postings",
                    "value": hr_active_jobs,
                    "icon": "work",
                    "color": "info",
                    "trend": {
                        "direction": "neutral",
                        "percentage": 0,
                        "period": "this week"
                    }
                },
                {
                    "id": "candidate-pipeline",
                    "label": "Candidates in Pipeline",
                    "value": hr_applications_received,
                    "icon": "people",
                    "color": "success",
                    "trend": {
                        "direction": "up" if hr_applications_received > 0 else "neutral",
                        "percentage": 8,
                        "period": "this week"
                    }
                }
            ]
        
        # Build recent activities from tracked activities
        recent_activities = []
        
        # Get recent activities from user profile
        tracked_activities = user_profile.get("recent_activity", []) if user_profile else []
        
        for activity in tracked_activities:
            if isinstance(activity, dict) and "activity_type" in activity and "description" in activity:
                activity_item = {
                    "id": f"{activity['activity_type']}_{activity.get('timestamp', 'unknown')}",
                    "title": activity["description"],
                    "icon": activity.get("icon", "info"),
                    "timestamp": activity.get("timestamp", datetime.now().isoformat()),
                    "type": activity["activity_type"],
                    "status": activity.get("status", "completed")
                }
                recent_activities.append(activity_item)
        
        # Add mock interview activities
        for interview in user_interviews[:3]:  # Limit to 3 most recent
            activity = {
                "id": interview.get("_id", ""),
                "title": f"Completed mock interview for {interview.get('role', 'Unknown Role')} position",
                "icon": "quiz",
                "timestamp": interview.get("created_at", datetime.now().isoformat()),
                "type": "interview",
                "status": "completed"
            }
            recent_activities.append(activity)
        
        # Sort activities by timestamp (most recent first) - handle mixed datetime/string types
        def get_timestamp_for_sort(activity):
            timestamp = activity.get("timestamp", "")
            if isinstance(timestamp, str):
                return timestamp
            elif hasattr(timestamp, 'isoformat'):
                return timestamp.isoformat()
            else:
                return str(timestamp)
        
        recent_activities.sort(key=get_timestamp_for_sort, reverse=True)
        recent_activities = recent_activities[:10]  # Limit to 10 total activities
        
        # If no real activities, add some default ones
        if not recent_activities:
            recent_activities = [
                {
                    "id": "1",
                    "title": "Profile created successfully",
                    "icon": "account_circle",
                    "timestamp": current_user.get("profile_created_on", datetime.now()).isoformat(),
                    "type": "profile",
                    "status": "completed"
                }
            ]
        
        dashboard_data = {
            "stats": stats,
            "recentActivities": recent_activities,
            "user": {
                "user_id": user_id,
                "name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip(),
                "email": current_user.get("email", ""),
                "user_type": user_type,
                "profile_completion": profile_completion
            },
            "lastUpdated": datetime.now().isoformat()
        }
        
        # Update dashboard in database
        # REMOVED: user_dashboards collection was write-only, never read
        
        return dashboard_data
        
    except Exception as e:
        logger.error("Error getting dashboard data: %s", e)
        
        # Fallback to basic data if database operations fail
        return {
            "stats": [
                {
                    "id": "applications",
                    "label": "Applications Sent",
                    "value": 0,
                    "icon": "send",
                    "color": "primary",
                    "trend": {"direction": "neutral", "percentage": 0, "period": "this week"}
                },
                {
                    "id": "interviews",
                    "label": "Mock Interview", 
                    "value": 0,
                    "icon": "record_voice_over",
                    "color": "accent",
                    "trend": {"direction": "neutral", "percentage": 0, "period": "this week"}
                }
            ],
            "recentActivities": [
                {
                    "id": "1",
                    "title": "Welcome to JobMitra!",
                    "icon": "info",
                    "timestamp": datetime.now().isoformat(),
                    "type": "system",
                    "status": "completed"
                }
            ],
            "user": {
                "user_id": current_user.get("user_id", ""),
                "name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip(),
                "email": current_user.get("email", ""),
                "user_type": current_user.get("user_type", "candidate")
            },
            "lastUpdated": datetime.now().isoformat()
        }


@router.get("/profile/current", tags=["User Management"])
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user profile from database."""
    try:
        user_id = current_user["user_id"]
        
        # Get complete user profile from database
        user_profile = await get_user_profile(user_id)
        
        if not user_profile:
            # If no profile found in database, return data from auth token
            return {
                "user_id": current_user["user_id"],
                "email": current_user["email"],
                "full_name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip(),
                "first_name": current_user.get("first_name", ""),
                "last_name": current_user.get("last_name", ""),
                "phone": current_user.get("phone", ""),
                "user_type": current_user.get("user_type", "candidate"),
                "profile_completion_percentage": current_user.get("profile_completion_count", 0),
                "skills": current_user.get("skills", []),
                "created_at": current_user.get("profile_created_on", datetime.now()).isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        # Format profile data for frontend
        profile_data = {
            "user_id": user_profile["user_id"],
            "email": user_profile["email"],
            "full_name": f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip(),
            "first_name": user_profile.get("first_name", ""),
            "last_name": user_profile.get("last_name", ""),
            "phone": user_profile.get("phone", ""),
            "date_of_birth": user_profile.get("date_of_birth"),
            "current_job_title": user_profile.get("professional_info", {}).get("current_role", ""),
            "desired_job_title": user_profile.get("professional_info", {}).get("desired_job_title", ""),
            "experience_years": user_profile.get("overall_experience_years", 0),
            "highest_qualification": user_profile.get("highest_qualification", ""),
            "skills": user_profile.get("skills", []),
            "professional_summary": user_profile.get("professional_info", {}).get("professional_summary", ""),
            "work_experience": user_profile.get("work_experience", []),
            "education": user_profile.get("education", []),
            "projects": user_profile.get("projects", []),
            "certifications": user_profile.get("certifications", []),
            "area_of_expertise": user_profile.get("professional_info", {}).get("area_of_expertise", []),
            "key_contributions": user_profile.get("professional_info", {}).get("key_contributions", ""),
            "preferred_work_types": user_profile.get("job_preferences", []),
            "preferred_employment_types": user_profile.get("employment_type", []),
            "social_links": {
                "github": user_profile.get("github_link", ""),
                "portfolio": user_profile.get("portfolio_url", ""),
                "linkedin": user_profile.get("linkedin_link", ""),
                "youtube": user_profile.get("youtube_link", "")
            },
            "location": {
                "city": user_profile.get("personal_info", {}).get("location", {}).get("city", ""),
                "state": user_profile.get("personal_info", {}).get("location", {}).get("state", ""),
                "country": user_profile.get("personal_info", {}).get("location", {}).get("country", "India"),
                "type": user_profile.get("work_preferences", {}).get("work_type", "hybrid")
            },
            "expected_salary": {
                "min": user_profile.get("professional_info", {}).get("current_salary", 0),
                "max": user_profile.get("professional_info", {}).get("expected_salary", 0),
                "currency": "INR",
                "period": "yearly"
            },
            "profile_completion_percentage": user_profile.get("profile_completion_count", 0),
            "profile_visits": user_profile.get("profile_visits", 0),
            "last_active": user_profile.get("last_active") if isinstance(user_profile.get("last_active"), str) else (user_profile.get("last_active").isoformat() if user_profile.get("last_active") else datetime.now().isoformat()),
            "is_active": user_profile.get("is_active", True),
            "is_public": user_profile.get("profile_settings", {}).get("is_public", True),
            "email_notifications": user_profile.get("profile_settings", {}).get("email_notifications", True),
            "profile_searchable": user_profile.get("profile_settings", {}).get("profile_searchable", True),
            "preferred_locations": user_profile.get("personal_info", {}).get("location", {}).get("city", "").split(",") if user_profile.get("personal_info", {}).get("location", {}).get("city") else [],
            "created_at": user_profile.get("profile_created_on") if isinstance(user_profile.get("profile_created_on"), str) else (user_profile.get("profile_created_on").isoformat() if user_profile.get("profile_created_on") else datetime.now().isoformat()),
            "updated_at": user_profile.get("updated_at") if isinstance(user_profile.get("updated_at"), str) else (user_profile.get("updated_at").isoformat() if user_profile.get("updated_at") else datetime.now().isoformat()),
            "user_type": user_profile.get("user_type", "candidate"),
            "user_status": user_profile.get("user_status", "active"),
            "user_plan": user_profile.get("user_plan", "free")
        }
        
        return profile_data
        
    except Exception as e:
        logger.error("Error getting user profile: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get user profile")


@router.get("/mock-interviews/history", tags=["Mock Interviews"])
async def get_interview_history(current_user: dict = Depends(get_current_user)):
	"""Get user's mock interview history."""
	try:
		user_id = current_user["user_id"]
		
		# Get mock interviews from database
		interviews_cursor = db.database["mock_interview_sessions"].find({
			"user_id": user_id
		}).sort("created_at", -1).limit(10)
		
		interviews = []
		async for interview in interviews_cursor:
			interviews.append({
				"session_id": interview.get("session_id", ""),
				"role": interview.get("role", "Technical Interview"),
				"score": interview.get("overall_score", 0),
				"created_at": interview.get("created_at", datetime.now()).isoformat() if hasattr(interview.get("created_at"), 'isoformat') else str(interview.get("created_at", datetime.now())),
				"status": "completed"
			})
		
		return {
			"success": True,
			"interviews": interviews
		}
	except Exception as e:
		logger.error("Error getting interview history: %s", e)
		return {
			"success": True,
			"interviews": []
		}


@router.get("/skills/technical", tags=["Skills"])
async def get_technical_skills(current_user: dict = Depends(get_current_user)):
	"""Get user's technical skills."""
	try:
		user_id = current_user["user_id"]
		user_profile = await db.database["users"].find_one({"user_id": user_id})
		
		if not user_profile:
			return []
		
		skills = user_profile.get("skills", [])
		technical_skills = []
		
		for idx, skill in enumerate(skills):
			skill_name = skill if isinstance(skill, str) else skill.get("name", "")
			if skill_name:
				technical_skills.append({
					"skill_id": f"tech_{idx}",
					"skill_name": skill_name,
					"current_level": 60,
					"level_text": "Intermediate"
				})
		
		return technical_skills
	except Exception as e:
		logger.error("Error getting technical skills: %s", e)
		return []


@router.get("/skills/soft", tags=["Skills"])
async def get_soft_skills(current_user: dict = Depends(get_current_user)):
	"""Get user's soft skills."""
	try:
		user_id = current_user["user_id"]
		user_profile = await db.database["users"].find_one({"user_id": user_id})
		
		if not user_profile:
			return []
		
		soft_skills_data = user_profile.get("communication_skills", [])
		soft_skills = []
		
		for idx, skill in enumerate(soft_skills_data):
			skill_name = skill if isinstance(skill, str) else skill.get("name", "")
			if skill_name:
				soft_skills.append({
					"skill_id": f"soft_{idx}",
					"skill_name": skill_name,
					"current_level": 70,
					"level_text": "Advanced"
				})
		
		return soft_skills
	except Exception as e:
		logger.error("Error getting soft skills: %s", e)
		return []


@router.get("/users/{user_id}/applications", tags=["Applications"])
async def get_user_applications_endpoint(user_id: str, current_user: dict = Depends(get_current_user)):
	"""Get all applications for a user from users.overall_jobs_applied."""
	try:
		if current_user["user_id"] != user_id:
			raise HTTPException(status_code=403, detail="Access denied")
		
		user = await db.database["users"].find_one({"user_id": user_id})
		if not user:
			raise HTTPException(status_code=404, detail="User not found")
		
		applied_records = [
			app for app in user.get("overall_jobs_applied", [])
			if isinstance(app, dict) and app.get("is_applied", False)
		]
		
		if not applied_records:
			return {"applications": [], "total_count": 0}
		
		job_ids = [app.get("job_id") for app in applied_records]
		jobs_cursor = db.database["jobs"].find({"job_id": {"$in": job_ids}})
		jobs_map = {}
		async for job in jobs_cursor:
			jobs_map[job.get("job_id")] = job
		
		applications = []
		for app_record in applied_records:
			job = jobs_map.get(app_record.get("job_id"), {})
			if job:
				applications.append({
					"application_id": app_record.get("application_id"),
					"job_title": job.get("title", ""),
					"company": job.get("company", ""),
					"status": app_record.get("status", "applied"),
					"applied_date": app_record.get("applied_date").isoformat() if hasattr(app_record.get("applied_date"), 'isoformat') else str(app_record.get("applied_date", "")),
					"match_percentage": app_record.get("match_percentage"),
					"tailor_resume_done": app_record.get("tailor_resume_done", False),
					"notes": app_record.get("notes"),
					"tags": [],
					"progress_percentage": None
				})
		
		return {"applications": applications, "total_count": len(applications)}
		
	except HTTPException:
		raise
	except Exception as e:
		logger.error("Error getting user applications: %s", e)
		raise HTTPException(status_code=500, detail="Failed to get applications")


@router.get("/analytics/user-stats", tags=["Analytics"])
async def get_user_analytics(current_user: dict = Depends(get_current_user)):
    """Get comprehensive user analytics from database."""
    try:
        user_id = current_user["user_id"]
        
        # Get user applications for analytics
        user_applications = await get_user_applications(user_id, limit=100)
        
        # Get user mock interviews
        user_interviews = await get_user_mock_interviews(user_id, limit=50)
        
        # Get user progress data
        user_progress = await get_user_progress(user_id)
        
        # Calculate application statistics
        total_applications = len(user_applications)
        application_statuses = {}
        for app in user_applications:
            status = app.get("status", "pending")
            application_statuses[status] = application_statuses.get(status, 0) + 1
        
        # Calculate monthly application trends (last 6 months)
        monthly_applications = {}
        for app in user_applications:
            try:
                app_date = datetime.fromisoformat(app.get("created_at", "").replace("Z", "+00:00"))
                month_key = app_date.strftime("%Y-%m")
                monthly_applications[month_key] = monthly_applications.get(month_key, 0) + 1
            except:
                continue
        
        # Calculate interview statistics
        total_interviews = len(user_interviews)
        interview_performance = {
            "total_sessions": total_interviews,
            "average_score": 0,
            "skills_practiced": []
        }
        
        if user_interviews:
            # Calculate average score if available
            scores = [interview.get("score", 0) for interview in user_interviews if interview.get("score")]
            if scores:
                interview_performance["average_score"] = sum(scores) / len(scores)
            
            # Get unique skills practiced
            skills_set = set()
            for interview in user_interviews:
                skills = interview.get("skills", [])
                if isinstance(skills, list):
                    skills_set.update(skills)
            interview_performance["skills_practiced"] = list(skills_set)
        
        # Learning progress
        learning_stats = {
            "completed_resources": user_progress.get("completed_resources", []) if user_progress else [],
            "current_skills": user_progress.get("current_skills", []) if user_progress else [],
            "skill_levels": user_progress.get("skill_levels", {}) if user_progress else {},
            "total_learning_hours": user_progress.get("total_learning_hours", 0) if user_progress else 0,
            "certificates_earned": user_progress.get("certificates_earned", 0) if user_progress else 0
        }
        
        # Profile metrics
        profile_metrics = {
            "profile_completion": current_user.get("profile_completion_count", 0),
            "profile_visits": current_user.get("profile_visits", 0),
            "last_active": current_user.get("last_active", datetime.now()).isoformat(),
            "account_age_days": (datetime.now() - current_user.get("profile_created_on", datetime.now())).days
        }
        
        return {
            "applications": {
                "total": total_applications,
                "by_status": application_statuses,
                "monthly_trend": monthly_applications,
                "success_rate": round((application_statuses.get("accepted", 0) / max(total_applications, 1)) * 100, 1)
            },
            "interviews": interview_performance,
            "learning": learning_stats,
            "profile": profile_metrics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting user analytics: %s", e)
        # Return basic analytics if database fails
        return {
            "applications": {
                "total": 0,
                "by_status": {},
                "monthly_trend": {},
                "success_rate": 0
            },
            "interviews": {
                "total_sessions": 0,
                "average_score": 0,
                "skills_practiced": []
            },
            "learning": {
                "completed_resources": [],
                "current_skills": [],
                "skill_levels": {},
                "total_learning_hours": 0,
                "certificates_earned": 0
            },
            "profile": {
                "profile_completion": current_user.get("profile_completion_count", 0),
                "profile_visits": 0,
                "last_active": datetime.now().isoformat(),
                "account_age_days": 0
            },
            "generated_at": datetime.now().isoformat()
        }


@router.get("/learning/resources", tags=["Learning"])
async def get_learning_resources_endpoint(
    skill: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get learning resources with optional filtering."""
    try:
        resources = await get_learning_resources(skill=skill, level=level, limit=limit)
        
        return {
            "resources": resources,
            "total_count": len(resources),
            "filters": {
                "skill": skill,
                "level": level,
                "limit": limit
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting learning resources: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get learning resources")


@router.get("/learning/progress", tags=["Learning"])
async def get_learning_progress_endpoint(current_user: dict = Depends(get_current_user)):
    """Get user's learning progress."""
    try:
        user_id = current_user["user_id"]
        progress = await get_user_progress(user_id)
        
        if not progress:
            # Return default progress structure
            return {
                "user_id": user_id,
                "completed_resources": [],
                "current_skills": [],
                "skill_levels": {},
                "total_learning_hours": 0,
                "certificates_earned": 0,
                "learning_streaks": {
                    "current_streak": 0,
                    "longest_streak": 0,
                    "last_activity": None
                },
                "updated_at": datetime.now().isoformat()
            }
        
        # Enhance progress data with additional metrics
        enhanced_progress = progress.copy()
        enhanced_progress["learning_streaks"] = {
            "current_streak": 0,  # Could be calculated from activity data
            "longest_streak": 0,
            "last_activity": progress.get("updated_at")
        }
        
        return enhanced_progress
        
    except Exception as e:
        logger.error("Error getting learning progress: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get learning progress")


def calculate_job_match_score(job, user_skills, user_certifications, user_experience_keywords):
    """
    Calculate job matching score based on user skills vs job requirements.
    Focus on skills matching between user and HR job postings.
    
    Returns score between 0.0 and 1.0
    """
    # Normalize user inputs
    user_skills_lower = [skill.lower().strip() for skill in user_skills if skill and skill.strip()]
    user_certs_lower = [cert.lower().strip() for cert in user_certifications if cert and cert.strip()]
    user_exp_keywords = [kw.lower().strip() for kw in user_experience_keywords if len(kw) > 3]
    
    if not user_skills_lower:
        return 0.0
    
    # Get job requirements
    job_skills_required = job.get("skills_required", [])
    job_skills_preferred = job.get("skills_preferred", [])
    job_skills = job.get("skills", [])  # Generic skills field
    
    # Combine all job skill requirements
    all_job_skills = []
    all_job_skills.extend(job_skills_required)
    all_job_skills.extend(job_skills_preferred) 
    all_job_skills.extend(job_skills)
    
    # Remove duplicates and normalize
    job_skills_lower = list(set([skill.lower().strip() for skill in all_job_skills if skill and skill.strip()]))
    
    if not job_skills_lower:
        return 0.0
    
    logger.debug("User skills: %s | Job skills: %s", user_skills_lower, job_skills_lower)
    
    # CORE SKILLS MATCHING: User Skills vs Job Requirements
    skills_matched = 0
    matched_skills = []
    
    for user_skill in user_skills_lower:
        for job_skill in job_skills_lower:
            # Exact match or partial match
            if (user_skill == job_skill or 
                user_skill in job_skill or 
                job_skill in user_skill or
                # Handle common variations (e.g., "js" vs "javascript")
                (user_skill == "js" and "javascript" in job_skill) or
                (user_skill == "javascript" and "js" in job_skill) or
                (user_skill == "react" and "reactjs" in job_skill) or
                (user_skill == "node" and "nodejs" in job_skill)):
                
                skills_matched += 1
                matched_skills.append(f"{user_skill} ↔ {job_skill}")
                break  # Only count each user skill once
    
    # Calculate match percentage based on user's skills
    user_skills_match_percentage = skills_matched / len(user_skills_lower)
    
    logger.debug("Skills matched: %d/%d = %.2f%%", skills_matched, len(user_skills_lower), user_skills_match_percentage * 100)
    
    # BONUS SCORING
    bonus_score = 0.0
    
    # Certification bonus
    if user_certs_lower and job_skills_lower:
        cert_matches = 0
        for cert in user_certs_lower:
            for job_skill in job_skills_lower:
                if cert in job_skill or job_skill in cert:
                    cert_matches += 1
                    break
        if cert_matches > 0:
            bonus_score += 0.1  # 10% bonus for certification matches
    
    # Experience keywords bonus (from job description)
    if user_exp_keywords and job.get("description"):
        description = job["description"].lower()
        exp_matches = 0
        for keyword in user_exp_keywords[:10]:  # Limit to top 10 keywords
            if keyword in description:
                exp_matches += 1
        if exp_matches >= 3:  # Need at least 3 experience matches
            bonus_score += 0.05  # 5% bonus for experience alignment
    
    # Calculate final score
    final_score = user_skills_match_percentage + bonus_score
    final_score = min(final_score, 1.0)  # Cap at 100%
    
    # Apply minimum threshold: include if user has 20-30% skill match
    if user_skills_match_percentage >= 0.20:
        return final_score
    else:
        return 0.0


@router.post("/jobs", tags=["Jobs"])
async def get_job_listings(
    request: JobSearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get job listings with intelligent matching based on user skills sent in request body."""
    
    try:
        # Extract parameters from request body
        page = request.page
        per_page = request.per_page
        keywords = request.keywords
        location = request.location
        experience_level = request.experience_level
        employment_type = request.employment_type
        job_type = request.job_type
        
        # Get user skills from request body (primary source)
        user_skills = request.user_skills
        user_certifications = request.user_certifications
        user_experience_keywords = request.user_experience_keywords
        
        # Fallback to user profile if skills not provided in request
        user_id = current_user["user_id"]
        if not user_skills:
            user_profile = await get_user_profile(user_id)
            logger.debug("User profile skills: %s", user_profile.get('skills', []) if user_profile else 'No profile')
            if user_profile:
                user_skills = user_profile.get("skills", [])
                user_certifications = [cert.get("name", "") for cert in user_profile.get("certifications", []) if isinstance(cert, dict)]
                user_certifications.extend([cert for cert in user_profile.get("certifications", []) if isinstance(cert, str)])
                
                # Get experience keywords from professional info
                prof_info = user_profile.get("professional_info", {})
                if prof_info.get("professional_summary"):
                    user_experience_keywords.extend(prof_info["professional_summary"].lower().split())
                if prof_info.get("key_contributions"):
                    user_experience_keywords.extend(prof_info["key_contributions"].lower().split())
        
        logger.debug("Job matching - skills: %d, source: %s",
                     len(user_skills), 'Request Body' if user_skills else 'User Profile')
        
        # Build basic MongoDB query
        query = {"is_active": True}
        
        # Keywords search (maintain existing functionality)
        if keywords:
            keyword_regex = {"$regex": keywords, "$options": "i"}
            query["$or"] = [
                {"title": keyword_regex},
                {"company": keyword_regex},
                {"description": keyword_regex},
                {"skills_required": keyword_regex},
                {"skills_preferred": keyword_regex}
            ]
        
        # Apply filters (ignoring location, salary as per requirement)
        if experience_level and experience_level not in ["all", "All Levels"]:
            query["experience_level"] = experience_level.replace("-", "_")
        
        if employment_type and employment_type not in ["all", "All Types"]:
            query["employment_type"] = employment_type.replace("-", "_")
        
        if job_type and job_type not in ["all", "All Types"]:
            query["job_type"] = job_type.replace("-", "_")
        
        # Get current user's applied jobs (only is_applied=True, handle legacy strings)
        user_profile = await db.database["users"].find_one({"user_id": user_id})
        applied_jobs_records = user_profile.get("overall_jobs_applied", []) if user_profile else []
        user_applied_jobs = []
        applied_jobs_map = {}
        for app in applied_jobs_records:
            if isinstance(app, dict) and app.get("is_applied", False):
                user_applied_jobs.append(app.get("job_id"))
                applied_jobs_map[app.get("job_id")] = app
            elif isinstance(app, str):
                user_applied_jobs.append(app)
        
        # Get jobs with a reasonable limit to prevent memory issues
        # Score in batches — fetch max 200 jobs for scoring (covers most use cases)
        MAX_JOBS_FOR_SCORING = 200
        collection = db.database["jobs"]
        cursor = collection.find(query).sort("posted_date", -1).limit(MAX_JOBS_FOR_SCORING)
        
        all_jobs = []
        async for job in cursor:
            job["_id"] = str(job["_id"])
            
            # Calculate intelligent matching score
            match_score = calculate_job_match_score(job, user_skills, user_certifications, user_experience_keywords)
            job["match_score"] = match_score
            
            # Check if user already applied and add application state
            job_id = job.get("job_id")
            job["already_applied"] = job_id in user_applied_jobs
            
            # Add application state if user has applied
            if job_id in user_applied_jobs:
                app_record = applied_jobs_map.get(job_id)
                if app_record:
                    job["match_analysis_done"] = app_record.get("match_analysis_done", False)
                    job["tailor_resume_done"] = app_record.get("tailor_resume_done", False)
                    if app_record.get("match_analysis_done") or app_record.get("tailor_resume_done"):
                        job["match_percentage"] = app_record.get("match_percentage", 0)
            
            all_jobs.append(job)
        
        # Sort by match score (highest first), then by posted_date (newest first) for ties
        all_jobs.sort(key=lambda x: (x["match_score"], x.get("posted_date", "")), reverse=True)
        
        logger.info("Job search: %d jobs matched criteria", len(all_jobs))
        
        # Apply pagination to scored and filtered results
        total_count = len(all_jobs)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_jobs = all_jobs[start_idx:end_idx]
        
        return {
            "jobs": paginated_jobs,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page,
            "has_next": end_idx < total_count,
            "has_prev": page > 1,
            "matching_info": {
                "user_skills_provided": len(user_skills),
                "user_skills": user_skills,
                "total_jobs_before_matching": await collection.count_documents(query),
                "jobs_after_skill_matching": total_count,
                "matching_criteria": "User skills vs Job requirements (20%+ threshold)",
                "data_source": "Request Body" if user_skills else "User Profile"
            },
            "filters": {
                "locations": ["All Locations", "Bangalore", "Mumbai", "Hyderabad", "Remote"],
                "experience_levels": ["All Levels", "entry", "junior", "mid", "senior", "lead", "executive"],
                "employment_types": ["All Types", "full_time", "part_time", "contract", "temporary", "internship"],
                "job_types": ["All Types", "remote", "onsite", "hybrid"],
                "companies": ["All Companies"],
                "salary_ranges": [
                    {"label": "All Ranges", "min": 0, "max": 10000000},
                    {"label": "₹10-15 LPA", "min": 1000000, "max": 1500000},
                    {"label": "₹15-20 LPA", "min": 1500000, "max": 2000000},
                    {"label": "₹20-25 LPA", "min": 2000000, "max": 2500000},
                    {"label": "₹25+ LPA", "min": 2500000, "max": 10000000}
                ]
            }
        }
        
    except Exception as e:
        logger.error("Database error in job search: %s", e, exc_info=True)
        
        # Return empty results if database fails
        return {
            "jobs": [],
            "total_count": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0,
            "has_next": False,
            "has_prev": False,
            "error": f"Failed to load jobs from database: {str(e)}",
            "filters": {
                "locations": ["All Locations"],
                "experience_levels": ["All Levels"],
                "employment_types": ["All Types"],
                "job_types": ["All Types"],
                "companies": ["All Companies"],
                "salary_ranges": []
            }
        }



