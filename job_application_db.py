"""
Database operations for job applications
"""

import logging

logger = logging.getLogger(__name__)

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from db import db
from job_application_schemas import JobApplication, ApplicantProfile, ProfileMatchAnalysis, ApplicationStatus, JobApplicationsResponse
from auth_db import get_user_by_id

class JobApplicationDatabase:
    """Database operations for job applications"""
    
    def __init__(self):
        self.applications_collection = "job_applications"
        self.jobs_collection = "jobs"
        self.users_collection = "users"
    
    async def apply_for_job(self, job_id: str, user_id: str, cover_letter: Optional[str] = None) -> str:
        """Apply for a job"""
        try:
            # Check if user already applied
            existing = await db.database[self.applications_collection].find_one({
                "job_id": job_id,
                "user_id": user_id
            })
            
            if existing:
                raise ValueError("User has already applied for this job")
            
            # Get user profile for match analysis
            user = await get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get job details
            job = await db.database[self.jobs_collection].find_one({"job_id": job_id})
            if not job:
                raise ValueError("Job not found")
            
            # Generate application ID
            application_id = f"app_{uuid.uuid4().hex[:12]}"
            
            # Calculate profile match
            profile_match = await self._calculate_profile_match(user, job)
            
            # Create application
            application = {
                "application_id": application_id,
                "job_id": job_id,
                "user_id": user_id,
                "applied_date": datetime.utcnow(),
                "status": ApplicationStatus.APPLIED.value,
                "cover_letter": cover_letter,
                "profile_match": profile_match.dict() if profile_match else None,
                "source": "internal",
                "notes": None
            }
            
            # Insert application
            await db.database[self.applications_collection].insert_one(application)
            
            # Update job application count
            await db.database[self.jobs_collection].update_one(
                {"job_id": job_id},
                {"$inc": {"applications_count": 1}}
            )
            
            # Add job to user's applied jobs list
            await db.database[self.users_collection].update_one(
                {"user_id": user_id},
                {"$addToSet": {"overall_jobs_applied": job_id}}
            )
            
            return application_id
            
        except Exception as e:
            logger.error("applying for job: %s", e)
            raise e
    
    async def get_job_applications(self, job_id: str, hr_user_id: str) -> JobApplicationsResponse:
        """Get all applications for a job from jobs.applications_received + users collection"""
        try:
            # Verify job belongs to HR user
            job = await db.database[self.jobs_collection].find_one({
                "job_id": job_id,
                "posted_by_hr_id": hr_user_id
            })
            
            if not job:
                raise ValueError("Job not found or access denied")
            
            applications_received = job.get("applications_received", [])
            
            applications = []
            for app in applications_received:
                user = await get_user_by_id(app.get("user_id", ""))
                if not user:
                    continue
                
                applicant = ApplicantProfile(
                    user_id=user["user_id"],
                    full_name=app.get("user_name", f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()),
                    email=app.get("user_email", user.get("email", "")),
                    phone=user.get("phone"),
                    overall_experience_years=user.get("overall_experience_years"),
                    current_role=user.get("current_role", user.get("professional_info", {}).get("current_role")),
                    skills=user.get("skills", []),
                    highest_qualification=user.get("highest_qualification"),
                    application_id=app.get("application_id", f"{user['user_id']}_{job_id}"),
                    applied_date=app.get("applied_date", app.get("applied_at", datetime.utcnow())),
                    status=ApplicationStatus(app.get("status", "applied")),
                    profile_match=None
                )
                applications.append(applicant)
            
            return JobApplicationsResponse(
                job_id=job_id,
                job_title=job["title"],
                total_applications=len(applications),
                applications=applications
            )
            
        except Exception as e:
            logger.error("getting job applications: %s", e)
            raise e
    
    async def update_application_status(self, application_id: str, status: ApplicationStatus, hr_user_id: str, notes: Optional[str] = None) -> bool:
        """Update application status (HR only)"""
        try:
            # Get application
            application = await db.database[self.applications_collection].find_one({
                "application_id": application_id
            })
            
            if not application:
                raise ValueError("Application not found")
            
            # Verify job belongs to HR user
            job = await db.database[self.jobs_collection].find_one({
                "job_id": application["job_id"],
                "posted_by_hr_id": hr_user_id
            })
            
            if not job:
                raise ValueError("Access denied")
            
            # Update application
            result = await db.database[self.applications_collection].update_one(
                {"application_id": application_id},
                {
                    "$set": {
                        "status": status.value,
                        "notes": notes,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error("updating application status: %s", e)
            raise e
    
    async def _calculate_profile_match(self, user: Dict[str, Any], job: Dict[str, Any]) -> Optional[ProfileMatchAnalysis]:
        """Calculate profile match analysis"""
        try:
            user_skills = set(skill.lower() for skill in user.get("skills", []))
            job_skills = set(skill.lower() for skill in job.get("skills_required", []))
            
            # Skills match
            matched_skills = list(user_skills.intersection(job_skills))
            missing_skills = list(job_skills - user_skills)
            skills_match = (len(matched_skills) / len(job_skills) * 100) if job_skills else 100
            
            # Experience match
            user_exp = user.get("overall_experience_years", 0)
            job_exp_map = {"entry": 1, "mid": 3, "senior": 5, "lead": 7, "executive": 10}
            required_exp = job_exp_map.get(job.get("experience_level", "mid"), 3)
            
            if user_exp >= required_exp:
                experience_match = 100
            elif user_exp >= required_exp * 0.7:
                experience_match = 80
            elif user_exp >= required_exp * 0.5:
                experience_match = 60
            else:
                experience_match = 40
            
            # Education match (simplified)
            education_match = 80 if user.get("highest_qualification") else 60
            
            # Overall match
            overall_match = (skills_match * 0.5 + experience_match * 0.3 + education_match * 0.2)
            
            # Generate recommendations
            strengths = []
            areas_for_improvement = []
            
            if skills_match >= 70:
                strengths.append("Strong technical skills match")
            else:
                areas_for_improvement.append("Could improve technical skills")
            
            if experience_match >= 80:
                strengths.append("Excellent experience level")
            elif experience_match < 60:
                areas_for_improvement.append("May need more experience")
            
            # Recommendation
            if overall_match >= 80:
                recommendation = "Highly Recommended"
            elif overall_match >= 60:
                recommendation = "Recommended"
            elif overall_match >= 40:
                recommendation = "Consider"
            else:
                recommendation = "Not Recommended"
            
            return ProfileMatchAnalysis(
                overall_match=int(overall_match),
                skills_match=int(skills_match),
                experience_match=int(experience_match),
                education_match=int(education_match),
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                strengths=strengths,
                areas_for_improvement=areas_for_improvement,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error("calculating profile match: %s", e)
            return None
    
    async def get_hr_jobs_with_applications(self, hr_email: str) -> List[Dict[str, Any]]:
        """Get all jobs posted by HR user with application counts"""
        try:
            # Get HR user by email
            hr_user = await db.database[self.users_collection].find_one({"email": hr_email})
            
            if not hr_user:
                return []
            
            hr_user_id = hr_user["user_id"]
            
            # Get all jobs posted by this HR
            jobs_cursor = db.database[self.jobs_collection].find({
                "posted_by_hr_id": hr_user_id
            }).sort("posted_date", -1)
            
            jobs_with_applications = []
            async for job in jobs_cursor:
                # Use the existing applications_count from job document
                # This should already be updated when applications are created
                job_data = dict(job)
                
                # Convert ObjectId to string for JSON serialization
                if "_id" in job_data:
                    job_data["_id"] = str(job_data["_id"])
                
                # Convert datetime objects to ISO strings
                for key, value in job_data.items():
                    if hasattr(value, 'isoformat'):
                        job_data[key] = value.isoformat()
                
                jobs_with_applications.append(job_data)
            
            return jobs_with_applications
            
        except Exception as e:
            logger.error("getting HR jobs with applications: %s", e)
            raise e