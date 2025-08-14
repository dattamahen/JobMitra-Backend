#!/usr/bin/env python3
"""
Create test user with problematic certification and portfolio data.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json

async def create_test_user():
    """Create a test user with problematic data to reproduce UI issues."""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017/jobmitra")
        db = client.jobmitra
        collection = db.user_profiles
        
        # Create user with problematic certifications and missing portfolio
        test_user = {
            "user_id": "test_user_123",
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "candidate",
            "user_status": "active",
            "user_plan": "free",
            
            # Problematic certifications - mix of objects and strings
            "certifications": [
                "[object Object]",  # This is what's causing the UI issue
                {
                    "name": "Valid Certification",
                    "issuer": "Test Institute"
                },
                "Another string certification"
            ],
            
            # Skills
            "skills": ["Python", "JavaScript", "React"],
            
            # Social links - some present, portfolio missing
            "github_link": "https://github.com/testuser",
            "linkedin_link": "https://linkedin.com/in/testuser",
            "youtube_link": "https://youtube.com/testuser",
            # Note: No portfolio_link field - this might be causing the empty portfolio
            
            # Timestamps
            "profile_created_on": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        # Insert the user
        result = await collection.insert_one(test_user)
        print(f"✅ Created test user with ID: {result.inserted_id}")
        
        # Verify the data
        user = await collection.find_one({"email": "testuser@example.com"})
        if user:
            print("\n=== CREATED USER DATA ===")
            print(f"Certifications: {user['certifications']}")
            print(f"Social links:")
            for key, value in user.items():
                if 'link' in key or 'url' in key:
                    print(f"  {key}: {value}")
            
            # Check for portfolio specifically
            portfolio_found = False
            for key in user.keys():
                if 'portfolio' in key.lower():
                    print(f"  Portfolio field found: {key} = {user[key]}")
                    portfolio_found = True
            
            if not portfolio_found:
                print("  ❌ No portfolio field found - this could be the UI issue!")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_test_user())
