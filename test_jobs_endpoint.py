#!/usr/bin/env python3
"""
Test the fixed jobs endpoint and add sample jobs if needed.
"""

import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

async def check_and_seed_jobs():
    """Check if jobs exist in database and add sample jobs if needed."""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017/jobmitra")
        db = client.jobmitra
        collection = db.jobs
        
        # Check existing jobs
        job_count = await collection.count_documents({})
        print(f"📊 Current jobs in database: {job_count}")
        
        if job_count == 0:
            print("📝 Adding sample jobs...")
            
            sample_jobs = [
                {
                    "job_id": "job_001",
                    "title": "Senior Python Developer",
                    "company": "TechCorp India",
                    "location": {
                        "city": "Bangalore",
                        "state": "Karnataka",
                        "country": "India",
                        "is_remote": False
                    },
                    "employment_type": "full_time",
                    "experience_level": "senior",
                    "job_type": "onsite",
                    "salary": {
                        "min": 1800000,
                        "max": 2500000,
                        "currency": "INR",
                        "period": "yearly"
                    },
                    "description": "We are looking for a Senior Python Developer to join our team and work on exciting projects using Django, FastAPI, and modern cloud technologies.",
                    "requirements": [
                        "5+ years of Python development experience",
                        "Strong knowledge of Django/FastAPI",
                        "Experience with cloud platforms (AWS/Azure)",
                        "Knowledge of database design and optimization"
                    ],
                    "skills_required": ["Python", "Django", "FastAPI", "AWS", "PostgreSQL"],
                    "skills_preferred": ["React", "Docker", "Kubernetes"],
                    "benefits": ["Health Insurance", "Flexible Work Hours", "Professional Development"],
                    "responsibilities": [
                        "Design and develop scalable web applications",
                        "Collaborate with cross-functional teams",
                        "Mentor junior developers",
                        "Code review and quality assurance"
                    ],
                    "posted_date": datetime.utcnow(),
                    "application_deadline": datetime.utcnow() + timedelta(days=30),
                    "is_active": True,
                    "posted_by_hr_id": "hr_001",
                    "views_count": 45,
                    "applications_count": 12,
                    "tags": ["python", "backend", "senior"]
                },
                {
                    "job_id": "job_002",
                    "title": "Frontend React Developer",
                    "company": "InnovateTech Solutions",
                    "location": {
                        "city": "Mumbai",
                        "state": "Maharashtra", 
                        "country": "India",
                        "is_remote": True
                    },
                    "employment_type": "full_time",
                    "experience_level": "mid",
                    "job_type": "remote",
                    "salary": {
                        "min": 1200000,
                        "max": 1800000,
                        "currency": "INR",
                        "period": "yearly"
                    },
                    "description": "Join our frontend team to build modern, responsive web applications using React, TypeScript, and cutting-edge UI frameworks.",
                    "requirements": [
                        "3+ years of React development experience",
                        "Strong TypeScript skills",
                        "Experience with state management (Redux/Context API)",
                        "Knowledge of modern CSS frameworks"
                    ],
                    "skills_required": ["React", "TypeScript", "JavaScript", "CSS", "HTML"],
                    "skills_preferred": ["Next.js", "Tailwind CSS", "Jest", "Cypress"],
                    "benefits": ["Remote Work", "Health Insurance", "Learning Budget"],
                    "responsibilities": [
                        "Develop responsive web applications",
                        "Collaborate with UI/UX designers",
                        "Write clean, maintainable code",
                        "Optimize application performance"
                    ],
                    "posted_date": datetime.utcnow() - timedelta(days=2),
                    "application_deadline": datetime.utcnow() + timedelta(days=25),
                    "is_active": True,
                    "posted_by_hr_id": "hr_002",
                    "views_count": 78,
                    "applications_count": 23,
                    "tags": ["react", "frontend", "remote"]
                },
                {
                    "job_id": "job_003",
                    "title": "DevOps Engineer",
                    "company": "CloudFirst Technologies",
                    "location": {
                        "city": "Hyderabad",
                        "state": "Telangana",
                        "country": "India",
                        "is_remote": False
                    },
                    "employment_type": "full_time",
                    "experience_level": "mid",
                    "job_type": "hybrid",
                    "salary": {
                        "min": 1500000,
                        "max": 2200000,
                        "currency": "INR",
                        "period": "yearly"
                    },
                    "description": "We're seeking a DevOps Engineer to help scale our infrastructure and improve our deployment pipelines using modern cloud technologies.",
                    "requirements": [
                        "3+ years of DevOps experience",
                        "Strong knowledge of AWS/Azure",
                        "Experience with Docker and Kubernetes",
                        "CI/CD pipeline expertise"
                    ],
                    "skills_required": ["AWS", "Docker", "Kubernetes", "Jenkins", "Terraform"],
                    "skills_preferred": ["Ansible", "Monitoring Tools", "Python", "Shell Scripting"],
                    "benefits": ["Hybrid Work", "Health Insurance", "Stock Options"],
                    "responsibilities": [
                        "Manage cloud infrastructure",
                        "Implement CI/CD pipelines",
                        "Monitor system performance",
                        "Ensure security best practices"
                    ],
                    "posted_date": datetime.utcnow() - timedelta(days=1),
                    "application_deadline": datetime.utcnow() + timedelta(days=20),
                    "is_active": True,
                    "posted_by_hr_id": "hr_003",
                    "views_count": 34,
                    "applications_count": 8,
                    "tags": ["devops", "cloud", "kubernetes"]
                }
            ]
            
            # Insert sample jobs
            result = await collection.insert_many(sample_jobs)
            print(f"✅ Added {len(result.inserted_ids)} sample jobs")
        
        # Check final count
        final_count = await collection.count_documents({})
        print(f"📊 Total jobs in database: {final_count}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error with database: {e}")
        import traceback
        traceback.print_exc()

def test_jobs_endpoint():
    """Test the jobs endpoint."""
    try:
        # Test the jobs endpoint
        url = "http://localhost:8000/api/v1/jobs?page=1&per_page=10"
        print(f"🔍 Testing endpoint: {url}")
        
        response = requests.get(url)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data.get('total_count', 0)} jobs")
            print(f"📝 Jobs returned: {len(data.get('jobs', []))}")
            
            # Print first job if available
            jobs = data.get('jobs', [])
            if jobs:
                first_job = jobs[0]
                print(f"📄 First job: {first_job.get('title', 'Unknown')} at {first_job.get('company', 'Unknown')}")
            else:
                print("📭 No jobs returned")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

async def main():
    print("🚀 Checking and seeding jobs database...")
    await check_and_seed_jobs()
    
    print("\n🔍 Testing jobs endpoint...")
    test_jobs_endpoint()

if __name__ == "__main__":
    asyncio.run(main())
