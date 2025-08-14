"""
Dashboard and Profile API endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from job_db import JobDatabase

# Create router for dashboard and profile endpoints
router = APIRouter()

# Initialize job database
job_db = JobDatabase()


"""
Dashboard and Profile API endpoints.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from job_db import JobDatabase
from auth_endpoints import get_current_user
from db_simple import (
    db, get_user_profile, get_user_applications, get_user_mock_interviews,
    get_user_dashboard, update_user_dashboard, get_learning_resources,
    get_user_progress
)

# Create router for dashboard and profile endpoints
router = APIRouter()

# Initialize job database
job_db = JobDatabase()


@router.get("/dashboard", tags=["Dashboard"])
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    """Dashboard endpoint that returns real data from MongoDB for authenticated user."""
    
    try:
        user_id = current_user["user_id"]
        user_type = current_user.get("user_type", "candidate")
        
        # Get user applications from database
        user_applications = await get_user_applications(user_id, limit=50)
        
        # Get user mock interviews from database
        user_interviews = await get_user_mock_interviews(user_id, limit=20)
        
        # Get user profile data
        user_profile = await get_user_profile(user_id)
        profile_completion = user_profile.get("profile_completion_count", 0) if user_profile else 0
        
        # Calculate application statistics
        total_applications = len(user_applications)
        
        # Calculate interviews scheduled (from applications or separate interview records)
        interviews_scheduled = len([app for app in user_applications 
                                  if app.get("status") == "interview_scheduled"]) + len(user_interviews)
        
        # Get recent applications for trend calculation
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_applications = [app for app in user_applications 
                             if datetime.fromisoformat(app.get("created_at", "").replace("Z", "+00:00")) > week_ago]
        
        # Calculate trend percentages
        apps_trend = len(recent_applications) if total_applications > 0 else 0
        
        # Get total job count from database
        try:
            total_jobs = await job_db.get_total_job_count()
            active_jobs = await job_db.get_active_job_count()
        except Exception:
            # Use actual database counts as fallback
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                client = AsyncIOMotorClient("mongodb://localhost:27017")
                db_fallback = client.jobmitra
                total_jobs = await db_fallback.jobs.count_documents({})
                active_jobs = await db_fallback.jobs.count_documents({"is_active": True})
                client.close()
            except Exception:
                total_jobs = 0  # No hardcoded fallback
                active_jobs = 0
        
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
                    "label": "Interviews Scheduled", 
                    "value": interviews_scheduled,
                    "icon": "event",
                    "color": "accent",
                    "trend": {
                        "direction": "up" if interviews_scheduled > 0 else "neutral",
                        "percentage": min(interviews_scheduled * 20, 100),
                        "period": "this week"
                    }
                },
                {
                    "id": "total-jobs",
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
            # Get HR-specific metrics from database
            try:
                # Query actual HR jobs from database instead of posted_jobs
                from motor.motor_asyncio import AsyncIOMotorClient
                client = AsyncIOMotorClient("mongodb://localhost:27017")
                db_hr = client.jobmitra
                
                hr_jobs_count = await db_hr.jobs.count_documents({"posted_by": user_id})
                hr_active_jobs = await db_hr.jobs.count_documents({"posted_by": user_id, "is_active": True})
                hr_applications_received = await db_hr.applications.count_documents({"job_posted_by": user_id})
                
                client.close()
                
            except Exception:
                # Fallback to zero if database queries fail
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
        
        # Build recent activities from real data
        recent_activities = []
        
        # Add application activities (most recent first)
        for app in user_applications[:5]:  # Limit to 5 most recent
            activity = {
                "id": app.get("_id", ""),
                "title": f"Applied to {app.get('job_title', 'Unknown Position')} at {app.get('company', 'Unknown Company')}",
                "icon": "send",
                "timestamp": app.get("created_at", datetime.now().isoformat()),
                "type": "application",
                "status": app.get("status", "pending")
            }
            recent_activities.append(activity)
        
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
        
        # Sort activities by timestamp (most recent first)
        recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
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
        await update_user_dashboard(user_id, dashboard_data)
        
        return dashboard_data
        
    except Exception as e:
        print(f"❌ Error getting dashboard data: {e}")
        
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
                    "label": "Interviews Scheduled", 
                    "value": 0,
                    "icon": "event",
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
            "skills": user_profile.get("skills", []),
            "professional_summary": user_profile.get("professional_info", {}).get("professional_summary", ""),
            "certifications": [cert.get("name", "") for cert in user_profile.get("certifications", [])],
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
            "last_active": user_profile.get("last_active", datetime.now()).isoformat(),
            "is_active": user_profile.get("is_active", True),
            "is_public": user_profile.get("profile_settings", {}).get("is_public", True),
            "email_notifications": user_profile.get("profile_settings", {}).get("email_notifications", True),
            "profile_searchable": user_profile.get("profile_settings", {}).get("profile_searchable", True),
            "preferred_locations": user_profile.get("personal_info", {}).get("location", {}).get("city", "").split(",") if user_profile.get("personal_info", {}).get("location", {}).get("city") else [],
            "created_at": user_profile.get("profile_created_on", datetime.now()).isoformat(),
            "updated_at": user_profile.get("updated_at", datetime.now()).isoformat(),
            "user_type": user_profile.get("user_type", "candidate"),
            "user_status": user_profile.get("user_status", "active"),
            "user_plan": user_profile.get("user_plan", "free")
        }
        
        return profile_data
        
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")


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
        print(f"❌ Error getting user analytics: {e}")
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
        print(f"❌ Error getting learning resources: {e}")
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
        print(f"❌ Error getting learning progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get learning progress")


@router.get("/jobs", tags=["Jobs"])
async def get_job_listings(
    page: int = 1, 
    per_page: int = 10,
    keywords: str = None,
    location: str = None,
    experience_level: str = None,
    employment_type: str = None,
    job_type: str = None
):
    """Get job listings for job search page with pagination and filtering."""
    
    try:
        # Use the real database for job search
        search_filters = {}
        
        if keywords:
            search_filters["keywords"] = keywords
        if location and location != "all":
            search_filters["location"] = location
        if experience_level and experience_level != "all":
            search_filters["experience_level"] = experience_level.replace("-", "_")
        if employment_type and employment_type != "all":
            search_filters["employment_type"] = employment_type.replace("-", "_")
        if job_type and job_type != "all":
            search_filters["job_type"] = job_type.replace("-", "_")
            
        # Search jobs using database
        search_result = await job_db.search_jobs(
            filters=search_filters,
            page=page,
            limit=per_page
        )
        
        # Return database results directly
        all_jobs = search_result["jobs"]
        total_count = search_result["total"]
        
        return {
            "jobs": all_jobs,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page,
            "has_next": page * per_page < total_count,
            "has_prev": page > 1,
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
        print(f"Database error in job search: {e}")
        # Return empty results if database fails
        return {
            "jobs": [],
            "total_count": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0,
            "has_next": False,
            "has_prev": False,
            "error": "Failed to load jobs from database",
            "filters": {
                "locations": ["All Locations"],
                "experience_levels": ["All Levels"],
                "employment_types": ["All Types"],
                "job_types": ["All Types"],
                "companies": ["All Companies"],
                "salary_ranges": []
            }
        }


@router.get("/applications", tags=["Applications"])
async def get_applications(
    page: int = 1, 
    per_page: int = 10,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get user applications with pagination from database."""
    try:
        user_id = current_user["user_id"]
        
        # Get user applications from database
        all_applications = await get_user_applications(user_id, limit=1000)  # Get all for filtering
        
        # Filter by status if provided
        if status and status != "all":
            filtered_applications = [app for app in all_applications if app.get("status") == status]
        else:
            filtered_applications = all_applications
        
        # Sort by creation date (most recent first)
        filtered_applications.sort(
            key=lambda x: x.get("created_at", ""), 
            reverse=True
        )
        
        # Calculate pagination
        total_count = len(filtered_applications)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_applications = filtered_applications[start_idx:end_idx]
        
        # Enhance application data with additional fields if needed
        enhanced_applications = []
        for app in paginated_applications:
            enhanced_app = app.copy()
            
            # Ensure required fields are present
            enhanced_app.setdefault("application_id", app.get("_id", ""))
            enhanced_app.setdefault("user_id", user_id)
            enhanced_app.setdefault("status", "pending")
            enhanced_app.setdefault("applied_date", app.get("created_at"))
            enhanced_app.setdefault("last_updated", app.get("updated_at", app.get("created_at")))
            enhanced_app.setdefault("priority", "medium")
            enhanced_app.setdefault("progress_percentage", 25)
            enhanced_app.setdefault("interview_stages", [])
            enhanced_app.setdefault("follow_up_dates", [])
            enhanced_app.setdefault("notes", "")
            enhanced_app.setdefault("tags", [])
            
            # Calculate progress percentage based on status
            status_progress = {
                "applied": 25,
                "under_review": 50,
                "interview_scheduled": 75,
                "interview_completed": 85,
                "offer_received": 100,
                "accepted": 100,
                "rejected": 100,
                "withdrawn": 100
            }
            enhanced_app["progress_percentage"] = status_progress.get(
                enhanced_app["status"], 25
            )
            
            enhanced_applications.append(enhanced_app)
        
        # Note: No fallback sample data - return empty list if no real applications
        
        return {
            "applications": enhanced_applications,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page,
            "has_next": end_idx < total_count,
            "has_prev": page > 1,
            "filters": {
                "status": status,
                "available_statuses": [
                    "all", "applied", "under_review", "interview_scheduled",
                    "interview_completed", "offer_received", "accepted", "rejected", "withdrawn"
                ]
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error getting applications: {e}")
        # Return empty result with error info
        return {
            "applications": [],
            "total_count": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0,
            "has_next": False,
            "has_prev": False,
            "error": "Failed to load applications from database",
            "generated_at": datetime.now().isoformat()
        }
