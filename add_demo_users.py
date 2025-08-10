#!/usr/bin/env python3
"""
Add demo HR user for login testing
"""

import pymongo
import hashlib
import secrets
from datetime import datetime

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{pwd_hash.hex()}"

def add_demo_users():
    """Add demo users for easy testing"""
    
    print("🎭 Adding demo users...")
    
    try:
        # Connect directly to MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        db = client.jobmitra
        users_collection = db.users
        
        print("✅ Connected to MongoDB")
        
        # Demo users to add
        demo_users = [
            {
                "user_id": "demo_hr_001",
                "email": "hr@company.com",
                "password_hash": hash_password("password123"),
                "username": "demo_hr",
                "user_type": "hr",
                "company_name": "Demo Company Inc.",
                "personal_info": {
                    "first_name": "Demo",
                    "last_name": "HR",
                    "phone": "+1 555 123 4567",
                    "location": {
                        "city": "San Francisco",
                        "state": "CA",
                        "country": "USA"
                    }
                },
                "professional_info": {
                    "current_role": "HR Manager",
                    "current_company": "Demo Company Inc.",
                    "total_experience": "5 years",
                    "industry": "Technology"
                },
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "user_id": "demo_admin_001",
                "email": "admin@system.com",
                "password_hash": hash_password("password123"),
                "username": "demo_admin",
                "user_type": "admin",
                "personal_info": {
                    "first_name": "Demo",
                    "last_name": "Admin",
                    "phone": "+1 555 987 6543",
                    "location": {
                        "city": "New York",
                        "state": "NY",
                        "country": "USA"
                    }
                },
                "professional_info": {
                    "current_role": "System Administrator",
                    "total_experience": "10 years",
                    "industry": "Technology"
                },
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        # Insert or update demo users
        for user_data in demo_users:
            # Check if user exists
            existing_user = users_collection.find_one({"email": user_data["email"]})
            
            if existing_user:
                # Update existing user
                result = users_collection.update_one(
                    {"email": user_data["email"]},
                    {"$set": user_data}
                )
                print(f"📝 Updated existing user: {user_data['email']} ({user_data['user_type']})")
            else:
                # Insert new user
                result = users_collection.insert_one(user_data)
                print(f"➕ Created new user: {user_data['email']} ({user_data['user_type']})")
        
        # Verify all users
        print("\n🔍 All users in database:")
        users = list(users_collection.find({}, {"email": 1, "user_type": 1, "company_name": 1}))
        
        job_seekers = []
        hr_users = []
        admins = []
        
        for user in users:
            email = user.get('email', 'N/A')
            user_type = user.get('user_type', 'NOT SET')
            company = user.get('company_name', '')
            
            if user_type == 'job_seeker':
                job_seekers.append(email)
            elif user_type == 'hr':
                hr_users.append(f"{email} ({company})")
            elif user_type == 'admin':
                admins.append(email)
            
            print(f"  📧 {email}: {user_type}")
        
        print(f"\n📊 Summary:")
        print(f"👤 Job Seekers ({len(job_seekers)}): {', '.join(job_seekers[:3])}{'...' if len(job_seekers) > 3 else ''}")
        print(f"🏢 HR Users ({len(hr_users)}): {', '.join(hr_users)}")
        print(f"👑 Admins ({len(admins)}): {', '.join(admins)}")
        
        client.close()
        print("\n✅ Demo users setup complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_demo_users()
