#!/usr/bin/env python3
"""
Check what user_001 (arjun.sharma@email.com) actually has in the database
"""
import asyncio
from db_simple import db

async def check_user_001():
    print("🔍 Checking user_001 (arjun.sharma@email.com) in database...")
    
    try:
        # Connect to database
        await db.connect_to_mongo()
        print("✅ Database connected")
        
        # Get user_001 specifically
        users_collection = db.database["users"]
        user = await users_collection.find_one({"user_id": "user_001"})
        
        if user:
            print(f"\n📋 Complete user_001 data:")
            print(f"Email: {user.get('email')}")
            print(f"Professional info: {user.get('professional_info', {})}")
            
            # Check for social links in various possible locations
            print(f"\n🔗 Social links analysis:")
            print(f"user.social_links: {user.get('social_links', 'NOT FOUND')}")
            print(f"user.github_url: {user.get('github_url', 'NOT FOUND')}")
            print(f"user.portfolio_url: {user.get('portfolio_url', 'NOT FOUND')}")
            print(f"user.linkedin_url: {user.get('linkedin_url', 'NOT FOUND')}")
            print(f"user.twitter_url: {user.get('twitter_url', 'NOT FOUND')}")
            
            # Check if social links are in professional_info
            prof_info = user.get('professional_info', {})
            print(f"professional_info.github_url: {prof_info.get('github_url', 'NOT FOUND')}")
            print(f"professional_info.portfolio_url: {prof_info.get('portfolio_url', 'NOT FOUND')}")
            print(f"professional_info.linkedin_url: {prof_info.get('linkedin_url', 'NOT FOUND')}")
            
            # Check all top-level keys
            print(f"\n🗂️  All top-level keys in user document:")
            for key in sorted(user.keys()):
                if key != '_id':  # Skip MongoDB internal ID
                    print(f"  - {key}: {type(user[key])}")
                    
        else:
            print("❌ user_001 not found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_user_001())
