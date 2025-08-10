#!/usr/bin/env python3
"""
Fix HR user by removing conflicting password fields and setting correct one
"""
from pymongo import MongoClient
import bcrypt

def fix_hr_user():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['jobmitra']
    users_collection = db['users']
    
    # New password
    new_password = "HR@25890"
    
    # Hash the password correctly
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update the HR user - remove password_hash and set password
    result = users_collection.update_one(
        {"email": "kavya.nair@email.com"},
        {
            "$set": {"password_hash": hashed_password},
            "$unset": {"password": ""}
        }
    )
    
    if result.modified_count > 0:
        print(f"✅ Fixed HR user password")
        print(f"✅ Password: {new_password}")
        print(f"✅ Hash: {hashed_password[:30]}...")
    else:
        print("❌ No updates made")
    
    # Verify the fix
    user = users_collection.find_one({"email": "kavya.nair@email.com"})
    if user:
        print(f"\n✅ Verification:")
        print(f"   Has password field: {'password' in user}")
        print(f"   Has password_hash field: {'password_hash' in user}")
        
        # Test the password
        stored_hash = user.get('password_hash', '')
        if bcrypt.checkpw(new_password.encode('utf-8'), stored_hash.encode('utf-8')):
            print(f"   ✅ Password verification: SUCCESS")
        else:
            print(f"   ❌ Password verification: FAILED")
    
    client.close()

if __name__ == "__main__":
    fix_hr_user()
