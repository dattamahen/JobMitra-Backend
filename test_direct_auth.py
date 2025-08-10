#!/usr/bin/env python3
"""
Test authentication directly without API
"""
import asyncio
from pymongo import MongoClient
import bcrypt

async def test_direct_auth():
    """Test authentication directly"""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['jobmitra']
    users_collection = db['users']
    
    # Test HR user
    email = "kavya.nair@email.com"
    password = "HRUser@12345"
    
    print(f"🔍 Testing direct authentication for: {email}")
    
    # Find user
    user = users_collection.find_one({"email": email})
    if not user:
        print(f"❌ User not found: {email}")
        return
    
    print(f"✅ User found: {email}")
    print(f"🔍 User type: {user.get('user_type')}")
    print(f"🔍 Has password_hash: {'password_hash' in user}")
    
    # Get stored password hash
    stored_hash = user.get("password_hash", "")
    print(f"🔍 Stored hash starts with: {stored_hash[:30]}...")
    
    # Test password
    try:
        is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        print(f"🔍 Password verification: {'✅ SUCCESS' if is_valid else '❌ FAILED'}")
    except Exception as e:
        print(f"❌ Password verification error: {e}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_direct_auth())
