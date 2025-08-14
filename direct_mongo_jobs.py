#!/usr/bin/env python3
"""
Direct MongoDB Job Creation using pymongo
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import json

def create_jobs_direct():
    """Create jobs directly using pymongo"""
    
    print("🔗 Connecting to MongoDB directly...")
    
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client.jobmitra
        
        print("✅ Connected to MongoDB")
        
        # Find Kavya user
        users = list(db.users.find({}))
        print(f"Found {len(users)} users")
        
        kavya = None
        for user in users:
            if 'kavya' in user.get('email', '').lower():
                kavya = user
                print(f"✅ Found Kavya: {user.get('email')}")
                break
        
        if not kavya:
            print("❌ Kavya not found in database")
            print("Available users:")
            for user in users:
                print(f"  - {user.get('email')} ({user.get('user_type')})")
            return
        
        # Check existing jobs
        existing_jobs = list(db.jobs.find({"posted_by_hr_id": kavya['user_id']}))
        print(f"Existing jobs for Kavya: {len(existing_jobs)}")
        
        # Clear existing jobs for fresh start
        if existing_jobs:
            db.jobs.delete_many({"posted_by_hr_id": kavya['user_id']})
            print("🗑️ Cleared existing jobs")
        
        # Create 10 new jobs
        jobs_to_create = []
        
        job_templates = [
            {"title": "Senior Full Stack Developer", "company": "TechCorp Solutions", "salary_min": 120000, "salary_max": 160000},
            {"title": "DevOps Engineer", "company": "CloudTech Inc", "salary_min": 100000, "salary_max": 140000},
            {"title": "Frontend React Developer", "company": "StartupXYZ", "salary_min": 80000, "salary_max": 110000},
            {"title": "Data Scientist", "company": "DataFlow Analytics", "salary_min": 110000, "salary_max": 150000},
            {"title": "Mobile App Developer", "company": "MobileFirst Tech", "salary_min": 105000, "salary_max": 145000},
            {"title": "Cybersecurity Analyst", "company": "SecureNet Solutions", "salary_min": 85000, "salary_max": 120000},
            {"title": "Product Manager", "company": "InnovateCorp", "salary_min": 130000, "salary_max": 170000},
            {"title": "Backend Python Developer", "company": "APIWorks Inc", "salary_min": 95000, "salary_max": 130000},
            {"title": "UX/UI Designer", "company": "DesignStudio Pro", "salary_min": 75000, "salary_max": 105000},
            {"title": "Machine Learning Engineer", "company": "AI Innovations Lab", "salary_min": 140000, "salary_max": 200000}
        ]
        
        for i, template in enumerate(job_templates):
            job = {
                "title": template["title"],
                "company": template["company"],
                "location": "San Francisco, CA",
                "employment_type": "full_time",
                "description": f"Exciting opportunity to work as a {template['title']} at {template['company']}. We are looking for talented individuals to join our team.",
                "requirements": [
                    "Bachelor's degree in relevant field",
                    "3+ years of experience",
                    "Strong communication skills"
                ],
                "skills": ["Python", "JavaScript", "Problem Solving"],
                "salary_range": {
                    "min": template["salary_min"],
                    "max": template["salary_max"],
                    "currency": "USD"
                },
                "posted_date": datetime.utcnow(),
                "application_deadline": datetime.utcnow() + timedelta(days=30),
                "is_remote": i % 2 == 0,  # Alternate remote/on-site
                "experience_level": "mid" if i < 5 else "senior",
                "is_active": True,
                "posted_by_hr_id": kavya['user_id'],
                "applications_count": (i + 1) * 5,  # 5, 10, 15, etc.
                "views_count": (i + 1) * 20  # 20, 40, 60, etc.
            }
            jobs_to_create.append(job)
        
        # Insert jobs
        result = db.jobs.insert_many(jobs_to_create)
        print(f"✅ Created {len(result.inserted_ids)} jobs")
        
        # Verify
        created_jobs = list(db.jobs.find({"posted_by_hr_id": kavya['user_id']}))
        print(f"✅ Verified: {len(created_jobs)} jobs in database")
        
        print("\n📋 Created Jobs:")
        total_applications = 0
        for i, job in enumerate(created_jobs, 1):
            print(f"  {i:2d}. {job['title']} - {job['company']}")
            print(f"      💰 ${job['salary_range']['min']:,} - ${job['salary_range']['max']:,}")
            print(f"      📊 {job['applications_count']} applications, {job['views_count']} views")
            total_applications += job['applications_count']
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Jobs: {len(created_jobs)}")
        print(f"   Total Applications: {total_applications}")
        print(f"   Average Applications: {total_applications // len(created_jobs)}")
        
        # Close connection
        client.close()
        print("\n🎉 SUCCESS: Jobs created in MongoDB!")
        print("💡 You can now test the HR dashboard API")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_jobs_direct()
