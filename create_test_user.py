#!/usr/bin/env python3
"""
Create a test user with proper credentials for testing.
"""

import asyncio
from auth_db import create_user

async def create_test_user():
    """Create a test user with proper credentials"""
    try:
        user_data = {
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "candidate",
            "skills": ["JavaScript", "Python", "React"],
            "phone": "+1234567890",
            "city": "Test City",
            "state": "Test State"
        }
        
        user = await create_user(user_data)
        
        if user:
            print("✅ Test user created successfully!")
            print(f"Email: {user['email']}")
            print(f"User ID: {user['user_id']}")
            print(f"Name: {user['first_name']} {user['last_name']}")
        else:
            print("❌ Failed to create test user")
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_user())
