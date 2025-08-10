#!/usr/bin/env python3
"""
Complete user data reset - Delete all users and create fresh ones
"""
from pymongo import MongoClient
import bcrypt
from datetime import datetime
import uuid

def delete_all_users():
    """Delete all users from database"""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['jobmitra']
    users_collection = db['users']
    
    # Count existing users
    existing_count = users_collection.count_documents({})
    print(f"📊 Found {existing_count} existing users")
    
    # Delete all users
    result = users_collection.delete_many({})
    print(f"🗑️ Deleted {result.deleted_count} users")
    
    client.close()
    return result.deleted_count

def create_fresh_users():
    """Create 2 users for each type: job_seeker, hr, admin"""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['jobmitra']
    users_collection = db['users']
    
    # Fresh user data
    users = [
        # Job Seekers (2)
        {
            "user_id": "user_001",
            "email": "arjun.sharma@email.com",
            "username": "arjun_sharma",
            "password": "JobSeeker@123",
            "user_type": "job_seeker",
            "personal_info": {
                "first_name": "Arjun",
                "last_name": "Sharma",
                "phone": "+91 98765 43210",
                "date_of_birth": "1995-03-15",
                "gender": "male",
                "location": {
                    "city": "Bangalore",
                    "state": "Karnataka",
                    "country": "India",
                    "pincode": "560001"
                }
            },
            "professional_info": {
                "current_role": "Senior Software Engineer",
                "current_company": "TechCorp India",
                "total_experience": "5 years",
                "industry": "Information Technology",
                "skills": ["Python", "React", "Node.js", "MongoDB", "AWS"],
                "current_salary": 1200000,
                "expected_salary": 1500000
            },
            "preferences": {
                "job_locations": ["Bangalore", "Mumbai", "Remote"],
                "remote_preference": "hybrid",
                "notice_period": "30 days"
            }
        },
        {
            "user_id": "user_002", 
            "email": "priya.patel@email.com",
            "username": "priya_patel",
            "password": "JobSeeker@456",
            "user_type": "job_seeker",
            "personal_info": {
                "first_name": "Priya",
                "last_name": "Patel",
                "phone": "+91 87654 32109",
                "date_of_birth": "1993-07-22",
                "gender": "female",
                "location": {
                    "city": "Mumbai",
                    "state": "Maharashtra", 
                    "country": "India",
                    "pincode": "400001"
                }
            },
            "professional_info": {
                "current_role": "Product Manager",
                "current_company": "Startup Labs",
                "total_experience": "4 years",
                "industry": "Technology",
                "skills": ["Product Management", "Analytics", "Agile", "SQL"],
                "current_salary": 1000000,
                "expected_salary": 1300000
            },
            "preferences": {
                "job_locations": ["Mumbai", "Pune", "Remote"],
                "remote_preference": "remote",
                "notice_period": "45 days"
            }
        },
        
        # HR Users (2)
        {
            "user_id": "user_003",
            "email": "kavya.nair@email.com", 
            "username": "kavya_nair",
            "password": "HRUser@12345",
            "user_type": "hr",
            "company_name": "Wipro Limited",
            "personal_info": {
                "first_name": "Kavya",
                "last_name": "Nair",
                "phone": "+91 21098 76543",
                "date_of_birth": "1990-09-30",
                "gender": "female",
                "location": {
                    "city": "Chennai",
                    "state": "Tamil Nadu",
                    "country": "India",
                    "pincode": "600001"
                }
            },
            "professional_info": {
                "current_role": "Senior HR Manager",
                "current_company": "Wipro Limited",
                "total_experience": "8 years",
                "industry": "Information Technology",
                "department": "Human Resources"
            }
        },
        {
            "user_id": "user_004",
            "email": "rajesh.hr@company.com",
            "username": "rajesh_hr", 
            "password": "HRUser@67890",
            "user_type": "hr",
            "company_name": "Infosys Technologies",
            "personal_info": {
                "first_name": "Rajesh",
                "last_name": "Kumar",
                "phone": "+91 98765 12345",
                "date_of_birth": "1988-05-12",
                "gender": "male",
                "location": {
                    "city": "Hyderabad",
                    "state": "Telangana",
                    "country": "India",
                    "pincode": "500001"
                }
            },
            "professional_info": {
                "current_role": "HR Business Partner",
                "current_company": "Infosys Technologies",
                "total_experience": "10 years",
                "industry": "Information Technology",
                "department": "Human Resources"
            }
        },
        
        # Admin Users (2)
        {
            "user_id": "user_005",
            "email": "admin@jobmitra.com",
            "username": "admin_primary",
            "password": "Admin@12345",
            "user_type": "admin",
            "personal_info": {
                "first_name": "System",
                "last_name": "Administrator",
                "phone": "+91 99999 00000",
                "date_of_birth": "1985-01-01",
                "gender": "other",
                "location": {
                    "city": "Delhi",
                    "state": "Delhi",
                    "country": "India",
                    "pincode": "110001"
                }
            },
            "professional_info": {
                "current_role": "System Administrator",
                "current_company": "JobMitra Platform",
                "total_experience": "15 years",
                "industry": "Technology",
                "department": "Administration"
            }
        },
        {
            "user_id": "user_006",
            "email": "superadmin@jobmitra.com",
            "username": "super_admin",
            "password": "SuperAdmin@99",
            "user_type": "admin",
            "personal_info": {
                "first_name": "Super",
                "last_name": "Admin",
                "phone": "+91 88888 99999",
                "date_of_birth": "1980-12-31",
                "gender": "other",
                "location": {
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "country": "India",
                    "pincode": "400001"
                }
            },
            "professional_info": {
                "current_role": "Platform Owner",
                "current_company": "JobMitra Platform",
                "total_experience": "20 years",
                "industry": "Technology",
                "department": "Executive"
            }
        }
    ]
    
    # Process each user
    processed_users = []
    for user_data in users:
        # Hash password
        password = user_data.pop("password")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Build final user document
        user_doc = {
            **user_data,
            "password_hash": hashed_password,
            "is_active": True,
            "is_verified": True,
            "profile_completion": 85,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        # Add job seeker specific fields
        if user_doc["user_type"] == "job_seeker":
            if "preferences" not in user_doc:
                user_doc["preferences"] = {
                    "job_locations": [],
                    "remote_preference": "hybrid",
                    "notice_period": "30 days"
                }
        
        processed_users.append(user_doc)
        print(f"✅ Prepared user: {user_data['email']} ({user_data['user_type']}) - Password: {password}")
    
    # Insert all users
    result = users_collection.insert_many(processed_users)
    print(f"\n🎉 Created {len(result.inserted_ids)} fresh users successfully!")
    
    client.close()
    return processed_users

def main():
    """Main function to reset all user data"""
    print("🚀 Starting complete user data reset...")
    print("=" * 50)
    
    # Step 1: Delete all existing users
    print("\n📂 Step 1: Deleting all existing users...")
    deleted_count = delete_all_users()
    
    # Step 2: Create fresh users
    print("\n📂 Step 2: Creating fresh users...")
    new_users = create_fresh_users()
    
    print("\n" + "=" * 50)
    print("✅ USER DATA RESET COMPLETE!")
    print(f"   🗑️ Deleted: {deleted_count} users")
    print(f"   ➕ Created: {len(new_users)} users")
    
    print("\n📋 NEW USER CREDENTIALS:")
    print("-" * 50)
    
    # Group by user type
    job_seekers = [u for u in new_users if u["user_type"] == "job_seeker"]
    hr_users = [u for u in new_users if u["user_type"] == "hr"]
    admin_users = [u for u in new_users if u["user_type"] == "admin"]
    
    print("\n👤 JOB SEEKERS:")
    for user in job_seekers:
        # We need to get the original password - let's hardcode for display
        if "arjun.sharma" in user["email"]:
            pwd = "JobSeeker@123"
        else:
            pwd = "JobSeeker@456"
        print(f"   📧 {user['email']} | 🔑 {pwd}")
    
    print("\n💼 HR USERS:")
    for user in hr_users:
        if "kavya.nair" in user["email"]:
            pwd = "HRUser@12345"
        else:
            pwd = "HRUser@67890"
        print(f"   📧 {user['email']} | 🔑 {pwd}")
    
    print("\n🔧 ADMIN USERS:")
    for user in admin_users:
        if "admin@jobmitra" in user["email"]:
            pwd = "Admin@12345"
        else:
            pwd = "SuperAdmin@99"
        print(f"   📧 {user['email']} | 🔑 {pwd}")

if __name__ == "__main__":
    main()
