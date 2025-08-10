#!/usr/bin/env python3
"""
Update existing users with user_type field
"""

import asyncio
from db_simple import db

async def update_user_types():
    """Add user_type to existing users"""
    
    print("🔧 Updating user types...")
    
    try:
        # Connect to database
        await db.connect_to_mongo()
        
        # Get users collection
        users_collection = db.database["users"]
        
        # Define user type mappings based on email
        user_type_mapping = {
            "kavya.nair@email.com": "hr",
            # All others default to job_seeker
        }
        
        # Get all users
        users_cursor = users_collection.find({})
        users = await users_cursor.to_list(length=None)
        
        updated_count = 0
        
        for user in users:
            email = user.get('email', '')
            
            # Determine user_type
            if email in user_type_mapping:
                user_type = user_type_mapping[email]
                company_name = "Wipro Limited" if user_type == "hr" else None
            else:
                user_type = "job_seeker"
                company_name = None
            
            # Prepare update data
            update_data = {"user_type": user_type}
            if company_name:
                update_data["company_name"] = company_name
            
            # Update user
            result = await users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                print(f"✅ Updated {email} -> {user_type}")
            else:
                print(f"⚠️  No update needed for {email}")
        
        print(f"\n🎉 Successfully updated {updated_count} users")
        
        # Verify updates
        print("\n🔍 Verifying updates...")
        updated_users_cursor = users_collection.find({})
        updated_users = await updated_users_cursor.to_list(length=None)
        
        for user in updated_users:
            print(f"  📧 {user.get('email', 'N/A')}: {user.get('user_type', 'NOT SET')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(update_user_types())
