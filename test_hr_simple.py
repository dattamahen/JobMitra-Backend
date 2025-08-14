#!/usr/bin/env python3
"""
Simple test to verify HR authentication and job posting
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_hr_auth():
    """Test HR authentication and job posting"""
    
    # Step 1: Login as HR user
    print("Step 1: Attempting HR login...")
    login_data = {
        "email": "hr001@test.com",
        "password": "test1234"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            print("Login successful!")
            print(f"User type: {login_result['user']['user_type']}")
            token = login_result['access_token']
            
            # Step 2: Test job posting
            print("\nStep 2: Attempting job posting...")
            
            job_data = {
                "title": "Test Engineer",
                "company": "TechCorp Solutions",
                "location": {
                    "city": "Bengaluru",
                    "state": "Karnataka",
                    "country": "India",
                    "is_remote": False,
                    "timezone": "IST"
                },
                "employment_type": "full-time",
                "experience_level": "mid",
                "salary": {
                    "min": 1,
                    "max": 10,
                    "currency": "INR",
                    "period": "yearly",
                    "is_negotiable": True
                },
                "description": "QA certification in web and mobile application testing with automation expertise. Looking for experienced professionals to join our quality assurance team.",
                "requirements": ["Automation testing experience", "Manual testing skills", "Knowledge of testing frameworks"],
                "responsibilities": ["Independent contributor", "Test case development", "Bug reporting and tracking"],
                "skills_required": ["TypeScript", "JavaScript", "React"],
                "skills_preferred": ["TypeScript", "Vue.js"],
                "benefits": ["Dental Insurance"],
                "application_deadline": "2025-08-20T18:30:00.000Z",
                "company_info": {
                    "company_size": "51-200",
                    "industry": "Technology",
                    "website": "www.test.com",
                    "description": "test business"
                },
                "job_type": "onsite",
                "is_active": True,
                "application_instructions": "Test instructions",
                "external_apply_url": "www.test.com",
                "hr_contact": {
                    "name": "Sarah Johnson",
                    "email": "hr001@test.com",
                    "phone": "8899898988",
                    "title": "HR Manager",
                    "department": "Human Resources"
                },
                "tags": []
            }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            job_response = requests.post(f"{BASE_URL}/api/v1/hr/jobs", json=job_data, headers=headers)
            print(f"Job posting response status: {job_response.status_code}")
            
            if job_response.status_code == 200:
                print("Job posted successfully!")
                print(json.dumps(job_response.json(), indent=2))
            else:
                print("Job posting failed!")
                print(f"Error: {job_response.text}")
                
        else:
            print("Login failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_hr_auth()