"""
Database operations for job postings functionality
"""

import logging

logger = logging.getLogger(__name__)

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
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
                "application_deadline": job_data.application_deadline or (datetime.utcnow() + timedelta(days=int(os.getenv("DEFAULT_JOB_EXPIRY_DAYS", "30")))).isoformat(),
                "external_apply_url": job_data.external_apply_url,
                "application_instructions": job_data.application_instructions,
                "tags": job_data.tags or [],
                "learning_resources": [lr.dict() for lr in (job_data.learning_resources or [])],
                
                # Metadata
                "posted_date": datetime.utcnow(),
                "updated_date": datetime.utcnow(),
                "is_active": True,
                "status": "active",
                "posted_by_hr_id": hr_user_id,
                "views_count": 0,
                "applications_count": [],
                "source": "internal",
                "job_score": None,
                "match_percentage": None
            }
            
            # Insert into database
            result = await db.database[self.jobs_collection].insert_one(job_doc)
            job_doc["_id"] = str(result.inserted_id)
            
            logger.debug("Job posting created: %s ", job_id)
            return job_id
            
        except Exception as e:
            logger.error("creating job posting: %s", e)
            raise Exception(f"Failed to create job posting: {str(e)}")
    
    async def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by job_id"""
        try:
            job = await db.database[self.jobs_collection].find_one({"job_id": job_id})
            if job:
                job["_id"] = str(job["_id"])
            return job
        except Exception as e:
            logger.error("getting job by ID: %s", e)
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
                # Transform job data to match HRJobListing schema
                hr_job = {
                    "_id": str(job["_id"]),
                    "job_id": job.get("job_id", str(job["_id"])),
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "location": self._format_location(job.get("location", "")),
                    "employment_type": job.get("employment_type", "full_time"),
                    "experience_level": job.get("experience_level", "mid"),
                    "job_type": job.get("job_type", "onsite"),
                    "salary_range": job.get("salary", {}),
                    "posted_date": job.get("posted_date", datetime.utcnow()),
                    "application_deadline": job.get("application_deadline"),
                    "is_active": job.get("is_active", True),
                    "applications_count": len(job.get("applications_count", [])),
                    "views_count": job.get("views_count", 0),
                    "description": job.get("description", ""),
                    "requirements": job.get("requirements", []),
                    "skills": job.get("skills_required", []),
                    "responsibilities": job.get("responsibilities", []),
                    "tags": job.get("tags", []),
                    "posted_by_hr_id": job.get("posted_by_hr_id", hr_user_id)
                }
                jobs.append(hr_job)
            
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
            logger.error("getting HR jobs: %s", e)
            raise Exception(f"Database error: {str(e)}")
    
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
            logger.error("searching jobs: %s", e)
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
            logger.error("updating job: %s", e)
            return False
    
    async def delete_job(self, job_id: str, hr_user_id: str) -> bool:
        """Delete job posting (only by the HR who posted it)"""
        try:
            # Soft delete - mark as closed instead of actually deleting
            result = await db.database[self.jobs_collection].update_one(
                {"job_id": job_id, "posted_by_hr_id": hr_user_id},
                {"$set": {"is_active": False, "status": "closed", "updated_date": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error("deleting job: %s", e)
            return False
    
    async def get_hr_dashboard(self, hr_user_id: str) -> HRJobDashboard:
        """Get dashboard stats for HR user using aggregation (memory-safe)."""
        try:
            logger.debug("Getting HR dashboard for user: %s", hr_user_id)

            # Use aggregation to compute stats without loading all docs
            pipeline = [
                {"$match": {"posted_by_hr_id": hr_user_id}},
                {"$facet": {
                    "stats": [{
                        "$group": {
                            "_id": None,
                            "total_jobs": {"$sum": 1},
                            "active_jobs": {"$sum": {"$cond": [{"$eq": ["$is_active", True]}, 1, 0]}},
                            "total_applications": {"$sum": {"$size": {"$ifNull": ["$applications_count", []]}}}
                        }
                    }],
                    "recent_jobs": [
                        {"$sort": {"posted_date": -1}},
                        {"$limit": 5}
                    ]
                }}
            ]

            agg_result = await db.database[self.jobs_collection].aggregate(pipeline).to_list(1)

            if not agg_result:
                return HRJobDashboard(total_jobs_posted=0, active_jobs=0, inactive_jobs=0,
                                     total_applications_received=0, jobs_expiring_soon=0, recent_jobs=[])

            facets = agg_result[0]
            stats = facets["stats"][0] if facets["stats"] else {"total_jobs": 0, "active_jobs": 0, "total_applications": 0}
            recent_jobs = facets["recent_jobs"]

            total_jobs = stats["total_jobs"]
            active_jobs = stats["active_jobs"]
            total_applications = stats["total_applications"]

            # Convert ObjectIds in recent jobs
            for job in recent_jobs:
                job["_id"] = str(job["_id"])

            # Count jobs expiring within 7 days (separate lightweight query)
            cutoff_date = datetime.utcnow() + timedelta(days=7)
            jobs_expiring_soon = await db.database[self.jobs_collection].count_documents({
                "posted_by_hr_id": hr_user_id,
                "is_active": True,
                "application_deadline": {"$lte": cutoff_date.isoformat()}
            })

            return HRJobDashboard(
                total_jobs_posted=total_jobs,
                active_jobs=active_jobs,
                inactive_jobs=total_jobs - active_jobs,
                total_applications_received=total_applications,
                jobs_expiring_soon=jobs_expiring_soon,
                recent_jobs=recent_jobs
            )

        except Exception as e:
            logger.error("getting HR dashboard: %s", e)
            return HRJobDashboard(
                total_jobs_posted=0, active_jobs=0, inactive_jobs=0,
                total_applications_received=0, jobs_expiring_soon=0, recent_jobs=[])
    
    async def increment_job_views(self, job_id: str) -> bool:
        """Increment view count for a job"""
        try:
            result = await db.database[self.jobs_collection].update_one(
                {"job_id": job_id},
                {"$inc": {"views_count": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error("incrementing job views: %s", e)
            return False
    
    async def add_job_application(self, job_id: str, user_id: str) -> bool:
        """Add user to job applications array"""
        try:
            # First, ensure applications_count is an array (handle legacy integer format)
            await db.database[self.jobs_collection].update_one(
                {"job_id": job_id, "applications_count": {"$type": "number"}},
                {"$set": {"applications_count": []}}
            )
            
            # Now add user to the array
            result = await db.database[self.jobs_collection].update_one(
                {"job_id": job_id},
                {"$addToSet": {"applications_count": user_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error("adding job application: %s", e)
            return False
    
    def _generate_job_id(self, title: str, company: str) -> str:
        """Generate unique job ID"""
        # Create base from title and company
        title_part = "".join(c.lower() for c in title if c.isalnum() or c.isspace()).replace(" ", "-")[:30]
        company_part = "".join(c.lower() for c in company if c.isalnum())[:15]
        
        # Add random suffix
        random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        
        return f"{title_part}-{company_part}-{random_suffix}"
    
    def _format_location(self, location) -> str:
        """Format location object to string"""
        if isinstance(location, str):
            return location
        
        if isinstance(location, dict):
            city = location.get("city", "")
            state = location.get("state", "")
            country = location.get("country", "")
            is_remote = location.get("is_remote", False)
            
            if is_remote:
                return "Remote"
            
            parts = [part for part in [city, state, country] if part]
            return ", ".join(parts) if parts else "Not specified"
        
        return "Not specified"
    
    async def get_total_job_count(self) -> int:
        """Get total count of all jobs"""
        try:
            return await db.database[self.jobs_collection].count_documents({})
        except Exception as e:
            logger.error("getting total job count: %s", e)
            return 0

    async def get_active_job_count(self) -> int:
        """Get count of active jobs (consistent with job search query)"""
        try:
            return await db.database[self.jobs_collection].count_documents({"is_active": True})
        except Exception as e:
            logger.error("getting active job count: %s", e)
            return 0

    # Cache for filter options (refreshes every 5 minutes)
    _filter_cache = None
    _filter_cache_time = None
    _FILTER_CACHE_TTL = 300  # 5 minutes

    async def _get_filter_options(self) -> Dict[str, List[str]]:
        """Get available filter options with in-memory caching."""
        import time
        now = time.time()

        if (self._filter_cache is not None and 
            self._filter_cache_time is not None and 
            now - self._filter_cache_time < self._FILTER_CACHE_TTL):
            return self._filter_cache

        try:
            locations = await db.database[self.jobs_collection].distinct("location.city", {"is_active": True})
            experience_levels = await db.database[self.jobs_collection].distinct("experience_level", {"is_active": True})
            employment_types = await db.database[self.jobs_collection].distinct("employment_type", {"is_active": True})
            job_types = await db.database[self.jobs_collection].distinct("job_type", {"is_active": True})
            companies = await db.database[self.jobs_collection].distinct("company", {"is_active": True})

            salary_ranges = [
                {"label": "₹0-5 LPA", "min": 0, "max": 500000},
                {"label": "₹5-10 LPA", "min": 500000, "max": 1000000},
                {"label": "₹10-15 LPA", "min": 1000000, "max": 1500000},
                {"label": "₹15-20 LPA", "min": 1500000, "max": 2000000},
                {"label": "₹20-25 LPA", "min": 2000000, "max": 2500000},
                {"label": "₹25+ LPA", "min": 2500000, "max": 10000000}
            ]

            JobDatabase._filter_cache = {
                "locations": ["All Locations"] + [loc for loc in locations if loc],
                "experience_levels": ["All Levels"] + experience_levels,
                "employment_types": ["All Types"] + employment_types,
                "job_types": ["All Types"] + job_types,
                "companies": ["All Companies"] + companies,
                "salary_ranges": salary_ranges
            }
            JobDatabase._filter_cache_time = now
            return JobDatabase._filter_cache

        except Exception as e:
            logger.error("getting filter options: %s", e)
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
