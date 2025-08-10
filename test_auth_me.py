#!/usr/bin/env python3
"""
Test the /auth/me endpoint directly to see what data it returns
"""
import asyncio
import aiohttp
import json

async def test_auth_me_endpoint():
    print("🔍 Testing /auth/me endpoint...")
    
    # You'll need to replace this with your actual JWT token
    # You can get this from the browser's developer tools > Application > Local Storage
    jwt_token = "YOUR_JWT_TOKEN_HERE"
    
    url = "http://localhost:8000/api/v1/auth/me"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"Status Code: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("Response Data:")
                    print(json.dumps(data, indent=2))
                    
                    # Check specific fields that should be updated
                    prof_info = data.get('professional_info', {})
                    print(f"\nKey Fields:")
                    print(f"- Professional Summary: {prof_info.get('professional_summary')}")
                    print(f"- Desired Job Title: {prof_info.get('desired_job_title')}")
                    print(f"- Certifications: {prof_info.get('certifications')}")
                    print(f"- Updated At: {data.get('updated_at')}")
                    
                else:
                    error_text = await response.text()
                    print(f"Error: {response.status}")
                    print(f"Response: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

if __name__ == "__main__":
    print("To test this:")
    print("1. Open browser developer tools")
    print("2. Go to Application > Local Storage")
    print("3. Find your JWT token")
    print("4. Replace 'YOUR_JWT_TOKEN_HERE' in this script")
    print("5. Run the script again")
    print()
    asyncio.run(test_auth_me_endpoint())
