#!/usr/bin/env python3
"""
Verify Jobs in MongoDB and Test HR Dashboard
"""

from pymongo import MongoClient
import requests
import json

def verify_jobs_in_mongo():
    """Verify jobs exist in MongoDB"""
    print("🔍 Verifying Jobs in MongoDB")
    print("=" * 40)
    
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client.jobmitra
        
        # Find Kavya
        kavya = db.users.find_one({"email": {"$regex": "kavya", "$options": "i"}})
        if not kavya:
            print("❌ Kavya not found")
            return False
        
        print(f"✅ Found Kavya: {kavya['email']}")
        
        # Count her jobs
        job_count = db.jobs.count_documents({"posted_by_hr_id": kavya['user_id']})
        print(f"✅ Kavya has {job_count} jobs in MongoDB")
        
        if job_count > 0:
            # Show some job details
            jobs = list(db.jobs.find({"posted_by_hr_id": kavya['user_id']}).limit(3))
            print("\n📋 Sample Jobs:")
            for job in jobs:
                print(f"  • {job['title']} - {job['company']}")
                print(f"    Applications: {job['applications_count']}")
        
        client.close()
        return job_count > 0
        
    except Exception as e:
        print(f"❌ MongoDB Error: {e}")
        return False

def test_hr_dashboard_api():
    """Test HR dashboard API"""
    print("\n🌐 Testing HR Dashboard API")
    print("=" * 40)
    
    try:
        # Login as Kavya
        login_data = {
            "email": "kavya.nair@email.com",
            "password": "HRUser@12345"
        }
        
        login_response = requests.post(
            'http://localhost:8000/api/v1/auth/login',
            json=login_data,
            verify=False  # Disable SSL verification
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()['access_token']
        print("✅ Login successful")
        
        # Test dashboard
        headers = {'Authorization': f'Bearer {token}'}
        dashboard_response = requests.get(
            'http://localhost:8000/api/v1/hr/dashboard',
            headers=headers,
            verify=False
        )
        
        if dashboard_response.status_code == 200:
            data = dashboard_response.json()
            print("✅ HR Dashboard API successful")
            print(f"\n📊 Dashboard Data:")
            print(f"   Total Jobs Posted: {data['total_jobs_posted']}")
            print(f"   Active Jobs: {data['active_jobs']}")
            print(f"   Total Applications: {data['total_applications_received']}")
            print(f"   Recent Jobs Count: {len(data['recent_jobs'])}")
            
            if data['total_jobs_posted'] > 0:
                print(f"\n🎉 SUCCESS! Real data is being returned from MongoDB")
                print(f"\n📋 Recent Jobs:")
                for i, job in enumerate(data['recent_jobs'][:3], 1):
                    print(f"   {i}. {job['title']} - {job['company']}")
                return True
            else:
                print(f"\n❌ Still returning empty data")
                return False
        else:
            print(f"❌ Dashboard API failed: {dashboard_response.status_code}")
            print(f"Response: {dashboard_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API Test Error: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 MONGODB JOB VERIFICATION")
    print("=" * 50)
    
    # Step 1: Verify jobs in MongoDB
    mongo_ok = verify_jobs_in_mongo()
    
    if mongo_ok:
        # Step 2: Test HR dashboard API
        api_ok = test_hr_dashboard_api()
        
        if api_ok:
            print(f"\n✅ COMPLETE SUCCESS!")
            print(f"✅ Jobs are in MongoDB")
            print(f"✅ HR Dashboard API returns real data")
            print(f"💡 You should now see job data instead of empty values")
        else:
            print(f"\n⚠️ PARTIAL SUCCESS")
            print(f"✅ Jobs are in MongoDB")
            print(f"❌ HR Dashboard API has issues")
    else:
        print(f"\n❌ FAILED - No jobs found in MongoDB")

if __name__ == "__main__":
    main()
