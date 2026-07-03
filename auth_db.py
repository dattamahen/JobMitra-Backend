"""
Database operations for authentication and user management
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import uuid
from db import db
from auth_utils import hash_password, verify_password
from default_profile_data import get_random_default_skills, get_random_objective

logger = logging.getLogger(__name__)

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
        
        # Determine default skills and objective
        default_skills = user_data.get("skills") or get_random_default_skills()
        default_summary = user_data.get("professional_summary") or get_random_objective()
        
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
            "skills": default_skills,
            "technical_skills": [],
            "work_experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "contributions": None,
            "communication_skills": [],
            "ai_tools": [],
            "professional_summary": default_summary,
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
            "user_plan": "F",
            
            # Feature Usage Tracking
            "feature_usage_count": 5,
            
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
            "created_at": now.isoformat() + "Z",
            "updated_at": now.isoformat() + "Z",
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
                "skills": default_skills,
                "current_salary": 0,
                "expected_salary": 0,
                "professional_summary": default_summary
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
        logger.error("Error creating user: %s", e)
        raise e

async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with email and password"""
    try:
        if db.database is None:
            logger.error("Database not connected")
            return None

        user = await db.database[USERS_COLLECTION].find_one({"email": email})

        if not user:
            logger.debug("User not found: %s", email)
            return None

        stored_password = user.get("password_hash") or user.get("password")
        if not stored_password:
            logger.warning("No password field for user: %s", email)
            return None

        if not verify_password(stored_password, password):
            logger.debug("Password verification failed for: %s", email)
            return None
            
        # Update last login with proper datetime
        await db.database[USERS_COLLECTION].update_one(
            {"_id": user["_id"]},
            {"$set": {
                "last_login": datetime.utcnow().isoformat() + "Z",
                "last_active": datetime.utcnow()
            }}
        )
        
        # Convert ObjectId to string
        user["_id"] = str(user["_id"])
        return user
        
    except Exception as e:
        logger.error("Error authenticating user: %s", e)
        return None

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        user = await db.database[USERS_COLLECTION].find_one({"user_id": user_id})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        logger.error("Error getting user by ID: %s", e)
        return None

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    try:
        user = await db.database[USERS_COLLECTION].find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        logger.error("Error getting user by email: %s", e)
        return None

async def update_user_profile(user_id: str, update_data: Dict[str, Any]) -> bool:
    """Update user profile with new schema support"""
    try:
        # Add timestamp for last update
        update_data["updated_at"] = datetime.utcnow().isoformat() + "Z"
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
        logger.error("Error updating user profile: %s", e)
        return False

async def change_user_password(user_id: str, new_password: str) -> bool:
    """Change user password"""
    try:
        new_hash = hash_password(new_password)
        
        result = await db.database[USERS_COLLECTION].update_one(
            {"user_id": user_id},
            {"$set": {
                "password_hash": new_hash,
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "last_active": datetime.utcnow()
            }}
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        logger.error("Error changing password: %s", e)
        return False

async def seed_users_data():
    """Seed the database with Indian users"""
    try:
        from user_seed_data import get_hashed_users
        
        # Check if users already exist
        existing_count = await db.database[USERS_COLLECTION].count_documents({})
        if existing_count > 0:
            logger.info("Users collection already has %d documents. Skipping seed.", existing_count)
            return
        
        users = get_hashed_users()
        result = await db.database[USERS_COLLECTION].insert_many(users)
        logger.info("Seeded %d users successfully", len(result.inserted_ids))
        return result.inserted_ids
        
    except Exception as e:
        logger.error("Error seeding users: %s", e)
        return None

async def list_all_users(page: int = 1, per_page: int = 50) -> List[Dict[str, Any]]:
    """List all users with pagination (for admin purposes)"""
    try:
        skip = (page - 1) * per_page
        cursor = db.database[USERS_COLLECTION].find(
            {},
            {"password_hash": 0}
        ).sort("last_active", -1).skip(skip).limit(per_page)
        users = await cursor.to_list(length=per_page)

        for user in users:
            user["_id"] = str(user["_id"])

        return users

    except Exception as e:
        logger.error("Error listing users: %s", e)
        return []
