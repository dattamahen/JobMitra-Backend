#!/usr/bin/env python3
"""
Fix the test user's applied jobs
"""

import asyncio
from db_simple import db

async def fix_test_user():
    """Fix test user's applied jobs"""
    try:
        await db.connect_to_mongo()
        print("Connected to database")
        
        # Find the test user
        user = await db.database["users"].find_one({"email": "test@example.com"})
        if user:
            user_id = user["user_id"]
            print(f"Found user with ID: {user_id}")
            
            # Add application record with correct user_id
            application_record = {
                "job_id": "front-end-ui-engineer-jobmitra-r9x8vi",
                "application_id": f"{user_id}_front-end-ui-engineer-jobmitra-r9x8vi",
                "status": "applied",
                "match_analysis_done": True,
                "match_percentage": 45,
                "tailor_resume_done": True,
                "is_applied": True,
                "applied_date": "2025-01-15T10:30:00"
            }
            
            # Update user with application
            result = await db.database["users"].update_one(
                {"user_id": user_id},
                {"$push": {"overall_jobs_applied": application_record}}
            )
            
            print(f"Updated user applications: {result.modified_count} documents modified")
        else:
            print("Test user not found")
        
        await db.close_mongo_connection()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_test_user())