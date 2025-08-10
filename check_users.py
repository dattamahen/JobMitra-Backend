#!/usr/bin/env python3
"""
Simple test to check database users
"""

import asyncio
from db_simple import db

async def check_users():
    """Check users in database"""
    
    print("🔍 Checking database users...")
    
    try:
        # Connect to database
        await db.connect_to_mongo()
        
        # Get users collection
        users_collection = db.database["users"]
        
        # Count total users
        total_users = await users_collection.count_documents({})
        print(f"📊 Total users in database: {total_users}")
        
        if total_users > 0:
            # Get all users
            users_cursor = users_collection.find({})
            users = await users_cursor.to_list(length=None)
            
            print("\n👥 Users found:")
            for user in users:
                user_type = user.get('user_type', 'NOT SET')
                print(f"  📧 Email: {user.get('email', 'N/A')}")
                print(f"  👤 User Type: {user_type}")
                print(f"  🏢 Company: {user.get('company_name', 'N/A')}")
                print(f"  ✅ Active: {user.get('is_active', False)}")
                print(f"  🔑 Has Password: {'password_hash' in user}")
                print(f"  🗃️  Raw user_type field: {repr(user.get('user_type'))}")
                print("  " + "-" * 40)
        else:
            print("❌ No users found in database!")
            print("🌱 Need to seed users first")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_users())
