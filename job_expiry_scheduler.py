"""
Background scheduler to auto-expire stale job listings.
Runs periodically to mark jobs as expired/inactive based on:
1. Past application_deadline
2. Jobs without deadline older than DEFAULT_JOB_EXPIRY_DAYS (posted_date + N days)
3. Jobs without deadline older than MAX_JOB_AGE_DAYS as a hard cap
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from db import db

logger = logging.getLogger(__name__)

MAX_JOB_AGE_DAYS = int(os.getenv("MAX_JOB_AGE_DAYS", "90"))
DEFAULT_JOB_EXPIRY_DAYS = int(os.getenv("DEFAULT_JOB_EXPIRY_DAYS", "30"))
CHECK_INTERVAL_HOURS = int(os.getenv("JOB_EXPIRY_CHECK_INTERVAL_HOURS", "6"))


async def expire_stale_jobs():
    """Mark jobs as expired based on deadline or age."""
    try:
        if db.fallback_mode or not db.database:
            return 0

        now = datetime.utcnow()
        default_cutoff = now - timedelta(days=DEFAULT_JOB_EXPIRY_DAYS)
        hard_cutoff = now - timedelta(days=MAX_JOB_AGE_DAYS)

        # 1. Expire jobs past their application_deadline (string format)
        r1 = await db.database["jobs"].update_many(
            {
                "application_deadline": {"$lt": now.isoformat(), "$ne": None},
                "status": {"$nin": ["expired", "closed", "filled"]},
            },
            {"$set": {"status": "expired", "is_active": False, "updated_date": now.isoformat()}},
        )

        # 2. Expire jobs without deadline, older than DEFAULT_JOB_EXPIRY_DAYS (datetime posted_date)
        r2 = await db.database["jobs"].update_many(
            {
                "$or": [
                    {"application_deadline": None},
                    {"application_deadline": {"$exists": False}},
                ],
                "posted_date": {"$lt": default_cutoff},
                "status": {"$nin": ["expired", "closed", "filled"]},
            },
            {"$set": {"status": "expired", "is_active": False, "updated_date": now.isoformat()}},
        )

        # 3. Hard cap: expire anything older than MAX_JOB_AGE_DAYS regardless
        r3 = await db.database["jobs"].update_many(
            {
                "posted_date": {"$lt": hard_cutoff},
                "status": {"$nin": ["expired", "closed", "filled"]},
            },
            {"$set": {"status": "expired", "is_active": False, "updated_date": now.isoformat()}},
        )

        total = r1.modified_count + r2.modified_count + r3.modified_count
        if total > 0:
            logger.info(f"Expired {total} stale job(s)")
        return total

    except Exception as e:
        logger.error(f"Error expiring stale jobs: {e}")
        return 0


async def job_expiry_loop():
    """Background loop that checks for stale jobs periodically."""
    while True:
        await expire_stale_jobs()
        await asyncio.sleep(CHECK_INTERVAL_HOURS * 3600)


def start_expiry_scheduler():
    """Start the background expiry task. Call from app startup."""
    asyncio.create_task(job_expiry_loop())
    logger.info(
        f"Job expiry scheduler started (interval: {CHECK_INTERVAL_HOURS}h, "
        f"default expiry: {DEFAULT_JOB_EXPIRY_DAYS}d, hard cap: {MAX_JOB_AGE_DAYS}d)"
    )
