#!/usr/bin/env python3
"""
Test the profile update endpoint by first registering a user.
"""

import requests
import json

# API configuration
BASE_URL = "http://localhost:8000/api/v1"
REGISTER_URL = f"{BASE_URL}/auth/register"
LOGIN_URL = f"{BASE_URL}/auth/login"
PROFILE_URL = f"{BASE_URL}/auth/profile"

def test_full_profile_flow():
    """Test the complete flow: register -> login -> update profile"""
    
    print("🧪 Testing Full Profile Flow...")
    
    # Step 1: Register a new user
    register_data = {
        "email": "newtestuser@example.com",
        "password": "password123",
        "first_name": "New",
        "last_name": "TestUser",
        "user_type": "candidate",
        "skills": ["JavaScript", "Python"],
        "phone": "+1234567890",
        "city": "Test City",
        "state": "Test State"
    }
    
    print("\n1. Registering new user...")
    try:
        register_response = requests.post(REGISTER_URL, json=register_data)
        print(f"Register response status: {register_response.status_code}")
        
        if register_response.status_code == 200:
            register_result = register_response.json()
            print("✅ User registration successful")
            print(f"User ID: {register_result['user_id']}")
        else:
            print("❌ User registration failed:", register_response.text)
            # Continue anyway in case user already exists
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return
    
    # Step 2: Login with the new user
    login_data = {
        "email": "newtestuser@example.com",
        "password": "password123"
    }
    
    print("\n2. Logging in...")
    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result["access_token"]
            print("✅ Login successful")
            print(f"Token: {token[:50]}...")
        else:
            print("❌ Login failed:", login_response.text)
            return
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 3: Test profile update with the corrected payload
    print("\n3. Testing profile update...")
    
    # Corrected payload (removing invalid certifications and fixing field names)
    profile_update_data = {
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
        "desired_job_title": "Software Architect",  # Fixed typo
        "area_of_expertise": ["Web Development", "API Design", "Cloud Architecture"],
        "key_contributions": "Led migration of legacy systems to microservices architecture, improving performance by 40%",
        "github_url": "https://github.com/user001",
        "portfolio_url": "https://www.test.com",
        "youtube_url": "https://www.youtube.com/@dattamahen"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"Sending profile update to: {PROFILE_URL}")
    print(f"Payload: {json.dumps(profile_update_data, indent=2)}")
    
    try:
        update_response = requests.put(PROFILE_URL, json=profile_update_data, headers=headers)
        print(f"\nProfile update response status: {update_response.status_code}")
        print(f"Response body: {update_response.text}")
        
        if update_response.status_code == 200:
            print("✅ Profile update successful!")
            
            # Parse and display the response
            response_data = update_response.json()
            print(f"Updated user ID: {response_data.get('user_id')}")
            print(f"Updated name: {response_data.get('first_name')} {response_data.get('last_name')}")
            print(f"Updated skills: {response_data.get('skills')}")
            
        else:
            print("❌ Profile update failed")
            try:
                error_detail = update_response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Raw error response: {update_response.text}")
                
    except Exception as e:
        print(f"❌ Profile update error: {e}")
        
    # Step 4: Test with problematic certifications
    print("\n4. Testing profile update with problematic certifications...")
    
    problematic_data = profile_update_data.copy()
    problematic_data["certifications"] = ["[object Object]"]  # This should be handled gracefully now
    
    try:
        update_response2 = requests.put(PROFILE_URL, json=problematic_data, headers=headers)
        print(f"Profile update with bad certs status: {update_response2.status_code}")
        print(f"Response: {update_response2.text}")
        
        if update_response2.status_code == 200:
            print("✅ Profile update handled problematic certifications successfully!")
        else:
            print("❌ Profile update still fails with problematic certifications")
            
    except Exception as e:
        print(f"❌ Profile update with bad certs error: {e}")

if __name__ == "__main__":
    test_full_profile_flow()
