#!/usr/bin/env python3
"""
Test script to check users in database and test authentication
"""

import asyncio
import requests
import json
from db_simple import db

async def check_database():
    """Check what users are in the database"""
    
    print("🔍 Checking database users...")
    
    try:
        # Connect to database
        await db.connect_to_mongo()
        
        # Get users collection
        users_collection = db.database["users"]
        
        # Count total users
        total_users = await users_collection.count_documents({})
        print(f"📊 Total users in database: {total_users}")
        
        if total_users > 0:
            # Get all users
            users_cursor = users_collection.find({})
            users = await users_cursor.to_list(length=None)
            
            print("\n👥 Users found:")
            for user in users:
                print(f"  📧 Email: {user.get('email', 'N/A')}")
                print(f"  🆔 User ID: {user.get('user_id', 'N/A')}")
                print(f"  👤 User Type: {user.get('user_type', 'NOT SET')}")
                print(f"  ✅ Active: {user.get('is_active', False)}")
                print(f"  🔑 Has Password: {'password_hash' in user}")
                print("  " + "-" * 40)
        else:
            print("❌ No users found in database!")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db.close_mongo_connection()

def test_login_api():
    """Test the login API endpoint"""
    
    print("\n🔐 Testing login API...")
    
    # Test data
    test_credentials = {
        "email": "arjun.sharma@email.com",
        "password": "TechLead@123"
    }
    
    try:
        # Make login request
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=test_credentials,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"🌐 Response Status: {response.status_code}")
        print(f"🌐 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ Login successful!")
            print(f"🔑 Access Token: {response_data.get('access_token', 'N/A')[:20]}...")
            print(f"👤 User Type: {response_data.get('user', {}).get('user_type', 'N/A')}")
            print(f"📧 User Email: {response_data.get('user', {}).get('email', 'N/A')}")
        else:
            print("❌ Login failed!")
            try:
                error_data = response.json()
                print(f"🚨 Error: {error_data}")
            except:
                print(f"🚨 Error: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is it running?")
    except Exception as e:
        print(f"❌ Request error: {e}")

async def main():
    """Main function"""
    await check_database()
    test_login_api()

if __name__ == "__main__":
    asyncio.run(main())
