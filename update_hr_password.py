#!/usr/bin/env python3
"""
Update HR user password to meet 8-character requirement
"""
import bcrypt
from pymongo import MongoClient

def update_hr_password():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['jobmitra']
    users_collection = db['users']
    
    # New password that meets 8-character requirement
    new_password = "HR@25890"
    
    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update the HR user
    result = users_collection.update_one(
        {"email": "kavya.nair@email.com"},
        {"$set": {"password": hashed_password}}
    )
    
    if result.modified_count > 0:
        print(f"✅ Updated password for kavya.nair@email.com")
        print(f"✅ New password: {new_password}")
    else:
        print("❌ No user found or password not updated")
    
    # Verify the update
    user = users_collection.find_one({"email": "kavya.nair@email.com"})
    if user:
        print(f"✅ User found with user_type: {user.get('user_type', 'Not set')}")
        print(f"✅ Password hash updated: {user['password'][:20]}...")
    
    client.close()

if __name__ == "__main__":
    update_hr_password()
