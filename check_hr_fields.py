#!/usr/bin/env python3
"""
Check the actual field names in the HR user document
"""
from pymongo import MongoClient

def check_hr_user_fields():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['jobmitra']
    users_collection = db['users']
    
    # Find the HR user
    hr_user = users_collection.find_one({"email": "kavya.nair@email.com"})
    
    if hr_user:
        print(f"✅ HR User document fields:")
        for key, value in hr_user.items():
            if key == 'password' or key == 'password_hash':
                print(f"   {key}: {str(value)[:30]}...")
            elif key == '_id':
                print(f"   {key}: {value}")
            else:
                print(f"   {key}: {value}")
    else:
        print("❌ HR User not found")
    
    client.close()

if __name__ == "__main__":
    check_hr_user_fields()
