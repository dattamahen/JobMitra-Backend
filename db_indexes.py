"""
Database Index Management
Creates indexes on application startup for optimal query performance.
Safe to run multiple times — MongoDB's create_index is idempotent.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


async def ensure_indexes(database: AsyncIOMotorDatabase) -> None:
    """Create all required indexes. Safe to call on every startup."""
    if database is None:
        logger.warning("Database not available — skipping index creation")
        return

    try:
        # ── Users Collection ─────────────────────────────────────
        users = database["users"]
        await users.create_index("user_id", unique=True)
        await users.create_index("email", unique=True)
        await users.create_index("user_type")
        await users.create_index("skills")
        await users.create_index("last_active")
        # Compound index for auth lookups
        await users.create_index([("email", 1), ("is_active", 1)])
        # Text index for user search
        await users.create_index([
            ("first_name", "text"),
            ("last_name", "text"),
            ("skills", "text"),
            ("professional_summary", "text")
        ])

        # ── Jobs Collection ──────────────────────────────────────
        jobs = database["jobs"]
        await jobs.create_index("job_id", unique=True)
        await jobs.create_index("posted_by_hr_id")
        await jobs.create_index("is_active")
        await jobs.create_index("posted_date")
        await jobs.create_index("experience_level")
        await jobs.create_index("employment_type")
        await jobs.create_index("job_type")
        await jobs.create_index("skills_required")
        await jobs.create_index("application_deadline")
        # Compound indexes for common queries
        await jobs.create_index([("is_active", 1), ("posted_date", -1)])
        await jobs.create_index([("posted_by_hr_id", 1), ("posted_date", -1)])
        await jobs.create_index([("is_active", 1), ("experience_level", 1)])
        # Text index for job search
        await jobs.create_index([
            ("title", "text"),
            ("description", "text"),
            ("company", "text"),
            ("skills_required", "text")
        ])

        # ── Job Applications Collection ──────────────────────────
        applications = database["job_applications"]
        await applications.create_index("job_id")
        await applications.create_index("user_id")
        await applications.create_index([("job_id", 1), ("user_id", 1)], unique=True)
        await applications.create_index([("user_id", 1), ("created_at", -1)])

        # ── Mock Interviews Collection ───────────────────────────
        mock_interviews = database["mock_interview_sessions"]
        await mock_interviews.create_index("user_id")
        await mock_interviews.create_index([("user_id", 1), ("created_at", -1)])

        # ── Query Logs Collection ────────────────────────────────
        query_logs = database["query_logs"]
        await query_logs.create_index([("created_at", -1)])
        await query_logs.create_index("user_id")
        # TTL index — auto-delete logs older than 30 days
        await query_logs.create_index("created_at", expireAfterSeconds=30 * 24 * 3600)

        # ── User Progress Collection ─────────────────────────────
        user_progress = database["user_progress"]
        await user_progress.create_index("user_id", unique=True)

        # ── User Dashboards Collection ───────────────────────────
        dashboards = database["user_dashboards"]
        await dashboards.create_index("user_id", unique=True)

        logger.info("All database indexes ensured successfully")

    except Exception as e:
        logger.error("Failed to create indexes: %s", e)
