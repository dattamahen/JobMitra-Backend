#!/usr/bin/env python3
"""
Simple script to test user authentication and fix the user_type issue
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from auth_db import authenticate_user, get_user_by_email, list_all_users, update_user_profile

async def test_user_auth():
    """Test authentication for the job seeker user"""
    
    print("🔍 Testing authentication...")
    
    test_email = "arjun.sharma@email.com"
    test_password = "TechLead@123"
    
    try:
        # Check if user exists
        user = await get_user_by_email(test_email)
        if user:
            print(f"✅ User {test_email} found in database")
            print(f"Current user_type: {user.get('user_type', 'NOT SET')}")
            
            # If user_type is missing, add it
            if 'user_type' not in user:
                print("📝 Adding user_type to user...")
                success = await update_user_profile(user['user_id'], {'user_type': 'job_seeker'})
                if success:
                    print("✅ Added user_type successfully")
                else:
                    print("❌ Failed to add user_type")
            
            # Test authentication
            auth_user = await authenticate_user(test_email, test_password)
            if auth_user:
                print("✅ Authentication successful!")
                print(f"User type: {auth_user.get('user_type', 'NOT SET')}")
            else:
                print("❌ Authentication failed")
        else:
            print(f"❌ User {test_email} not found in database")
            
            # List all users to see what we have
            all_users = await list_all_users()
            print(f"Found {len(all_users)} users in database:")
            for u in all_users[:3]:  # Show first 3
                print(f"  - {u.get('email', 'NO EMAIL')} (type: {u.get('user_type', 'NOT SET')})")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def fix_all_users():
    """Add user_type to all users that don't have it"""
    
    print("🔧 Fixing all users...")
    
    try:
        all_users = await list_all_users()
        print(f"Found {len(all_users)} users")
        
        fixed_count = 0
        for user in all_users:
            email = user.get('email', '')
            
            # Determine user_type based on email
            if 'kavya.nair@email.com' in email:
                user_type = 'hr'
            else:
                user_type = 'job_seeker'
            
            # Update if missing or different
            current_type = user.get('user_type')
            if current_type != user_type:
                print(f"📝 Updating {email}: {current_type} -> {user_type}")
                success = await update_user_profile(user['user_id'], {'user_type': user_type})
                if success:
                    fixed_count += 1
                    print(f"✅ Fixed {email}")
                else:
                    print(f"❌ Failed to fix {email}")
                    
        print(f"🎉 Fixed {fixed_count} users")
        
    except Exception as e:
        print(f"❌ Error fixing users: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function"""
    print("🚀 Starting user authentication test...")
    await test_user_auth()
    print("\n" + "="*50 + "\n")
    await fix_all_users()
    print("\n" + "="*50 + "\n")
    print("🔄 Testing again after fix...")
    await test_user_auth()

if __name__ == "__main__":
    asyncio.run(main())
