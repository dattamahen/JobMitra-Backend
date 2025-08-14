"""
Focused test to demonstrate the POST /jobs API with detailed output.
"""

import requests
import json

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test.developer@example.com"
TEST_USER_PASSWORD = "SecurePass123!"

def test_focused_job_matching():
    """Test job matching with detailed output."""
    
    print("🎯 Focused Job Matching Test")
    print("=" * 50)
    
    # Login
    login_data = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test with specific skills
    request_body = {
        "page": 1,
        "per_page": 5,
        "user_skills": ["Python", "JavaScript", "React", "MongoDB", "FastAPI"],
        "user_certifications": ["AWS Developer", "React Certified"],
        "user_experience_keywords": ["backend", "frontend", "fullstack", "api", "database"]
    }
    
    print(f"\n📤 REQUEST:")
    print(f"   Skills: {request_body['user_skills']}")
    print(f"   Certifications: {request_body['user_certifications']}")
    print(f"   Experience Keywords: {request_body['user_experience_keywords'][:3]}...")
    
    # Make request
    response = requests.post(f"{BASE_URL}/jobs", headers=headers, json=request_body)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n📥 RESPONSE:")
        print(f"   ✅ Status: Success")
        print(f"   📊 Total Jobs Found: {result['total_count']}")
        print(f"   📋 Matching Logic: {result['matching_info']['matching_criteria']}")
        print(f"   🔍 Data Source: {result['matching_info']['data_source']}")
        
        if result['jobs']:
            print(f"\n🎯 TOP MATCHING JOBS:")
            for i, job in enumerate(result['jobs'][:3], 1):
                print(f"   {i}. {job['title']} at {job.get('company', 'Unknown')}")
                print(f"      📈 Match Score: {job['match_percentage']}%")
                print(f"      🛠️  Required Skills: {job.get('skills_required', [])[:3]}...")
                print(f"      💼 Experience Level: {job.get('experience_level', 'N/A')}")
                print()
        else:
            print(f"   ⚠️ No matching jobs found")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    test_focused_job_matching()
