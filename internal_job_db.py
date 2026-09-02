"""
Database operations for Internal Job Postings.
Collection: internal_jobs
Auto-expires after 15 days via scheduler hook.
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from db import db
from internal_job_schemas import InternalJobPostRequest, InternalJobSearchFilters

logger = logging.getLogger(__name__)

COLLECTION = "internal_jobs"
EXPIRY_DAYS = 15


class InternalJobDatabase:

    def _generate_id(self, title: str, company: str) -> str:
        title_part = "".join(c.lower() for c in title if c.isalnum() or c.isspace()).replace(" ", "-")[:25]
        company_part = "".join(c.lower() for c in company if c.isalnum())[:12]
        suffix = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
        return f"ijob-{title_part}-{company_part}-{suffix}"

    async def create(self, job: InternalJobPostRequest, user_id: str, user_email: str) -> str:
        try:
            job_id = self._generate_id(job.title, job.company)
            now = datetime.utcnow()
            doc = {
                "internal_job_id": job_id,
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "skills_required": job.skills_required,
                "experience_level": job.experience_level,
                "employment_type": job.employment_type,
                "job_type": job.job_type,
                "location": {
                    "city": job.location_city,
                    "state": job.location_state,
                    "country": "India",
                    "is_remote": job.job_type == "remote"
                },
                "requirements": job.requirements or [
                    "Bachelor's degree or equivalent experience",
                    "Strong communication skills",
                    "Ability to work in a team"
                ],
                "responsibilities": job.responsibilities or [
                    "Execute assigned tasks with quality",
                    "Collaborate with cross-functional teams",
                    "Deliver work on time"
                ],
                "posted_by_user_id": user_id,
                "posted_by_email": user_email,
                "official_email": job.official_email,
                "posted_date": now,
                "expires_at": now + timedelta(days=EXPIRY_DAYS),
                "status": "active",
                "is_active": True,
                "views_count": 0,
                "applications_count": 0,
                "applications_received": [],
                "source": "internal_referral",
                # Generic company info defaults
                "company_info": {
                    "company_size": "51-200",
                    "industry": "Technology",
                    "website": "",
                    "description": ""
                },
                # Generic HR contact — poster's official email
                "hr_contact": {
                    "name": "Hiring Team",
                    "email": job.official_email,
                    "phone": "Not provided",
                    "title": "Recruiter",
                    "department": "Human Resources"
                },
                "salary": None,
                "benefits": ["Competitive compensation", "Growth opportunities"],
                "tags": [],
            }
            await db.database[COLLECTION].insert_one(doc)
            logger.info("Internal job created: %s by %s", job_id, user_id)
            return job_id
        except Exception as e:
            logger.error("create internal job: %s", e)
            raise

    async def get_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        try:
            job = await db.database[COLLECTION].find_one({"internal_job_id": job_id, "is_active": True})
            if job:
                job["_id"] = str(job["_id"])
            return job
        except Exception as e:
            logger.error("get internal job: %s", e)
            return None

    async def get_by_poster(self, user_id: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Jobs posted by a specific user — for Refer & Hire section."""
        try:
            skip = (page - 1) * per_page
            total = await db.database[COLLECTION].count_documents({"posted_by_user_id": user_id})
            cursor = db.database[COLLECTION].find(
                {"posted_by_user_id": user_id}
            ).sort("posted_date", -1).skip(skip).limit(per_page)
            jobs = []
            async for job in cursor:
                job["_id"] = str(job["_id"])
                jobs.append(job)
            return {
                "jobs": jobs,
                "total_count": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page,
            }
        except Exception as e:
            logger.error("get jobs by poster: %s", e)
            return {"jobs": [], "total_count": 0, "page": page, "per_page": per_page, "total_pages": 0}

    async def search(self, filters: InternalJobSearchFilters) -> Dict[str, Any]:
        """Search active internal jobs — for Internal Job Market (paid)."""
        try:
            query: Dict[str, Any] = {"is_active": True, "status": "active"}

            if filters.keywords:
                regex = {"$regex": filters.keywords, "$options": "i"}
                query["$or"] = [
                    {"title": regex},
                    {"company": regex},
                    {"description": regex},
                    {"skills_required": {"$in": [regex]}}
                ]
            if filters.location:
                query["location.city"] = {"$regex": filters.location, "$options": "i"}
            if filters.experience_level and filters.experience_level != "all":
                query["experience_level"] = filters.experience_level
            if filters.employment_type and filters.employment_type != "all":
                query["employment_type"] = filters.employment_type
            if filters.job_type and filters.job_type != "all":
                query["job_type"] = filters.job_type

            skip = (filters.page - 1) * filters.per_page
            total = await db.database[COLLECTION].count_documents(query)
            cursor = db.database[COLLECTION].find(query).sort("posted_date", -1).skip(skip).limit(filters.per_page)
            jobs = []
            async for job in cursor:
                job["_id"] = str(job["_id"])
                jobs.append(job)
            return {
                "jobs": jobs,
                "total_count": total,
                "page": filters.page,
                "per_page": filters.per_page,
                "total_pages": (total + filters.per_page - 1) // filters.per_page,
            }
        except Exception as e:
            logger.error("search internal jobs: %s", e)
            return {"jobs": [], "total_count": 0, "page": filters.page, "per_page": filters.per_page, "total_pages": 0}

    async def apply(self, job_id: str, user_id: str, user_email: str, user_name: str) -> bool:
        """Record application on internal job and in user's application history."""
        try:
            job = await db.database[COLLECTION].find_one({"internal_job_id": job_id})
            if not job:
                return False
            # Prevent duplicate
            existing = [a for a in job.get("applications_received", []) if a.get("user_id") == user_id]
            if existing:
                return False

            now = datetime.utcnow()
            application_id = f"{user_id}_{job_id}"

            # Write 1: internal_jobs.applications_received[]
            await db.database[COLLECTION].update_one(
                {"internal_job_id": job_id},
                {
                    "$inc": {"applications_count": 1},
                    "$push": {
                        "applications_received": {
                            "user_id": user_id,
                            "user_email": user_email,
                            "user_name": user_name,
                            "applied_date": now,
                            "status": "applied"
                        }
                    }
                }
            )

            # Write 2: users.internal_job_applications[] — for My Applications page
            await db.database["users"].update_one(
                {"user_id": user_id},
                {"$push": {
                    "internal_job_applications": {
                        "application_id": application_id,
                        "internal_job_id": job_id,
                        "job_title": job.get("title", ""),
                        "company": job.get("company", ""),
                        "application_source": "internal_referral",
                        "status": "applied",
                        "applied_date": now,
                        "last_updated": now,
                        "is_applied": True
                    }
                }}
            )
            return True
        except Exception as e:
            logger.error("apply internal job: %s", e)
            return False

    async def increment_views(self, job_id: str) -> None:
        try:
            await db.database[COLLECTION].update_one(
                {"internal_job_id": job_id},
                {"$inc": {"views_count": 1}}
            )
        except Exception:
            pass

    async def expire_stale(self) -> int:
        """Archive internal jobs older than 15 days. Called by scheduler."""
        try:
            cutoff = datetime.utcnow()
            result = await db.database[COLLECTION].update_many(
                {"expires_at": {"$lte": cutoff}, "is_active": True},
                {"$set": {"is_active": False, "status": "expired"}}
            )
            count = result.modified_count
            if count:
                logger.info("Expired %d internal job(s)", count)
            return count
        except Exception as e:
            logger.error("expire internal jobs: %s", e)
            return 0

    async def delete_by_poster(self, job_id: str, user_id: str) -> bool:
        try:
            result = await db.database[COLLECTION].update_one(
                {"internal_job_id": job_id, "posted_by_user_id": user_id},
                {"$set": {"is_active": False, "status": "removed"}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error("delete internal job: %s", e)
            return False


internal_job_db = InternalJobDatabase()
