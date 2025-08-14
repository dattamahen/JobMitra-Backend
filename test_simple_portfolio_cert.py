#!/usr/bin/env python3
"""
Test portfolio and certification data flow.
"""

import asyncio
import requests
import json
from motor.motor_asyncio import AsyncIOMotorClient

async def setup_test_data():
    """Setup test data in database."""
    client = AsyncIOMotorClient("mongodb://localhost:27017/jobmitra")
    db = client.jobmitra
    collection = db.user_profiles
    
    # Create/update test user with problematic data
    user_data = {
        "user_id": "test_user_123",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "user_type": "candidate",
        "user_status": "active",
        "user_plan": "free",
        "profile_created_on": "2024-01-01T00:00:00",
        "last_active": "2024-01-01T00:00:00",
        
        # Problematic certifications data
        "certifications": [
            "[object Object]",  # This should be filtered out
            {
                "name": "Valid Certification",
                "issuer": "Test Institute"
            },
            "String Certification"  # This should be converted
        ],
        
        # Social links data
        "social_links": {
            "github": "https://github.com/testuser",
            "linkedin": "https://linkedin.com/in/testuser", 
            "youtube": "https://youtube.com/testuser",
            "portfolio": "https://myportfolio.dev"  # This is what frontend expects
        },
        
        # Also add legacy fields
        "portfolio_url": "https://myportfolio.dev",
        "github_url": "https://github.com/testuser",
        "linkedin_url": "https://linkedin.com/in/testuser",
        
        "skills": ["Python", "JavaScript", "React"],
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj5OOH9AESgy"  # testpassword123
    }
    
    await collection.replace_one(
        {"email": "testuser@example.com"},
        user_data,
        upsert=True
    )
    
    print("✅ Test user data setup complete")
    await client.close()

def test_auth_endpoints():
    """Test authentication endpoints."""
    
    # Test login
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            token = login_result["access_token"]
            print("✅ Login successful")
            print(f"📝 User in login response has certifications: {login_result.get('user', {}).get('certifications', 'Not present')}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /auth/me endpoint
    try:
        response = requests.get("http://localhost:8000/api/v1/auth/me", headers=headers)
        if response.status_code == 200:
            me_data = response.json()
            print("✅ /auth/me successful")
            print(f"📝 Social links: {me_data.get('social_links')}")
            print(f"📝 Certifications: {me_data.get('certifications')}")
            
            # Check portfolio specifically
            social_links = me_data.get('social_links', {})
            portfolio = social_links.get('portfolio') if social_links else None
            print(f"📝 Portfolio from social_links.portfolio: {portfolio}")
            
        else:
            print(f"❌ /auth/me failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ /auth/me error: {e}")
    
    # Test profile update
    update_data = {
        "certifications": ["[object Object]", "Another Valid Cert"],
        "portfolio_url": "https://updated-portfolio.dev",
        "skills": ["Python", "TypeScript", "Angular"]
    }
    
    try:
        response = requests.put("http://localhost:8000/api/v1/auth/profile", json=update_data, headers=headers)
        if response.status_code == 200:
            update_result = response.json()
            print("✅ Profile update successful")
            print(f"📝 Updated certifications: {update_result.get('certifications')}")
        else:
            print(f"❌ Profile update failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Profile update error: {e}")
    
    # Final check of /auth/me
    try:
        response = requests.get("http://localhost:8000/api/v1/auth/me", headers=headers)
        if response.status_code == 200:
            final_data = response.json()
            print("\n=== FINAL STATE ===")
            social_links = final_data.get('social_links', {})
            print(f"📝 Final social_links: {social_links}")
            print(f"📝 Final certifications: {final_data.get('certifications')}")
            
            # This is what frontend looks for
            portfolio_link = social_links.get('portfolio') if social_links else None
            print(f"📝 Portfolio link (what frontend sees): {portfolio_link}")
            
        else:
            print(f"❌ Final /auth/me failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Final check error: {e}")

async def main():
    print("Setting up test data...")
    await setup_test_data()
    
    print("\nTesting auth endpoints...")
    test_auth_endpoints()

if __name__ == "__main__":
    asyncio.run(main())
