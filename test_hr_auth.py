#!/usr/bin/env python3
"""
Test HR authentication flow step by step
"""

import json
import requests
import time

def test_hr_authentication():
    """Test the complete HR authentication flow"""
    
    print("🔐 Testing HR Authentication Flow...")
    
    # Step 1: Login
    print("\n1️⃣ Testing Login...")
    login_data = {
        "email": "hr@company.com",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Login successful!")
            print(f"Token Type: {login_result.get('token_type')}")
            print(f"User Type: {login_result.get('user', {}).get('user_type')}")
            print(f"User Email: {login_result.get('user', {}).get('email')}")
            
            access_token = login_result.get('access_token')
            print(f"Access Token (first 20 chars): {access_token[:20]}...")
            
            # Step 2: Test HR Dashboard
            print("\n2️⃣ Testing HR Dashboard Access...")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            dashboard_response = requests.get(
                "http://localhost:8000/api/v1/hr/dashboard",
                headers=headers,
                timeout=10
            )
            
            print(f"Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✅ HR Dashboard access successful!")
                dashboard_data = dashboard_response.json()
                print(f"Dashboard Data: {json.dumps(dashboard_data, indent=2)}")
            else:
                print("❌ HR Dashboard access failed!")
                try:
                    error_data = dashboard_response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error: {dashboard_response.text}")
            
            # Step 3: Test HR Jobs
            print("\n3️⃣ Testing HR Jobs Access...")
            
            jobs_response = requests.get(
                "http://localhost:8000/api/v1/hr/jobs",
                headers=headers,
                timeout=10
            )
            
            print(f"Jobs Status: {jobs_response.status_code}")
            
            if jobs_response.status_code == 200:
                print("✅ HR Jobs access successful!")
                jobs_data = jobs_response.json()
                print(f"Jobs Data: {json.dumps(jobs_data, indent=2)}")
            else:
                print("❌ HR Jobs access failed!")
                try:
                    error_data = jobs_response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error: {jobs_response.text}")
                    
        else:
            print("❌ Login failed!")
            try:
                error_data = login_response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error: {login_response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is it running on localhost:8000?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_job_seeker_authentication():
    """Test job seeker authentication for comparison"""
    
    print("\n\n👤 Testing Job Seeker Authentication...")
    
    login_data = {
        "email": "arjun.sharma@email.com",
        "password": "TechLead@123"
    }
    
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Job Seeker login successful!")
            print(f"User Type: {login_result.get('user', {}).get('user_type')}")
            print(f"User Email: {login_result.get('user', {}).get('email')}")
        else:
            print("❌ Job Seeker login failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_hr_authentication()
    test_job_seeker_authentication()
