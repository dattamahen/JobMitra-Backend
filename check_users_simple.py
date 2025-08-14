#!/usr/bin/env python3
"""
Check available users in the database.
"""

import asyncio
from auth_db import list_all_users

async def check_users():
    """Check what users exist in the database"""
    try:
        users = await list_all_users()
        print("Available users:")
        for i, user in enumerate(users[:5]):
            print(f"{i+1}. Email: {user.get('email')}, User ID: {user.get('user_id')}")
            
        if len(users) == 0:
            print("No users found in database.")
            print("\nLet's seed some test users...")
            
            # Import seeding function
            from auth_db import seed_users_data
            result = await seed_users_data()
            
            if result:
                print(f"Seeded {len(result)} users successfully!")
                # Check users again
                users = await list_all_users()
                print("\nNew users:")
                for i, user in enumerate(users[:5]):
                    print(f"{i+1}. Email: {user.get('email')}, User ID: {user.get('user_id')}")
            else:
                print("Failed to seed users.")
                
    except Exception as e:
        print(f"Error checking users: {e}")

if __name__ == "__main__":
    asyncio.run(check_users())
