"""
Migration script to clear overall_jobs_applied field for all users
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def clear_applications():
    """Clear overall_jobs_applied field for all users"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.jobmitra
    users_collection = db.users
    
    print("🔄 Clearing overall_jobs_applied field for all users...")
    
    # Update all users to have empty overall_jobs_applied array
    result = await users_collection.update_many(
        {},  # Match all users
        {"$set": {"overall_jobs_applied": []}}
    )
    
    print(f"✅ Cleared applications for {result.modified_count} users")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(clear_applications())