"""
Simple script to seed users in the database
"""

import asyncio
from user_seed_data import get_hashed_users
from db_simple import db

async def seed_users():
    try:
        # Initialize database connection
        await db.connect_to_mongo()
        
        if db.fallback_mode:
            print("❌ Cannot seed users in fallback mode. MongoDB connection required.")
            return
        
        # Check if users collection exists and has data
        users_collection = db.database["users"]
        existing_count = await users_collection.count_documents({})
        
        if existing_count > 0:
            print(f"Database already has {existing_count} users. Skipping seed.")
            return
        
        # Get the hashed users from seed data
        users = get_hashed_users()
        
        # Insert users into database
        result = await users_collection.insert_many(users)
        
        print(f"✅ Successfully seeded {len(result.inserted_ids)} users:")
        for user in users:
            print(f"   - {user['personal_info']['first_name']} {user['personal_info']['last_name']} ({user['email']})")
        
    except Exception as e:
        print(f"❌ Error seeding users: {e}")
        print("Make sure MongoDB is running and the connection is working.")

if __name__ == "__main__":
    asyncio.run(seed_users())
