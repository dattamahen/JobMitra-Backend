"""
Optimized database operations with connection pooling and caching
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import settings
from cache import cache
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
    
    async def connect(self):
        """Initialize MongoDB connection with optimized settings"""
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
                minPoolSize=settings.MONGO_MIN_POOL_SIZE,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,
            )
            
            self.db = self.client.jobmitra
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("MongoDB connected successfully")
            
            # Create indexes for performance
            await self.create_indexes()
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    async def create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # User indexes
            await self.db.users.create_index("email", unique=True)
            await self.db.users.create_index("user_id", unique=True)
            await self.db.users.create_index([("skills", 1), ("user_type", 1)])
            
            # Job indexes
            await self.db.jobs.create_index("job_id", unique=True)
            await self.db.jobs.create_index([("skills_required", 1), ("location_type", 1)])
            await self.db.jobs.create_index([("created_at", -1)])
            
            # Application indexes
            await self.db.applications.create_index([("user_id", 1), ("job_id", 1)], unique=True)
            await self.db.applications.create_index([("user_id", 1), ("created_at", -1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Index creation failed: {e}")
    
    async def get_user_cached(self, user_id: str) -> Optional[Dict]:
        """Get user with caching"""
        cache_key = f"user:{user_id}"
        
        # Try cache first
        cached_user = await cache.get(cache_key)
        if cached_user:
            return cached_user
        
        # Fetch from database
        user = await self.db.users.find_one({"user_id": user_id})
        if user:
            user["_id"] = str(user["_id"])
            await cache.set(cache_key, user)
        
        return user
    
    async def update_user_cached(self, user_id: str, update_data: Dict) -> bool:
        """Update user and invalidate cache"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.db.users.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Invalidate cache
                await cache.invalidate_user_cache(user_id)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"User update failed: {e}")
            return False
    
    async def search_jobs_optimized(self, query: str, filters: Dict, limit: int = 20) -> List[Dict]:
        """Optimized job search with caching"""
        cache_key = f"jobs:search:{hash(str(filters))}:{query}:{limit}"
        
        # Try cache first
        cached_jobs = await cache.get(cache_key)
        if cached_jobs:
            return cached_jobs
        
        # Build MongoDB query
        mongo_query = {}
        
        if query:
            mongo_query["$text"] = {"$search": query}
        
        if filters.get("skills"):
            mongo_query["skills_required"] = {"$in": filters["skills"]}
        
        if filters.get("location_type"):
            mongo_query["location_type"] = filters["location_type"]
        
        if filters.get("experience_level"):
            mongo_query["experience_level"] = filters["experience_level"]
        
        # Execute query with projection for performance
        cursor = self.db.jobs.find(
            mongo_query,
            {
                "job_id": 1, "title": 1, "company": 1, "location": 1,
                "salary_range": 1, "skills_required": 1, "experience_level": 1,
                "job_type": 1, "created_at": 1, "_id": 0
            }
        ).sort("created_at", -1).limit(limit)
        
        jobs = await cursor.to_list(length=limit)
        
        # Cache results
        await cache.set(cache_key, jobs, 300)  # 5 minutes
        
        return jobs
    
    async def get_user_applications_cached(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get user applications with caching"""
        cache_key = f"applications:{user_id}:{limit}"
        
        # Try cache first
        cached_apps = await cache.get(cache_key)
        if cached_apps:
            return cached_apps
        
        # Fetch from database with job details
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$sort": {"created_at": -1}},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "job_id",
                    "foreignField": "job_id",
                    "as": "job_details"
                }
            },
            {"$unwind": "$job_details"},
            {
                "$project": {
                    "_id": 0,
                    "application_id": 1,
                    "job_id": 1,
                    "status": 1,
                    "applied_at": 1,
                    "job_title": "$job_details.title",
                    "company": "$job_details.company",
                    "match_percentage": 1,
                    "match_analysis_done": 1,
                    "tailor_resume_done": 1
                }
            }
        ]
        
        applications = await self.db.applications.aggregate(pipeline).to_list(length=limit)
        
        # Cache results
        await cache.set(cache_key, applications, 180)  # 3 minutes
        
        return applications
    
    async def create_application_optimized(self, application_data: Dict) -> Optional[str]:
        """Create application with optimized performance"""
        try:
            application_data["created_at"] = datetime.utcnow()
            
            # Use upsert to handle duplicates gracefully
            result = await self.db.applications.update_one(
                {
                    "user_id": application_data["user_id"],
                    "job_id": application_data["job_id"]
                },
                {"$set": application_data},
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                # Invalidate related caches
                await cache.delete(f"applications:{application_data['user_id']}:*")
                return application_data.get("application_id")
            
            return None
            
        except Exception as e:
            logger.error(f"Application creation failed: {e}")
            return None
    
    async def get_dashboard_data_cached(self, user_id: str) -> Dict:
        """Get dashboard data with aggressive caching"""
        cache_key = f"dashboard:{user_id}"
        
        # Try cache first
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # Fetch aggregated data
        dashboard_data = {
            "total_applications": await self.db.applications.count_documents({"user_id": user_id}),
            "pending_applications": await self.db.applications.count_documents({
                "user_id": user_id, 
                "status": {"$in": ["applied", "under_review"]}
            }),
            "recent_jobs": await self.db.jobs.find({}, {
                "job_id": 1, "title": 1, "company": 1, "_id": 0
            }).sort("created_at", -1).limit(5).to_list(length=5)
        }
        
        # Cache for 10 minutes
        await cache.set(cache_key, dashboard_data, 600)
        
        return dashboard_data

# Global database instance
db_manager = DatabaseManager()