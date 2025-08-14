#!/usr/bin/env python3
"""
Test the profile endpoint with portfolio and certification issues.
"""

import asyncio
import json
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient

async def test_portfolio_and_certifications():
    """Test the current profile endpoint with problematic data."""
    
    # First, let's create a user with portfolio data
    client = AsyncIOMotorClient("mongodb://localhost:27017/jobmitra")
    db = client.jobmitra
    collection = db.user_profiles
    
    # Update the test user to include portfolio_url field
    update_result = await collection.update_one(
        {"email": "testuser@example.com"},
        {"$set": {
            "portfolio_url": "https://myportfolio.dev",
            "social_links": {
                "github": "https://github.com/testuser",
                "linkedin": "https://linkedin.com/in/testuser", 
                "youtube": "https://youtube.com/testuser",
                "portfolio": "https://myportfolio.dev"  # This is what the frontend expects
            }
        }}
    )
    
    print(f"✅ Updated user with portfolio data: {update_result.modified_count} documents")
    
    # Register and login to get token
    async with aiohttp.ClientSession() as session:
        
        # Register user
        register_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        async with session.post("http://localhost:8000/api/v1/auth/register", json=register_data) as resp:
            if resp.status in [200, 400]:  # 400 means user exists already
                print("✅ User registration/exists confirmed")
                
        # Login to get token
        login_data = {
            "email": "testuser@example.com", 
            "password": "testpassword123"
        }
        
        async with session.post("http://localhost:8000/api/v1/auth/login", json=login_data) as resp:
            if resp.status == 200:
                login_response = await resp.json()
                token = login_response["access_token"]
                print("✅ Login successful")
            else:
                print(f"❌ Login failed: {resp.status}")
                print(await resp.text())
                return
                
        # Test /auth/me endpoint
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get("http://localhost:8000/api/v1/auth/me", headers=headers) as resp:
            if resp.status == 200:
                me_data = await resp.json()
                print("✅ /auth/me successful")
                print(f"📝 Social links in response: {me_data.get('social_links')}")
                print(f"📝 Certifications in response: {me_data.get('certifications')}")
            else:
                print(f"❌ /auth/me failed: {resp.status}")
                print(await resp.text())
                return
                
        # Test profile update with problematic data
        update_data = {
            "certifications": ["[object Object]", "Valid Certification"],
            "portfolio_url": "https://mynewportfolio.dev",
            "skills": ["Python", "JavaScript"]
        }
        
        async with session.put("http://localhost:8000/api/v1/auth/profile", json=update_data, headers=headers) as resp:
            if resp.status == 200:
                profile_response = await resp.json()
                print("✅ Profile update successful")
                print(f"📝 Updated certifications: {profile_response.get('certifications')}")
                print(f"📝 Updated social links: {profile_response.get('social_links')}")
            else:
                print(f"❌ Profile update failed: {resp.status}")
                print(await resp.text())
                
        # Check final /auth/me to see what frontend would receive
        async with session.get("http://localhost:8000/api/v1/auth/me", headers=headers) as resp:
            if resp.status == 200:
                final_data = await resp.json()
                print("\n=== FINAL /AUTH/ME DATA ===")
                print(f"📝 Social links: {final_data.get('social_links')}")
                print(f"📝 Certifications: {final_data.get('certifications')}")
                
                # Check what frontend would see for portfolio
                social_links = final_data.get('social_links', {})
                portfolio = social_links.get('portfolio') if social_links else None
                print(f"📝 Portfolio link frontend would see: {portfolio}")
                
            else:
                print(f"❌ Final /auth/me failed: {resp.status}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_portfolio_and_certifications())
