"""
Simplified MongoDB database functions with fallback mode.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, List

# Try to import MongoDB drivers, fallback to mock if not available
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MONGODB_AVAILABLE = True
    print("MongoDB drivers available")
except ImportError:
    print("MongoDB drivers not available - using fallback mode")
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
            "query_logs": []
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
        """Establish connection to MongoDB or use fallback mode."""
        if not MONGODB_AVAILABLE:
            print("Using fallback mode - data will not persist")
            return
            
        try:
            # Get MongoDB URI from environment variables
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmitra")
            
            # Create async MongoDB client
            self.client = AsyncIOMotorClient(mongo_uri)
            
            # Extract database name from URI or use default
            if "/" in mongo_uri and mongo_uri.split("/")[-1]:
                db_name = mongo_uri.split("/")[-1].split("?")[0]  # Remove query params
            else:
                db_name = "jobmitra"
                
            self.database = self.client[db_name]
            
            # Test the connection
            await self.client.admin.command('ping')
            print(f"Successfully connected to MongoDB: {db_name}")
            self.fallback_mode = False
            
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            print("Switching to fallback mode - data will not persist")
            self.fallback_mode = True
    
    async def close_mongo_connection(self):
        """Close the MongoDB connection."""
        if self.client and not self.fallback_mode:
            self.client.close()
            print("MongoDB connection closed")
        else:
            print("Fallback mode - no connection to close")


# Global database instance
db = Database()


# Collection names
COLLECTIONS = {
    "users": "users",
    "jobs": "job_listings", 
    "applications": "job_applications",
    "mock_interviews": "mock_interview_sessions",
    "learning_resources": "learning_resources",
    "user_progress": "user_progress",
    "dashboards": "user_dashboards",
    "query_logs": "query_logs"
}


# Database Functions
async def log_to_db(query: str, response: str, metadata: Dict[str, Any] = None):
    """Log query and response to database."""
    try:
        log_entry = {
            "query": query,
            "response": response,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        if db.fallback_mode:
            # Use fallback storage
            db.fallback_data["query_logs"].append(log_entry)
            # Keep only last 100 logs
            if len(db.fallback_data["query_logs"]) > 100:
                db.fallback_data["query_logs"] = db.fallback_data["query_logs"][-100:]
            print("Log saved to fallback storage")
        else:
            # Use MongoDB
            collection = db.database[COLLECTIONS["query_logs"]]
            result = await collection.insert_one(log_entry)
            print(f"Log entry saved with ID: {result.inserted_id}")
        
        return True
        
    except Exception as e:
        print(f"Error logging to database: {e}")
        return False


async def get_query_logs(limit: int = 10, user_id: Optional[str] = None):
    """Retrieve recent query logs from database."""
    try:
        if db.fallback_mode:
            # Use fallback storage
            logs = db.fallback_data["query_logs"]
            if user_id:
                logs = [log for log in logs if log.get("user_id") == user_id]
            return logs[-limit:] if logs else []
        else:
            # Use MongoDB
            collection = db.database[COLLECTIONS["query_logs"]]
            
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
        print(f"Error retrieving logs: {e}")
        return []


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
        print(f"Error creating user profile: {e}")
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
        print(f"Error getting user profile: {e}")
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
        print(f"Error updating user profile: {e}")
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
        print(f"Error creating job listing: {e}")
        return None


async def search_jobs(query: str = "", filters: Dict[str, Any] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Search for jobs based on criteria."""
    try:
        collection = db.database[COLLECTIONS["jobs"]]
        
        # Build search query
        search_query = {}
        
        # Text search
        if query:
            search_query["$or"] = [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"company": {"$regex": query, "$options": "i"}}
            ]
        
        # Apply filters
        if filters:
            if "skills" in filters:
                search_query["required_skills"] = {"$in": filters["skills"]}
            if "location_type" in filters:
                search_query["location_type"] = filters["location_type"]
            if "experience_level" in filters:
                search_query["experience_level"] = filters["experience_level"]
        
        cursor = collection.find(search_query).sort("created_at", -1).limit(limit)
        jobs = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for job in jobs:
            if "_id" in job:
                job["_id"] = str(job["_id"])
        
        return jobs
        
    except Exception as e:
        print(f"Error searching jobs: {e}")
        return []


# Application Management Functions
async def create_job_application(app_data: Dict[str, Any]) -> Optional[str]:
    """Create a new job application."""
    try:
        app_data["created_at"] = datetime.utcnow()
        app_data["updated_at"] = datetime.utcnow()
        
        collection = db.database[COLLECTIONS["applications"]]
        result = await collection.insert_one(app_data)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error creating application: {e}")
        return None


async def get_user_applications(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get applications for a user from user profile's overall_jobs_applied array."""
    try:
        # Get user profile to access overall_jobs_applied array (same as dashboard)
        user_profile = await get_user_profile(user_id)
        if not user_profile:
            return []
        
        # Get applications from overall_jobs_applied array
        overall_jobs_applied = user_profile.get("overall_jobs_applied", [])
        
        # Filter only applied jobs (is_applied=True) and get job details
        applications = []
        jobs_collection = db.database["jobs"]
        
        for app_record in overall_jobs_applied:
            if isinstance(app_record, dict) and app_record.get("is_applied", False):
                job_id = app_record.get("job_id")
                if job_id:
                    # Get job details
                    job = await jobs_collection.find_one({"job_id": job_id})
                    if job:
                        # Convert to application format
                        application = {
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
                        }
                        applications.append(application)
        
        # Sort by applied date (most recent first)
        applications.sort(key=lambda x: x.get("applied_date", ""), reverse=True)
        
        return applications[:limit]
        
    except Exception as e:
        print(f"Error getting user applications: {e}")
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
        print(f"Error creating mock interview: {e}")
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
        print(f"Error getting mock interviews: {e}")
        return []


# Dashboard Functions
async def get_user_dashboard(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user dashboard data without creating persistent dashboard entries."""
    try:
        # Get user profile to check user type
        user_profile = await get_user_profile(user_id)
        if not user_profile:
            return None
            
        user_type = user_profile.get("user_type", "candidate")
        
        # Generate dashboard data dynamically without storing in database
        if user_type == "hire":
            # For HR users, count applications received for their job postings
            jobs_collection = db.database[COLLECTIONS["jobs"]]
            applications_collection = db.database[COLLECTIONS["applications"]]
            
            hr_jobs = await jobs_collection.find({"posted_by_hr_id": user_id}).to_list(None)
            hr_job_ids = [job.get('job_id') for job in hr_jobs if job.get('job_id')]
            
            if hr_job_ids:
                applications_received = await applications_collection.count_documents({"job_id": {"$in": hr_job_ids}})
            else:
                applications_received = 0
            
            dashboard_data = {
                "user_id": user_id,
                "applications_count": applications_received,
                "total_job_postings": len(hr_jobs),
                "total_interviews": 0,
                "profile_completion": 75,
                "recent_activity": [],
                "stats": [
                    {
                        "id": "applications-received",
                        "label": "Applications Received",
                        "value": applications_received,
                        "icon": "inbox",
                        "color": "accent",
                        "trend": {
                            "direction": "neutral",
                            "percentage": 15,
                            "period": "this week"
                        }
                    }
                ],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        else:
            # For candidates, count applications from overall_jobs_applied array
            applications_sent = len(user_profile.get("overall_jobs_applied", []))
            
            dashboard_data = {
                "user_id": user_id,
                "applications_count": applications_sent,
                "total_interviews": 0,
                "profile_completion": 75,
                "recent_activity": [],
                "stats": [
                    {
                        "id": "applications-sent",
                        "label": "Applications Sent",
                        "value": applications_sent,
                        "icon": "send",
                        "color": "primary",
                        "trend": {
                            "direction": "neutral",
                            "percentage": 0,
                            "period": "this week"
                        }
                    }
                ],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        
        return dashboard_data
        
    except Exception as e:
        print(f"Error getting dashboard: {e}")
        return None


async def update_user_dashboard(user_id: str, dashboard_data: Dict[str, Any]) -> bool:
    """Update user dashboard."""
    try:
        collection = db.database[COLLECTIONS["dashboards"]]
        dashboard_data["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"user_id": user_id},
            {"$set": dashboard_data},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None
    except Exception as e:
        print(f"Error updating dashboard: {e}")
        return False


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
        print(f"Error getting learning resources: {e}")
        return []


async def get_user_progress(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user learning progress."""
    try:
        collection = db.database[COLLECTIONS["user_progress"]]
        progress = await collection.find_one({"user_id": user_id})
        
        if not progress:
            # Create default progress
            progress_data = {
                "user_id": user_id,
                "completed_resources": [],
                "current_skills": ["Python", "JavaScript"],
                "skill_levels": {"Python": "intermediate", "JavaScript": "beginner"},
                "total_learning_hours": 25,
                "certificates_earned": 2,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = await collection.insert_one(progress_data)
            progress = await collection.find_one({"_id": result.inserted_id})
        
        if progress and "_id" in progress:
            progress["_id"] = str(progress["_id"])
        
        return progress
        
    except Exception as e:
        print(f"Error getting user progress: {e}")
        return None


async def update_application_status(application_id: str, status: str) -> bool:
    """Update application status in job's applications_received array."""
    try:
        print(f"Updating application status: {application_id} to {status}")
        
        # Use 'jobs' collection directly, not from COLLECTIONS mapping
        jobs_collection = db.database["jobs"]
        
        # First check if document exists
        test_job = await jobs_collection.find_one({"applications_received.application_id": application_id})
        print(f"Found job with application: {test_job is not None}")
        if test_job:
            print(f"Job ID: {test_job.get('job_id')}")
        
        # Update status in job's applications_received array
        result = await jobs_collection.update_one(
            {"applications_received.application_id": application_id},
            {
                "$set": {
                    "applications_received.$.status": status,
                    "updated_date": datetime.utcnow()
                }
            }
        )
        print(f"Update result - modified_count: {result.modified_count}")
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating application status: {e}")
        import traceback
        traceback.print_exc()
        return False
