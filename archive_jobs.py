"""
Job archival utility.
When a job becomes inactive for any reason (expired, closed, filled, deleted),
it is moved to the `archived_jobs` collection and hard-deleted from `jobs`.
All references in users.overall_jobs_applied are also purged.
"""

import logging
from datetime import datetime
from db import db

logger = logging.getLogger(__name__)


async def archive_job(job_id: str, reason: str, archived_by: str = "system") -> bool:
    """
    Move a job to archived_jobs, delete from jobs, and purge user references.
    Returns True if the job was found and archived, False if already gone.
    """
    try:
        job = await db.database["jobs"].find_one({"job_id": job_id})
        if not job:
            return False

        archive_doc = {
            "job_id": job_id,
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "posted_by_hr_id": job.get("posted_by_hr_id", ""),
            "posted_date": job.get("posted_date"),
            "archive_reason": reason,
            "archived_by": archived_by,
            "archived_at": datetime.utcnow(),
        }

        await db.database["archived_jobs"].insert_one(archive_doc)
        await db.database["jobs"].delete_one({"job_id": job_id})

        # Purge all user references to this job
        await db.database["users"].update_many(
            {"overall_jobs_applied.job_id": job_id},
            {"$pull": {"overall_jobs_applied": {"job_id": job_id}}}
        )

        logger.info("Archived job %s (reason: %s, by: %s)", job_id, reason, archived_by)
        return True

    except Exception as e:
        logger.error("Failed to archive job %s: %s", job_id, e)
        return False


async def archive_jobs_bulk(job_ids: list[str], reason: str, archived_by: str = "system") -> int:
    """Archive multiple jobs. Returns count of successfully archived jobs."""
    count = 0
    for job_id in job_ids:
        if await archive_job(job_id, reason, archived_by):
            count += 1
    return count
