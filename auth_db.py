"""
Database operations for authentication and user management
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from db_simple import db
from auth_utils import hash_password, verify_password

# Collection names
USERS_COLLECTION = "users"
SESSIONS_COLLECTION = "user_sessions"

async def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = await db.database[USERS_COLLECTION].find_one({
            "$or": [
                {"email": user_data["email"]},
                {"username": user_data["username"]}
            ]
        })
        
        if existing_user:
            if existing_user["email"] == user_data["email"]:
                raise ValueError("Email already registered")
            else:
                raise ValueError("Username already taken")
        
        # Create user document
        user_doc = {
            "user_id": str(uuid.uuid4()),
            "email": user_data["email"],
            "username": user_data["username"],
            "password_hash": hash_password(user_data["password"]),
            "personal_info": {
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "phone": user_data["phone"],
                "location": {
                    "city": user_data["city"],
                    "state": user_data["state"],
                    "country": "India"
                }
            },
            "professional_info": {
                "current_role": "",
                "current_company": "",
                "total_experience": "",
                "industry": "",
                "skills": [],
                "current_salary": 0,
                "expected_salary": 0
            },
            "preferences": {
                "job_locations": [],
                "remote_preference": "hybrid",
                "notice_period": "30 days"
            },
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        result = await db.database[USERS_COLLECTION].insert_one(user_doc)
        user_doc["_id"] = str(result.inserted_id)
        return user_doc
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        raise e

async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with email and password"""
    try:
        user = await db.database[USERS_COLLECTION].find_one({"email": email})
        
        if not user:
            return None
        
        # Check both password_hash and password fields for compatibility
        stored_password = user.get("password_hash") or user.get("password")
        if not stored_password:
            return None
        
        if not verify_password(stored_password, password):
            return None
            
        # Update last login
        await db.database[USERS_COLLECTION].update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.now().isoformat()}}
        )
        
        # Convert ObjectId to string
        user["_id"] = str(user["_id"])
        return user
        
    except Exception as e:
        print(f"❌ Error authenticating user: {e}")
        return None

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        user = await db.database[USERS_COLLECTION].find_one({"user_id": user_id})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        print(f"❌ Error getting user by ID: {e}")
        return None

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    try:
        user = await db.database[USERS_COLLECTION].find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        print(f"❌ Error getting user by email: {e}")
        return None

async def update_user_profile(user_id: str, update_data: Dict[str, Any]) -> bool:
    """Update user profile"""
    try:
        update_data["updated_at"] = datetime.now().isoformat()
        
        result = await db.database[USERS_COLLECTION].update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        print(f"❌ Error updating user profile: {e}")
        return False

async def change_user_password(user_id: str, new_password: str) -> bool:
    """Change user password"""
    try:
        new_hash = hash_password(new_password)
        
        result = await db.database[USERS_COLLECTION].update_one(
            {"user_id": user_id},
            {"$set": {
                "password_hash": new_hash,
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        print(f"❌ Error changing password: {e}")
        return False

async def seed_users_data():
    """Seed the database with Indian users"""
    try:
        from user_seed_data import get_hashed_users
        
        # Check if users already exist
        existing_count = await db.database[USERS_COLLECTION].count_documents({})
        if existing_count > 0:
            print(f"Users collection already has {existing_count} documents. Skipping seed.")
            return
        
        users = get_hashed_users()
        result = await db.database[USERS_COLLECTION].insert_many(users)
        print(f"✅ Seeded {len(result.inserted_ids)} users successfully")
        return result.inserted_ids
        
    except Exception as e:
        print(f"❌ Error seeding users: {e}")
        return None

async def list_all_users() -> List[Dict[str, Any]]:
    """List all users (for admin purposes)"""
    try:
        cursor = db.database[USERS_COLLECTION].find({}, {
            "password_hash": 0  # Exclude password hash
        })
        users = await cursor.to_list(length=None)
        
        for user in users:
            user["_id"] = str(user["_id"])
            
        return users
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return []
