#!/usr/bin/env python3
"""
Debug HR Jobs API Response for UI Issues
"""

import requests
import json
from datetime import datetime

def debug_hr_jobs_response():
    """Debug the exact API response structure"""
    
    print("🔧 DEBUGGING HR JOBS API RESPONSE")
    print("=" * 60)
    
    # Login as Kavya
    login_data = {
        "email": "kavya.nair@email.com",
        "password": "HRUser@12345"
    }
    
    try:
        print("1. Logging in...")
        login_response = requests.post(
            'http://localhost:8000/api/v1/auth/login', 
            json=login_data,
            verify=False
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()['access_token']
        print("✅ Login successful")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test HR Jobs endpoint with detailed response analysis
        print("\n2. Calling HR Jobs API...")
        jobs_response = requests.get(
            'http://localhost:8000/api/v1/hr/jobs',
            headers=headers,
            verify=False
        )
        
        print(f"   Status Code: {jobs_response.status_code}")
        print(f"   Response Headers: {dict(jobs_response.headers)}")
        
        if jobs_response.status_code == 200:
            try:
                jobs_data = jobs_response.json()
                print("✅ JSON Response parsed successfully")
                
                # Analyze response structure
                print(f"\n📊 Response Structure Analysis:")
                print(f"   Response Type: {type(jobs_data)}")
                print(f"   Response Keys: {list(jobs_data.keys()) if isinstance(jobs_data, dict) else 'Not a dict'}")
                
                if 'jobs' in jobs_data:
                    jobs_array = jobs_data['jobs']
                    print(f"   Jobs Array Length: {len(jobs_array)}")
                    print(f"   Jobs Array Type: {type(jobs_array)}")
                    
                    if jobs_array:
                        first_job = jobs_array[0]
                        print(f"\n📋 First Job Structure:")
                        print(f"   Job Type: {type(first_job)}")
                        print(f"   Job Keys: {list(first_job.keys()) if isinstance(first_job, dict) else 'Not a dict'}")
                        
                        # Check each field
                        print(f"\n🔍 Field Analysis:")
                        for key, value in first_job.items():
                            value_type = type(value).__name__
                            value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                            print(f"   {key}: {value_type} = {value_preview}")
                        
                        # Check for potential UI issues
                        print(f"\n⚠️ Potential UI Issues:")
                        
                        # Check date formats
                        if 'posted_date' in first_job:
                            posted_date = first_job['posted_date']
                            print(f"   Posted Date Type: {type(posted_date)} = {posted_date}")
                            if isinstance(posted_date, str):
                                try:
                                    parsed_date = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                                    print(f"   ✅ Date is parseable: {parsed_date}")
                                except:
                                    print(f"   ❌ Date format might be invalid")
                        
                        # Check for None values
                        none_fields = [k for k, v in first_job.items() if v is None]
                        if none_fields:
                            print(f"   Null Fields: {none_fields}")
                        
                        # Check for empty arrays
                        empty_arrays = [k for k, v in first_job.items() if isinstance(v, list) and len(v) == 0]
                        if empty_arrays:
                            print(f"   Empty Arrays: {empty_arrays}")
                
                # Full response for debugging
                print(f"\n📄 FULL RESPONSE (formatted):")
                print("=" * 50)
                print(json.dumps(jobs_data, indent=2, default=str))
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"Raw response: {jobs_response.text[:500]}...")
                
        else:
            print(f"❌ API call failed: {jobs_response.status_code}")
            print(f"Response: {jobs_response.text}")
        
        # Also test dashboard for comparison
        print(f"\n3. Testing Dashboard for comparison...")
        dashboard_response = requests.get(
            'http://localhost:8000/api/v1/hr/dashboard',
            headers=headers,
            verify=False
        )
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print(f"✅ Dashboard works: {dashboard_data['total_jobs_posted']} jobs")
        else:
            print(f"❌ Dashboard failed: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_hr_jobs_response()
