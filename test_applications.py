#!/usr/bin/env python3
"""
Test script to check applications endpoint
"""

import asyncio
import sys
from db_simple import db
from auth_db import get_user_by_id

async def test_applications():
    """Test applications data"""
    try:
        # Connect to database
        await db.connect_to_mongo()
        print("Connected to database")
        
        # Get all users
        users_cursor = db.database["users"].find({})
        users = []
        async for user in users_cursor:
            users.append(user)
        
        print(f"Found {len(users)} users")
        
        for user in users:
            user_id = user.get("user_id")
            email = user.get("email", "No email")
            applied_jobs = user.get("overall_jobs_applied", [])
            
            print(f"\nUser: {user_id} ({email})")
            print(f"   Applied jobs count: {len(applied_jobs)}")
            
            if applied_jobs:
                for i, app in enumerate(applied_jobs):
                    job_id = app.get("job_id", "No job_id")
                    status = app.get("status", "No status")
                    is_applied = app.get("is_applied", False)
                    applied_date = app.get("applied_date", "No date")
                    print(f"   [{i+1}] Job: {job_id}, Status: {status}, Applied: {is_applied}, Date: {applied_date}")
        
        # Close connection
        await db.close_mongo_connection()
        print("\nDatabase connection closed")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_applications())