"""
Engagement email campaign runner.
Dispatches to the correct eligibility query, sends emails in parallel batches,
logs results, and returns a CampaignRunReport.
"""
import asyncio
import logging
from datetime import datetime

from engagement_email_db import engagement_email_db
from engagement_email_schemas import CampaignRunReport
from email_service import email_service

logger = logging.getLogger(__name__)

_BATCH_SIZE = 20


async def _send_one(campaign_id: str, user: dict, send_fn, *args) -> str:
    """Send to one user via asyncio.to_thread. Returns 'sent' or 'failed'."""
    try:
        ok = await asyncio.to_thread(send_fn, user["email"], user["first_name"], *args)
        status = "sent" if ok else "failed"
    except Exception as e:
        logger.error("Engagement send error [%s] user=%s: %s", campaign_id, user.get("user_id"), e)
        status = "failed"
    await engagement_email_db.log_send(campaign_id, user["user_id"], user["email"], status)
    return status


async def _run_in_batches(campaign_id: str, users: list[dict], send_fn, *args) -> tuple[int, int]:
    """Send to all users in batches of _BATCH_SIZE. Returns (sent_count, failed_count)."""
    sent = failed = 0
    for i in range(0, len(users), _BATCH_SIZE):
        batch = users[i: i + _BATCH_SIZE]
        results = await asyncio.gather(
            *[_send_one(campaign_id, u, send_fn, *args) for u in batch],
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, Exception) or r == "failed":
                failed += 1
            else:
                sent += 1
    return sent, failed


# ── Per-campaign runners ──────────────────────────────────────────────

async def _run_profile_nudge(campaign_id: str, config: dict) -> CampaignRunReport:
    """Profile completion nudge campaign."""
    threshold = config.get("profile_completion_threshold", 80)
    cooldown = config.get("cooldown_days", 14)

    users = []
    async for u in engagement_email_db.get_eligible_profile_nudge_users(threshold, cooldown):
        users.append(u)

    eligible = len(users)
    sent = failed = 0
    for i in range(0, eligible, _BATCH_SIZE):
        batch = users[i: i + _BATCH_SIZE]
        tasks = []
        for u in batch:
            pct = u.get("profile_completion_count", 0)
            missing = _infer_missing_sections(u)
            tasks.append(_send_one(
                campaign_id, u,
                email_service.send_profile_nudge_email,
                pct, missing,
            ))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception) or r == "failed":
                failed += 1
            else:
                sent += 1

    return CampaignRunReport(
        campaign_id=campaign_id, run_at=datetime.utcnow(),
        eligible_count=eligible, sent_count=sent,
        skipped_count=0, failed_count=failed,
    )


def _infer_missing_sections(user: dict) -> list[str]:
    """Return list of missing profile section labels for a user."""
    missing = []
    if not user.get("skills"):
        missing.append("Skills")
    if not user.get("work_experience"):
        missing.append("Work experience")
    if not user.get("education"):
        missing.append("Education")
    if not user.get("professional_summary"):
        missing.append("Professional summary")
    if not user.get("phone"):
        missing.append("Phone number")
    return missing or ["Profile details"]


async def _run_mock_interview_nudge(campaign_id: str, config: dict) -> CampaignRunReport:
    """Mock interview inactivity nudge campaign."""
    inactive_days = config.get("mock_interview_inactive_days", 30)
    cooldown = config.get("cooldown_days", 14)

    users = []
    async for u in engagement_email_db.get_eligible_mock_interview_nudge_users(inactive_days, cooldown):
        users.append(u)

    sent, failed = await _run_in_batches(
        campaign_id, users,
        email_service.send_mock_interview_nudge_email,
        inactive_days,
    )
    return CampaignRunReport(
        campaign_id=campaign_id, run_at=datetime.utcnow(),
        eligible_count=len(users), sent_count=sent,
        skipped_count=0, failed_count=failed,
    )


async def _run_project_contest(campaign_id: str, config: dict) -> CampaignRunReport:
    """Project contest nudge campaign (AM and PM slots share same logic)."""
    max_exp = config.get("fresher_max_experience_years", 0)
    cooldown = config.get("cooldown_days", 7)

    users = []
    async for u in engagement_email_db.get_eligible_project_contest_users(max_exp, cooldown, campaign_id):
        users.append(u)

    sent, failed = await _run_in_batches(
        campaign_id, users,
        email_service.send_project_contest_nudge_email,
    )
    return CampaignRunReport(
        campaign_id=campaign_id, run_at=datetime.utcnow(),
        eligible_count=len(users), sent_count=sent,
        skipped_count=0, failed_count=failed,
    )


async def _run_job_digest(campaign_id: str, config: dict) -> CampaignRunReport:
    """Weekly job digest campaign."""
    cooldown = config.get("cooldown_days", 7)

    jobs = await engagement_email_db.get_recent_jobs(days=7, limit=5)
    if not jobs:
        logger.info("Job digest: no recent jobs found, skipping run")
        return CampaignRunReport(
            campaign_id=campaign_id, run_at=datetime.utcnow(),
            eligible_count=0, sent_count=0, skipped_count=0, failed_count=0,
        )

    users = []
    async for u in engagement_email_db.get_eligible_job_digest_users(cooldown):
        users.append(u)

    eligible = len(users)
    sent = failed = 0
    for i in range(0, eligible, _BATCH_SIZE):
        batch = users[i: i + _BATCH_SIZE]
        tasks = [
            _send_one(campaign_id, u, email_service.send_job_digest_email, jobs)
            for u in batch
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception) or r == "failed":
                failed += 1
            else:
                sent += 1

    return CampaignRunReport(
        campaign_id=campaign_id, run_at=datetime.utcnow(),
        eligible_count=eligible, sent_count=sent,
        skipped_count=0, failed_count=failed,
    )


# ── Dispatch map ──────────────────────────────────────────────────────

CAMPAIGN_RUNNERS = {
    "profile_nudge": _run_profile_nudge,
    "mock_interview_nudge": _run_mock_interview_nudge,
    "project_contest_am": _run_project_contest,
    "project_contest_pm": _run_project_contest,
    "job_digest": _run_job_digest,
}


async def run_campaign(campaign_id: str, config: dict) -> CampaignRunReport:
    """
    Run a single campaign by ID. Dispatches to the correct runner,
    logs results, and sends admin report.
    """
    runner = CAMPAIGN_RUNNERS.get(campaign_id)
    if not runner:
        logger.warning("No runner registered for campaign_id: %s", campaign_id)
        return CampaignRunReport(
            campaign_id=campaign_id, run_at=datetime.utcnow(),
            eligible_count=0, sent_count=0, skipped_count=0, failed_count=0,
        )

    logger.info("Engagement campaign starting: %s", campaign_id)
    try:
        report = await runner(campaign_id, config)
    except Exception as e:
        logger.error("Campaign runner failed [%s]: %s", campaign_id, e)
        report = CampaignRunReport(
            campaign_id=campaign_id, run_at=datetime.utcnow(),
            eligible_count=0, sent_count=0, skipped_count=0, failed_count=0,
        )

    logger.info(
        "Campaign %s done — eligible=%d sent=%d failed=%d",
        campaign_id, report.eligible_count, report.sent_count, report.failed_count,
    )

    try:
        await asyncio.to_thread(
            email_service.send_engagement_campaign_report,
            [report.model_dump()],
        )
    except Exception as e:
        logger.warning("Admin report send failed for %s: %s", campaign_id, e)

    return report
