#!/usr/bin/env python3
"""
Debug script to check database connection and user authentication
"""
import asyncio
from db_simple import db

async def debug_database():
    print("🔍 Debugging database connection and user data...")
    
    try:
        # Initialize database connection
        print("\n1. Connecting to database...")
        await db.connect_to_mongo()
        print("   ✅ Database connected successfully")
        
        # Check database connection
        print("\n2. Checking database collections...")
        collections = await db.database.list_collection_names()
        print(f"   Collections in database: {collections}")
        
        # Check if users collection exists and has data
        print("\n3. Checking users collection...")
        if "users" in collections:
            users_collection = db.database["users"]
            user_count = await users_collection.count_documents({})
            print(f"   Users in collection: {user_count}")
            
            if user_count > 0:
                # Get first few users (limited data for privacy)
                users = await users_collection.find({}).limit(3).to_list(3)
                for i, user in enumerate(users):
                    print(f"   User {i+1}: {user.get('email', 'No email')} (ID: {user.get('user_id', 'No ID')})")
                    
                    # Check professional info structure
                    prof_info = user.get('professional_info', {})
                    print(f"             Professional summary: {prof_info.get('professional_summary', 'None')}")
                    print(f"             Desired job: {prof_info.get('desired_job_title', 'None')}")
                    print(f"             Certifications: {prof_info.get('certifications', [])}")
                    print(f"             Updated: {user.get('updated_at', 'No timestamp')}")
                    print()
                    
                # Test a specific profile update
                print("\n4. Testing profile update...")
                test_user = users[0]
                user_id = test_user.get('user_id')
                
                update_data = {
                    "professional_info.professional_summary": f"Updated summary at {datetime.now().isoformat()}",
                    "professional_info.desired_job_title": "Test Senior Developer",
                    "updated_at": datetime.now().isoformat()
                }
                
                print(f"   Updating user {user_id} with: {update_data}")
                
                result = await users_collection.update_one(
                    {"user_id": user_id},
                    {"$set": update_data}
                )
                
                print(f"   Update result: modified_count={result.modified_count}, matched_count={result.matched_count}")
                
                # Verify the update
                print("\n5. Verifying update...")
                updated_user = await users_collection.find_one({"user_id": user_id})
                if updated_user:
                    prof_info = updated_user.get('professional_info', {})
                    print(f"   New professional summary: {prof_info.get('professional_summary', 'None')}")
                    print(f"   New desired job: {prof_info.get('desired_job_title', 'None')}")
                    print(f"   Updated at: {updated_user.get('updated_at', 'No timestamp')}")
                else:
                    print("   ❌ Could not retrieve updated user")
                
            else:
                print("   ❌ No users found in users collection")
        else:
            print("   ❌ Users collection doesn't exist")
            
        # Check if there are any other collections with user data
        print("\n6. Summary of all collections...")
        for collection_name in collections:
            collection = db.database[collection_name]
            count = await collection.count_documents({})
            print(f"   {collection_name}: {count} documents")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close database connection
        try:
            await db.close_mongo_connection()
            print("\n✅ Database connection closed")
        except:
            pass

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(debug_database())
