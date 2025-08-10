#!/usr/bin/env python3
"""
Simple script to manually seed users and test authentication
"""

import asyncio
import hashlib
import secrets
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import pymongo
from db_simple import db

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{pwd_hash.hex()}"

async def manual_seed():
    """Manually seed test users"""
    
    print("🌱 Manual seeding of test users...")
    
    try:
        # Connect to database manually
        await db.connect_to_mongo()
        print("✅ Connected to MongoDB")
        
        # Get the users collection
        users_collection = db.database["users"]
        
        # Check existing users
        existing_count = await users_collection.count_documents({})
        print(f"📊 Found {existing_count} existing users")
        
        # Test users to create
        test_users = [
            {
                "user_id": "user_001",
                "email": "arjun.sharma@email.com",
                "password_hash": hash_password("TechLead@123"),
                "username": "arjun_sharma",
                "user_type": "job_seeker",
                "personal_info": {
                    "first_name": "Arjun",
                    "last_name": "Sharma",
                    "phone": "+91 98765 43210",
                    "location": {
                        "city": "Bangalore",
                        "state": "Karnataka",
                        "country": "India"
                    }
                },
                "professional_info": {
                    "current_role": "Senior Software Engineer",
                    "current_company": "Infosys Limited",
                    "total_experience": "8 years",
                    "industry": "Information Technology",
                    "skills": ["Java", "Spring Boot", "Microservices", "AWS", "React"]
                },
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "user_id": "user_hr_001",
                "email": "kavya.nair@email.com",
                "password_hash": hash_password("HR@258"),
                "username": "kavya_nair",
                "user_type": "hr",
                "company_name": "Wipro Limited",
                "personal_info": {
                    "first_name": "Kavya",
                    "last_name": "Nair",
                    "phone": "+91 21098 76543",
                    "location": {
                        "city": "Kochi",
                        "state": "Kerala",
                        "country": "India"
                    }
                },
                "professional_info": {
                    "current_role": "HR Business Partner",
                    "current_company": "Wipro Limited",
                    "total_experience": "8 years",
                    "industry": "Information Technology"
                },
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        # Insert or update users
        for user_data in test_users:
            # Check if user exists
            existing_user = await users_collection.find_one({"email": user_data["email"]})
            
            if existing_user:
                # Update existing user with user_type
                result = await users_collection.update_one(
                    {"email": user_data["email"]},
                    {"$set": {"user_type": user_data["user_type"], "company_name": user_data.get("company_name")}}
                )
                print(f"📝 Updated existing user: {user_data['email']} (user_type: {user_data['user_type']})")
            else:
                # Insert new user
                result = await users_collection.insert_one(user_data)
                print(f"➕ Created new user: {user_data['email']} (user_type: {user_data['user_type']})")
        
        # Verify users
        total_users = await users_collection.count_documents({})
        job_seekers = await users_collection.count_documents({"user_type": "job_seeker"})
        hr_users = await users_collection.count_documents({"user_type": "hr"})
        
        print(f"🎉 Seeding complete!")
        print(f"📊 Total users: {total_users}")
        print(f"👤 Job seekers: {job_seekers}")
        print(f"🏢 HR users: {hr_users}")
        
    except Exception as e:
        print(f"❌ Error during manual seeding: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(manual_seed())
