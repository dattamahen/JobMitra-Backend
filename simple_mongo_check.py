#!/usr/bin/env python3
"""
Simple MongoDB Check and Job Creation
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_simple import db

async def simple_check():
    """Simple check of MongoDB contents"""
    try:
        print("🔍 Checking MongoDB...")
        
        # Check users collection
        users = await db.database.users.find({}).to_list(None)
        print(f"Users in database: {len(users)}")
        
        # Find Kavya
        kavya = None
        for user in users:
            if 'kavya' in user.get('email', '').lower():
                kavya = user
                print(f"Found Kavya: {user.get('email')} - {user.get('user_id')}")
                break
        
        if not kavya:
            print("❌ Kavya not found")
            return
        
        # Check jobs collection
        jobs = await db.database.jobs.find({}).to_list(None)
        print(f"Total jobs in database: {len(jobs)}")
        
        # Check Kavya's jobs
        kavya_jobs = await db.database.jobs.find({"posted_by_hr_id": kavya['user_id']}).to_list(None)
        print(f"Kavya's jobs: {len(kavya_jobs)}")
        
        # If no jobs, create one simple job
        if len(kavya_jobs) == 0:
            print("Creating a simple test job...")
            
            simple_job = {
                "title": "Test Software Developer",
                "company": "Test Company",
                "location": "Test City",
                "employment_type": "full_time",
                "description": "Test job description",
                "requirements": ["Test requirement 1", "Test requirement 2"],
                "skills": ["Python", "JavaScript"],
                "salary_range": {"min": 80000, "max": 120000, "currency": "USD"},
                "posted_date": datetime.utcnow(),
                "application_deadline": datetime.utcnow() + timedelta(days=30),
                "is_remote": False,
                "experience_level": "mid",
                "is_active": True,
                "posted_by_hr_id": kavya['user_id'],
                "applications_count": 5,
                "views_count": 25
            }
            
            result = await db.database.jobs.insert_one(simple_job)
            print(f"✅ Created job with ID: {result.inserted_id}")
            
            # Verify
            kavya_jobs_after = await db.database.jobs.find({"posted_by_hr_id": kavya['user_id']}).to_list(None)
            print(f"Kavya's jobs after creation: {len(kavya_jobs_after)}")
            
        else:
            print("✅ Kavya already has jobs:")
            for job in kavya_jobs:
                print(f"  - {job['title']} at {job['company']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_check())
