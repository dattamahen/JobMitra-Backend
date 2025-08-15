"""
Activity tracking for user dashboard
"""

from datetime import datetime
from db_simple import db

async def log_user_activity(user_id: str, activity_type: str, title: str, details: dict = None):
    """Log user activity for dashboard recent activities"""
    try:
        activity = {
            "activity_type": activity_type,
            "description": title,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        # Add to user's recent_activity array, keep only last 3
        await db.database["users"].update_one(
            {"user_id": user_id},
            {
                "$push": {
                    "recent_activity": {
                        "$each": [activity],
                        "$slice": -3  # Keep only last 3 activities
                    }
                }
            }
        )
        
    except Exception as e:
        print(f"❌ Error logging activity: {e}")