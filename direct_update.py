#!/usr/bin/env python3
"""
Direct MongoDB update using pymongo
"""

import pymongo
from datetime import datetime

def update_users_direct():
    """Update users directly with pymongo"""
    
    print("🔧 Direct MongoDB update...")
    
    try:
        # Connect directly to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client.jobmitra
        users_collection = db.users
        
        print("✅ Connected to MongoDB directly")
        
        # Count users
        total_users = users_collection.count_documents({})
        print(f"📊 Total users: {total_users}")
        
        # Update all users
        updates = [
            ("kavya.nair@email.com", "hr", "Wipro Limited"),
        ]
        
        # Set all others to job_seeker first
        result = users_collection.update_many(
            {},
            {"$set": {"user_type": "job_seeker"}}
        )
        print(f"✅ Set {result.modified_count} users as job_seeker")
        
        # Set specific HR users
        for email, user_type, company in updates:
            result = users_collection.update_one(
                {"email": email},
                {"$set": {"user_type": user_type, "company_name": company}}
            )
            if result.modified_count > 0:
                print(f"✅ Updated {email} -> {user_type}")
        
        # Verify updates
        print("\n🔍 Verification:")
        users = list(users_collection.find({}, {"email": 1, "user_type": 1, "company_name": 1}))
        for user in users:
            print(f"  📧 {user.get('email', 'N/A')}: {user.get('user_type', 'NOT SET')}")
            
        client.close()
        print("✅ MongoDB connection closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_users_direct()
