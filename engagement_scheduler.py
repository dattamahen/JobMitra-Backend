"""
Engagement email scheduler.
Runs an hourly loop, checks each campaign's day_of_week + hour_utc + minute_utc
against current UTC time, and fires campaigns that are due.
"""
import asyncio
import logging
from datetime import datetime, timedelta

from config import settings

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 3600  # 1 hour


def _is_due(config: dict, now: datetime) -> bool:
    """Return True if this campaign should fire in the current hour window."""
    if not config.get("enabled", False):
        return False
    if now.weekday() != config["day_of_week"]:
        return False
    if now.hour != config["hour_utc"]:
        return False
    # Check last_run_at — skip if already run within this hour window
    last_run = config.get("last_run_at")
    if last_run:
        window_start = now.replace(minute=0, second=0, microsecond=0)
        if last_run >= window_start:
            return False
    return True


async def _run_due_campaigns() -> None:
    """Load all configs and fire any campaigns due right now."""
    if not settings.ENGAGEMENT_CAMPAIGNS_ENABLED:
        logger.debug("Engagement campaigns disabled (ENGAGEMENT_CAMPAIGNS_ENABLED=false)")
        return

    from db import db
    if db.fallback_mode or db.database is None:
        return

    from engagement_email_db import engagement_email_db
    from engagement_email_runner import run_campaign

    now = datetime.utcnow()
    configs = await engagement_email_db.get_all_configs()

    for config in configs:
        campaign_id = config["campaign_id"]
        if not _is_due(config, now):
            continue
        logger.info("Engagement scheduler: firing campaign %s", campaign_id)
        try:
            await run_campaign(campaign_id, config)
            await engagement_email_db.mark_last_run(campaign_id, now)
        except Exception as e:
            logger.error("Engagement scheduler error for %s: %s", campaign_id, e)


async def _engagement_scheduler_loop() -> None:
    """Background loop — checks every hour."""
    while True:
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
        await _run_due_campaigns()


def start_engagement_scheduler() -> None:
    """Start the engagement email scheduler. Call from app lifespan startup."""
    loop = asyncio.get_event_loop()
    loop.create_task(_engagement_scheduler_loop())
    logger.info("Engagement email scheduler started (interval: 1h)")
