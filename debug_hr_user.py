#!/usr/bin/env python3
"""
Debug HR authentication by checking database user data
"""
from pymongo import MongoClient
import bcrypt

def debug_hr_user():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['jobmitra']
    users_collection = db['users']
    
    # Find the HR user
    hr_user = users_collection.find_one({"email": "kavya.nair@email.com"})
    
    if hr_user:
        print(f"✅ HR User found:")
        print(f"   Email: {hr_user.get('email')}")
        print(f"   User Type: {hr_user.get('user_type')}")
        print(f"   Username: {hr_user.get('username')}")
        print(f"   Password Hash: {hr_user.get('password', 'Not found')[:30]}...")
        
        # Test password verification
        stored_password = hr_user.get('password', '')
        test_passwords = ['HR@258', 'HR@25890', 'password123']
        
        print(f"\n🔍 Testing passwords:")
        for pwd in test_passwords:
            try:
                if bcrypt.checkpw(pwd.encode('utf-8'), stored_password.encode('utf-8')):
                    print(f"   ✅ '{pwd}' - MATCHES")
                else:
                    print(f"   ❌ '{pwd}' - DOES NOT MATCH")
            except Exception as e:
                print(f"   ❌ '{pwd}' - ERROR: {e}")
    else:
        print("❌ HR User not found in database")
    
    # Also check all users to see what we have
    print(f"\n📋 All users in database:")
    all_users = users_collection.find({}, {"email": 1, "user_type": 1, "username": 1})
    for user in all_users:
        print(f"   {user.get('email')} - Type: {user.get('user_type')} - Username: {user.get('username')}")
    
    client.close()

if __name__ == "__main__":
    debug_hr_user()
