#!/usr/bin/env python3
"""
Test HR Dashboard with Demo Data
"""

import requests
import json
from datetime import datetime

def test_hr_dashboard():
    """Test HR login and dashboard with new demo data"""
    
    print("🔐 Testing HR Dashboard with Demo Data")
    print("=" * 50)
    
    # Step 1: Login as HR user
    login_data = {
        'email': 'hr1@company.com',
        'password': 'hrpassword1'
    }
    
    try:
        print("1. Logging in as HR user...")
        login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data, verify=False)
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            print("   ✅ HR Login successful")
            
            # Step 2: Test dashboard
            print("2. Fetching HR dashboard...")
            headers = {'Authorization': f'Bearer {token}'}
            dashboard_response = requests.get('http://localhost:8000/api/v1/hr/dashboard', headers=headers, verify=False)
            
            if dashboard_response.status_code == 200:
                print("   ✅ HR Dashboard API successful")
                dashboard_data = dashboard_response.json()
                
                print("\n📊 HR Dashboard Data:")
                print("-" * 30)
                print(f"Total Jobs Posted: {dashboard_data['total_jobs_posted']}")
                print(f"Active Jobs: {dashboard_data['active_jobs']}")
                print(f"Inactive Jobs: {dashboard_data['inactive_jobs']}")
                print(f"Total Applications: {dashboard_data['total_applications_received']}")
                print(f"Jobs Expiring Soon: {dashboard_data['jobs_expiring_soon']}")
                print(f"Recent Jobs Count: {len(dashboard_data['recent_jobs'])}")
                
                print("\n📋 Recent Jobs:")
                for i, job in enumerate(dashboard_data['recent_jobs'], 1):
                    print(f"  {i}. {job['title']} at {job['company']}")
                    print(f"     Location: {job['location']}")
                    print(f"     Applications: {job['applications_count']}")
                    print(f"     Active: {'Yes' if job['is_active'] else 'No'}")
                    print()
                
                print("✅ HR Dashboard now returns rich demo data like job-seeker dashboard!")
                
            else:
                print(f"   ❌ Dashboard failed: {dashboard_response.status_code}")
                print(f"   Error: {dashboard_response.text}")
                
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Please ensure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_hr_dashboard()
