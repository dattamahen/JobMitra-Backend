#!/usr/bin/env python3
"""
Simple script to test backend API
"""
import sys
import os
import subprocess
import time
import requests
import threading

def start_server():
    """Start the backend server"""
    try:
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        return process
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running!")
                break
        except:
            print(f"⏳ Attempt {i+1}/10 - Server not ready yet...")
            time.sleep(2)
    else:
        print("❌ Server failed to start")
        return False
    
    # Test login
    print("\n🔐 Testing login...")
    login_data = {
        "email": "kavya.nair@email.com", 
        "password": "HRUser@12345"
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print("✅ Login successful")
            
            # Test HR jobs endpoint
            print("\n📋 Testing HR jobs endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            jobs_response = requests.get(f"{base_url}/api/v1/hr/jobs", headers=headers)
            
            print(f"HR Jobs Status: {jobs_response.status_code}")
            if jobs_response.status_code == 200:
                data = jobs_response.json()
                print(f"✅ HR Jobs working! Got {len(data.get('jobs', []))} jobs")
                print(f"Response keys: {list(data.keys())}")
            else:
                print(f"❌ HR Jobs failed: {jobs_response.text}")
        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
    
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Backend API Test")
    
    # Start server in background
    server_process = start_server()
    if server_process:
        try:
            # Give server time to start
            time.sleep(3)
            test_api()
        finally:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
    else:
        print("❌ Could not start server")
