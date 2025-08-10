#!/usr/bin/env python3
"""
Debug script to check database connection and user authentication
"""
import asyncio
from db import database, init_database
import auth_db

async def debug_database():
    print("🔍 Debugging database connection and user data...")
    
    try:
        # Initialize database connection
        print("\n1. Initializing database...")
        await init_database()
        print("   ✅ Database initialized")
        
        # Check database connection
        print("\n2. Checking database connection...")
        collections = await database.list_collection_names()
        print(f"   Collections in database: {collections}")
        
        # Check if users collection exists and has data
        print("\n3. Checking users collection...")
        if "users" in collections:
            users_collection = database["users"]
            user_count = await users_collection.count_documents({})
            print(f"   Users in collection: {user_count}")
            
            if user_count > 0:
                # Get first few users
                users = await users_collection.find({}).limit(3).to_list(3)
                for i, user in enumerate(users):
                    print(f"   User {i+1}: {user.get('email', 'No email')} (ID: {user.get('user_id', 'No ID')})")
                    print(f"             Profile: {user.get('professional_info', 'No professional_info')}")
            else:
                print("   ❌ No users found in users collection")
        else:
            print("   ❌ Users collection doesn't exist")
            
        # Check if there are any other collections with user data
        print("\n4. Checking all collections for user data...")
        for collection_name in collections:
            collection = database[collection_name]
            count = await collection.count_documents({})
            print(f"   {collection_name}: {count} documents")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_database())
