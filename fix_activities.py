"""
Fix existing activity field names in database
"""

import asyncio
from db_simple import db

async def fix_activity_fields():
    """Fix activity field names from type/title to activity_type/description"""
    try:
        await db.connect_to_mongo()
        
        # Get all users with recent_activity
        users = await db.database["users"].find({"recent_activity": {"$exists": True}}).to_list(None)
        
        for user in users:
            activities = user.get("recent_activity", [])
            fixed_activities = []
            
            for activity in activities:
                if isinstance(activity, dict):
                    # Convert old format to new format
                    fixed_activity = {
                        "activity_type": activity.get("type", activity.get("activity_type", "unknown")),
                        "description": activity.get("title", activity.get("description", "Unknown activity")),
                        "timestamp": activity.get("timestamp", ""),
                        "details": activity.get("details", {})
                    }
                    fixed_activities.append(fixed_activity)
            
            # Update user with fixed activities
            await db.database["users"].update_one(
                {"_id": user["_id"]},
                {"$set": {"recent_activity": fixed_activities}}
            )
        
        print(f"Fixed activities for {len(users)} users")
        
    except Exception as e:
        print(f"Error fixing activities: {e}")
    finally:
        await db.close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(fix_activity_fields())