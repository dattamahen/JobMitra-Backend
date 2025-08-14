#!/usr/bin/env python3
"""
Restart Backend and Test HR Dashboard
"""

import subprocess
import time
import requests
import json
import os
import signal
import sys

def find_and_kill_process():
    """Find and kill existing FastAPI process"""
    try:
        # For Windows, find python processes on port 8000
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if ':8000 ' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    print(f"Found process on port 8000 with PID: {pid}")
                    subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                    print("Killed existing process")
                    time.sleep(2)
                    break
    except Exception as e:
        print(f"Error killing process: {e}")

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    
    # Change to backend directory
    backend_dir = r"e:\Projects\JobMitra-Backend"
    os.chdir(backend_dir)
    
    # Start uvicorn with reload
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(10):
        time.sleep(1)
        try:
            response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend started successfully!")
                return process
        except:
            continue
    
    print("❌ Backend failed to start")
    return None

def test_hr_dashboard():
    """Test HR dashboard after restart"""
    print("\n🔐 Testing HR Dashboard...")
    
    # Login
    login_data = {
        'email': 'hr1@company.com',
        'password': 'hrpassword1'
    }
    
    try:
        login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            print("✅ HR Login successful")
            
            # Test dashboard
            headers = {'Authorization': f'Bearer {token}'}
            dashboard_response = requests.get('http://localhost:8000/api/v1/hr/dashboard', headers=headers)
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                print("✅ HR Dashboard API successful")
                print(f"\n📊 Dashboard Stats:")
                print(f"   Total Jobs: {dashboard_data['total_jobs_posted']}")
                print(f"   Active Jobs: {dashboard_data['active_jobs']}")
                print(f"   Recent Jobs: {len(dashboard_data['recent_jobs'])}")
                
                if dashboard_data['total_jobs_posted'] > 0:
                    print("🎉 SUCCESS: HR Dashboard now returns demo data!")
                    return True
                else:
                    print("❌ FAILED: Still returning empty data")
                    return False
            else:
                print(f"❌ Dashboard failed: {dashboard_response.status_code}")
                return False
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Restarting Backend to Apply Changes...")
    print("=" * 50)
    
    # Kill existing process
    find_and_kill_process()
    
    # Start new process
    backend_process = start_backend()
    
    if backend_process:
        try:
            # Test the dashboard
            success = test_hr_dashboard()
            
            if success:
                print("\n✅ HR Dashboard fix confirmed!")
                print("💡 You can now test in your browser or frontend")
            else:
                print("\n❌ HR Dashboard still needs fixing")
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
        finally:
            print("🔪 Terminating backend...")
            backend_process.terminate()
            backend_process.wait()
    else:
        print("❌ Could not start backend")
