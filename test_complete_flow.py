#!/usr/bin/env python3
"""
Complete end-to-end test: register -> login -> update profile
"""

import requests
import json

# API configuration
BASE_URL = "http://localhost:8000/api/v1"
REGISTER_URL = f"{BASE_URL}/auth/register"
LOGIN_URL = f"{BASE_URL}/auth/login"
PROFILE_URL = f"{BASE_URL}/auth/profile"
ME_URL = f"{BASE_URL}/auth/me"

def test_complete_flow():
    """Test complete flow with valid authentication"""
    
    print("🧪 Testing Complete Profile Update Flow...")
    
    # Step 1: Register (or use existing user)
    user_email = "complete_test@example.com"
    user_password = "password123"
    
    register_data = {
        "email": user_email,
        "password": user_password,
        "first_name": "Complete",
        "last_name": "Test",
        "user_type": "candidate"
    }
    
    print("\n1. Registering user...")
    try:
        register_response = requests.post(REGISTER_URL, json=register_data)
        if register_response.status_code == 200:
            print("✅ Registration successful")
        elif register_response.status_code == 400 and "already registered" in register_response.text:
            print("ℹ️ User already exists, proceeding with login")
        else:
            print(f"❌ Registration failed: {register_response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Step 2: Login
    print("\n2. Logging in...")
    login_data = {"email": user_email, "password": user_password}
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result["access_token"]
            print("✅ Login successful")
            print(f"Token: {token[:50]}...")
        else:
            print(f"❌ Login failed: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 3: Check current profile
    print("\n3. Getting current profile...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        me_response = requests.get(ME_URL, headers=headers)
        if me_response.status_code == 200:
            print("✅ Profile retrieval successful")
            profile_data = me_response.json()
            print(f"Current name: {profile_data['first_name']} {profile_data['last_name']}")
        else:
            print(f"❌ Profile retrieval failed: {me_response.text}")
    except Exception as e:
        print(f"❌ Profile retrieval error: {e}")
    
    # Step 4: Test profile update with original problematic payload
    print("\n4. Testing profile update with your original payload...")
    
    # Your exact original problematic payload
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
        "desired_job_title": "Software Architect", # Fixed typo
        "certifications": ["[object Object]"], # This should now be handled gracefully
        "area_of_expertise": ["Web Development", "API Design", "Cloud Architecture"],
        "key_contributions": "Led migration of legacy systems to microservices architecture, improving performance by 40%",
        "github_url": "https://github.com/user001",
        "portfolio_url": "https://www.test.com",
        "youtube_url": "https://www.youtube.com/@dattamahen"
    }
    
    try:
        update_response = requests.put(PROFILE_URL, json=profile_update_data, headers=headers)
        print(f"Profile update status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            print("✅ Profile update successful!")
            
            # Get updated profile
            print("\n5. Verifying updated profile...")
            me_response2 = requests.get(ME_URL, headers=headers)
            if me_response2.status_code == 200:
                updated_profile = me_response2.json()
                print(f"Updated name: {updated_profile['first_name']} {updated_profile['last_name']}")
                print(f"Updated phone: {updated_profile['phone']}")
                print(f"Updated skills: {updated_profile['skills']}")
                print(f"Professional info: {updated_profile.get('professional_info', {})}")
                print(f"Social links: {updated_profile.get('social_links', {})}")
            else:
                print(f"❌ Could not verify updated profile: {me_response2.text}")
                
        elif update_response.status_code == 422:
            print("❌ Still getting 422 validation error:")
            try:
                error_detail = update_response.json()
                print(json.dumps(error_detail, indent=2))
            except:
                print(update_response.text)
        else:
            print(f"❌ Profile update failed with status {update_response.status_code}:")
            print(update_response.text)
            
    except Exception as e:
        print(f"❌ Profile update error: {e}")

if __name__ == "__main__":
    test_complete_flow()
