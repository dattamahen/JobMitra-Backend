#!/usr/bin/env python3
"""
Test the intelligent job matching algorithm.
"""

import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def create_test_user_with_skills():
    """Create a test user with comprehensive skills for matching."""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017/jobmitra")
        db = client.jobmitra
        collection = db.user_profiles
        
        # Create user with skills that match some jobs
        test_user = {
            "user_id": "test_match_user",
            "email": "testmatch@example.com",
            "first_name": "John",
            "last_name": "Developer",
            "user_type": "candidate",
            "user_status": "active",
            "user_plan": "free",
            "profile_created_on": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            
            # Skills that should match with jobs in database
            "skills": [
                "Python", "JavaScript", "React", "TypeScript", 
                "Node.js", "MongoDB", "AWS", "Docker"
            ],
            
            # Certifications
            "certifications": [
                {"name": "AWS Certified Developer", "issuer": "Amazon"},
                {"name": "Python Professional", "issuer": "Python Institute"}
            ],
            
            # Professional info with keywords
            "professional_info": {
                "professional_summary": "Experienced full-stack developer with expertise in Python, React, and cloud technologies. Strong background in web development, API design, and database management.",
                "key_contributions": "Led development of scalable web applications, implemented microservices architecture, optimized database performance",
                "current_role": "Senior Software Developer",
                "total_experience": "5 years"
            },
            
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5OOH9AESgy"  # testpassword123
        }
        
        # Insert or update the user
        await collection.replace_one(
            {"email": "testmatch@example.com"},
            test_user,
            upsert=True
        )
        
        print("✅ Created test user with matching skills")
        print(f"📝 User skills: {test_user['skills']}")
        print(f"🏆 User certifications: {[cert['name'] for cert in test_user['certifications']]}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")

def test_intelligent_job_matching():
    """Test the intelligent job matching endpoint."""
    try:
        # First login to get token
        login_data = {
            "email": "testmatch@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result["access_token"]
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return
        
        # Test the enhanced jobs endpoint
        headers = {"Authorization": f"Bearer {token}"}
        url = "http://localhost:8000/api/v1/jobs?page=1&per_page=5"
        
        print(f"\n🔍 Testing intelligent job matching: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Total jobs after intelligent filtering: {data.get('total_count', 0)}")
            print(f"📊 Matching info: {data.get('matching_info', {})}")
            
            jobs = data.get('jobs', [])
            print(f"\n📋 Top {len(jobs)} matched jobs:")
            
            for i, job in enumerate(jobs, 1):
                match_score = job.get('match_score', 0)
                match_percentage = job.get('match_percentage', 0)
                title = job.get('title', 'Unknown')
                company = job.get('company', 'Unknown')
                skills_required = job.get('skills_required', [])
                
                print(f"\n  {i}. {title} at {company}")
                print(f"     Match Score: {match_score:.3f} ({match_percentage}%)")
                print(f"     Required Skills: {skills_required[:5]}{'...' if len(skills_required) > 5 else ''}")
                
                # Show why it matched
                if match_percentage >= 80:
                    print(f"     🎯 Excellent Match!")
                elif match_percentage >= 60:
                    print(f"     ✅ Great Match!")
                elif match_percentage >= 40:
                    print(f"     👍 Good Match")
                elif match_percentage >= 20:
                    print(f"     📝 Decent Match")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

async def main():
    print("🚀 Setting up test user with skills...")
    await create_test_user_with_skills()
    
    print("\n🧠 Testing intelligent job matching...")
    test_intelligent_job_matching()

if __name__ == "__main__":
    asyncio.run(main())
