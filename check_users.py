#!/usr/bin/env python3
"""
Check users in database
"""

import asyncio
from db_simple import db

async def check_users():
    """Check users in database"""
    try:
        await db.connect_to_mongo()
        print("Connected to database")
        
        # Get all users
        users_cursor = db.database["users"].find({})
        users = []
        async for user in users_cursor:
            users.append(user)
        
        print(f"Found {len(users)} users:")
        
        for user in users:
            user_id = user.get("user_id")
            email = user.get("email")
            password = user.get("password", "No password field")
            print(f"  User ID: {user_id}")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            print("  ---")
        
        await db.close_mongo_connection()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_users())