"""
Test HR authentication and token generation
"""

import asyncio
import sys
sys.path.append('.')

from auth_db import get_user_by_id, create_user
from auth_utils import create_access_token
from db_simple import db

async def test_hr_auth():
    print("=== Testing HR Authentication ===")
    
    await db.connect_to_mongo()
    
    try:
        # Check if HR user exists
        hr_user = await get_user_by_id("hr001")
        if not hr_user:
            print("HR user not found, creating...")
            # Create HR user
            user_data = {
                "user_id": "hr001",
                "email": "hr001@test.com", 
                "password": "test1234",
                "full_name": "HR Manager",
                "user_type": "hire"
            }
            result = await create_user(user_data)
            print(f"HR user created: {result}")
            hr_user = await get_user_by_id("hr001")
        
        if hr_user:
            print(f"HR user found: {hr_user['email']} (Type: {hr_user['user_type']})")
            
            # Generate token
            token = create_access_token({"user_id": hr_user["user_id"]})
            print(f"Generated token: {token}")
            
            print("\nTo test the API, use this curl command:")
            print(f'curl -X GET "http://localhost:8000/api/v1/hr/jobs" -H "Authorization: Bearer {token}"')
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_hr_auth())