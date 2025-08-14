"""
Simple test for HR jobs functionality without authentication
"""

import asyncio
import sys
sys.path.append('.')

from job_db import job_db
from db_simple import db

async def test_hr_jobs():
    print("=== Testing HR Jobs Function ===")
    
    # Connect to database
    await db.connect_to_mongo()
    
    try:
        # Test with the HR user ID from the job
        hr_user_id = "hr001"
        print(f"Testing with HR user ID: {hr_user_id}")
        
        result = await job_db.get_jobs_by_hr(hr_user_id)
        print(f"Result: {result}")
        
        if result["jobs"]:
            print(f"Found {len(result['jobs'])} jobs:")
            for job in result["jobs"]:
                print(f"  - {job['title']} at {job['company']}")
        else:
            print("No jobs found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_hr_jobs())