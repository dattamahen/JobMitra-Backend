"""
Simplified MongoDB database functions with fallback mode.
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MONGODB_AVAILABLE = True
except ImportError:
    logger.warning("MongoDB drivers not available — using fallback mode")
    MONGODB_AVAILABLE = False
    AsyncIOMotorClient = None


class Database:
    """Database handler class with fallback mode."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.fallback_mode = not MONGODB_AVAILABLE
        
        # Fallback in-memory storage
        self.fallback_data = {
            "users": {},
            "jobs": {},
            "applications": {},
            "mock_interviews": {},
            "learning_resources": [],
            "user_progress": {},
            "dashboards": {},
        }
        
        if self.fallback_mode:
            self._seed_fallback_data()
        
    def _seed_fallback_data(self):
        """Add sample data for fallback mode."""
        self.fallback_data["learning_resources"] = [
            {
                "title": "Python Programming Fundamentals",
                "description": "Learn Python basics for web development",
                "skill": "Python",
                "level": "beginner",
                "type": "course",
                "url": "https://example.com/python-course",
                "duration_minutes": 480
            },
            {
                "title": "React.js Complete Guide",
                "description": "Master React.js for frontend development",
                "skill": "React",
                "level": "intermediate",
                "type": "course",
                "url": "https://example.com/react-course",
                "duration_minutes": 720
            }
        ]
        
    async def connect_to_mongo(self):
        """Establish connection to MongoDB with connection pooling."""
        if not MONGODB_AVAILABLE:
            if os.getenv("APP_ENV", "local") in ("prod", "production"):
                raise RuntimeError("MongoDB drivers required in production — cannot use fallback mode")
            logger.warning("Using fallback mode — data will not persist")
            return

        try:
            from config import settings
            mongo_uri = settings.MONGO_URI
            self.client = AsyncIOMotorClient(
                mongo_uri,
                maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
                minPoolSize=settings.MONGO_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                retryWrites=True
            )

            if "/" in mongo_uri and mongo_uri.split("/")[-1]:
                db_name = mongo_uri.split("/")[-1].split("?")[0]
            else:
                db_name = "jobmitra"

            self.database = self.client[db_name]
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB: %s (pool: %d-%d)", db_name, settings.MONGO_MIN_POOL_SIZE, settings.MONGO_MAX_POOL_SIZE)
            self.fallback_mode = False

        except Exception as e:
            logger.error("MongoDB connection failed: %s", e)
            self.fallback_mode = True
    
    async def close_mongo_connection(self):
        """Close the MongoDB connection."""
        if self.client and not self.fallback_mode:
            self.client.close()
            logger.info("MongoDB connection closed")
        else:
            logger.debug("Fallback mode — no connection to close")


# Global database instance
db = Database()


# Collection names
COLLECTIONS = {
    "users": "users",
    "jobs": "jobs",
    "mock_interviews": "mock_interview_sessions",
    "learning_resources": "learning_resources",
}


# User Management Functions
async def create_user_profile(user_data: Dict[str, Any]) -> Optional[str]:
    """Create a new user profile."""
    try:
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        
        collection = db.database[COLLECTIONS["users"]]
        result = await collection.insert_one(user_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error("Error creating user profile: %s", e)
        return None


async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile by user_id."""
    try:
        collection = db.database[COLLECTIONS["users"]]
        user = await collection.find_one({"user_id": user_id})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        logger.error("Error getting user profile: %s", e)
        return None


async def update_user_profile(user_id: str, update_data: Dict[str, Any]) -> bool:
    """Update user profile."""
    try:
        collection = db.database[COLLECTIONS["users"]]
        update_data["updated_at"] = datetime.utcnow()
        result = await collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error("Error updating user profile: %s", e)
        return False


# Job Management Functions
async def create_job_listing(job_data: Dict[str, Any]) -> Optional[str]:
    """Create a new job listing."""
    try:
        job_data["created_at"] = datetime.utcnow()
        job_data["updated_at"] = datetime.utcnow()
        
        collection = db.database[COLLECTIONS["jobs"]]
        result = await collection.insert_one(job_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error("Error creating job listing: %s", e)
        return None


async def search_jobs(query: str = "", filters: Dict[str, Any] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Search for jobs using text index and filters."""
    try:
        collection = db.database[COLLECTIONS["jobs"]]

        search_query: Dict[str, Any] = {"is_active": True}

        # Use text index for keyword search (much faster than $regex)
        if query:
            search_query["$text"] = {"$search": query}

        # Apply filters
        if filters:
            if "skills" in filters and filters["skills"]:
                search_query["skills_required"] = {"$in": filters["skills"]}
            if "location_type" in filters and filters["location_type"]:
                search_query["location.type"] = filters["location_type"]
            if "experience_level" in filters and filters["experience_level"]:
                search_query["experience_level"] = filters["experience_level"]

        # Sort by text relevance if searching, otherwise by date
        if query:
            cursor = collection.find(
                search_query, {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit)
        else:
            cursor = collection.find(search_query).sort("posted_date", -1).limit(limit)

        jobs = await cursor.to_list(length=limit)

        for job in jobs:
            if "_id" in job:
                job["_id"] = str(job["_id"])
            job.pop("score", None)

        return jobs

    except Exception as e:
        # Fallback to regex if text index not available
        if "text index" in str(e).lower() or "$text" in str(e):
            return await _search_jobs_regex_fallback(query, filters, limit)
        logger.error("Error searching jobs: %s", e)
        return []


async def _search_jobs_regex_fallback(query: str, filters: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
    """Fallback search using regex when text index is unavailable."""
    try:
        collection = db.database[COLLECTIONS["jobs"]]
        search_query: Dict[str, Any] = {"is_active": True}

        if query:
            search_query["$or"] = [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"company": {"$regex": query, "$options": "i"}}
            ]

        if filters:
            if "skills" in filters and filters["skills"]:
                search_query["skills_required"] = {"$in": filters["skills"]}
            if "location_type" in filters and filters["location_type"]:
                search_query["location.type"] = filters["location_type"]
            if "experience_level" in filters and filters["experience_level"]:
                search_query["experience_level"] = filters["experience_level"]

        cursor = collection.find(search_query).sort("posted_date", -1).limit(limit)
        jobs = await cursor.to_list(length=limit)

        for job in jobs:
            if "_id" in job:
                job["_id"] = str(job["_id"])

        return jobs
    except Exception as e:
        logger.error("Regex search fallback failed: %s", e)
        return []



async def get_user_applications(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get applications for a user from user profile's overall_jobs_applied array."""
    try:
        user_profile = await get_user_profile(user_id)
        if not user_profile:
            return []

        overall_jobs_applied = user_profile.get("overall_jobs_applied", [])

        # Filter applied jobs and collect job_ids
        applied_records = []
        job_ids = []
        for app_record in overall_jobs_applied:
            if isinstance(app_record, dict) and app_record.get("is_applied", False):
                job_id = app_record.get("job_id")
                if job_id:
                    applied_records.append(app_record)
                    job_ids.append(job_id)

        if not job_ids:
            return []

        # Batch fetch all jobs in ONE query instead of N queries
        jobs_collection = db.database["jobs"]
        jobs_cursor = jobs_collection.find({"job_id": {"$in": job_ids}})
        jobs_map = {}
        async for job in jobs_cursor:
            jobs_map[job["job_id"]] = job

        # Build application list
        applications = []
        for app_record in applied_records:
            job_id = app_record.get("job_id")
            job = jobs_map.get(job_id)
            if job:
                applications.append({
                    "_id": str(job.get("_id", "")),
                    "application_id": f"app_{job_id}_{user_id}",
                    "job_id": job_id,
                    "user_id": user_id,
                    "job_title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "status": app_record.get("status", "applied"),
                    "applied_date": app_record.get("applied_date", app_record.get("timestamp", "")),
                    "match_percentage": app_record.get("match_percentage", 0),
                    "match_analysis_done": app_record.get("match_analysis_done", False),
                    "tailor_resume_done": app_record.get("tailor_resume_done", False),
                    "created_at": app_record.get("timestamp", ""),
                    "updated_at": app_record.get("timestamp", "")
                })

        # Sort by applied date (most recent first)
        applications.sort(key=lambda x: x.get("applied_date", ""), reverse=True)
        return applications[:limit]

    except Exception as e:
        logger.error("Error getting user applications: %s", e)
        return []


# Mock Interview Functions
async def create_mock_interview(interview_data: Dict[str, Any]) -> Optional[str]:
    """Create a new mock interview session."""
    try:
        interview_data["created_at"] = datetime.utcnow()
        interview_data["updated_at"] = datetime.utcnow()
        
        collection = db.database[COLLECTIONS["mock_interviews"]]
        result = await collection.insert_one(interview_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error("Error creating mock interview: %s", e)
        return None


async def get_user_mock_interviews(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get mock interviews for a user."""
    try:
        collection = db.database[COLLECTIONS["mock_interviews"]]
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        interviews = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for interview in interviews:
            if "_id" in interview:
                interview["_id"] = str(interview["_id"])
        
        return interviews
        
    except Exception as e:
        logger.error("Error getting mock interviews: %s", e)
        return []


# Learning Resources Functions
async def get_learning_resources(skill: str = None, level: str = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Get learning resources with optional filters."""
    try:
        collection = db.database[COLLECTIONS["learning_resources"]]
        
        # Build query
        query = {}
        if skill:
            query["skill"] = {"$regex": skill, "$options": "i"}
        if level:
            query["level"] = level.lower()
        
        cursor = collection.find(query).limit(limit)
        resources = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for resource in resources:
            if "_id" in resource:
                resource["_id"] = str(resource["_id"])
        
        # If no resources found, return sample data
        if not resources:
            sample_resources = [
                {
                    "title": "Python Programming Fundamentals",
                    "description": "Learn Python basics for web development",
                    "skill": skill or "Python",
                    "level": level or "beginner",
                    "type": "course",
                    "url": "https://example.com/python-course",
                    "duration_minutes": 480
                },
                {
                    "title": "React.js Complete Guide", 
                    "description": "Master React.js for frontend development",
                    "skill": skill or "React",
                    "level": level or "intermediate",
                    "type": "course",
                    "url": "https://example.com/react-course",
                    "duration_minutes": 720
                }
            ]
            return sample_resources[:limit]
        
        return resources
        
    except Exception as e:
        logger.error("Error getting learning resources: %s", e)
        return []


async def get_user_progress(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user learning progress — returns None if not found, never auto-creates."""
    return None


async def update_application_status(application_id: str, status: str) -> bool:
    """Update application status in job's applications_received array."""
    try:
        logger.debug("Updating application status: %s -> %s", application_id, status)

        jobs_collection = db.database["jobs"]

        test_job = await jobs_collection.find_one({"applications_received.application_id": application_id})
        logger.debug("Found job with application: %s", test_job is not None)
        
        result = await jobs_collection.update_one(
            {"applications_received.application_id": application_id},
            {
                "$set": {
                    "applications_received.$.status": status,
                    "updated_date": datetime.utcnow()
                }
            }
        )
        logger.debug("Update result — modified_count: %s", result.modified_count)
        return result.modified_count > 0
    except Exception as e:
        logger.error("Error updating application status: %s", e, exc_info=True)
        return False
