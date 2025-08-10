"""
Test script to verify job posting is saving to database
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_simple import db
from job_db import job_db


async def test_database_connection():
    """Test if database connection is working"""
    try:
        await db.connect_to_mongo()
        print("✅ Database connection test completed")
        print(f"Fallback mode: {db.fallback_mode}")
        
        if not db.fallback_mode:
            # Test database operations
            collections = await db.database.list_collection_names()
            print(f"Available collections: {collections}")
            
            # Check if jobs collection exists
            jobs_count = await db.database["jobs"].count_documents({})
            print(f"Current jobs in database: {jobs_count}")
            
            # List some jobs if they exist
            if jobs_count > 0:
                jobs = await db.database["jobs"].find({}).limit(5).to_list(5)
                print("Sample jobs:")
                for i, job in enumerate(jobs, 1):
                    print(f"{i}. {job.get('title', 'No title')} at {job.get('company', 'No company')}")
        
        return not db.fallback_mode
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_job_posting():
    """Test job posting functionality"""
    try:
        from job_schemas import JobPostRequest, JobLocation, SalaryInfo, CompanyInfo, HRContact, ExperienceLevel, EmploymentType, JobType, CompanySize, Currency, SalaryPeriod
        
        # Create test job data
        test_job = {
            "title": "Test Software Engineer",
            "company": "Test Company",
            "location": JobLocation(
                city="Bangalore",
                state="Karnataka", 
                country="India",
                is_remote=False,
                timezone="IST"
            ),
            "employment_type": EmploymentType.FULL_TIME,
            "experience_level": ExperienceLevel.MID,
            "job_type": JobType.ONSITE,
            "salary": SalaryInfo(
                min=800000,
                max=1200000,
                currency=Currency.INR,
                period=SalaryPeriod.YEARLY,
                is_negotiable=True
            ),
            "description": "Test job posting to verify database connectivity. This is a longer description to meet the minimum character requirements for the job posting validation.",
            "requirements": ["Python programming experience", "FastAPI framework knowledge", "MongoDB database skills"],
            "responsibilities": ["Develop APIs using FastAPI", "Write comprehensive tests", "Debug and fix issues"],
            "skills_required": ["Python", "FastAPI", "MongoDB"],
            "skills_preferred": ["React", "Docker"],
            "benefits": ["Health Insurance", "Work from Home"],
            "company_info": CompanyInfo(
                company_size=CompanySize.MEDIUM,
                industry="Technology",
                website="https://testcompany.com",
                description="A test company for database testing"
            ),
            "hr_contact": HRContact(
                name="Test HR",
                email="hr@testcompany.com",
                phone="+91-9876543210",
                title="HR Manager",
                department="Human Resources"
            ),
            "tags": ["python", "backend", "api"],
            "application_deadline": None,
            "application_instructions": "Apply through our portal",
            "external_apply_url": None
        }
        
        # Convert to JobPostRequest
        job_request = JobPostRequest(**test_job)
        
        # Create job posting
        job_id = await job_db.create_job_posting(job_request, "test_hr_user_123")
        print(f"✅ Job posting created with ID: {job_id}")
        
        # Verify job was saved
        saved_job = await job_db.get_job_by_id(job_id)
        if saved_job:
            print(f"✅ Job verified in database: {saved_job['title']} at {saved_job['company']}")
            print(f"Job details: Posted on {saved_job['posted_date']}")
            return True
        else:
            print("❌ Job not found in database after creation")
            return False
            
    except Exception as e:
        print(f"❌ Job posting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_mongodb_compass():
    """Check what should be visible in MongoDB Compass"""
    try:
        if db.fallback_mode:
            print("❌ Currently in fallback mode - no data will be visible in MongoDB Compass")
            print("To fix this, set the MONGO_URI environment variable")
            return
        
        print("✅ Connected to MongoDB - checking what should be visible in Compass:")
        
        # List all databases
        admin_db = db.client.admin
        databases = await admin_db.command("listDatabases")
        print(f"Available databases: {[db_info['name'] for db_info in databases['databases']]}")
        
        # Check current database
        current_db_name = db.database.name
        print(f"Current database: {current_db_name}")
        
        # List collections in current database
        collections = await db.database.list_collection_names()
        print(f"Collections in {current_db_name}: {collections}")
        
        # Check jobs collection
        if "jobs" in collections:
            jobs_count = await db.database["jobs"].count_documents({})
            print(f"Jobs collection contains {jobs_count} documents")
            
            if jobs_count > 0:
                print("Recent jobs:")
                async for job in db.database["jobs"].find({}).sort("posted_date", -1).limit(3):
                    print(f"- {job.get('title')} at {job.get('company')} (ID: {job.get('job_id')})")
        else:
            print("No 'jobs' collection found")
            
    except Exception as e:
        print(f"❌ Error checking MongoDB Compass data: {e}")


async def main():
    """Main test function"""
    print("🔍 Testing JobMitra Database Connection and Job Posting")
    print("=" * 60)
    
    # Test 1: Database connection
    print("\n1. Testing database connection...")
    db_connected = await test_database_connection()
    
    if not db_connected:
        print("\n❌ Database not connected. To fix this:")
        print("1. Install MongoDB locally or use MongoDB Atlas")
        print("2. Set MONGO_URI environment variable")
        print("3. Example: MONGO_URI=mongodb://localhost:27017/jobmitra")
        print("4. Or create a .env file with MONGO_URI=your_mongodb_connection_string")
        return
    
    # Test 2: Job posting
    print("\n2. Testing job posting...")
    job_posted = await test_job_posting()
    
    # Test 3: Check Compass visibility
    print("\n3. Checking MongoDB Compass visibility...")
    await check_mongodb_compass()
    
    # Close connection
    await db.close_mongo_connection()
    
    print("\n" + "=" * 60)
    if db_connected and job_posted:
        print("✅ All tests passed! Jobs should be visible in MongoDB Compass")
    else:
        print("❌ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
