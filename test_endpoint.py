#!/usr/bin/env python3
"""
Test the applications endpoint directly
"""

import asyncio
import requests
import json

async def test_endpoint():
    """Test the applications endpoint"""
    
    # First, let's try to login and get a token
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        print("Attempting to login...")
        login_response = requests.post(login_url, json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get("access_token")
            print(f"Got token: {token[:20]}...")
            
            # Now test the applications endpoint
            user_id = login_result.get("user", {}).get("user_id")
            apps_url = f"http://localhost:8000/api/v1/users/{user_id}/applied-jobs"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            print("Testing applications endpoint...")
            apps_response = requests.get(apps_url, headers=headers)
            print(f"Applications status: {apps_response.status_code}")
            
            if apps_response.status_code == 200:
                apps_data = apps_response.json()
                print(f"Applications data: {json.dumps(apps_data, indent=2)}")
            else:
                print(f"Applications error: {apps_response.text}")
        else:
            print(f"Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())