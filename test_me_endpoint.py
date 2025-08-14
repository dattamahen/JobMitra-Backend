#!/usr/bin/env python3
"""
Test the /auth/me endpoint to debug the 500 error.
"""

import requests
import json

# API configuration
BASE_URL = "http://localhost:8000/api/v1"
ME_URL = f"{BASE_URL}/auth/me"

def test_me_endpoint():
    """Test the /auth/me endpoint with different scenarios"""
    
    print("🧪 Testing /auth/me endpoint...")
    
    # Test 1: Without token (should get 401)
    print("\n1. Testing without token...")
    try:
        response = requests.get(ME_URL)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: With invalid token (should get 401)
    print("\n2. Testing with invalid token...")
    try:
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(ME_URL, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Try to create a valid token scenario by registering and logging in
    print("\n3. Testing complete flow: register -> login -> /auth/me...")
    
    # Register a test user
    register_url = f"{BASE_URL}/auth/register"
    register_data = {
        "email": "debug_user@test.com",
        "password": "password123",
        "first_name": "Debug",
        "last_name": "User",
        "user_type": "candidate"
    }
    
    try:
        reg_response = requests.post(register_url, json=register_data)
        print(f"Register status: {reg_response.status_code}")
        if reg_response.status_code != 200:
            print(f"Register response: {reg_response.text}")
        
        # Try to login
        login_url = f"{BASE_URL}/auth/login"
        login_data = {
            "email": "debug_user@test.com",
            "password": "password123"
        }
        
        login_response = requests.post(login_url, json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result["access_token"]
            print("✅ Login successful, now testing /auth/me...")
            
            # Test /auth/me with valid token
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(ME_URL, headers=headers)
            print(f"/auth/me status: {me_response.status_code}")
            print(f"/auth/me response: {me_response.text}")
            
            if me_response.status_code == 500:
                print("❌ 500 error confirmed - there's a bug in the /auth/me endpoint")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error in flow test: {e}")

if __name__ == "__main__":
    test_me_endpoint()
