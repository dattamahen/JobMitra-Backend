#!/usr/bin/env python3
"""
Simple HR Dashboard Test
"""

import requests
import json

def test_hr_api():
    """Test HR dashboard API with detailed error handling"""
    
    print("🧪 Testing HR Dashboard API")
    print("=" * 40)
    
    try:
        # Step 1: Test health endpoint
        print("1. Testing health endpoint...")
        health_response = requests.get('http://localhost:8000/api/v1/health', timeout=5)
        if health_response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
            return
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend at http://localhost:8000")
        print("   💡 Please start the backend with: python -m uvicorn main:app --reload")
        return
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return
    
    # Step 2: Login as HR
    print("2. Logging in as HR...")
    login_data = {
        'email': 'hr1@company.com',
        'password': 'hrpassword1'
    }
    
    try:
        login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            print("   ✅ HR Login successful")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Step 3: Test HR dashboard
    print("3. Testing HR dashboard...")
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        dashboard_response = requests.get('http://localhost:8000/api/v1/hr/dashboard', headers=headers, timeout=10)
        
        print(f"   Status Code: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            print("   ✅ HR Dashboard API successful")
            
            print("\n📊 Dashboard Response:")
            print(json.dumps(dashboard_data, indent=2))
            
            # Check if we got demo data
            if dashboard_data.get('total_jobs_posted', 0) > 0:
                print("\n🎉 SUCCESS: Demo data is working!")
            else:
                print("\n❌ FAILED: Still getting empty data")
                
        else:
            print(f"   ❌ Dashboard failed: {dashboard_response.status_code}")
            print(f"   Response: {dashboard_response.text}")
            
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")

if __name__ == "__main__":
    test_hr_api()
