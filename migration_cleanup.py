#!/usr/bin/env python3
"""
Migration script to clean up specific fields from MongoDB collections
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    # Connect to MongoDB
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmitra"))
    db = client.get_default_database()
    
    try:
        # Delete applications_count from jobs collection  
        jobs_result = await db.job_listings.update_many(
            {},
            {"$unset": {"applications_count": ""}}
        )
        print(f"✅ Removed applications_count from {jobs_result.modified_count} jobs")
        
        # Also try alternative field name
        jobs_result2 = await db.job_listings.update_many(
            {},
            {"$unset": {"application_count": ""}}
        )
        print(f"✅ Removed application_count from {jobs_result2.modified_count} jobs")
        
        # Delete overall_jobs_applied from users collection
        users_result = await db.user_profiles.update_many(
            {},
            {"$unset": {"overall_jobs_applied": ""}}
        )
        print(f"✅ Removed overall_jobs_applied from {users_result.modified_count} users")
        
        # Also check if there are any documents with this field
        remaining_users = await db.user_profiles.count_documents({"overall_jobs_applied": {"$exists": True}})
        print(f"📊 Remaining users with overall_jobs_applied field: {remaining_users}")
        
        remaining_jobs = await db.job_listings.count_documents({"applications_count": {"$exists": True}})
        print(f"📊 Remaining jobs with applications_count field: {remaining_jobs}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(run_migration())