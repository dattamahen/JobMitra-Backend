"""
MongoDB Compass Viewing Guide for New User Schema
This script shows you exactly what to look for in MongoDB Compass
"""

import asyncio
from db_simple import db
import json
from datetime import datetime

async def display_schema_info():
    """Display information about the new user schema for MongoDB Compass viewing"""
    
    print("🔍 MongoDB Compass Viewing Guide for New User Schema")
    print("=" * 60)
    
    await db.connect_to_mongo()
    
    try:
        # Get a sample user to show the new schema
        collection = db.database["users"]
        sample_user = await collection.find_one({})
        
        if sample_user:
            print("\n📋 SAMPLE USER DOCUMENT STRUCTURE:")
            print("-" * 40)
            
            # Convert ObjectId and datetime for display
            if "_id" in sample_user:
                sample_user["_id"] = str(sample_user["_id"])
            
            # Convert datetime objects to strings for display
            for key, value in sample_user.items():
                if isinstance(value, datetime):
                    sample_user[key] = value.isoformat()
            
            # Pretty print the document structure
            print(json.dumps(sample_user, indent=2, default=str))
            
        print("\n" + "=" * 60)
        print("🧭 HOW TO VIEW IN MONGODB COMPASS:")
        print("=" * 60)
        
        print("\n1. 📂 CONNECT TO DATABASE:")
        print("   - Open MongoDB Compass")
        print("   - Connect to: mongodb://localhost:27017")
        print("   - Database name: 'jobmitra'")
        print("   - Collection name: 'users'")
        
        print("\n2. 🔍 NEW FIELDS TO LOOK FOR:")
        print("   ✅ Basic Personal Info:")
        print("      • first_name (string)")
        print("      • last_name (string)")
        print("      • date_of_birth (date)")
        print("      • phone (string)")
        
        print("   ✅ Professional Info:")
        print("      • overall_experience_years (number)")
        print("      • highest_qualification (string)")
        print("      • previous_organizations (array)")
        print("      • skills (array)")
        print("      • certifications (array)")
        print("      • contributions (string)")
        print("      • communication_skills (array)")
        print("      • ai_tools (array)")
        
        print("   ✅ Social Links:")
        print("      • social_links.github (string)")
        print("      • social_links.youtube (string)")
        print("      • social_links.linkedin (string)")
        print("      • social_links.playstore (string)")
        
        print("   ✅ Job Application Tracking:")
        print("      • overall_jobs_applied (array)")
        
        print("   ✅ User Classification:")
        print("      • user_type ('candidate' or 'hire')")
        print("      • user_status ('active' or 'inactive')")
        print("      • user_plan ('free', 'subscribed', or 'pro')")
        
        print("   ✅ Preferences:")
        print("      • job_preferences (array: 'remote', 'hybrid', 'on-site')")
        print("      • employment_type (array: 'full-time', 'part-time', 'freelancing', 'contract')")
        
        print("   ✅ Timestamps:")
        print("      • profile_created_on (date)")
        print("      • last_active (date)")
        
        print("   ✅ Analytics & Metrics:")
        print("      • match_analysis_count (number)")
        print("      • match_tailored_count (number)")
        print("      • mock_interview_count (number)")
        print("      • profile_completion_count (number)")
        print("      • profile_visits (number)")
        print("      • recent_activity (array)")
        
        print("\n3. 📊 DATABASE STATISTICS:")
        total_users = await collection.count_documents({})
        users_with_new_fields = await collection.count_documents({"user_type": {"$exists": True}})
        users_with_skills = await collection.count_documents({"skills": {"$exists": True, "$ne": []}})
        
        print(f"   • Total users: {total_users}")
        print(f"   • Users with new schema: {users_with_new_fields}")
        print(f"   • Users with skills: {users_with_skills}")
        
        print("\n4. 🔎 INDEXES CREATED:")
        indexes = await collection.list_indexes().to_list(length=None)
        print("   The following indexes were created for better performance:")
        for index in indexes:
            if index["name"] != "_id_":
                keys = list(index["key"].keys())
                print(f"   • {', '.join(keys)}")
        
        print("\n5. 📱 QUICK COMPASS QUERIES TO TRY:")
        print("   Filter examples you can use in MongoDB Compass:")
        print('   • Find candidates: {"user_type": "candidate"}')
        print('   • Find users with skills: {"skills": {"$exists": true, "$ne": []}}')
        print('   • Find remote workers: {"job_preferences": "remote"}')
        print('   • Find active users: {"user_status": "active"}')
        print('   • Find users with experience: {"overall_experience_years": {"$gt": 0}}')
        
        print("\n" + "=" * 60)
        print("🎉 ALL NEW FIELDS ARE NOW VISIBLE IN MONGODB COMPASS!")
        print("=" * 60)
        
        # Show sample documents with new fields
        print("\n📄 SAMPLE USERS WITH NEW FIELDS:")
        print("-" * 40)
        
        cursor = collection.find({}).limit(3)
        users = await cursor.to_list(length=3)
        
        for i, user in enumerate(users, 1):
            print(f"\n🧑 User {i}: {user.get('email', 'N/A')}")
            print(f"   • Name: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
            print(f"   • Type: {user.get('user_type', 'N/A')}")
            print(f"   • Status: {user.get('user_status', 'N/A')}")
            print(f"   • Experience: {user.get('overall_experience_years', 'N/A')} years")
            print(f"   • Skills: {len(user.get('skills', []))} skills")
            print(f"   • Plan: {user.get('user_plan', 'N/A')}")
            print(f"   • Profile visits: {user.get('profile_visits', 0)}")
            print(f"   • Mock interviews: {user.get('mock_interview_count', 0)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(display_schema_info())
