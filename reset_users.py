#!/usr/bin/env python3
"""
Script to reset users and create test data
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

async def reset_users():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmitra"))
    db = client.get_default_database()
    
    try:
        # Delete all existing users
        result = await db.user_profiles.delete_many({})
        print(f"✅ Deleted {result.deleted_count} existing users")
        
        # Create 3 candidates
        candidates = [
            {
                "user_id": "user001",
                "email": "user001@test.com",
                "password_hash": "$2b$12$Oif1rByysRH0P5/xgBAr3.WWr7rs/AYiBSKA3fYxp6jjGlX.jKorK",
                "first_name": "Alex",
                "last_name": "Johnson",
                "user_type": "candidate",
                "user_status": "active",
                "skills": ["ruby", "javascript", "angular", "python", "go"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": "user002", 
                "email": "user002@test.com",
                "password_hash": "$2b$12$Oif1rByysRH0P5/xgBAr3.WWr7rs/AYiBSKA3fYxp6jjGlX.jKorK",
                "first_name": "Sarah",
                "last_name": "Davis",
                "user_type": "candidate",
                "user_status": "active",
                "skills": ["react", "node.js", "mongodb", "aws"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": "user003",
                "email": "user003@test.com", 
                "password_hash": "$2b$12$Oif1rByysRH0P5/xgBAr3.WWr7rs/AYiBSKA3fYxp6jjGlX.jKorK",
                "first_name": "David",
                "last_name": "Wilson",
                "user_type": "candidate",
                "user_status": "active",
                "skills": ["java", "spring", "mysql", "docker"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Create 3 HR users
        hr_users = [
            {
                "user_id": "hr001",
                "email": "hr001@test.com",
                "password_hash": "$2b$12$0MkXX1rA.SKHwd2BcCy2d.bH3uwFNBfUdii3xzQ65Xypf6VCYgNK2",
                "first_name": "Jennifer",
                "last_name": "Smith",
                "user_type": "hire",
                "user_status": "active",
                "skills": ["Recruitment", "Talent Acquisition"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": "hr002",
                "email": "hr002@test.com",
                "password_hash": "$2b$12$0MkXX1rA.SKHwd2BcCy2d.bH3uwFNBfUdii3xzQ65Xypf6VCYgNK2",
                "first_name": "Michael",
                "last_name": "Brown",
                "user_type": "hire",
                "user_status": "active",
                "skills": ["Recruitment", "HR Analytics"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "user_id": "hr003",
                "email": "hr003@test.com",
                "password_hash": "$2b$12$0MkXX1rA.SKHwd2BcCy2d.bH3uwFNBfUdii3xzQ65Xypf6VCYgNK2",
                "first_name": "Lisa",
                "last_name": "Garcia",
                "user_type": "hire", 
                "user_status": "active",
                "skills": ["Technical Recruiting", "Employee Relations"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Insert candidates
        await db.user_profiles.insert_many(candidates)
        print(f"✅ Created {len(candidates)} candidates")
        
        # Insert HR users
        await db.user_profiles.insert_many(hr_users)
        print(f"✅ Created {len(hr_users)} HR users")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(reset_users())