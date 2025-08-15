"""
Migration script to convert overall_jobs_applied from array of strings to array of objects
"""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from schemas import JobApplicationRecord

async def migrate_applications():
    """Migrate existing string-based job applications to object format"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.jobmitra
    users_collection = db.users
    
    print("🔄 Starting migration of overall_jobs_applied field...")
    
    # Find all users with string-based overall_jobs_applied
    cursor = users_collection.find({
        "overall_jobs_applied": {"$exists": True, "$type": "array"}
    })
    
    migrated_count = 0
    skipped_count = 0
    
    async for user in cursor:
        user_id = user.get("user_id")
        applied_jobs = user.get("overall_jobs_applied", [])
        
        # Check if already migrated (contains objects)
        if applied_jobs and isinstance(applied_jobs[0], dict):
            print(f"⏭️  Skipping {user_id} - already migrated")
            skipped_count += 1
            continue
        
        # Convert string array to object array
        new_applied_jobs = []
        for job_id in applied_jobs:
            if isinstance(job_id, str):
                application_record = JobApplicationRecord(
                    job_id=job_id,
                    application_id=f"{user_id}_{job_id}",
                    status="applied",
                    applied_date=datetime.utcnow(),
                    last_updated=datetime.utcnow()
                )
                new_applied_jobs.append(application_record.dict())
        
        # Update user document
        if new_applied_jobs:
            result = await users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"overall_jobs_applied": new_applied_jobs}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Migrated {user_id} - {len(new_applied_jobs)} applications")
                migrated_count += 1
            else:
                print(f"❌ Failed to migrate {user_id}")
        else:
            print(f"⚠️  No applications to migrate for {user_id}")
    
    print(f"\n🎉 Migration completed!")
    print(f"   Migrated: {migrated_count} users")
    print(f"   Skipped: {skipped_count} users")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_applications())