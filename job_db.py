"""
Database operations for job postings functionality
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import secrets
import string

from db_simple import db
from job_schemas import JobListing, JobPostRequest, JobSearchFilters, HRJobDashboard
from auth_db import get_user_by_id


class JobDatabase:
    """Database operations for job management"""
    
    def __init__(self):
        self.jobs_collection = "jobs"
        self.applications_collection = "job_applications"
    
    async def create_job_posting(self, job_data: JobPostRequest, hr_user_id: str) -> str:
        """Create a new job posting"""
        try:
            # Generate unique job_id
            job_id = self._generate_job_id(job_data.title, job_data.company)
            
            # Create job document
            job_doc = {
                "job_id": job_id,
                "title": job_data.title,
                "company": job_data.company,
                "location": job_data.location.dict(),
                "employment_type": job_data.employment_type.value,
                "experience_level": job_data.experience_level.value,
                "job_type": job_data.job_type.value,
                "salary": job_data.salary.dict() if job_data.salary else None,
                "description": job_data.description,
                "requirements": job_data.requirements,
                "responsibilities": job_data.responsibilities,
                "skills_required": job_data.skills_required,
                "skills_preferred": job_data.skills_preferred or [],
                "benefits": job_data.benefits or [],
                "company_info": job_data.company_info.dict(),
                "hr_contact": job_data.hr_contact.dict(),
                "application_deadline": job_data.application_deadline,
                "external_apply_url": job_data.external_apply_url,
                "application_instructions": job_data.application_instructions,
                "tags": job_data.tags or [],
                "learning_resources": [lr.dict() for lr in (job_data.learning_resources or [])],
                
                # Metadata
                "posted_date": datetime.utcnow(),
                "updated_date": datetime.utcnow(),
                "is_active": True,
                "posted_by_hr_id": hr_user_id,
                "views_count": 0,
                "applications_count": 0,
                "source": "internal",
                "job_score": None,
                "match_percentage": None
            }
            
            # Insert into database
            result = await db.database[self.jobs_collection].insert_one(job_doc)
            job_doc["_id"] = str(result.inserted_id)
            
            print(f"✅ Job posting created: {job_id}")
            return job_id
            
        except Exception as e:
            print(f"❌ Error creating job posting: {e}")
            raise Exception(f"Failed to create job posting: {str(e)}")
    
    async def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by job_id"""
        try:
            job = await db.database[self.jobs_collection].find_one({"job_id": job_id})
            if job:
                job["_id"] = str(job["_id"])
            return job
        except Exception as e:
            print(f"❌ Error getting job by ID: {e}")
            return None
    
    async def get_jobs_by_hr(self, hr_user_id: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get all jobs posted by a specific HR user"""
        try:
            skip = (page - 1) * per_page
            
            # Get total count
            total_count = await db.database[self.jobs_collection].count_documents({
                "posted_by_hr_id": hr_user_id
            })
            
            # Get jobs with pagination
            cursor = db.database[self.jobs_collection].find({
                "posted_by_hr_id": hr_user_id
            }).sort("posted_date", -1).skip(skip).limit(per_page)
            
            jobs = []
            async for job in cursor:
                job["_id"] = str(job["_id"])
                jobs.append(job)
            
            return {
                "jobs": jobs,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page,
                "has_next": skip + per_page < total_count,
                "has_prev": page > 1
            }
            
        except Exception as e:
            print(f"❌ Error getting HR jobs: {e}")
            return {"jobs": [], "total_count": 0, "page": page, "per_page": per_page}
    
    async def search_jobs(self, filters: JobSearchFilters, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Search jobs with filters - replaces the mock data in dashboard_endpoints.py"""
        try:
            # Build MongoDB query
            query = {"is_active": True}
            
            # Keywords search
            if filters.keywords:
                keyword_regex = {"$regex": filters.keywords, "$options": "i"}
                query["$or"] = [
                    {"title": keyword_regex},
                    {"company": keyword_regex},
                    {"description": keyword_regex},
                    {"skills_required": {"$in": [keyword_regex]}},
                    {"skills_preferred": {"$in": [keyword_regex]}}
                ]
            
            # Location filter
            if filters.location and filters.location != "all":
                location_regex = {"$regex": filters.location.replace("-", " "), "$options": "i"}
                query["$or"] = query.get("$or", []) + [
                    {"location.city": location_regex},
                    {"location.state": location_regex},
                    {"location.country": location_regex}
                ]
                
                if filters.location.lower() == "remote":
                    query["location.is_remote"] = True
            
            # Experience level filter
            if filters.experience_level:
                if isinstance(filters.experience_level, list):
                    query["experience_level"] = {"$in": [level.value for level in filters.experience_level]}
                else:
                    query["experience_level"] = filters.experience_level.value
            
            # Employment type filter
            if filters.employment_type:
                if isinstance(filters.employment_type, list):
                    query["employment_type"] = {"$in": [emp_type.value for emp_type in filters.employment_type]}
                else:
                    query["employment_type"] = filters.employment_type.value
            
            # Job type filter
            if filters.job_type:
                if isinstance(filters.job_type, list):
                    query["job_type"] = {"$in": [job_type.value for job_type in filters.job_type]}
                else:
                    query["job_type"] = filters.job_type.value
            
            # Salary range filter
            if filters.salary_min or filters.salary_max:
                salary_query = {}
                if filters.salary_min:
                    salary_query["salary.min"] = {"$gte": filters.salary_min}
                if filters.salary_max:
                    salary_query["salary.max"] = {"$lte": filters.salary_max}
                query.update(salary_query)
            
            # Date filter
            if filters.posted_within_days:
                cutoff_date = datetime.utcnow() - timedelta(days=filters.posted_within_days)
                query["posted_date"] = {"$gte": cutoff_date}
            
            # Get total count
            total_count = await db.database[self.jobs_collection].count_documents(query)
            
            # Get jobs with pagination
            skip = (page - 1) * per_page
            cursor = db.database[self.jobs_collection].find(query).sort("posted_date", -1).skip(skip).limit(per_page)
            
            jobs = []
            async for job in cursor:
                job["_id"] = str(job["_id"])
                jobs.append(job)
            
            # Get filter options for frontend
            filter_options = await self._get_filter_options()
            
            return {
                "jobs": jobs,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page,
                "has_next": skip + per_page < total_count,
                "has_prev": page > 1,
                "filters": filter_options
            }
            
        except Exception as e:
            print(f"❌ Error searching jobs: {e}")
            return {"jobs": [], "total_count": 0, "page": page, "per_page": per_page}
    
    async def update_job(self, job_id: str, update_data: Dict[str, Any], hr_user_id: str) -> bool:
        """Update job posting (only by the HR who posted it)"""
        try:
            update_data["updated_date"] = datetime.utcnow()
            
            result = await db.database[self.jobs_collection].update_one(
                {"job_id": job_id, "posted_by_hr_id": hr_user_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Error updating job: {e}")
            return False
    
    async def delete_job(self, job_id: str, hr_user_id: str) -> bool:
        """Delete job posting (only by the HR who posted it)"""
        try:
            # Soft delete - mark as inactive instead of actually deleting
            result = await db.database[self.jobs_collection].update_one(
                {"job_id": job_id, "posted_by_hr_id": hr_user_id},
                {"$set": {"is_active": False, "updated_date": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"❌ Error deleting job: {e}")
            return False
    
    async def get_hr_dashboard(self, hr_user_id: str) -> HRJobDashboard:
        """Get dashboard stats for HR user"""
        try:
            # Get all jobs by this HR
            all_jobs = await db.database[self.jobs_collection].find({
                "posted_by_hr_id": hr_user_id
            }).to_list(None)
            
            # Calculate stats
            total_jobs = len(all_jobs)
            active_jobs = len([job for job in all_jobs if job.get("is_active", True)])
            inactive_jobs = total_jobs - active_jobs
            total_applications = sum(job.get("applications_count", 0) for job in all_jobs)
            
            # Jobs expiring soon (within 7 days)
            cutoff_date = datetime.utcnow() + timedelta(days=7)
            jobs_expiring_soon = len([
                job for job in all_jobs 
                if job.get("application_deadline") and 
                   datetime.fromisoformat(str(job["application_deadline"])) <= cutoff_date
            ])
            
            # Recent jobs (last 5)
            recent_jobs = sorted(all_jobs, key=lambda x: x.get("posted_date", datetime.min), reverse=True)[:5]
            for job in recent_jobs:
                job["_id"] = str(job["_id"])
            
            return HRJobDashboard(
                total_jobs_posted=total_jobs,
                active_jobs=active_jobs,
                inactive_jobs=inactive_jobs,
                total_applications_received=total_applications,
                jobs_expiring_soon=jobs_expiring_soon,
                recent_jobs=recent_jobs
            )
            
        except Exception as e:
            print(f"❌ Error getting HR dashboard: {e}")
            return HRJobDashboard(
                total_jobs_posted=0,
                active_jobs=0,
                inactive_jobs=0,
                total_applications_received=0,
                jobs_expiring_soon=0,
                recent_jobs=[]
            )
    
    async def increment_job_views(self, job_id: str) -> bool:
        """Increment view count for a job"""
        try:
            result = await db.database[self.jobs_collection].update_one(
                {"job_id": job_id},
                {"$inc": {"views_count": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error incrementing job views: {e}")
            return False
    
    async def increment_job_applications(self, job_id: str) -> bool:
        """Increment application count for a job"""
        try:
            result = await db.database[self.jobs_collection].update_one(
                {"job_id": job_id},
                {"$inc": {"applications_count": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error incrementing job applications: {e}")
            return False
    
    def _generate_job_id(self, title: str, company: str) -> str:
        """Generate unique job ID"""
        # Create base from title and company
        title_part = "".join(c.lower() for c in title if c.isalnum() or c.isspace()).replace(" ", "-")[:30]
        company_part = "".join(c.lower() for c in company if c.isalnum())[:15]
        
        # Add random suffix
        random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        
        return f"{title_part}-{company_part}-{random_suffix}"
    
    async def _get_filter_options(self) -> Dict[str, List[str]]:
        """Get available filter options from existing jobs"""
        try:
            # Get unique values for filters
            locations = await db.database[self.jobs_collection].distinct("location.city", {"is_active": True})
            experience_levels = await db.database[self.jobs_collection].distinct("experience_level", {"is_active": True})
            employment_types = await db.database[self.jobs_collection].distinct("employment_type", {"is_active": True})
            job_types = await db.database[self.jobs_collection].distinct("job_type", {"is_active": True})
            companies = await db.database[self.jobs_collection].distinct("company", {"is_active": True})
            
            # Get salary ranges (simplified)
            salary_ranges = [
                {"label": "₹0-5 LPA", "min": 0, "max": 500000},
                {"label": "₹5-10 LPA", "min": 500000, "max": 1000000},
                {"label": "₹10-15 LPA", "min": 1000000, "max": 1500000},
                {"label": "₹15-20 LPA", "min": 1500000, "max": 2000000},
                {"label": "₹20-25 LPA", "min": 2000000, "max": 2500000},
                {"label": "₹25+ LPA", "min": 2500000, "max": 10000000}
            ]
            
            return {
                "locations": ["All Locations"] + [loc for loc in locations if loc],
                "experience_levels": ["All Levels"] + experience_levels,
                "employment_types": ["All Types"] + employment_types,
                "job_types": ["All Types"] + job_types,
                "companies": ["All Companies"] + companies,
                "salary_ranges": salary_ranges
            }
            
        except Exception as e:
            print(f"❌ Error getting filter options: {e}")
            return {
                "locations": ["All Locations"],
                "experience_levels": ["All Levels"],
                "employment_types": ["All Types"],
                "job_types": ["All Types"],
                "companies": ["All Companies"],
                "salary_ranges": []
            }


# Global instance
job_db = JobDatabase()
