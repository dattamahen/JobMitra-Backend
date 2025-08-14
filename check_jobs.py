#!/usr/bin/env python3
"""
Check jobs in database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_jobs():
    """Check what jobs exist in database"""
    
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/jobmitra')
    
    try:
        client = AsyncIOMotorClient(mongo_uri)
        db = client.get_database()
        
        print("Checking jobs in database...")
        
        jobs = await db.jobs.find({}, {"job_id": 1, "title": 1, "company": 1, "posted_by_hr_id": 1, "posted_date": 1, "is_active": 1}).to_list(length=None)
        
        print(f"Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"- {job.get('job_id', 'No ID')} | {job.get('title', 'No title')} | {job.get('company', 'No company')} | HR: {job.get('posted_by_hr_id', 'No HR')} | Active: {job.get('is_active', False)}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_jobs())