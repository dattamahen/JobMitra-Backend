"""
Test script for the new POST /jobs API endpoint.
Demonstrates how to send user skills in request body for intelligent job matching.
"""

import asyncio
import json
import requests
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test.developer@example.com"
TEST_USER_PASSWORD = "SecurePass123!"

async def test_jobs_post_api():
    """Test the POST /jobs endpoint with user skills."""
    
    print("🚀 Testing POST /jobs API with user skills...")
    
    # Step 1: Login to get authentication token
    print("\n1️⃣ Authenticating user...")
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if login_response.status_code == 200:
            auth_data = login_response.json()
            token = auth_data["access_token"]
            print(f"✅ Login successful! Token: {token[:20]}...")
        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Prepare headers with authentication
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 3: Test different job search scenarios
    test_scenarios = [
        {
            "name": "Full Stack Developer Skills",
            "request_body": {
                "page": 1,
                "per_page": 5,
                "user_skills": [
                    "Python", "JavaScript", "React", "Node.js", "MongoDB", 
                    "Docker", "AWS", "TypeScript", "FastAPI", "PostgreSQL"
                ],
                "user_certifications": [
                    "AWS Solutions Architect", "MongoDB Certified Developer"
                ],
                "user_experience_keywords": [
                    "backend", "frontend", "api", "database", "cloud", 
                    "microservices", "rest", "automation"
                ]
            }
        },
        {
            "name": "Data Science Skills",
            "request_body": {
                "page": 1,
                "per_page": 5,
                "user_skills": [
                    "Python", "Machine Learning", "TensorFlow", "Pandas", 
                    "NumPy", "Scikit-learn", "SQL", "Jupyter", "Data Analysis"
                ],
                "user_certifications": [
                    "Google Data Analytics", "Coursera ML Certificate"
                ],
                "user_experience_keywords": [
                    "machine learning", "data science", "analytics", "modeling",
                    "statistics", "visualization", "algorithms"
                ]
            }
        },
        {
            "name": "Frontend Developer Skills",
            "request_body": {
                "page": 1,
                "per_page": 5,
                "user_skills": [
                    "React", "Angular", "Vue.js", "JavaScript", "TypeScript",
                    "HTML", "CSS", "SASS", "Webpack", "Redux"
                ],
                "user_certifications": [
                    "React Developer Certification"
                ],
                "user_experience_keywords": [
                    "frontend", "ui", "ux", "responsive", "component",
                    "spa", "performance", "optimization"
                ]
            }
        }
    ]
    
    # Step 4: Test each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i+1}️⃣ Testing: {scenario['name']}")
        print(f"   Skills: {scenario['request_body']['user_skills'][:3]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/jobs", 
                headers=headers, 
                json=scenario['request_body']
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success! Found {result['total_count']} matching jobs")
                print(f"   📊 Matching Info: {result['matching_info']['matching_criteria']}")
                
                # Show top 3 matches
                if result['jobs']:
                    print(f"   🎯 Top matches:")
                    for job in result['jobs'][:3]:
                        print(f"      • {job.get('title', 'N/A')} at {job.get('company', 'N/A')} - {job.get('match_percentage', 0):.1f}% match")
                else:
                    print(f"   ⚠️ No jobs found matching criteria")
                    
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request error: {e}")
    
    # Step 5: Test with minimal skills
    print(f"\n4️⃣ Testing: Minimal Skills (Edge Case)")
    minimal_request = {
        "page": 1,
        "per_page": 3,
        "user_skills": ["Python"],
        "keywords": "developer"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/jobs", headers=headers, json=minimal_request)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Minimal skills test: {result['total_count']} jobs found")
        else:
            print(f"   ❌ Minimal skills test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Minimal skills test error: {e}")
    
    print(f"\n🎉 POST /jobs API testing completed!")

if __name__ == "__main__":
    asyncio.run(test_jobs_post_api())
