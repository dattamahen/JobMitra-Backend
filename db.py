"""
MongoDB database connection and operations module.
Handles async database operations using motor driver.
"""

import logging
logger = logging.getLogger(__name__)

import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, Any, List
from pymongo import IndexModel

# Temporarily comment out schemas import to avoid dependency issues
# from schemas import (
#     COLLECTION_NAMES, 
#     get_indexes,
#     UserProfile,
#     JobListing,
#     JobApplication,
#     Resume,
#     MockInterviewSession,
#     LearningResource,
#     SkillAssessment,
#     UserProgress,
#     UserSubscription,
#     UserDashboard,
#     QueryLog,
#     SystemConfig
# )


class Database:
    """MongoDB database handler class."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        
    async def connect_to_mongo(self):
        """Establish connection to MongoDB using URI from environment variables."""
        try:
            # Get MongoDB URI from environment variables
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmitra")
            
            # Create async MongoDB client
            self.client = AsyncIOMotorClient(mongo_uri)
            
            # Extract database name from URI or use default
            if "/" in mongo_uri and mongo_uri.split("/")[-1]:
                db_name = mongo_uri.split("/")[-1]
            else:
                db_name = "jobmitra"
                
            self.database = self.client[db_name]
            
            # Test the connection
            await self.client.admin.command('ismaster')
            logger.debug("Successfully connected to MongoDB: %s", db_name)
            
            # Setup indexes for performance
            await self.setup_indexes()
            
        except Exception as e:
            logger.error("connecting to MongoDB: %s", e)
            raise e
    
    async def setup_indexes(self):
        """Setup database indexes for performance optimization."""
        try:
            # Temporarily disable index setup due to schemas dependency
            logger.info("Skipping index setup for now - will be implemented later")
            
        except Exception as e:
            logger.error("setting up indexes: %s", e)
            # Don't raise error as this is not critical for basic functionality
    
    async def close_mongo_connection(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database instance
db = Database()


async def log_to_db(query: str, response: str, user_id: Optional[str] = None, 
                   processing_time_ms: Optional[int] = None) -> bool:
    """
    Log query and response to MongoDB collection.
    
    Args:
        query (str): User's input query
        response (str): AI-generated response
        user_id (str, optional): User ID if authenticated
        processing_time_ms (int, optional): Processing time in milliseconds
        
    Returns:
        bool: True if logged successfully, False otherwise
    """
    try:
        # Create log entry with timestamp
        log_entry = QueryLog(
            user_id=user_id,
            query=query,
            response=response,
            processing_time_ms=processing_time_ms
        )
        
        # Insert into query_logs collection
        collection = db.database[COLLECTION_NAMES["query_logs"]]
        result = await collection.insert_one(log_entry.dict(by_alias=True, exclude_unset=True))
        
        logger.debug("Log entry saved with ID: %s", result.inserted_id)
        return True
        
    except Exception as e:
        logger.error("logging to database: %s", e)
        return False


async def get_query_logs(limit: int = 10, user_id: Optional[str] = None):
    """
    Retrieve recent query logs from database.
    
    Args:
        limit (int): Number of logs to retrieve
        user_id (str, optional): Filter by user ID
        
    Returns:
        list: List of query log documents
    """
    try:
        collection = db.database[COLLECTION_NAMES["query_logs"]]
        
        # Build query filter
        query_filter = {}
        if user_id:
            query_filter["user_id"] = user_id
            
        cursor = collection.find(query_filter).sort("created_at", -1).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for log in logs:
            if "_id" in log:
                log["_id"] = str(log["_id"])
                
        return logs
        
    except Exception as e:
        logger.error("retrieving logs: %s", e)
        return []


# User Management Functions
async def create_user_profile(user_data: Dict[str, Any]) -> Optional[str]:
    """Create a new user profile."""
    try:
        user_profile = UserProfile(**user_data)
        collection = db.database[COLLECTION_NAMES["users"]]
        result = await collection.insert_one(user_profile.dict(by_alias=True, exclude_unset=True))
        return str(result.inserted_id)
    except Exception as e:
        logger.error("creating user profile: %s", e)
        return None


async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile by user_id."""
    try:
        collection = db.database[COLLECTION_NAMES["users"]]
        user = await collection.find_one({"user_id": user_id})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        logger.error("getting user profile: %s", e)
        return None


async def update_user_profile(user_id: str, update_data: Dict[str, Any]) -> bool:
    """Update user profile."""
    try:
        collection = db.database[COLLECTION_NAMES["users"]]
        update_data["updated_at"] = datetime.utcnow()
        result = await collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error("updating user profile: %s", e)
        return False


# Job Management Functions
async def create_job_listing(job_data: Dict[str, Any]) -> Optional[str]:
    """Create a new job listing."""
    try:
        job_listing = JobListing(**job_data)
        collection = db.database[COLLECTION_NAMES["jobs"]]
        result = await collection.insert_one(job_listing.dict(by_alias=True, exclude_unset=True))
        return str(result.inserted_id)
    except Exception as e:
        logger.error("creating job listing: %s", e)
        return None


async def search_jobs(query: str, filters: Optional[Dict[str, Any]] = None, 
                     limit: int = 20) -> List[Dict[str, Any]]:
    """Search for jobs based on query and filters."""
    try:
        collection = db.database[COLLECTION_NAMES["jobs"]]
        
        # Build search pipeline
        search_query = {"is_active": True}
        
        if query:
            search_query["$text"] = {"$search": query}
            
        if filters:
            if "skills" in filters:
                search_query["skills"] = {"$in": filters["skills"]}
            if "location_type" in filters:
                search_query["location.type"] = filters["location_type"]
            if "experience_level" in filters:
                search_query["experience_level"] = filters["experience_level"]
                
        cursor = collection.find(search_query).limit(limit)
        jobs = await cursor.to_list(length=limit)
        
        for job in jobs:
            job["_id"] = str(job["_id"])
            
        return jobs
    except Exception as e:
        logger.error("searching jobs: %s", e)
        return []


# Application Management Functions
async def create_job_application(application_data: Dict[str, Any]) -> Optional[str]:
    """Create a new job application."""
    try:
        job_application = JobApplication(**application_data)
        collection = db.database[COLLECTION_NAMES["applications"]]
        result = await collection.insert_one(job_application.dict(by_alias=True, exclude_unset=True))
        return str(result.inserted_id)
    except Exception as e:
        logger.error("creating job application: %s", e)
        return None


async def get_user_applications(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get all applications for a user."""
    try:
        collection = db.database[COLLECTION_NAMES["applications"]]
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        applications = await cursor.to_list(length=limit)
        
        for app in applications:
            app["_id"] = str(app["_id"])
            
        return applications
    except Exception as e:
        logger.error("getting user applications: %s", e)
        return []


# Mock Interview Functions
async def create_mock_interview(interview_data: Dict[str, Any]) -> Optional[str]:
    """Create a new mock interview session."""
    try:
        mock_interview = MockInterviewSession(**interview_data)
        collection = db.database[COLLECTION_NAMES["mock_interviews"]]
        result = await collection.insert_one(mock_interview.dict(by_alias=True, exclude_unset=True))
        return str(result.inserted_id)
    except Exception as e:
        logger.error("creating mock interview: %s", e)
        return None


async def get_user_mock_interviews(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get mock interview history for a user."""
    try:
        collection = db.database[COLLECTION_NAMES["mock_interviews"]]
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        interviews = await cursor.to_list(length=limit)
        
        for interview in interviews:
            interview["_id"] = str(interview["_id"])
            
        return interviews
    except Exception as e:
        logger.error("getting user mock interviews: %s", e)
        return []


# Dashboard and Analytics Functions
async def get_user_dashboard(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user dashboard data."""
    try:
        collection = db.database[COLLECTION_NAMES["dashboards"]]
        dashboard = await collection.find_one({"user_id": user_id})
        
        if not dashboard:
            # Create default dashboard if doesn't exist
            default_dashboard = UserDashboard(user_id=user_id)
            await collection.insert_one(default_dashboard.dict(by_alias=True, exclude_unset=True))
            dashboard = default_dashboard.dict(by_alias=True, exclude_unset=True)
        
        if dashboard and "_id" in dashboard:
            dashboard["_id"] = str(dashboard["_id"])
            
        return dashboard
    except Exception as e:
        logger.error("getting user dashboard: %s", e)
        return None


async def update_user_dashboard(user_id: str, dashboard_data: Dict[str, Any]) -> bool:
    """Update user dashboard data."""
    try:
        collection = db.database[COLLECTION_NAMES["dashboards"]]
        dashboard_data["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"user_id": user_id},
            {"$set": dashboard_data},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    except Exception as e:
        logger.error("updating user dashboard: %s", e)
        return False


# Learning and Progress Functions
async def get_learning_resources(skill: Optional[str] = None, 
                               level: Optional[str] = None,
                               limit: int = 20) -> List[Dict[str, Any]]:
    """Get learning resources with optional filters."""
    try:
        collection = db.database[COLLECTION_NAMES["learning_resources"]]
        
        query_filter = {}
        if skill:
            query_filter["skill"] = {"$regex": skill, "$options": "i"}
        if level:
            query_filter["level"] = level
            
        cursor = collection.find(query_filter).limit(limit)
        resources = await cursor.to_list(length=limit)
        
        for resource in resources:
            resource["_id"] = str(resource["_id"])
            
        return resources
    except Exception as e:
        logger.error("getting learning resources: %s", e)
        return []


async def get_user_progress(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user learning progress."""
    try:
        collection = db.database[COLLECTION_NAMES["user_progress"]]
        progress = await collection.find_one({"user_id": user_id})
        
        if not progress:
            # Create default progress if doesn't exist
            default_progress = UserProgress(user_id=user_id)
            await collection.insert_one(default_progress.dict(by_alias=True, exclude_unset=True))
            progress = default_progress.dict(by_alias=True, exclude_unset=True)
        
        if progress and "_id" in progress:
            progress["_id"] = str(progress["_id"])
            
        return progress
    except Exception as e:
        logger.error("getting user progress: %s", e)
        return None
