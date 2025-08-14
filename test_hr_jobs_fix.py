#!/usr/bin/env python3
"""
Test HR Jobs API with Fixed Schema
"""

import requests
import json

def test_hr_jobs_api():
    """Test HR jobs API after schema fix"""
    
    print("🧪 Testing HR Jobs API After Schema Fix")
    print("=" * 50)
    
    # Login as Kavya
    login_data = {
        "email": "kavya.nair@email.com",
        "password": "HRUser@12345"
    }
    
    try:
        print("1. Logging in as HR user...")
        login_response = requests.post(
            'http://localhost:8000/api/v1/auth/login', 
            json=login_data,
            verify=False
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json()['access_token']
        print("✅ Login successful")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test HR dashboard (should work)
        print("\n2. Testing HR Dashboard...")
        dashboard_response = requests.get(
            'http://localhost:8000/api/v1/hr/dashboard',
            headers=headers,
            verify=False
        )
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print(f"✅ HR Dashboard: {dashboard_data['total_jobs_posted']} jobs")
        else:
            print(f"❌ Dashboard failed: {dashboard_response.status_code}")
        
        # Test HR jobs list (was failing before)
        print("\n3. Testing HR Jobs List...")
        jobs_response = requests.get(
            'http://localhost:8000/api/v1/hr/jobs',
            headers=headers,
            verify=False
        )
        
        if jobs_response.status_code == 200:
            jobs_data = jobs_response.json()
            print(f"✅ HR Jobs List successful!")
            print(f"   Total Jobs: {jobs_data['total_count']}")
            print(f"   Jobs in Response: {len(jobs_data['jobs'])}")
            
            if jobs_data['jobs']:
                print(f"\n📋 Sample Jobs:")
                for i, job in enumerate(jobs_data['jobs'][:3], 1):
                    print(f"   {i}. {job['title']} - {job['company']}")
                    print(f"      💰 Salary: {job.get('salary_range', 'Not specified')}")
                    print(f"      📊 {job['applications_count']} applications, {job['views_count']} views")
                    print(f"      🔧 Active: {'Yes' if job['is_active'] else 'No'}")
            
            print(f"\n🎉 SUCCESS: HR Jobs API is now working!")
            
        else:
            print(f"❌ Jobs list failed: {jobs_response.status_code}")
            print(f"Error: {jobs_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_hr_jobs_api()
