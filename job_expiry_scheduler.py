"""
Background scheduler to auto-archive stale job listings.
Runs periodically to find and archive jobs based on:
1. Past application_deadline
2. Jobs older than DEFAULT_JOB_EXPIRY_DAYS by posted_date
3. Hard cap: MAX_JOB_AGE_DAYS
Archived jobs are moved to `archived_jobs` collection and hard-deleted from `jobs`.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from db import db
from archive_jobs import archive_jobs_bulk

logger = logging.getLogger(__name__)

MAX_JOB_AGE_DAYS = int(os.getenv("MAX_JOB_AGE_DAYS", "90"))
DEFAULT_JOB_EXPIRY_DAYS = int(os.getenv("DEFAULT_JOB_EXPIRY_DAYS", "30"))
CHECK_INTERVAL_HOURS = int(os.getenv("JOB_EXPIRY_CHECK_INTERVAL_HOURS", "6"))


def _is_before(value, cutoff_dt: datetime, cutoff_iso: str) -> bool:
    """Check if a date field (BSON datetime or ISO string) is before the cutoff."""
    if isinstance(value, datetime):
        return value < cutoff_dt
    if isinstance(value, str):
        return value < cutoff_iso
    return False


async def expire_stale_jobs() -> int:
    """Find and archive stale jobs. Returns total count archived."""
    try:
        if db.fallback_mode or not db.database:
            return 0

        now = datetime.utcnow()
        now_iso = now.isoformat()
        default_cutoff = now - timedelta(days=DEFAULT_JOB_EXPIRY_DAYS)
        default_cutoff_iso = default_cutoff.isoformat()
        hard_cutoff = now - timedelta(days=MAX_JOB_AGE_DAYS)
        hard_cutoff_iso = hard_cutoff.isoformat()

        # Collect job_ids to archive (deduplicated)
        to_archive: set[str] = set()

        # 1. Past application_deadline
        async for job in db.database["jobs"].find(
            {"application_deadline": {"$ne": None, "$exists": True}},
            {"job_id": 1, "application_deadline": 1}
        ):
            if _is_before(job.get("application_deadline"), now, now_iso):
                to_archive.add(job["job_id"])

        # 2. Older than DEFAULT_JOB_EXPIRY_DAYS by posted_date
        async for job in db.database["jobs"].find(
            {"posted_date": {"$exists": True}},
            {"job_id": 1, "posted_date": 1}
        ):
            if _is_before(job.get("posted_date"), default_cutoff, default_cutoff_iso):
                to_archive.add(job["job_id"])

        # 3. Hard cap: older than MAX_JOB_AGE_DAYS
        async for job in db.database["jobs"].find(
            {"posted_date": {"$exists": True}},
            {"job_id": 1, "posted_date": 1}
        ):
            if _is_before(job.get("posted_date"), hard_cutoff, hard_cutoff_iso):
                to_archive.add(job["job_id"])

        if not to_archive:
            return 0

        total = await archive_jobs_bulk(list(to_archive), reason="expired", archived_by="scheduler")
        if total > 0:
            logger.info("Scheduler archived %d stale job(s)", total)
        return total

    except Exception as e:
        logger.error("Error in expire_stale_jobs: %s", e)
        return 0


async def job_expiry_loop():
    """Background loop that checks for stale jobs periodically."""
    while True:
        await asyncio.sleep(CHECK_INTERVAL_HOURS * 3600)  # startup sweep already ran
        await expire_stale_jobs()


def start_expiry_scheduler():
    """Start the background expiry task. Call from app startup."""
    asyncio.create_task(job_expiry_loop())
    logger.info(
        "Job expiry scheduler started (interval: %dh, default expiry: %dd, hard cap: %dd)",
        CHECK_INTERVAL_HOURS, DEFAULT_JOB_EXPIRY_DAYS, MAX_JOB_AGE_DAYS,
    )
