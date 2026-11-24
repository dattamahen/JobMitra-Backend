"""
Database operations for the engagement email campaign system.
All eligibility queries use MongoDB aggregation with $lookup against
engagement_send_log to enforce per-user cooldowns.
"""
import logging
from datetime import datetime, timedelta
from typing import AsyncGenerator

from db import db

logger = logging.getLogger(__name__)

CAMPAIGN_CONFIG_COL = "engagement_campaign_config"
SEND_LOG_COL = "engagement_send_log"


class EngagementEmailDB:

    @property
    def _cfg(self):
        return db.database[CAMPAIGN_CONFIG_COL]

    @property
    def _log(self):
        return db.database[SEND_LOG_COL]

    async def get_all_configs(self) -> list[dict]:
        """Return all campaign config documents."""
        docs = []
        async for doc in self._cfg.find({}, {"_id": 0}):
            docs.append(doc)
        return docs

    async def get_config(self, campaign_id: str) -> dict | None:
        """Return a single campaign config document."""
        return await self._cfg.find_one({"campaign_id": campaign_id}, {"_id": 0})

    async def update_config(self, campaign_id: str, updates: dict) -> bool:
        """Partial update of a campaign config document."""
        result = await self._cfg.update_one(
            {"campaign_id": campaign_id},
            {"$set": updates}
        )
        return result.matched_count > 0

    async def mark_last_run(self, campaign_id: str, run_at: datetime) -> None:
        """Record the last run timestamp for a campaign."""
        await self._cfg.update_one(
            {"campaign_id": campaign_id},
            {"$set": {"last_run_at": run_at}}
        )

    async def log_send(self, campaign_id: str, user_id: str, email: str, status: str) -> None:
        """Insert a send log entry."""
        await self._log.insert_one({
            "campaign_id": campaign_id,
            "user_id": user_id,
            "email": email,
            "sent_at": datetime.utcnow(),
            "status": status,
        })

    async def get_logs(self, page: int = 1, per_page: int = 20) -> dict:
        """Return paginated send log entries, newest first."""
        skip = (page - 1) * per_page
        total = await self._log.count_documents({})
        docs = []
        async for doc in self._log.find({}, {"_id": 0}).sort("sent_at", -1).skip(skip).limit(per_page):
            docs.append(doc)
        return {
            "items": docs,
            "total_count": total,
            "page": page,
            "per_page": per_page,
            "total_pages": max(1, (total + per_page - 1) // per_page),
            "has_next": (skip + per_page) < total,
            "has_prev": page > 1,
        }

    # ── Eligibility queries ───────────────────────────────────────────

    async def get_eligible_profile_nudge_users(
        self, threshold_pct: int, cooldown_days: int
    ) -> AsyncGenerator[dict, None]:
        """
        Yield candidates whose profile_completion_count < threshold
        and have not received this campaign within cooldown_days.
        Projects only: user_id, email, first_name, profile_completion_count.
        """
        cutoff = datetime.utcnow() - timedelta(days=cooldown_days)
        pipeline = [
            {"$match": {
                "user_type": "candidate",
                "is_active": True,
                "profile_completion_count": {"$lt": threshold_pct},
            }},
            {"$lookup": {
                "from": SEND_LOG_COL,
                "let": {"uid": "$user_id"},
                "pipeline": [
                    {"$match": {"$expr": {
                        "$and": [
                            {"$eq": ["$user_id", "$$uid"]},
                            {"$eq": ["$campaign_id", "profile_nudge"]},
                            {"$gte": ["$sent_at", cutoff]},
                        ]
                    }}}
                ],
                "as": "recent_sends",
            }},
            {"$match": {"recent_sends": {"$size": 0}}},
            {"$project": {
                "_id": 0,
                "user_id": 1,
                "email": 1,
                "first_name": 1,
                "profile_completion_count": 1,
            }},
        ]
        async for doc in db.database["users"].aggregate(pipeline):
            yield doc

    async def get_eligible_mock_interview_nudge_users(
        self, inactive_days: int, cooldown_days: int
    ) -> AsyncGenerator[dict, None]:
        """
        Yield candidates with no mock interview session in the last inactive_days
        and not sent this campaign within cooldown_days.
        """
        cutoff = datetime.utcnow() - timedelta(days=cooldown_days)
        activity_cutoff = datetime.utcnow() - timedelta(days=inactive_days)
        pipeline = [
            {"$match": {"user_type": "candidate", "is_active": True}},
            {"$lookup": {
                "from": "mock_interview_sessions",
                "let": {"uid": "$user_id"},
                "pipeline": [
                    {"$match": {"$expr": {
                        "$and": [
                            {"$eq": ["$user_id", "$$uid"]},
                            {"$gte": ["$created_at", activity_cutoff]},
                        ]
                    }}}
                ],
                "as": "recent_interviews",
            }},
            {"$match": {"recent_interviews": {"$size": 0}}},
            {"$lookup": {
                "from": SEND_LOG_COL,
                "let": {"uid": "$user_id"},
                "pipeline": [
                    {"$match": {"$expr": {
                        "$and": [
                            {"$eq": ["$user_id", "$$uid"]},
                            {"$eq": ["$campaign_id", "mock_interview_nudge"]},
                            {"$gte": ["$sent_at", cutoff]},
                        ]
                    }}}
                ],
                "as": "recent_sends",
            }},
            {"$match": {"recent_sends": {"$size": 0}}},
            {"$project": {"_id": 0, "user_id": 1, "email": 1, "first_name": 1}},
        ]
        async for doc in db.database["users"].aggregate(pipeline):
            yield doc

    async def get_eligible_project_contest_users(
        self, max_exp_years: int, cooldown_days: int, campaign_id: str
    ) -> AsyncGenerator[dict, None]:
        """
        Yield freshers (experience_years == 0 OR is_fresher == true) with
        zero entries in project_contest_entries and not sent within cooldown_days.
        """
        cutoff = datetime.utcnow() - timedelta(days=cooldown_days)
        pipeline = [
            {"$match": {
                "user_type": "candidate",
                "is_active": True,
                "$or": [
                    {"overall_experience_years": {"$lte": max_exp_years}},
                    {"is_fresher": True},
                ],
            }},
            {"$lookup": {
                "from": "project_contest_entries",
                "let": {"uid": "$user_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$lead_user_id", "$$uid"]}}}
                ],
                "as": "contest_entries",
            }},
            {"$match": {"contest_entries": {"$size": 0}}},
            {"$lookup": {
                "from": SEND_LOG_COL,
                "let": {"uid": "$user_id"},
                "pipeline": [
                    {"$match": {"$expr": {
                        "$and": [
                            {"$eq": ["$user_id", "$$uid"]},
                            {"$eq": ["$campaign_id", campaign_id]},
                            {"$gte": ["$sent_at", cutoff]},
                        ]
                    }}}
                ],
                "as": "recent_sends",
            }},
            {"$match": {"recent_sends": {"$size": 0}}},
            {"$project": {"_id": 0, "user_id": 1, "email": 1, "first_name": 1}},
        ]
        async for doc in db.database["users"].aggregate(pipeline):
            yield doc

    async def get_eligible_job_digest_users(
        self, cooldown_days: int
    ) -> AsyncGenerator[dict, None]:
        """
        Yield all active candidates not sent job_digest within cooldown_days.
        Also returns recent jobs (last 7 days) for the digest body.
        """
        cutoff = datetime.utcnow() - timedelta(days=cooldown_days)
        pipeline = [
            {"$match": {"user_type": "candidate", "is_active": True}},
            {"$lookup": {
                "from": SEND_LOG_COL,
                "let": {"uid": "$user_id"},
                "pipeline": [
                    {"$match": {"$expr": {
                        "$and": [
                            {"$eq": ["$user_id", "$$uid"]},
                            {"$eq": ["$campaign_id", "job_digest"]},
                            {"$gte": ["$sent_at", cutoff]},
                        ]
                    }}}
                ],
                "as": "recent_sends",
            }},
            {"$match": {"recent_sends": {"$size": 0}}},
            {"$project": {"_id": 0, "user_id": 1, "email": 1, "first_name": 1}},
        ]
        async for doc in db.database["users"].aggregate(pipeline):
            yield doc

    async def get_recent_jobs(self, days: int = 7, limit: int = 5) -> list[dict]:
        """Return up to `limit` active jobs posted in the last `days` days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        jobs = []
        async for job in db.database["jobs"].find(
            {"is_active": True, "posted_date": {"$gte": cutoff}},
            {"_id": 0, "job_id": 1, "title": 1, "company": 1, "location": 1, "employment_type": 1},
        ).sort("posted_date", -1).limit(limit):
            jobs.append(job)
        return jobs

    async def seed_default_configs(self) -> None:
        """Insert default campaign configs if the collection is empty."""
        count = await self._cfg.count_documents({})
        if count > 0:
            return

        defaults = [
            {
                "campaign_id": "profile_nudge",
                "enabled": True,
                "day_of_week": 1,   # Tuesday
                "hour_utc": 17,
                "minute_utc": 30,
                "cooldown_days": 14,
                "description": "Weekly profile completion nudge — Tue 11 PM IST",
                "profile_completion_threshold": 80,
                "mock_interview_inactive_days": 30,
                "fresher_max_experience_years": 0,
                "last_run_at": None,
            },
            {
                "campaign_id": "mock_interview_nudge",
                "enabled": True,
                "day_of_week": 5,   # Saturday
                "hour_utc": 16,
                "minute_utc": 30,
                "cooldown_days": 14,
                "description": "Mock interview nudge — Sat 10 PM IST",
                "profile_completion_threshold": 80,
                "mock_interview_inactive_days": 30,
                "fresher_max_experience_years": 0,
                "last_run_at": None,
            },
            {
                "campaign_id": "project_contest_am",
                "enabled": True,
                "day_of_week": 4,   # Friday
                "hour_utc": 5,
                "minute_utc": 30,
                "cooldown_days": 7,
                "description": "Project contest nudge AM — Fri 11 AM IST",
                "profile_completion_threshold": 80,
                "mock_interview_inactive_days": 30,
                "fresher_max_experience_years": 0,
                "last_run_at": None,
            },
            {
                "campaign_id": "project_contest_pm",
                "enabled": True,
                "day_of_week": 4,   # Friday
                "hour_utc": 11,
                "minute_utc": 0,
                "cooldown_days": 7,
                "description": "Project contest nudge PM — Fri 4:30 PM IST",
                "profile_completion_threshold": 80,
                "mock_interview_inactive_days": 30,
                "fresher_max_experience_years": 0,
                "last_run_at": None,
            },
            {
                "campaign_id": "job_digest",
                "enabled": True,
                "day_of_week": 6,   # Sunday
                "hour_utc": 17,
                "minute_utc": 30,
                "cooldown_days": 7,
                "description": "Weekly job digest — Sun 11 PM IST",
                "profile_completion_threshold": 80,
                "mock_interview_inactive_days": 30,
                "fresher_max_experience_years": 0,
                "last_run_at": None,
            },
        ]
        await self._cfg.insert_many(defaults)
        logger.info("Seeded %d default engagement campaign configs", len(defaults))


engagement_email_db = EngagementEmailDB()
