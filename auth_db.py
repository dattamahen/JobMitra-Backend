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
    """Create a new user with comprehensive profile"""
    try:
        # Check if user already exists
        query_conditions = [{"email": user_data["email"]}]
        
        # Only add username condition if username is provided
        if user_data.get("username"):
            query_conditions.append({"username": user_data["username"]})
        
        existing_user = await db.database[USERS_COLLECTION].find_one({
            "$or": query_conditions
        })
        
        if existing_user:
            if existing_user["email"] == user_data["email"]:
                raise ValueError("Email already registered")
            elif user_data.get("username") and existing_user.get("username") == user_data["username"]:
                raise ValueError("Username already taken")
        
        # Create timestamp
        now = datetime.utcnow()
        
        # Create comprehensive user document with new schema
        user_doc = {
            "user_id": str(uuid.uuid4()),
            "email": user_data["email"],
            "password_hash": hash_password(user_data["password"]),
            
            # Basic Personal Information
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "date_of_birth": user_data.get("date_of_birth"),
            "phone": user_data.get("phone"),
            
            # Professional Information
            "overall_experience_years": user_data.get("overall_experience_years"),
            "highest_qualification": user_data.get("highest_qualification"),
            "previous_organizations": [],
            "skills": user_data.get("skills", []),
            "technical_skills": [],
            "work_experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "contributions": None,
            "communication_skills": [],
            "ai_tools": [],
            "professional_summary": None,
            "current_role": None,
            "current_company": None,
            "portfolio_link": None,
            "desired_job_title": None,
            "expected_salary": None,
            "currency": "INR",
            "linkedin_link": None,
            "github_link": None,
            "city": None,
            "state": None,
            
            # Social Links
            "social_links": {
                "github": None,
                "youtube": None,
                "linkedin": None,
                "playstore": None
            },
            
            # Job Application Tracking
            "overall_jobs_applied": [],
            
            # User Classification
            "user_type": user_data.get("user_type", "candidate"),
            "user_status": "active",
            "user_plan": "free",
            
            # Preferences
            "job_preferences": user_data.get("job_preferences", []),
            "employment_type": user_data.get("employment_type", []),
            
            # Timestamps
            "profile_created_on": now,
            "last_active": now,
            
            # Analytics and Metrics
            "match_analysis_count": 0,
            "match_tailored_count": 0,
            "mock_interview_count": 0,
            "profile_completion_count": 20,  # Basic registration completion
            "profile_visits": 0,
            "recent_activity": [],
            
            # Legacy compatibility fields
            "username": user_data.get("username"),
            "is_active": True,
            "is_verified": False,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "last_login": None,
            
            # Legacy structure for backward compatibility
            "personal_info": {
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "phone": user_data.get("phone", ""),
                "location": {
                    "city": user_data.get("city", ""),
                    "state": user_data.get("state", ""),
                    "country": "India"
                }
            },
            "professional_info": {
                "current_role": "",
                "current_company": "",
                "total_experience": "",
                "industry": "",
                "skills": user_data.get("skills", []),
                "current_salary": 0,
                "expected_salary": 0
            },
            "preferences": {
                "job_locations": [],
                "remote_preference": "hybrid",
                "notice_period": "30 days"
            }
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
        print(f"🔍 Authenticating user: {email}")
        
        # Check if database is connected
        if not db.database:
            print("❌ Database not connected")
            return None
            
        user = await db.database[USERS_COLLECTION].find_one({"email": email})
        
        if not user:
            print(f"❌ User not found: {email}")
            return None
        
        print(f"✅ User found: {user['user_id']}")
        
        # Check both password_hash and password fields for compatibility
        stored_password = user.get("password_hash") or user.get("password")
        if not stored_password:
            print(f"❌ No password field found for user: {email}")
            return None
        
        print(f"🔐 Stored password hash: {stored_password[:20]}...")
        print(f"🔑 Provided password: {password}")
        
        password_valid = verify_password(stored_password, password)
        print(f"🔍 Password verification result: {password_valid}")
        
        if not password_valid:
            print(f"❌ Password verification failed for user: {email}")
            return None
            
        # Update last login with proper datetime
        await db.database[USERS_COLLECTION].update_one(
            {"_id": user["_id"]},
            {"$set": {
                "last_login": datetime.utcnow().isoformat(),
                "last_active": datetime.utcnow()
            }}
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
    """Update user profile with new schema support"""
    try:
        # Add timestamp for last update
        update_data["updated_at"] = datetime.utcnow().isoformat()
        update_data["last_active"] = datetime.utcnow()
        
        # Handle nested updates for legacy compatibility
        set_updates = {}
        
        for key, value in update_data.items():
            if key == "personal_info" and isinstance(value, dict):
                # Update nested personal_info fields
                for sub_key, sub_value in value.items():
                    set_updates[f"personal_info.{sub_key}"] = sub_value
            elif key == "professional_info" and isinstance(value, dict):
                # Update nested professional_info fields
                for sub_key, sub_value in value.items():
                    set_updates[f"professional_info.{sub_key}"] = sub_value
            elif key == "preferences" and isinstance(value, dict):
                # Update nested preferences fields
                for sub_key, sub_value in value.items():
                    set_updates[f"preferences.{sub_key}"] = sub_value
            elif key == "social_links" and isinstance(value, dict):
                # Update nested social_links fields
                for sub_key, sub_value in value.items():
                    set_updates[f"social_links.{sub_key}"] = sub_value
            else:
                # Direct field update
                set_updates[key] = value
        
        result = await db.database[USERS_COLLECTION].update_one(
            {"user_id": user_id},
            {"$set": set_updates}
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
                "updated_at": datetime.utcnow().isoformat(),
                "last_active": datetime.utcnow()
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
