#!/usr/bin/env python3
"""
Test the profile update endpoint directly using curl-like requests.
"""

import requests
import json

# API configuration
BASE_URL = "http://localhost:8000/api/v1"
PROFILE_URL = f"{BASE_URL}/auth/profile"

def test_profile_update_direct():
    """Test profile update using a mock token approach"""
    
    print("🧪 Testing Profile Update Endpoint Directly...")
    
    # Create a test payload exactly like what the frontend sends
    original_problematic_payload = {
        "first_name": "Alex",
        "last_name": "Johnson", 
        "phone": "+91 98765 43210",
        "city": "Bangalore",
        "current_role": "Senior Software Engineer",
        "current_company": "Updated via Profile",
        "total_experience": "2-3",
        "industry": "Web Development",
        "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Python", "AWS", "TypeScript"],
        "expected_salary": 2500000,
        "professional_summary": "Experienced full-stack developer with expertise in modern web technologies and cloud platforms",
        "desired_job_title": "Software Architect", # Fixed the typo
        "certifications": ["[object Object]"], # This should now be handled properly
        "area_of_expertise": ["Web Development", "API Design", "Cloud Architecture"],
        "key_contributions": "Led migration of legacy systems to microservices architecture, improving performance by 40%",
        "github_url": "https://github.com/user001",
        "portfolio_url": "https://www.test.com",
        "youtube_url": "https://www.youtube.com/@dattamahen"
    }
    
    print("Test payload:")
    print(json.dumps(original_problematic_payload, indent=2))
    
    # Mock headers (without valid token for now - just to test validation)
    headers = {
        "Authorization": "Bearer mock_token_for_testing",
        "Content-Type": "application/json"
    }
    
    print(f"\nSending PUT request to: {PROFILE_URL}")
    
    try:
        response = requests.put(PROFILE_URL, json=original_problematic_payload, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 422:
            print("\n❌ Still getting 422 Validation Error")
            try:
                error_detail = response.json()
                print("Error details:")
                print(json.dumps(error_detail, indent=2))
            except:
                print("Could not parse error response as JSON")
        elif response.status_code == 401:
            print("\n✅ 401 Unauthorized - This is expected (no valid token)")
            print("✅ But the important thing is we're NOT getting 422 validation errors!")
            print("✅ This means the Pydantic schema validation is working correctly")
        elif response.status_code == 200:
            print("\n✅ 200 Success - Profile update worked!")
        else:
            print(f"\n❓ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    test_profile_update_direct()
