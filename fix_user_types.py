#!/usr/bin/env python3
"""
Script to add user_type field to existing users in the database
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from auth_db import list_all_users, update_user_profile
from user_seed_data import get_hashed_users

async def fix_user_types():
    """Add user_type field to existing users"""
    
    print("🔍 Checking existing users...")
    
    try:
        # Get all existing users
        existing_users = await list_all_users()
        print(f"Found {len(existing_users)} existing users")
        
        # Get the updated user data with user_type
        updated_users_data = get_hashed_users()
        
        # Create a mapping of email to user_type
        email_to_user_type = {}
        for user_data in updated_users_data:
            email_to_user_type[user_data['email']] = user_data.get('user_type', 'job_seeker')
        
        # Update each existing user
        updated_count = 0
        for user in existing_users:
            email = user.get('email')
            if email and email in email_to_user_type:
                user_type = email_to_user_type[email]
                
                # Check if user already has user_type
                if 'user_type' not in user or user.get('user_type') != user_type:
                    print(f"📝 Updating user {email} with user_type: {user_type}")
                    
                    update_data = {'user_type': user_type}
                    
                    # For HR users, also add company_name if missing
                    if user_type == 'hr' and 'company_name' not in user:
                        # Find the company_name from updated data
                        for user_data in updated_users_data:
                            if user_data['email'] == email and 'company_name' in user_data:
                                update_data['company_name'] = user_data['company_name']
                                break
                    
                    success = await update_user_profile(user['user_id'], update_data)
                    if success:
                        updated_count += 1
                        print(f"✅ Updated user {email}")
                    else:
                        print(f"❌ Failed to update user {email}")
                else:
                    print(f"✅ User {email} already has correct user_type: {user.get('user_type')}")
            else:
                print(f"⚠️  User {email} not found in updated data, setting as job_seeker")
                success = await update_user_profile(user['user_id'], {'user_type': 'job_seeker'})
                if success:
                    updated_count += 1
        
        print(f"🎉 Successfully updated {updated_count} users")
        
    except Exception as e:
        print(f"❌ Error fixing user types: {e}")
        raise

async def main():
    """Main function"""
    print("🚀 Starting user_type fix...")
    await fix_user_types()
    print("✅ User type fix completed!")

if __name__ == "__main__":
    asyncio.run(main())
