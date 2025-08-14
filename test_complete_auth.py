#!/usr/bin/env python3
"""
Complete authentication flow test - Frontend simulation
"""
import requests
import json

def test_complete_auth_flow():
    """Test the complete authentication flow as frontend would do it"""
    base_url = "http://localhost:8000"
    
    print("🔍 COMPLETE AUTHENTICATION FLOW TEST")
    print("=" * 50)
    
    # Step 1: HR Login
    print("\n1️⃣ HR Login:")
    login_data = {
        "email": "kavya.nair@email.com",
        "password": "HRUser@12345"
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            json=login_data
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"   ✅ Login Success")
            print(f"   📧 Email: {login_result['user']['email']}")
            print(f"   👤 User Type: {login_result['user']['user_type']}")
            print(f"   🔑 Token: {login_result['access_token'][:30]}...")
            
            token = login_result['access_token']
            
            # Step 2: HR Dashboard Access
            print("\n2️⃣ HR Dashboard Access:")
            dashboard_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            dashboard_response = requests.get(
                f"{base_url}/api/v1/hr/dashboard",
                headers=dashboard_headers
            )
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                print(f"   ✅ Dashboard Success")
                print(f"   📊 Total Jobs: {dashboard_data.get('total_jobs_posted', 0)}")
                print(f"   📊 Active Jobs: {dashboard_data.get('active_jobs', 0)}")
                
                # Step 3: Test other HR endpoints
                print("\n3️⃣ Other HR Endpoints:")
                
                # Test HR jobs endpoint
                jobs_response = requests.get(
                    f"{base_url}/api/v1/hr/jobs",
                    headers=dashboard_headers
                )
                
                print(f"   📋 HR Jobs Endpoint: {jobs_response.status_code}")
                if jobs_response.status_code == 200:
                    jobs_data = jobs_response.json()
                    print(f"      Jobs count: {len(jobs_data) if isinstance(jobs_data, list) else 'N/A'}")
                else:
                    print(f"      Error: {jobs_response.text}")
                    
            else:
                print(f"   ❌ Dashboard Failed: {dashboard_response.status_code}")
                print(f"      Error: {dashboard_response.text}")
                
        else:
            print(f"   ❌ Login Failed: {login_response.status_code}")
            print(f"      Error: {login_response.text}")
            
    except Exception as e:
        print(f"   ❌ Request Failed: {e}")
    
    # Step 4: Test Job Seeker for comparison
    print("\n4️⃣ Job Seeker Test (for comparison):")
    js_login_data = {
        "email": "arjun.sharma@email.com", 
        "password": "JobSeeker@123"
    }
    
    try:
        js_login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            headers={"Content-Type": "application/json"},
            json=js_login_data
        )
        
        if js_login_response.status_code == 200:
            js_result = js_login_response.json()
            print(f"   ✅ Job Seeker Login Success")
            print(f"   👤 User Type: {js_result['user']['user_type']}")
            
            # Test dashboard endpoint for job seeker
            js_token = js_result['access_token']
            js_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {js_token}"
            }
            
            js_dashboard_response = requests.get(
                f"{base_url}/api/v1/dashboard",
                headers=js_headers
            )
            
            print(f"   📊 Job Seeker Dashboard: {js_dashboard_response.status_code}")
            
        else:
            print(f"   ❌ Job Seeker Login Failed: {js_login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Job Seeker Test Failed: {e}")

if __name__ == "__main__":
    test_complete_auth_flow()
