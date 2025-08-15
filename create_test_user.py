#!/usr/bin/env python3
"""
Create a test user with proper authentication
"""

import asyncio
from db_simple import db
from auth_db import create_user

async def create_test_user():
    """Create a test user with authentication"""
    try:
        await db.connect_to_mongo()
        print("Connected to database")
        
        # Create a test user
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "user_id": "test_user_001"
        }
        
        result = await create_user(user_data)
        print(f"User created: {result}")
        
        # Add some applied jobs to this user
        application_record = {
            "job_id": "front-end-ui-engineer-jobmitra-r9x8vi",
            "application_id": "test_user_001_front-end-ui-engineer-jobmitra-r9x8vi",
            "status": "applied",
            "match_analysis_done": True,
            "match_percentage": 45,
            "tailor_resume_done": True,
            "is_applied": True,
            "applied_date": "2025-01-15T10:30:00"
        }
        
        await db.database["users"].update_one(
            {"user_id": "test_user_001"},
            {"$push": {"overall_jobs_applied": application_record}}
        )
        
        print("Added test application to user")
        
        await db.close_mongo_connection()
        print("Database connection closed")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_user())