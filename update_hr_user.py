#!/usr/bin/env python3
"""
Update HR user type in database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def update_hr_user():
    """Update HR user type from 'hire' to 'hr'"""
    
    # Get MongoDB URI from environment
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/jobmitra')
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_uri)
        db = client.get_database()
        
        print("Connecting to MongoDB...")
        
        # Check current HR user
        hr_user = await db.users.find_one({"email": "kavya.nair@email.com"})
        
        if hr_user:
            print(f"Found HR user: {hr_user['email']}")
            print(f"Current user_type: {hr_user.get('user_type', 'Not set')}")
            
            # Update user_type to 'hr'
            result = await db.users.update_one(
                {"email": "kavya.nair@email.com"},
                {"$set": {"user_type": "hr"}}
            )
            
            if result.modified_count > 0:
                print("Successfully updated HR user type to 'hr'")
                
                # Verify the update
                updated_user = await db.users.find_one({"email": "kavya.nair@email.com"})
                print(f"Updated user_type: {updated_user.get('user_type')}")
            else:
                print("No changes made (user_type might already be 'hr')")
        else:
            print("HR user not found")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_hr_user())