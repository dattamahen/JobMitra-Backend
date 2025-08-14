#!/usr/bin/env python3
"""
Test MongoDB connection.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongo_connection():
    """Test MongoDB connection"""
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        
        # Test the connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # List databases
        db_list = await client.list_database_names()
        print(f"Available databases: {db_list}")
        
        # Check jobmitra database
        if "jobmitra" in db_list:
            db = client.jobmitra
            collections = await db.list_collection_names()
            print(f"Collections in jobmitra: {collections}")
            
            # Check users collection
            if "users" in collections:
                user_count = await db.users.count_documents({})
                print(f"Number of users in database: {user_count}")
                
                if user_count > 0:
                    # Get first user
                    first_user = await db.users.find_one({})
                    print(f"First user email: {first_user.get('email') if first_user else 'None'}")
                else:
                    print("No users found in the users collection")
            else:
                print("Users collection does not exist")
        else:
            print("jobmitra database does not exist")
            
        client.close()
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongo_connection())
