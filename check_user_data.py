#!/usr/bin/env python3
"""
Check user data in database to debug UI display issues.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def check_user_data():
    """Check the current user data in MongoDB."""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017/jobmitra")
        db = client.jobmitra
        collection = db.user_profiles
        
        # Find the test user
        user = await collection.find_one({"email": "alexjohnson@example.com"})
        
        if not user:
            print("❌ User not found")
            return
            
        print("✅ User found")
        print("\n=== CERTIFICATIONS DATA ===")
        certifications = user.get("certifications", [])
        print(f"Type: {type(certifications)}")
        print(f"Length: {len(certifications) if isinstance(certifications, list) else 'Not a list'}")
        print(f"Raw value: {certifications}")
        
        if isinstance(certifications, list):
            for i, cert in enumerate(certifications):
                print(f"  [{i}] Type: {type(cert)}, Value: {cert}")
        
        print("\n=== SOCIAL LINKS DATA ===")
        social_fields = {}
        for key, value in user.items():
            if any(term in key.lower() for term in ['link', 'url', 'portfolio', 'github', 'linkedin', 'youtube', 'playstore']):
                social_fields[key] = value
        
        if social_fields:
            for key, value in social_fields.items():
                print(f"  {key}: {value}")
        else:
            print("  No social link fields found")
        
        print("\n=== ALL USER FIELDS ===")
        for key in sorted(user.keys()):
            if key != '_id':
                value = user[key]
                if isinstance(value, (str, int, float, bool)) or value is None:
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {type(value)} (length: {len(value) if hasattr(value, '__len__') else 'N/A'})")
        
        print("\n=== CHECKING FOR PORTFOLIO FIELD ===")
        portfolio_fields = []
        for key in user.keys():
            if 'portfolio' in key.lower():
                portfolio_fields.append((key, user[key]))
        
        if portfolio_fields:
            for key, value in portfolio_fields:
                print(f"  Found portfolio field: {key} = {value}")
        else:
            print("  No portfolio fields found in user data")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error checking user data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_user_data())
