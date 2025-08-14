#!/usr/bin/env python3
"""
Test job application functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_job_applications():
    """Test job application flow"""
    
    # Step 1: Login as job seeker
    print("Step 1: Login as job seeker...")
    job_seeker_login = {
        "email": "user001@test.com",
        "password": "test1234"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=job_seeker_login)
    if response.status_code != 200:
        print(f"Job seeker login failed: {response.text}")
        return
    
    job_seeker_token = response.json()["access_token"]
    print("Job seeker login successful!")
    
    # Step 2: Apply for a job
    print("\nStep 2: Apply for job...")
    job_id = "this-is-job-title-techcorpsolutio-2yupmn"  # Use existing job
    
    application_data = {
        "job_id": job_id,
        "cover_letter": "I am very interested in this position and believe my skills align well with the requirements."
    }
    
    headers = {
        "Authorization": f"Bearer {job_seeker_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/applications/apply", json=application_data, headers=headers)
    print(f"Application response status: {response.status_code}")
    
    if response.status_code == 200:
        print("Application submitted successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Application failed: {response.text}")
        return
    
    # Step 3: Login as HR and check applications
    print("\nStep 3: Login as HR...")
    hr_login = {
        "email": "hr001@test.com",
        "password": "test1234"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=hr_login)
    if response.status_code != 200:
        print(f"HR login failed: {response.text}")
        return
    
    hr_token = response.json()["access_token"]
    print("HR login successful!")
    
    # Step 4: Get job applications
    print("\nStep 4: Get job applications...")
    hr_headers = {
        "Authorization": f"Bearer {hr_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/hr/jobs/{job_id}/applications", headers=hr_headers)
    print(f"Applications response status: {response.status_code}")
    
    if response.status_code == 200:
        applications = response.json()
        print("Applications retrieved successfully!")
        print(f"Total applications: {applications['total_applications']}")
        print(json.dumps(applications, indent=2))
    else:
        print(f"Failed to get applications: {response.text}")

if __name__ == "__main__":
    test_job_applications()