#!/usr/bin/env python3
"""
Test the auth_db functions directly to see where the issue is.
"""

import asyncio
from auth_db import create_user, authenticate_user, get_user_by_id
from db_simple import db

async def test_auth_db():
    """Test auth database functions"""
    try:
        print("🧪 Testing auth database functions...")
        
        # First, manually connect to the database
        print("\n0. Connecting to database...")
        await db.connect_to_mongo()
        
        if db.database is None:
            print("❌ Database connection failed - db.database is None")
            print(f"Fallback mode: {db.fallback_mode}")
            return
        else:
            print("✅ Database connected successfully")
            print(f"Database name: {db.database.name}")
        
        # Test user creation
        print("\n1. Testing user creation...")
        test_user_data = {
            "email": "direct_test@example.com",
            "password": "password123",
            "first_name": "Direct",
            "last_name": "Test",
            "user_type": "candidate",
            "skills": ["Testing"]
        }
        
        try:
            user = await create_user(test_user_data)
            print("✅ User creation successful!")
            print(f"Created user ID: {user['user_id']}")
            print(f"Email: {user['email']}")
            
            # Test authentication
            print("\n2. Testing authentication...")
            auth_user = await authenticate_user("direct_test@example.com", "password123")
            
            if auth_user:
                print("✅ Authentication successful!")
                print(f"Authenticated user ID: {auth_user['user_id']}")
                
                # Test get_user_by_id
                print("\n3. Testing get_user_by_id...")
                retrieved_user = await get_user_by_id(auth_user['user_id'])
                
                if retrieved_user:
                    print("✅ get_user_by_id successful!")
                    print(f"Retrieved user: {retrieved_user['first_name']} {retrieved_user['last_name']}")
                else:
                    print("❌ get_user_by_id failed")
            else:
                print("❌ Authentication failed")
                
        except ValueError as ve:
            if "already registered" in str(ve):
                print("ℹ️ User already exists, testing authentication...")
                auth_user = await authenticate_user("direct_test@example.com", "password123")
                if auth_user:
                    print("✅ Authentication with existing user successful!")
                    print(f"User ID: {auth_user['user_id']}")
                else:
                    print("❌ Authentication with existing user failed")
            else:
                print(f"❌ User creation failed with ValueError: {ve}")
        except Exception as e:
            print(f"❌ User creation failed with error: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Overall test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the database connection
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_auth_db())
