#!/usr/bin/env python3
"""
Debug and Direct MongoDB Job Creation
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from bson import ObjectId

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_simple import db
from auth_db import get_user_by_email

async def check_users():
    """Check if users exist in the database"""
    print("👥 Checking Users in Database")
    print("=" * 40)
    
    users = await db.database.users.find({}).to_list(None)
    print(f"Found {len(users)} users in database:")
    
    for user in users:
        print(f"  • {user.get('name', 'Unknown')} ({user.get('email', 'No email')})")
        print(f"    User Type: {user.get('user_type', 'Not set')}")
        print(f"    User ID: {user.get('user_id', 'Not set')}")
        print()

async def check_kavya_user():
    """Check Kavya Nair specifically"""
    print("🔍 Checking Kavya Nair User")
    print("=" * 40)
    
    kavya = await get_user_by_email("kavya.nair@email.com")
    if kavya:
        print("✅ Found Kavya Nair:")
        print(f"   Name: {kavya.get('name')}")
        print(f"   Email: {kavya.get('email')}")
        print(f"   User Type: {kavya.get('user_type')}")
        print(f"   User ID: {kavya.get('user_id')}")
        return kavya
    else:
        print("❌ Kavya Nair not found")
        
        # Try to find by partial email match
        all_users = await db.database.users.find({}).to_list(None)
        for user in all_users:
            if 'kavya' in user.get('email', '').lower():
                print(f"Found similar user: {user.get('email')} - {user.get('name')}")
        return None

async def check_existing_jobs():
    """Check existing jobs in database"""
    print("📋 Checking Existing Jobs")
    print("=" * 40)
    
    jobs = await db.database.jobs.find({}).to_list(None)
    print(f"Found {len(jobs)} jobs in database:")
    
    for job in jobs:
        print(f"  • {job.get('title', 'No title')} - {job.get('company', 'No company')}")
        print(f"    Posted by HR ID: {job.get('posted_by_hr_id', 'Not set')}")
        print(f"    Posted date: {job.get('posted_date', 'Not set')}")
        print()

async def create_jobs_directly():
    """Create jobs directly in MongoDB"""
    print("🏗️ Creating Jobs Directly in MongoDB")
    print("=" * 50)
    
    # Check if Kavya exists
    kavya = await check_kavya_user()
    if not kavya:
        print("❌ Cannot create jobs - Kavya Nair user not found")
        return
    
    hr_user_id = kavya['user_id']
    print(f"✅ Using HR User ID: {hr_user_id}")
    
    # Define jobs to create
    jobs_data = [
        {
            "title": "Senior Full Stack Developer",
            "company": "TechCorp Solutions",
            "location": "San Francisco, CA",
            "employment_type": "full_time",
            "description": "We are seeking a highly skilled Senior Full Stack Developer to join our dynamic engineering team.",
            "requirements": ["5+ years experience", "React/Node.js", "MongoDB"],
            "skills": ["React", "Node.js", "MongoDB", "JavaScript"],
            "salary_range": {"min": 120000, "max": 160000, "currency": "USD"},
            "posted_date": datetime.utcnow(),
            "application_deadline": datetime.utcnow() + timedelta(days=30),
            "is_remote": False,
            "experience_level": "senior",
            "is_active": True,
            "posted_by_hr_id": hr_user_id,
            "applications_count": 15,
            "views_count": 120
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudTech Inc",
            "location": "Remote",
            "employment_type": "full_time",
            "description": "Join our DevOps team to help build and maintain scalable infrastructure.",
            "requirements": ["3+ years DevOps", "Docker/Kubernetes", "AWS"],
            "skills": ["Docker", "Kubernetes", "AWS", "Python"],
            "salary_range": {"min": 100000, "max": 140000, "currency": "USD"},
            "posted_date": datetime.utcnow(),
            "application_deadline": datetime.utcnow() + timedelta(days=25),
            "is_remote": True,
            "experience_level": "mid",
            "is_active": True,
            "posted_by_hr_id": hr_user_id,
            "applications_count": 8,
            "views_count": 85
        },
        {
            "title": "Frontend React Developer",
            "company": "StartupXYZ",
            "location": "New York, NY",
            "employment_type": "contract",
            "description": "We're looking for a talented Frontend Developer to join our startup.",
            "requirements": ["3+ years React", "JavaScript/TypeScript", "CSS"],
            "skills": ["React", "JavaScript", "TypeScript", "CSS"],
            "salary_range": {"min": 80000, "max": 110000, "currency": "USD"},
            "posted_date": datetime.utcnow(),
            "application_deadline": datetime.utcnow() + timedelta(days=18),
            "is_remote": False,
            "experience_level": "mid",
            "is_active": True,
            "posted_by_hr_id": hr_user_id,
            "applications_count": 22,
            "views_count": 95
        },
        {
            "title": "Data Scientist",
            "company": "DataFlow Analytics",
            "location": "Boston, MA",
            "employment_type": "full_time",
            "description": "Join our data science team to extract insights from large datasets.",
            "requirements": ["Master's degree", "Python/SQL", "Machine Learning"],
            "skills": ["Python", "SQL", "Machine Learning", "Statistics"],
            "salary_range": {"min": 110000, "max": 150000, "currency": "USD"},
            "posted_date": datetime.utcnow(),
            "application_deadline": datetime.utcnow() + timedelta(days=35),
            "is_remote": False,
            "experience_level": "mid",
            "is_active": True,
            "posted_by_hr_id": hr_user_id,
            "applications_count": 12,
            "views_count": 78
        },
        {
            "title": "Mobile App Developer",
            "company": "MobileFirst Tech",
            "location": "Austin, TX",
            "employment_type": "full_time",
            "description": "Create innovative mobile applications for iOS and Android platforms.",
            "requirements": ["4+ years mobile dev", "Swift/Kotlin", "React Native"],
            "skills": ["iOS", "Android", "Swift", "Kotlin", "React Native"],
            "salary_range": {"min": 105000, "max": 145000, "currency": "USD"},
            "posted_date": datetime.utcnow(),
            "application_deadline": datetime.utcnow() + timedelta(days=28),
            "is_remote": False,
            "experience_level": "senior",
            "is_active": True,
            "posted_by_hr_id": hr_user_id,
            "applications_count": 18,
            "views_count": 110
        },
        {
            "title": "Python Backend Developer",
            "company": "APIWorks Inc",
            "location": "Remote",
            "employment_type": "full_time",
            "description": "Build robust and scalable APIs using Python and Django/FastAPI.",
            "requirements": ["4+ years Python", "Django/FastAPI", "PostgreSQL"],
            "skills": ["Python", "Django", "FastAPI", "PostgreSQL"],
            "salary_range": {"min": 95000, "max": 130000, "currency": "USD"},
            "posted_date": datetime.utcnow(),
            "application_deadline": datetime.utcnow() + timedelta(days=26),
            "is_remote": True,
            "experience_level": "mid",
            "is_active": True,
            "posted_by_hr_id": hr_user_id,
            "applications_count": 25,
            "views_count": 140
        },
        {
            "title": "UX/UI Designer",
            "company": "DesignStudio Pro",
            "location": "Los Angeles, CA",
            "employment_type": "full_time",
            "description": "Create intuitive and beautiful user experiences for digital products.",
            "requirements": ["3+ years UX/UI", "Figma/Sketch", "User research"],
            "skills": ["UI Design", "UX Design", "Figma", "Prototyping"],
            "salary_range": {"min": 75000, "max": 105000, "currency": "USD"},
            "posted_date": datetime.utcnow(),
            "application_deadline": datetime.utcnow() + timedelta(days=22),
            "is_remote": False,
            "experience_level": "mid",
            "is_active": True,
            "posted_by_hr_id": hr_user_id,
            "applications_count": 30,
            "views_count": 160
        },
        {
            "title": "Cybersecurity Analyst",
            "company": "SecureNet Solutions",
            "location": "Washington, DC",
            "employment_type": "full_time",
            "description": "Help protect critical infrastructure and sensitive data.",
            "requirements": ["2+ years cybersecurity", "SIEM tools", "Security frameworks"],
            "skills": ["Cybersecurity", "SIEM", "Network Security"],
            "salary_range": {"min": 85000, "max": 120000, "currency": "USD"},
            "posted_date": datetime.utcnow(),
            "application_deadline": datetime.utcnow() + timedelta(days=40),
            "is_remote": False,
            "experience_level": "mid",
            "is_active": True,
            "posted_by_hr_id": hr_user_id,
            "applications_count": 14,
            "views_count": 90
        },
        {
            "title": "Product Manager",
            "company": "InnovateCorp",
            "location": "Seattle, WA",
            "employment_type": "full_time",
            "description": "Lead the development of our next-generation SaaS products.",
            "requirements": ["5+ years product management", "SaaS experience", "Agile"],
            "skills": ["Product Management", "Strategy", "Analytics"],
            "salary_range": {"min": 130000, "max": 170000, "currency": "USD"},
            "posted_date": datetime.utcnow(),
            "application_deadline": datetime.utcnow() + timedelta(days=32),
            "is_remote": False,
            "experience_level": "senior",
            "is_active": True,
            "posted_by_hr_id": hr_user_id,
            "applications_count": 20,
            "views_count": 180
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Innovations Lab",
            "location": "Palo Alto, CA",
            "employment_type": "full_time",
            "description": "Build and deploy machine learning models at scale.",
            "requirements": ["Master's/PhD", "4+ years ML", "TensorFlow/PyTorch"],
            "skills": ["Machine Learning", "Python", "TensorFlow", "PyTorch"],
            "salary_range": {"min": 140000, "max": 200000, "currency": "USD"},
            "posted_date": datetime.utcnow(),
            "application_deadline": datetime.utcnow() + timedelta(days=45),
            "is_remote": False,
            "experience_level": "senior",
            "is_active": True,
            "posted_by_hr_id": hr_user_id,
            "applications_count": 35,
            "views_count": 220
        }
    ]
    
    # Insert jobs into MongoDB
    try:
        result = await db.database.jobs.insert_many(jobs_data)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} jobs into MongoDB")
        
        # Verify insertion
        created_jobs = await db.database.jobs.find({"posted_by_hr_id": hr_user_id}).to_list(None)
        print(f"✅ Verified: {len(created_jobs)} jobs found for Kavya Nair")
        
        print("\n📋 Created Jobs:")
        for i, job in enumerate(created_jobs, 1):
            print(f"   {i:2d}. {job['title']} - {job['company']}")
            print(f"       Applications: {job['applications_count']}, Views: {job['views_count']}")
        
        return len(created_jobs)
        
    except Exception as e:
        print(f"❌ Error inserting jobs: {e}")
        import traceback
        traceback.print_exc()
        return 0

async def test_hr_dashboard():
    """Test HR dashboard with the new data"""
    print("\n📊 Testing HR Dashboard Query")
    print("=" * 40)
    
    kavya = await get_user_by_email("kavya.nair@email.com")
    if not kavya:
        print("❌ Cannot test - Kavya Nair not found")
        return
    
    hr_user_id = kavya['user_id']
    
    # Query jobs directly from MongoDB
    jobs = await db.database.jobs.find({"posted_by_hr_id": hr_user_id}).to_list(None)
    
    if jobs:
        total_jobs = len(jobs)
        active_jobs = len([job for job in jobs if job.get("is_active", True)])
        total_applications = sum(job.get("applications_count", 0) for job in jobs)
        
        print(f"✅ Direct MongoDB Query Results:")
        print(f"   Total Jobs: {total_jobs}")
        print(f"   Active Jobs: {active_jobs}")
        print(f"   Total Applications: {total_applications}")
        
        print(f"\n📋 Recent Jobs (first 3):")
        for i, job in enumerate(jobs[:3], 1):
            print(f"   {i}. {job['title']} at {job['company']}")
            print(f"      ID: {job['_id']}")
            print(f"      Posted: {job['posted_date']}")
    else:
        print("❌ No jobs found in direct query")

async def main():
    """Main debug and creation function"""
    print("🔧 MONGODB JOB CREATION DEBUG & FIX")
    print("=" * 60)
    
    # Step 1: Check users
    await check_users()
    
    # Step 2: Check existing jobs
    await check_existing_jobs()
    
    # Step 3: Check Kavya specifically
    kavya = await check_kavya_user()
    
    if kavya:
        # Step 4: Create jobs directly
        created_count = await create_jobs_directly()
        
        if created_count > 0:
            # Step 5: Test the results
            await test_hr_dashboard()
            
            print(f"\n🎉 SUCCESS!")
            print(f"✅ Created {created_count} jobs for Kavya Nair")
            print(f"📊 Jobs are now in MongoDB and should appear in HR dashboard")
        else:
            print(f"\n❌ FAILED to create jobs")
    else:
        print(f"\n❌ CANNOT PROCEED - Kavya Nair user not found")

if __name__ == "__main__":
    asyncio.run(main())
