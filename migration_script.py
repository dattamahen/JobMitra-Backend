"""
Migration script to update existing users to new schema
"""

import asyncio
from datetime import datetime
from db_simple import db
from typing import List, Dict, Any

USERS_COLLECTION = "users"

async def migrate_users_to_new_schema():
    """Migrate existing users to the new comprehensive schema"""
    try:
        print("🔄 Starting user schema migration...")
        
        # Get all existing users
        cursor = db.database[USERS_COLLECTION].find({})
        users = await cursor.to_list(length=None)
        
        migration_count = 0
        
        for user in users:
            print(f"📝 Migrating user: {user.get('email', 'Unknown')}")
            
            # Prepare update document
            update_doc = {}
            
            # Migrate basic personal info from nested structure to top-level
            personal_info = user.get("personal_info", {})
            if personal_info:
                if not user.get("first_name") and personal_info.get("first_name"):
                    update_doc["first_name"] = personal_info["first_name"]
                if not user.get("last_name") and personal_info.get("last_name"):
                    update_doc["last_name"] = personal_info["last_name"]
                if not user.get("phone") and personal_info.get("phone"):
                    update_doc["phone"] = personal_info["phone"]
            
            # Add new fields with defaults if they don't exist
            new_fields = {
                "date_of_birth": None,
                "overall_experience_years": None,
                "highest_qualification": None,
                "previous_organizations": [],
                "certifications": [],
                "contributions": None,
                "communication_skills": [],
                "ai_tools": [],
                "overall_jobs_applied": [],
                "user_type": "candidate",  # Default to candidate
                "user_status": "active",
                "user_plan": "free",
                "job_preferences": [],
                "employment_type": [],
                "match_analysis_count": 0,
                "match_tailored_count": 0,
                "mock_interview_count": 0,
                "profile_completion_count": user.get("profile_completion", 20),
                "profile_visits": 0,
                "recent_activity": []
            }
            
            for field, default_value in new_fields.items():
                if field not in user:
                    update_doc[field] = default_value
            
            # Migrate timestamps
            if "created_at" in user and not user.get("profile_created_on"):
                try:
                    if isinstance(user["created_at"], str):
                        update_doc["profile_created_on"] = datetime.fromisoformat(user["created_at"].replace('Z', '+00:00'))
                    else:
                        update_doc["profile_created_on"] = user["created_at"]
                except:
                    update_doc["profile_created_on"] = datetime.utcnow()
            elif not user.get("profile_created_on"):
                update_doc["profile_created_on"] = datetime.utcnow()
            
            if not user.get("last_active"):
                update_doc["last_active"] = user.get("profile_created_on", datetime.utcnow())
            
            # Ensure social_links structure
            if not user.get("social_links"):
                update_doc["social_links"] = {
                    "github": None,
                    "youtube": None,
                    "linkedin": None,
                    "playstore": None
                }
            else:
                # Update existing social_links to new structure
                social_links = user["social_links"]
                updated_social_links = {
                    "github": social_links.get("github"),
                    "youtube": social_links.get("youtube"),
                    "linkedin": social_links.get("linkedin"),
                    "playstore": social_links.get("playstore")
                }
                update_doc["social_links"] = updated_social_links
            
            # Extract skills from professional_info if exists
            professional_info = user.get("professional_info", {})
            if professional_info and professional_info.get("skills") and not user.get("skills"):
                update_doc["skills"] = professional_info["skills"]
            elif not user.get("skills"):
                update_doc["skills"] = []
            
            # Update the user if there are changes
            if update_doc:
                update_doc["updated_at"] = datetime.utcnow().isoformat()
                
                result = await db.database[USERS_COLLECTION].update_one(
                    {"_id": user["_id"]},
                    {"$set": update_doc}
                )
                
                if result.modified_count > 0:
                    migration_count += 1
                    print(f"✅ Successfully migrated user: {user.get('email', 'Unknown')}")
                else:
                    print(f"ℹ️ No changes needed for user: {user.get('email', 'Unknown')}")
            else:
                print(f"ℹ️ User already up to date: {user.get('email', 'Unknown')}")
        
        print(f"🎉 Migration completed! Updated {migration_count} users.")
        
        # Create indexes for new fields
        await create_new_indexes()
        
        return migration_count
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise e

async def create_new_indexes():
    """Create indexes for new schema fields"""
    try:
        print("📊 Creating indexes for new schema...")
        
        # Create indexes for commonly queried fields
        indexes = [
            ("user_type", 1),
            ("user_status", 1),
            ("user_plan", 1),
            ("skills", 1),
            ("job_preferences", 1),
            ("employment_type", 1),
            ("last_active", -1),
            ("profile_created_on", -1),
            ("overall_experience_years", 1),
            ("highest_qualification", 1)
        ]
        
        for field, direction in indexes:
            try:
                await db.database[USERS_COLLECTION].create_index([(field, direction)])
                print(f"✅ Created index for {field}")
            except Exception as e:
                print(f"⚠️ Index creation warning for {field}: {e}")
        
        print("📊 Index creation completed!")
        
    except Exception as e:
        print(f"❌ Index creation failed: {e}")

async def validate_migration():
    """Validate that the migration was successful"""
    try:
        print("🔍 Validating migration...")
        
        # Count users with new fields
        total_users = await db.database[USERS_COLLECTION].count_documents({})
        users_with_new_schema = await db.database[USERS_COLLECTION].count_documents({
            "user_type": {"$exists": True},
            "user_status": {"$exists": True},
            "profile_created_on": {"$exists": True}
        })
        
        print(f"📊 Total users: {total_users}")
        print(f"📊 Users with new schema: {users_with_new_schema}")
        
        if total_users == users_with_new_schema:
            print("✅ Migration validation successful!")
            return True
        else:
            print("❌ Migration validation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

async def rollback_migration():
    """Rollback migration if needed (removes new fields)"""
    try:
        print("🔄 Rolling back migration...")
        
        # Fields to remove in rollback
        fields_to_remove = [
            "date_of_birth", "overall_experience_years", "highest_qualification",
            "previous_organizations", "certifications", "contributions",
            "communication_skills", "ai_tools", "overall_jobs_applied",
            "user_type", "user_status", "user_plan", "job_preferences",
            "employment_type", "match_analysis_count", "match_tailored_count",
            "mock_interview_count", "profile_completion_count", "profile_visits",
            "recent_activity", "profile_created_on", "last_active"
        ]
        
        result = await db.database[USERS_COLLECTION].update_many(
            {},
            {"$unset": {field: "" for field in fields_to_remove}}
        )
        
        print(f"🔄 Rollback completed. Modified {result.modified_count} users.")
        return result.modified_count
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        raise e

if __name__ == "__main__":
    async def main():
        await db.connect_to_mongo()
        
        try:
            # Run migration
            migration_count = await migrate_users_to_new_schema()
            
            # Validate migration
            if await validate_migration():
                print("🎉 Migration completed successfully!")
            else:
                print("❌ Migration validation failed. Consider running rollback.")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            
        finally:
            await db.close_mongo_connection()
    
    asyncio.run(main())
