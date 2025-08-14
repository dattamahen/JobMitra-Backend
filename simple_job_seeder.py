#!/usr/bin/env python3
"""
Simple Job Data Seeder
"""

import asyncio
import requests
import json
from datetime import datetime, timedelta

def create_jobs_via_api():
    """Create jobs using the HR API endpoints"""
    
    print("🏢 Creating Jobs for Kavya Nair via API")
    print("=" * 50)
    
    # Step 1: Login as Kavya Nair
    login_data = {
        "email": "kavya.nair@email.com",
        "password": "HRUser@12345"
    }
    
    try:
        login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json()['access_token']
        print("✅ Logged in as Kavya Nair")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Define 10 job postings
        jobs_to_create = [
            {
                "title": "Senior Full Stack Developer",
                "company": "TechCorp Solutions",
                "location": "San Francisco, CA",
                "employment_type": "full_time",
                "description": "We are seeking a highly skilled Senior Full Stack Developer to join our dynamic engineering team.",
                "requirements": ["5+ years experience", "React/Node.js", "MongoDB"],
                "skills": ["React", "Node.js", "MongoDB", "JavaScript"],
                "salary_range": {"min": 120000, "max": 160000, "currency": "USD"},
                "application_deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "is_remote": False,
                "experience_level": "senior"
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
                "application_deadline": (datetime.utcnow() + timedelta(days=25)).isoformat(),
                "is_remote": True,
                "experience_level": "mid"
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
                "application_deadline": (datetime.utcnow() + timedelta(days=18)).isoformat(),
                "is_remote": False,
                "experience_level": "mid"
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
                "application_deadline": (datetime.utcnow() + timedelta(days=35)).isoformat(),
                "is_remote": False,
                "experience_level": "mid"
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
                "application_deadline": (datetime.utcnow() + timedelta(days=28)).isoformat(),
                "is_remote": False,
                "experience_level": "senior"
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
                "application_deadline": (datetime.utcnow() + timedelta(days=40)).isoformat(),
                "is_remote": False,
                "experience_level": "mid"
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
                "application_deadline": (datetime.utcnow() + timedelta(days=32)).isoformat(),
                "is_remote": False,
                "experience_level": "senior"
            },
            {
                "title": "Backend Python Developer",
                "company": "APIWorks Inc",
                "location": "Remote",
                "employment_type": "full_time",
                "description": "Build robust and scalable APIs using Python and Django/FastAPI.",
                "requirements": ["4+ years Python", "Django/FastAPI", "PostgreSQL"],
                "skills": ["Python", "Django", "FastAPI", "PostgreSQL"],
                "salary_range": {"min": 95000, "max": 130000, "currency": "USD"},
                "application_deadline": (datetime.utcnow() + timedelta(days=26)).isoformat(),
                "is_remote": True,
                "experience_level": "mid"
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
                "application_deadline": (datetime.utcnow() + timedelta(days=22)).isoformat(),
                "is_remote": False,
                "experience_level": "mid"
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
                "application_deadline": (datetime.utcnow() + timedelta(days=45)).isoformat(),
                "is_remote": False,
                "experience_level": "senior"
            }
        ]
        
        created_count = 0
        
        for i, job_data in enumerate(jobs_to_create, 1):
            try:
                response = requests.post(
                    'http://localhost:8000/api/v1/hr/jobs',
                    headers=headers,
                    json=job_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ {i:2d}. Created: {job_data['title']}")
                    created_count += 1
                else:
                    print(f"❌ {i:2d}. Failed: {job_data['title']} - {response.status_code}")
                    print(f"    Error: {response.text}")
                    
            except Exception as e:
                print(f"❌ {i:2d}. Exception: {job_data['title']} - {e}")
        
        print(f"\n🎉 Successfully created {created_count} out of {len(jobs_to_create)} jobs!")
        
        # Test the HR dashboard to see the results
        print("\n📊 Testing HR Dashboard with new data...")
        dashboard_response = requests.get('http://localhost:8000/api/v1/hr/dashboard', headers=headers)
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print("✅ HR Dashboard Response:")
            print(f"   Total Jobs Posted: {dashboard_data['total_jobs_posted']}")
            print(f"   Active Jobs: {dashboard_data['active_jobs']}")
            print(f"   Recent Jobs: {len(dashboard_data['recent_jobs'])}")
            
            if dashboard_data['total_jobs_posted'] > 0:
                print("\n📋 Recent Jobs:")
                for job in dashboard_data['recent_jobs'][:3]:
                    print(f"   • {job['title']} at {job['company']}")
        else:
            print(f"❌ Dashboard test failed: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_jobs_via_api()
