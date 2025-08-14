#!/usr/bin/env python3
"""
Check user credentials in the database.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_user_credentials():
    """Check user credentials"""
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.jobmitra
        
        users = await db.users.find({}).to_list(None)
        print(f"Found {len(users)} users:")
        
        for i, user in enumerate(users):
            print(f"\n{i+1}. User:")
            print(f"   Email: {user.get('email')}")
            print(f"   User ID: {user.get('user_id')}")
            print(f"   First Name: {user.get('first_name')}")
            print(f"   Last Name: {user.get('last_name')}")
            print(f"   Has password field: {'password' in user}")
            print(f"   Created: {user.get('profile_created_on')}")
            
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_user_credentials())
