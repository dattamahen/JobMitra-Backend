"""
Contest Level Scheduler — automatically advances contest entries between levels
based on time gates derived from each entry's submission date.

Schedule:
  spark_confirmed      + 30 days → blueprint_open   (generates questionnaire via LLM)
  blueprint_evaluated  + 30 days → proof_open        (sends proof submission email)
  proof_evaluated      + 30 days → interview_scheduled (sends interview ready email)

Runs every CONTEST_SCHEDULER_INTERVAL_HOURS (default: 6).
"""

import asyncio
import json
import logging
import re
from datetime import datetime

from db import db
from email_service import email_service
from multi_llm_service import MultiLLMService
from prompt_manager import prompt_manager

logger = logging.getLogger(__name__)

COLLECTION = "project_contest_entries"
CHECK_INTERVAL_HOURS = 6

llm = MultiLLMService()


def _strip_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text).strip()
    return text


async def _resolve_recipients(entry: dict) -> list[dict]:
    """Build recipient list with registration status for all team members."""
    recipients = [{"name": entry["lead_name"], "email": entry["lead_email"], "is_registered": True}]
    for m in entry.get("team_members", []):
        email = m.get("email", "")
        if not email:
            continue
        user = await db.database["users"].find_one({"email": email}, {"_id": 0, "user_id": 1})
        recipients.append({
            "name": f"{m.get('first_name', '')} {m.get('last_name', '')}".strip() or "Team Member",
            "email": email,
            "is_registered": bool(user),
        })
    return recipients


# ── Transition handlers ───────────────────────────────────────

async def _open_blueprint(entry: dict) -> None:
    """Generate blueprint questionnaire and transition to blueprint_open."""
    entry_id = entry["entry_id"]
    try:
        raw_data = prompt_manager.get_raw("contest_level_prompts")
        l2 = raw_data.get("level2_blueprint_questionnaire", {})
        team_roles = ", ".join(
            [f"{entry['lead_name']} (Lead)"] +
            [
                f"{m.get('first_name', '')} {m.get('last_name', '')}".strip()
                + f" ({m.get('role_in_project', 'Member')})"
                for m in entry.get("team_members", [])
            ]
        )
        system_prompt = l2.get("system_prompt", "").format(
            refined_title=entry.get("refined_title", entry.get("raw_project_name")),
            refined_description=entry.get("refined_description", entry.get("raw_description")),
            inferred_domain=entry.get("inferred_domain", ""),
            inferred_problem_statement=entry.get("inferred_problem_statement", ""),
            inferred_target_users=entry.get("inferred_target_users", ""),
            category=entry.get("category", ""),
            tech_stack=", ".join(entry.get("tech_stack", [])) or "Not specified",
            team_size=entry.get("team_size", 1),
            team_roles=team_roles,
        )
        llm_response = await llm.generate(
            f"{system_prompt}\n\n{l2.get('output_instruction', 'Return JSON only.')}",
            model="gemini", temperature=0.6,
        )
        result = json.loads(_strip_json(llm_response.get("content", "{}")))
        questions = result.get("questions", [])
    except Exception as e:
        logger.warning("Scheduler: blueprint question generation failed for %s: %s", entry_id, e)
        return  # Don't advance if LLM fails — retry next cycle

    await db.database[COLLECTION].update_one(
        {"entry_id": entry_id},
        {"$set": {
            "blueprint_questions": questions,
            "status": "blueprint_open",
            "blueprint_opened_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }}
    )
    recipients = await _resolve_recipients(entry)
    await asyncio.to_thread(email_service.send_contest_blueprint_open, recipients, entry)
    logger.info("Scheduler: blueprint_open → %s", entry_id)


async def _open_proof(entry: dict) -> None:
    """Transition blueprint_evaluated (advanced) entry to proof_open."""
    entry_id = entry["entry_id"]
    await db.database[COLLECTION].update_one(
        {"entry_id": entry_id},
        {"$set": {
            "status": "proof_open",
            "proof_opened_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }}
    )
    recipients = await _resolve_recipients(entry)
    await asyncio.to_thread(email_service.send_contest_proof_open, recipients, entry)
    logger.info("Scheduler: proof_open → %s", entry_id)


async def _open_interview(entry: dict) -> None:
    """Transition proof_evaluated (advanced) entry to interview_scheduled."""
    entry_id = entry["entry_id"]
    await db.database[COLLECTION].update_one(
        {"entry_id": entry_id},
        {"$set": {
            "status": "interview_scheduled",
            "interview_scheduled_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }}
    )
    recipients = await _resolve_recipients(entry)
    # Send individual interview-ready emails to each participant
    for r in recipients:
        role = "Team Lead" if r["email"] == entry["lead_email"] else "Team Member"
        await asyncio.to_thread(email_service.send_contest_interview_scheduled, r, entry, role)
    logger.info("Scheduler: interview_scheduled → %s", entry_id)


# ── Main sweep ────────────────────────────────────────────────

async def run_contest_level_sweep() -> None:
    """Single sweep — find all entries due for a level transition and advance them."""
    if db.fallback_mode or db.database is None:
        return

    now = datetime.utcnow()
    col = db.database[COLLECTION]

    try:
        # 1. spark_confirmed → blueprint_open (blueprint_opens_at has passed)
        async for entry in col.find(
            {"status": "spark_confirmed", "blueprint_opens_at": {"$lte": now}},
            {"_id": 0}
        ):
            await _open_blueprint(entry)

        # 2. blueprint_evaluated (advanced, not eliminated) → proof_open
        async for entry in col.find(
            {
                "status": "blueprint_evaluated",
                "eliminated_at_level": {"$exists": False},
                "proof_opens_at": {"$lte": now},
            },
            {"_id": 0}
        ):
            await _open_proof(entry)

        # 3. proof_evaluated (advanced, not eliminated) → interview_scheduled
        async for entry in col.find(
            {
                "status": "proof_evaluated",
                "eliminated_at_level": {"$exists": False},
                "interview_opens_at": {"$lte": now},
            },
            {"_id": 0}
        ):
            await _open_interview(entry)

    except Exception as e:
        logger.error("Contest scheduler sweep error: %s", e)


async def _contest_scheduler_loop() -> None:
    """Background loop — runs sweep every CHECK_INTERVAL_HOURS."""
    while True:
        await asyncio.sleep(CHECK_INTERVAL_HOURS * 3600)
        await run_contest_level_sweep()


def start_contest_scheduler() -> None:
    """Start the contest level scheduler. Call from app lifespan startup."""
    loop = asyncio.get_event_loop()
    loop.create_task(_contest_scheduler_loop())
    logger.info("Contest level scheduler started (interval: %dh)", CHECK_INTERVAL_HOURS)
