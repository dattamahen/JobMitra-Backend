"""
Debug script for HR jobs functionality
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def debug_hr_jobs():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.jobmitra
    
    print("=== DEBUG HR JOBS ===")
    
    # Check the specific job
    job_id = '689dc76a94b8fc569eb6ed7a'
    job = await db.jobs.find_one({'_id': ObjectId(job_id)})
    
    if job:
        print(f"Job found: {job.get('title', 'No title')}")
        print(f"   Company: {job.get('company', 'No company')}")
        print(f"   Posted by HR: {job.get('posted_by_hr_id', 'No HR ID')}")
        print(f"   Active: {job.get('is_active', True)}")
        
        hr_id = job.get('posted_by_hr_id')
        if hr_id:
            # Check if HR user exists
            hr_user = await db.user_profiles.find_one({'user_id': hr_id})
            if hr_user:
                print(f"HR User found: {hr_user.get('email')} (Type: {hr_user.get('user_type')})")
                
                # Test the jobs query
                jobs_cursor = db.jobs.find({'posted_by_hr_id': hr_id})
                jobs = await jobs_cursor.to_list(None)
                print(f"Jobs by this HR: {len(jobs)}")
                
                for job in jobs:
                    print(f"   - {job.get('title')} (Active: {job.get('is_active', True)})")
                    
            else:
                print(f"HR User with ID {hr_id} not found")
                
                # Show all HR users
                hr_users = await db.user_profiles.find({'user_type': 'hire'}).to_list(None)
                print(f"Available HR users ({len(hr_users)}):")
                for user in hr_users:
                    print(f"   - {user.get('user_id')} ({user.get('email')})")
    else:
        print("Job not found")
        
        # Show all jobs
        all_jobs = await db.jobs.find({}).to_list(None)
        print(f"All jobs in database: {len(all_jobs)}")
        for job in all_jobs[:3]:  # Show first 3
            print(f"   - {job.get('title')} by {job.get('posted_by_hr_id')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_hr_jobs())