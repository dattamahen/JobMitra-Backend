import asyncio
from auth_db import authenticate_user
from db_simple import db

async def debug_auth():
    try:
        print('🔍 Debugging authentication...')
        
        # Connect to database
        await db.connect_to_mongo()
        
        if db.fallback_mode:
            print('❌ Database is in fallback mode - cannot authenticate')
            return
        
        # Test authentication
        email = 'arjun.sharma@email.com'
        password = 'TechLead@123'
        
        print(f'Testing login for: {email}')
        
        user = await authenticate_user(email, password)
        
        if user:
            print('✅ Authentication successful!')
            print(f'User: {user["personal_info"]["first_name"]} {user["personal_info"]["last_name"]}')
            print(f'Email: {user["email"]}')
            print(f'User ID: {user["user_id"]}')
        else:
            print('❌ Authentication failed')
            
            # Check if user exists
            users_collection = db.database["users"]
            existing_user = await users_collection.find_one({"email": email})
            
            if existing_user:
                print(f'✅ User found in database')
                print(f'Stored email: {existing_user["email"]}')
                print('❌ Password verification failed')
            else:
                print('❌ User not found in database')
                
                # Show all users
                all_users = await users_collection.find({}, {"email": 1, "personal_info.first_name": 1, "personal_info.last_name": 1}).to_list(10)
                print(f'Found {len(all_users)} users in database:')
                for u in all_users:
                    print(f'  - {u["personal_info"]["first_name"]} {u["personal_info"]["last_name"]} ({u["email"]})')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_auth())
