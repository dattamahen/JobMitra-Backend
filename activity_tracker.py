"""
Activity Tracker — Persists user activities to MongoDB.
Activities are stored in the user's `recent_activity` array
and displayed on the dashboard.

Tracked activities:
  1. Profile updates
  2. Mock interviews
  3. CV downloads
  4. Skill assessments
  5. Subscriptions / payments
"""

from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Icon and type mapping for each activity category
ACTIVITY_CONFIG = {
    "profile_update": {"icon": "person", "type": "profile"},
    "mock_interview": {"icon": "quiz", "type": "interview"},
    "cv_download": {"icon": "download", "type": "resume"},
    "skill_assessment": {"icon": "assessment", "type": "assessment"},
    "subscription": {"icon": "card_membership", "type": "other"},
    "job_application": {"icon": "send", "type": "application"},
}

MAX_RECENT_ACTIVITIES = 30


async def log_user_activity(
    user_id: str,
    activity_type: str,
    description: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Persist a user activity to MongoDB.

    Args:
        user_id: User identifier
        activity_type: One of profile_update, mock_interview, cv_download,
                        skill_assessment, subscription (or any custom key)
        description: Human-readable activity title shown on dashboard
        metadata: Optional extra data (job_id, score, etc.)
    """
    try:
        from db_simple import db

        if db.database is None:
            logger.warning("DB not connected — activity not persisted for %s", user_id)
            return

        config = ACTIVITY_CONFIG.get(activity_type, {"icon": "info", "type": "other"})

        activity = {
            "activity_type": config["type"],
            "description": description,
            "icon": config["icon"],
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
            "metadata": metadata or {},
        }

        # Push to front of array and cap at MAX_RECENT_ACTIVITIES
        await db.database["users"].update_one(
            {"user_id": user_id},
            {
                "$push": {
                    "recent_activity": {
                        "$each": [activity],
                        "$position": 0,
                        "$slice": MAX_RECENT_ACTIVITIES,
                    }
                }
            },
        )

        logger.info("Activity logged: [%s] %s — %s", user_id, activity_type, description)

    except Exception as e:
        # Never let activity tracking break the main flow
        logger.error("Failed to log activity for %s: %s", user_id, e)
