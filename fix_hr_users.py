#!/usr/bin/env python3
"""
Fix HR users type from 'hire' to 'hr'
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def fix_hr_users():
    """Fix HR users type from 'hire' to 'hr'"""
    
    # Get MongoDB URI from environment
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/jobmitra')
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_uri)
        db = client.get_database()
        
        print("Connecting to MongoDB...")
        
        # Update all users with user_type 'hire' to 'hr'
        result = await db.users.update_many(
            {"user_type": "hire"},
            {"$set": {"user_type": "hr"}}
        )
        
        print(f"Updated {result.modified_count} users from 'hire' to 'hr'")
        
        # Verify the update
        hr_users = await db.users.find({"user_type": "hr"}, {"email": 1, "user_type": 1, "first_name": 1, "last_name": 1}).to_list(length=None)
        
        print(f"HR users after update:")
        for user in hr_users:
            print(f"- {user.get('email', 'No email')} | Type: {user.get('user_type', 'No type')} | Name: {user.get('first_name', '')} {user.get('last_name', '')}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_hr_users())