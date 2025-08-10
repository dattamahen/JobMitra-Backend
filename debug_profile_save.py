#!/usr/bin/env python3
"""
Debug script to test profile save functionality
"""
import asyncio
import auth_db
from datetime import datetime

async def test_profile_save():
    print("🔍 Testing profile save functionality...")
    
    # First, try to get any user from the database
    print("\n1. Checking existing users...")
    try:
        users = await auth_db.list_all_users()
        print(f"   Found {len(users)} users in database")
        
        if users:
            test_user = users[0]  # Use first user for testing
            user_id = test_user.get("user_id")
            print(f"   Testing with user: {test_user.get('email')} (ID: {user_id})")
            
            # 2. Try to update this user's profile
            print("\n2. Testing profile update...")
            update_data = {
                "professional_info.professional_summary": "Test summary updated at " + datetime.now().isoformat(),
                "professional_info.desired_job_title": "Test Job Title",
                "professional_info.certifications": ["Test Cert 1", "Test Cert 2"],
                "updated_at": datetime.now().isoformat()
            }
            
            print(f"   Update data: {update_data}")
            
            success = await auth_db.update_user_profile(user_id, update_data)
            print(f"   Update result: {success}")
            
            # 3. Verify the update by reading the user back
            print("\n3. Verifying update...")
            updated_user = await auth_db.get_user_by_id(user_id)
            
            if updated_user:
                print(f"   Professional info: {updated_user.get('professional_info', {})}")
                print(f"   Updated at: {updated_user.get('updated_at')}")
            else:
                print("   ❌ Could not retrieve updated user")
                
        else:
            print("   ❌ No users found in database")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_profile_save())
