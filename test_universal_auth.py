#!/usr/bin/env python3
"""
Universal Authentication Test - All User Types & All Endpoints
"""
import requests
import json

def test_user_type(email, password, user_type, endpoints_to_test):
    """Test authentication and endpoint access for a specific user type"""
    base_url = "http://localhost:8000"
    
    print(f"\n🔍 Testing {user_type.upper()} User: {email}")
    print("-" * 60)
    
    # Step 1: Login
    login_data = {"email": email, "password": password}
    
    try:
        login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"✅ Login Success")
            print(f"   👤 User Type: {login_result['user']['user_type']}")
            
            token = login_result['access_token']
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            # Step 2: Test each endpoint
            for endpoint_name, endpoint_path in endpoints_to_test.items():
                try:
                    response = requests.get(f"{base_url}{endpoint_path}", headers=headers)
                    status_icon = "✅" if response.status_code == 200 else "❌"
                    print(f"   {status_icon} {endpoint_name}: {response.status_code}")
                    
                    if response.status_code != 200 and response.status_code != 404:
                        print(f"      Error: {response.text[:100]}...")
                        
                except Exception as e:
                    print(f"   ❌ {endpoint_name}: Exception - {e}")
            
        else:
            print(f"❌ Login Failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Request Failed: {e}")

def main():
    """Test all user types with their respective endpoints"""
    print("🚀 UNIVERSAL AUTHENTICATION TEST - ALL USER TYPES")
    print("=" * 70)
    
    # Define test users
    test_users = [
        {
            "email": "arjun.sharma@email.com",
            "password": "JobSeeker@123", 
            "user_type": "job_seeker",
            "endpoints": {
                "Dashboard": "/api/v1/dashboard",
                "Profile": "/api/v1/auth/profile",
                "Jobs Search": "/api/v1/jobs",
                "Recommended Jobs": "/api/v1/jobs/recommended"
            }
        },
        {
            "email": "kavya.nair@email.com",
            "password": "HRUser@12345",
            "user_type": "hr", 
            "endpoints": {
                "HR Dashboard": "/api/v1/hr/dashboard",
                "HR Jobs": "/api/v1/hr/jobs",
                "Profile": "/api/v1/auth/profile",
                "General Dashboard": "/api/v1/dashboard"
            }
        },
        {
            "email": "admin@jobmitra.com",
            "password": "Admin@12345",
            "user_type": "admin",
            "endpoints": {
                "HR Dashboard": "/api/v1/hr/dashboard", 
                "HR Jobs": "/api/v1/hr/jobs",
                "Profile": "/api/v1/auth/profile",
                "General Dashboard": "/api/v1/dashboard"
            }
        }
    ]
    
    # Test each user type
    for user in test_users:
        test_user_type(
            user["email"], 
            user["password"], 
            user["user_type"], 
            user["endpoints"]
        )
    
    print(f"\n🎯 SUMMARY:")
    print("=" * 70)
    print("✅ = Endpoint accessible (200 OK)")
    print("❌ = Endpoint blocked or error")
    print("\nExpected Results:")
    print("- Job Seekers: Should access general endpoints")
    print("- HR Users: Should access HR + general endpoints") 
    print("- Admin Users: Should access all endpoints")

if __name__ == "__main__":
    main()
