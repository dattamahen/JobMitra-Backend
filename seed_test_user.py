"""
Quick script to seed a test user for development
"""
import asyncio
from datetime import datetime
from auth_db import create_user

async def seed_test_user():
    """Create a test user with ID 'user001'"""
    try:
        user_data = {
            "user_id": "user001",
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "user_type": "candidate",
            "overall_experience_years": 3,
            "highest_qualification": "Bachelor's",
            "skills": ["JavaScript", "Python", "React"],
            "job_preferences": ["remote", "full-time"],
            "employment_type": ["full-time"]
        }
        
        user = await create_user(user_data)
        print(f"✅ Test user created successfully: {user['user_id']}")
        return user
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(seed_test_user())