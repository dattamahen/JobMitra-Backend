"""
Project Contest Endpoints — 5-level AI-driven contest lifecycle.
Router prefix: /api/v1/project-contest
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from activity_tracker import log_user_activity
from auth_endpoints import get_current_user
from email_service import email_service
from multi_llm_service import MultiLLMService
from project_contest_db import contest_db
from project_contest_schemas import (
    ALL_CATEGORIES,
    CONTEST_SUBSCRIPTION_BENEFITS,
    NON_TECHNICAL_CATEGORIES,
    PRICING,
    SCORE_THRESHOLDS,
    TECHNICAL_CATEGORIES,
    BlueprintSubmitRequest,
    ContestPaymentConfirm,
    InterviewAnswerRequest,
    ProofSubmitRequest,
    SparkConfirmRequest,
    SparkSubmitRequest,
)
from prompt_manager import prompt_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/project-contest", tags=["Project Contest"])

llm = MultiLLMService()
GMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@gmail\.com$")

_CONTEST_BLOCKED_RE = re.compile(
    r"\bsex\b|\bporn\b|\bescort\b|\bprostitut|\bterror|\bbomb\b|\bweapon\b"
    r"|\btheft\b|\bsteal\b|\bdrug\b|\bnarco|\bhack\b|\bphish"
    r"|\bkill\b|\bmurder\b|\bjihad\b|\bnaxal|\bsediti"
    r"|\bfuck\b|\bshit\b|\bbitch\b|\basshole\b|\bchutiya\b|\bmadarchod\b|\bbenchod\b",
    re.IGNORECASE
)


async def _check_contest_content(name: str, description: str, tech_stack: list[str]) -> None:
    """Regex pre-check + LLM moderation. Raises 422 if content is objectionable."""
    combined = f"{name} {description} {' '.join(tech_stack)}"
    if _CONTEST_BLOCKED_RE.search(combined):
        raise HTTPException(
            status_code=422,
            detail="Project content contains restricted words or topics. Please revise and resubmit."
        )
    try:
        mod_variant = prompt_manager.get_random("contest_moderation")
        prompt = (
            mod_variant["system_prompt"]
            + f"\n\nProject Name: {name}"
            + f"\nDescription: {description[:500]}"
            + f"\nTech Stack: {', '.join(tech_stack)}"
        )
        res = await llm.generate(prompt, model="gemini", temperature=0.0)
        result = json.loads(_strip_json(res.get("content", "{}")))
        if not result.get("safe", True):
            raise HTTPException(
                status_code=422,
                detail=result.get("reason", "Project content violates community guidelines.")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Contest moderation LLM failed, regex passed: %s", e)


# ── Helpers ──────────────────────────────────────────────────

def _strip_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text).strip()
    return text


def _build_recipients(entry: dict) -> list[dict]:
    """Build recipient list: lead + all team members with name/email/is_registered flag."""
    recipients = [{"name": entry["lead_name"], "email": entry["lead_email"], "is_registered": True}]
    for m in entry.get("team_members", []):
        recipients.append({
            "name": m.get("full_name", "Team Member"),
            "email": m.get("email", ""),
            "is_registered": m.get("is_registered", False),
        })
    return [r for r in recipients if r["email"]]


async def _resolve_member_registration(entry: dict) -> list[dict]:
    """Check which team members have accounts and return enriched recipient list."""
    from db import db
    recipients = [{"name": entry["lead_name"], "email": entry["lead_email"], "is_registered": True}]
    for m in entry.get("team_members", []):
        email = m.get("email", "")
        if not email:
            continue
        user = await db.database["users"].find_one({"email": email}, {"_id": 0, "user_id": 1})
        recipients.append({
            "name": m.get("full_name", "Team Member"),
            "email": email,
            "is_registered": bool(user),
        })
    return recipients


def _serialize_entry(entry: dict) -> dict:
    entry.pop("_id", None)
    for k, v in entry.items():
        if isinstance(v, datetime):
            entry[k] = v.isoformat() + "Z"
    return entry


# ── Public endpoints ─────────────────────────────────────────

@router.get("/categories")
async def get_categories():
    """Return all available project categories."""
    return {"technical": TECHNICAL_CATEGORIES, "non_technical": NON_TECHNICAL_CATEGORIES}


@router.get("/pricing")
async def get_pricing():
    """Return pricing tiers, subscription benefits, and Razorpay payment link."""
    from credits_endpoints import _get_paid_plan
    plan = await _get_paid_plan()
    return {
        "solo": {"members": 1, "amount": PRICING["solo"], "currency": PRICING["currency"]},
        "team": {"members": "2-4", "amount": PRICING["team"], "currency": PRICING["currency"]},
        "benefits": CONTEST_SUBSCRIPTION_BENEFITS,
        "payment_link": plan.get("payment_link", ""),
    }


@router.get("/leaderboard")
async def get_leaderboard(limit: int = Query(20, le=50)):
    """Public finalist leaderboard ordered by composite score."""
    from db import db
    cursor = db.database["project_contest_entries"].find(
        {"status": {"$in": ["finalist", "winner"]}},
        {"_id": 0, "entry_id": 1, "refined_title": 1, "raw_project_name": 1,
         "category": 1, "team_size": 1, "composite_score": 1, "status": 1}
    ).sort("composite_score", -1).limit(limit)
    entries = await cursor.to_list(length=limit)
    return {"entries": entries, "count": len(entries)}


@router.get("/my-entries")
async def get_my_entries(current_user: dict = Depends(get_current_user)):
    """Get all contest entries for the authenticated user."""
    entries = await contest_db.get_user_entries(current_user["user_id"])
    return {"success": True, "data": {"entries": entries, "count": len(entries)}}


@router.get("/entry/{entry_id}")
async def get_entry(entry_id: str, current_user: dict = Depends(get_current_user)):
    """Get a single contest entry detail."""
    entry = await contest_db.get_participant_entry(entry_id, current_user["user_id"])
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found.")
    return {"success": True, "data": _serialize_entry(entry)}


# ── Level 1 — Spark ─────────────────────────────────────────

@router.post("/submit")
async def submit_spark(req: SparkSubmitRequest, current_user: dict = Depends(get_current_user)):
    """Level 1: Submit raw project idea. LLM refines it and returns for confirmation."""
    try:
        if req.category not in ALL_CATEGORIES:
            raise HTTPException(status_code=400, detail="Invalid category.")
        if len(req.team_members) > 3:
            raise HTTPException(status_code=400, detail="Maximum 4 team members including lead.")

        await _check_contest_content(req.raw_project_name, req.raw_description, req.tech_stack)


        lead_email = current_user.get("email", "")
        for m in req.team_members:
            if not GMAIL_REGEX.match(m.email):
                raise HTTPException(status_code=400, detail=f"Team member email must be Gmail: {m.email}")
            if m.email == lead_email:
                raise HTTPException(status_code=400, detail="Team member email cannot match lead email.")

        team_size = 1 + len(req.team_members)
        tier, amount = contest_db.determine_pricing(team_size)
        entry_id = contest_db.generate_entry_id()
        lead_name = f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip()

        raw_data = prompt_manager.get_raw("contest_level_prompts")
        l1 = raw_data.get("level1_idea_refinement", {})
        system_prompt = l1.get("system_prompt", "").format(
            project_name=req.raw_project_name,
            raw_description=req.raw_description,
            category=req.category,
            tech_stack=", ".join(req.tech_stack) if req.tech_stack else "Not specified",
            team_size=team_size,
        )
        try:
            llm_response = await llm.generate(
                f"{system_prompt}\n\n{l1.get('output_instruction', 'Return JSON only.')}",
                model="gemini", temperature=0.5,
            )
            refined = json.loads(_strip_json(llm_response.get("content", "{}")))
        except Exception as e:
            logger.warning("LLM idea refinement failed, using fallback: %s", e)
            refined = {
                "refined_title": req.raw_project_name,
                "refined_description": req.raw_description,
                "inferred_domain": req.category.replace("_", " ").title(),
                "inferred_problem_statement": req.raw_description[:200],
                "inferred_target_users": "General users",
                "idea_quality_score": 65,
                "clarity_issues": [],
                "confirmation_message": f"We understood your project as: {req.raw_project_name}. Does this accurately represent your project?",
            }

        entry = {
            "entry_id": entry_id,
            "lead_user_id": current_user["user_id"],
            "lead_email": lead_email,
            "lead_name": lead_name,
            "raw_project_name": req.raw_project_name,
            "raw_description": req.raw_description,
            "refined_title": refined.get("refined_title", req.raw_project_name),
            "refined_description": refined.get("refined_description", req.raw_description),
            "inferred_domain": refined.get("inferred_domain", ""),
            "inferred_problem_statement": refined.get("inferred_problem_statement", ""),
            "inferred_target_users": refined.get("inferred_target_users", ""),
            "idea_quality_score": refined.get("idea_quality_score", 0),
            "project_type": req.project_type,
            "category": req.category,
            "tech_stack": req.tech_stack,
            "team_size": team_size,
            "team_members": [m.model_dump() for m in req.team_members],
            "college_name": req.college_name,
            "graduation_year": req.graduation_year,
            "pricing_tier": tier,
            "amount_paid": 0,
            "payment_status": "pending",
            "subscription_granted": False,
            "subscription_benefits": {},
            "status": "spark_submitted",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await contest_db.create_entry(entry)

        # Send invite emails to team members immediately after submission
        if req.team_members:
            team_recipients = []
            for m in req.team_members:
                from db import db as _db
                existing = await _db.database["users"].find_one({"email": m.email}, {"_id": 0, "user_id": 1})
                team_recipients.append({
                    "name": m.full_name,
                    "email": m.email,
                    "is_registered": bool(existing),
                })
            await asyncio.to_thread(email_service.send_contest_team_invites, team_recipients, entry)

        return {
            "success": True,
            "message": "Project idea received and refined by AI.",
            "data": {
                "entry_id": entry_id,
                "refined_title": entry["refined_title"],
                "refined_description": entry["refined_description"],
                "inferred_domain": entry["inferred_domain"],
                "inferred_problem_statement": entry["inferred_problem_statement"],
                "inferred_target_users": entry["inferred_target_users"],
                "idea_quality_score": entry["idea_quality_score"],
                "confirmation_message": refined.get("confirmation_message", "Does this accurately represent your project?"),
                "clarity_issues": refined.get("clarity_issues", []),
                "pricing_tier": tier,
                "amount": amount,
                "currency": PRICING["currency"],
                "team_size": team_size,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error submitting spark: %s", e)
        raise HTTPException(status_code=500, detail="Failed to submit project")


@router.post("/confirm-idea")
async def confirm_idea(req: SparkConfirmRequest, current_user: dict = Depends(get_current_user)):
    """Level 1: Team confirms the LLM-refined idea. Returns payment details."""
    try:
        entry = await contest_db.get_by_id_and_lead(req.entry_id, current_user["user_id"])
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found.")
        if entry.get("status") != "spark_submitted":
            raise HTTPException(status_code=400, detail="Entry is not awaiting confirmation.")
        if not req.confirmed:
            raise HTTPException(status_code=400, detail="Confirmation declined. Please resubmit with corrections.")

        idea_score = entry.get("idea_quality_score", 0)
        if idea_score < SCORE_THRESHOLDS["idea_quality"]:
            raise HTTPException(
                status_code=422,
                detail=f"Idea quality score {idea_score}/100 is below the minimum {SCORE_THRESHOLDS['idea_quality']}. Please refine your idea."
            )

        _, amount = contest_db.determine_pricing(entry["team_size"])
        return {
            "success": True,
            "message": "Idea confirmed. Please complete payment to activate your entry.",
            "data": {"entry_id": req.entry_id, "amount": amount, "currency": PRICING["currency"], "pricing_tier": entry["pricing_tier"]},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error confirming idea: %s", e)
        raise HTTPException(status_code=500, detail="Failed to confirm idea")


@router.post("/payment/confirm")
async def confirm_payment(req: ContestPaymentConfirm, current_user: dict = Depends(get_current_user)):
    """Level 1: Confirm payment. Grants subscription to all members. Sends emails."""
    try:
        entry = await contest_db.get_by_id_and_lead(req.entry_id, current_user["user_id"])
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found.")
        if entry.get("payment_status") == "confirmed":
            raise HTTPException(status_code=400, detail="Payment already confirmed.")

        _, expected = contest_db.determine_pricing(entry["team_size"])
        if req.amount != expected:
            raise HTTPException(status_code=400, detail=f"Amount must be {int(expected)}.")

        benefits = CONTEST_SUBSCRIPTION_BENEFITS.copy()
        await contest_db.grant_subscription(current_user["user_id"], benefits)
        for m in entry.get("team_members", []):
            if m.get("email"):
                await contest_db.grant_subscription_by_email(m["email"], benefits)

        await contest_db.confirm_payment(req.entry_id, req.upi_transaction_id, req.amount, benefits)
        await contest_db.confirm_spark(req.entry_id, await contest_db.get_by_id(req.entry_id) or {})
        await contest_db.set_fields(req.entry_id, {"status": "spark_confirmed"})

        from db import db
        await db.database["payments"].insert_one({
            "user_id": current_user["user_id"], "type": "project_contest",
            "entry_id": req.entry_id, "upi_transaction_id": req.upi_transaction_id,
            "amount": req.amount, "currency": PRICING["currency"],
            "status": "confirmed", "timestamp": datetime.utcnow().isoformat() + "Z",
        })

        updated = await contest_db.get_by_id(req.entry_id)
        recipients = await _resolve_member_registration(updated)
        await asyncio.to_thread(email_service.send_contest_spark_confirmed, recipients, updated)

        await log_user_activity(
            current_user["user_id"], "project_contest",
            f"Payment confirmed: {updated.get('refined_title', updated.get('raw_project_name'))}",
            {"entry_id": req.entry_id}
        )
        return {"success": True, "message": "Payment confirmed. Entry is live!", "data": {"benefits": benefits}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error confirming payment: %s", e)
        raise HTTPException(status_code=500, detail="Failed to confirm payment")


# ── Level 2 — Blueprint ──────────────────────────────────────

@router.post("/entry/{entry_id}/blueprint/generate")
async def generate_blueprint_questions(entry_id: str, current_user: dict = Depends(get_current_user)):
    """Level 2: Generate custom questionnaire for the entry. Called when blueprint_open."""
    try:
        entry = await contest_db.get_by_id_and_lead(entry_id, current_user["user_id"])
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found.")
        if entry.get("status") not in ("spark_confirmed", "blueprint_open"):
            raise HTTPException(status_code=400, detail="Entry is not ready for blueprint.")

        raw_data = prompt_manager.get_raw("contest_level_prompts")
        l2 = raw_data.get("level2_blueprint_questionnaire", {})
        team_roles = ", ".join(
            [f"{entry['lead_name']} (Lead)"] +
            [f"{m.get('full_name', 'Member')} ({m.get('role_in_project', 'Member')})" for m in entry.get("team_members", [])]
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
        try:
            llm_response = await llm.generate(
                f"{system_prompt}\n\n{l2.get('output_instruction', 'Return JSON only.')}",
                model="gemini", temperature=0.6,
            )
            result = json.loads(_strip_json(llm_response.get("content", "{}")))
            questions = result.get("questions", [])
        except Exception as e:
            logger.warning("LLM blueprint generation failed: %s", e)
            raise HTTPException(status_code=500, detail="Failed to generate questionnaire. Please try again.")

        await contest_db.store_blueprint_questions(entry_id, questions)

        recipients = await _resolve_member_registration(entry)
        await asyncio.to_thread(email_service.send_contest_blueprint_open, recipients, entry)

        return {
            "success": True,
            "message": "Blueprint questionnaire generated.",
            "data": {
                "questionnaire_title": result.get("questionnaire_title", "Blueprint Questionnaire"),
                "instructions_for_team": result.get("instructions_for_team", ""),
                "questions": questions,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error generating blueprint: %s", e)
        raise HTTPException(status_code=500, detail="Failed to generate blueprint")


@router.get("/entry/{entry_id}/blueprint/questions")
async def get_blueprint_questions(entry_id: str, current_user: dict = Depends(get_current_user)):
    """Level 2: Get the generated questionnaire for an entry."""
    entry = await contest_db.get_participant_entry(entry_id, current_user["user_id"])
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found.")
    return {"success": True, "data": {"questions": entry.get("blueprint_questions", [])}}


@router.post("/entry/{entry_id}/blueprint/submit")
async def submit_blueprint(entry_id: str, req: BlueprintSubmitRequest, current_user: dict = Depends(get_current_user)):
    """Level 2: Submit answers to the blueprint questionnaire."""
    try:
        entry = await contest_db.get_by_id_and_lead(entry_id, current_user["user_id"])
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found.")
        if entry.get("status") != "blueprint_open":
            raise HTTPException(status_code=400, detail="Blueprint is not open for submission.")

        answers = [a.model_dump() for a in req.answers]
        await contest_db.submit_blueprint(entry_id, answers)

        # Evaluate immediately
        raw_data = prompt_manager.get_raw("contest_level_prompts")
        l2e = raw_data.get("level2_blueprint_evaluation", {})
        questions = entry.get("blueprint_questions", [])
        qa_pairs = [
            {"question": next((q["question"] for q in questions if q["question_number"] == a["question_number"]), ""),
             "section": next((q["section"] for q in questions if q["question_number"] == a["question_number"]), ""),
             "answer": a["answer"]}
            for a in answers
        ]
        system_prompt = l2e.get("system_prompt", "").format(
            project_name=entry.get("refined_title", entry.get("raw_project_name")),
            domain=entry.get("inferred_domain", ""),
            category=entry.get("category", ""),
            tech_stack=", ".join(entry.get("tech_stack", [])),
            blueprint_qa_pairs=json.dumps(qa_pairs, indent=2),
        )
        try:
            llm_response = await llm.generate(
                f"{system_prompt}\n\n{l2e.get('output_instruction', 'Return JSON only.')}",
                model="gemini", temperature=0.3,
            )
            eval_result = json.loads(_strip_json(llm_response.get("content", "{}")))
        except Exception as e:
            logger.warning("LLM blueprint evaluation failed: %s", e)
            eval_result = {"blueprint_score": 70, "advancement_decision": "advance", "feedback_summary": "Evaluation unavailable. Entry advanced by default.", "dimension_scores": {}}

        advance = eval_result.get("advancement_decision") == "advance"
        score = eval_result.get("blueprint_score", 0)
        feedback = eval_result.get("feedback_summary", "")

        await contest_db.store_blueprint_evaluation(entry_id, eval_result, advance)

        updated = await contest_db.get_by_id(entry_id)
        recipients = await _resolve_member_registration(updated)
        await asyncio.to_thread(
            email_service.send_contest_blueprint_result, recipients, updated, score, feedback, advance
        )
        if not advance:
            await asyncio.to_thread(
                email_service.send_contest_eliminated, recipients, updated,
                "Level 2 — Blueprint", score, SCORE_THRESHOLDS["blueprint"], feedback
            )

        return {
            "success": True,
            "message": "Blueprint submitted and evaluated.",
            "data": {"blueprint_score": score, "advanced": advance, "feedback": feedback},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error submitting blueprint: %s", e)
        raise HTTPException(status_code=500, detail="Failed to submit blueprint")


# ── Level 3 — Proof ──────────────────────────────────────────

@router.post("/entry/{entry_id}/proof/submit")
async def submit_proof(entry_id: str, req: ProofSubmitRequest, current_user: dict = Depends(get_current_user)):
    """Level 3: Submit YouTube demo, GitHub URL, and optional live demo URL."""
    try:
        entry = await contest_db.get_by_id_and_lead(entry_id, current_user["user_id"])
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found.")
        if entry.get("status") != "proof_open":
            raise HTTPException(status_code=400, detail="Proof submission is not open.")

        await contest_db.submit_proof(entry_id, req.youtube_url, req.github_url, req.demo_url)

        # Extract YouTube metadata from URL
        yt_title, yt_desc, yt_duration = "", "", 0
        yt_match = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", req.youtube_url)
        yt_video_id = yt_match.group(1) if yt_match else ""

        # Extract GitHub repo name
        gh_match = re.search(r"github\.com/[^/]+/([^/]+)", req.github_url)
        gh_repo_name = gh_match.group(1) if gh_match else req.github_url

        raw_data = prompt_manager.get_raw("contest_level_prompts")
        l3 = raw_data.get("level3_demo_evaluation", {})
        system_prompt = l3.get("system_prompt", "").format(
            project_name=entry.get("refined_title", entry.get("raw_project_name")),
            domain=entry.get("inferred_domain", ""),
            category=entry.get("category", ""),
            tech_stack=", ".join(entry.get("tech_stack", [])),
            blueprint_score=entry.get("blueprint_score", 0),
            blueprint_summary=entry.get("blueprint_feedback", ""),
            youtube_title=yt_title or req.youtube_url,
            youtube_description=yt_desc,
            youtube_duration_seconds=yt_duration,
            github_repo_name=gh_repo_name,
            github_readme_excerpt="",
            github_commit_count=0,
            github_last_commit_date="Unknown",
            demo_url=req.demo_url or "Not provided",
        )
        try:
            llm_response = await llm.generate(
                f"{system_prompt}\n\n{l3.get('output_instruction', 'Return JSON only.')}",
                model="gemini", temperature=0.3,
            )
            eval_result = json.loads(_strip_json(llm_response.get("content", "{}")))
        except Exception as e:
            logger.warning("LLM proof evaluation failed: %s", e)
            eval_result = {"demo_score": 72, "advancement_decision": "advance", "feedback_summary": "Evaluation unavailable. Entry advanced by default.", "dimension_scores": {}, "demo_red_flags": []}

        advance = eval_result.get("advancement_decision") == "advance"
        score = eval_result.get("demo_score", 0)
        feedback = eval_result.get("feedback_summary", "")

        await contest_db.store_proof_evaluation(entry_id, eval_result, advance)

        updated = await contest_db.get_by_id(entry_id)
        recipients = await _resolve_member_registration(updated)
        await asyncio.to_thread(
            email_service.send_contest_proof_result, recipients, updated, score, feedback, advance
        )
        if not advance:
            await asyncio.to_thread(
                email_service.send_contest_eliminated, recipients, updated,
                "Level 3 — Proof", score, SCORE_THRESHOLDS["demo"], feedback
            )

        return {
            "success": True,
            "message": "Demo submitted and evaluated.",
            "data": {"demo_score": score, "advanced": advance, "feedback": feedback},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error submitting proof: %s", e)
        raise HTTPException(status_code=500, detail="Failed to submit proof")


# ── Level 4 — Interview ───────────────────────────────────────

@router.post("/entry/{entry_id}/interview/start")
async def start_interview(entry_id: str, current_user: dict = Depends(get_current_user)):
    """Level 4: Start the AI interview for the current participant."""
    try:
        entry = await contest_db.get_participant_entry(entry_id, current_user["user_id"])
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found.")
        if entry.get("status") not in ("interview_scheduled", "interview_in_progress"):
            raise HTTPException(status_code=400, detail="Interview is not open.")

        # Check if this participant already has a session
        sessions = entry.get("interview_sessions", [])
        existing = next((s for s in sessions if s["participant_user_id"] == current_user["user_id"]), None)
        if existing:
            return {"success": True, "message": "Interview already started.", "data": {"current_round": len(existing["rounds"]), "session": existing}}

        # Determine participant role
        participant_role = "Team Lead" if entry["lead_user_id"] == current_user["user_id"] else next(
            (m.get("role_in_project", "Team Member") for m in entry.get("team_members", []) if m.get("user_id") == current_user["user_id"]),
            "Team Member"
        )

        # Generate Round 1 questions
        raw_data = prompt_manager.get_raw("contest_interview_questions")
        rounds_config = raw_data.get("rounds", [])
        r1_config = next((r for r in rounds_config if r["round"] == 1), {})
        system_prompt = r1_config.get("system_prompt", "").format(
            project_name=entry.get("refined_title", entry.get("raw_project_name")),
            project_description=entry.get("refined_description", entry.get("raw_description")),
            category=entry.get("category", ""),
            tech_stack=", ".join(entry.get("tech_stack", [])),
            participant_role=participant_role,
            team_size=entry.get("team_size", 1),
        )
        try:
            llm_response = await llm.generate(
                f"{system_prompt}\n\n{raw_data.get('output_instruction', 'Return JSON only.')}",
                model="gemini", temperature=0.7,
            )
            r1_result = json.loads(_strip_json(llm_response.get("content", "{}")))
            questions = r1_result.get("questions", [])
        except Exception as e:
            logger.warning("LLM round 1 question generation failed: %s", e)
            raise HTTPException(status_code=500, detail="Failed to generate interview questions. Please try again.")

        await contest_db.init_interview_session(entry_id, current_user["user_id"], participant_role, questions)

        # Send interview scheduled email to this participant
        recipient = {"name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip(), "email": current_user.get("email", "")}
        await asyncio.to_thread(email_service.send_contest_interview_scheduled, recipient, entry, participant_role)

        return {
            "success": True,
            "message": "Interview started. Round 1 questions ready.",
            "data": {"round": 1, "round_name": "Conceptual Depth", "questions": questions},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error starting interview: %s", e)
        raise HTTPException(status_code=500, detail="Failed to start interview")


@router.post("/entry/{entry_id}/interview/answer")
async def submit_answer(entry_id: str, req: InterviewAnswerRequest, current_user: dict = Depends(get_current_user)):
    """Level 4: Submit one answer. Returns per-answer evaluation and next question if available."""
    try:
        if req.participant_user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied.")

        entry = await contest_db.get_participant_entry(entry_id, current_user["user_id"])
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found.")

        sessions = entry.get("interview_sessions", [])
        session = next((s for s in sessions if s["participant_user_id"] == current_user["user_id"]), None)
        if not session:
            raise HTTPException(status_code=400, detail="Interview session not found. Call /start first.")

        rounds = session.get("rounds", [])
        current_round = next((r for r in rounds if r["round_number"] == req.round_number), None)
        if not current_round:
            raise HTTPException(status_code=400, detail=f"Round {req.round_number} not found.")

        questions = current_round.get("questions", [])
        question = next((q for q in questions if q["id"] == req.question_id), None)
        if not question:
            raise HTTPException(status_code=400, detail=f"Question {req.question_id} not found.")

        # Evaluate the answer
        raw_data = prompt_manager.get_raw("contest_interview_evaluation")
        eval_variant = next((v for v in raw_data.get("variants", []) if v["id"] == "contest_eval_per_answer"), {})
        system_prompt = eval_variant.get("system_prompt", "").format(
            project_name=entry.get("refined_title", entry.get("raw_project_name")),
            category=entry.get("category", ""),
            tech_stack=", ".join(entry.get("tech_stack", [])),
            participant_role=session.get("participant_role", "Team Member"),
            round_number=req.round_number,
            round_name=current_round.get("round_name", ""),
            question=question.get("question", ""),
            question_intent=question.get("intent", ""),
            expected_depth=question.get("expected_depth", ""),
            answer=req.answer,
        )
        try:
            llm_response = await llm.generate(
                f"{system_prompt}\n\n{raw_data.get('output_instruction', 'Return JSON only.')}",
                model="gemini", temperature=0.3,
            )
            evaluation = json.loads(_strip_json(llm_response.get("content", "{}")))
        except Exception as e:
            logger.warning("LLM answer evaluation failed: %s", e)
            evaluation = {"score": 60, "depth_signal": "partial_understanding", "what_was_strong": "", "what_was_missing": "", "follow_up_signal": "", "red_flags": None}

        await contest_db.store_answer_evaluation(
            entry_id, current_user["user_id"], req.round_number, req.question_id, req.answer, evaluation
        )

        # Check if round is complete (all 8 answers submitted)
        existing_answers = len(current_round.get("answers", [])) + 1
        round_complete = existing_answers >= 8
        response_data: dict = {"evaluation": evaluation, "round_complete": round_complete}

        if round_complete:
            # Generate round summary
            await _finalize_round(entry_id, current_user["user_id"], req.round_number, entry, session)

            if req.round_number < 3:
                # Generate next round questions
                next_questions = await _generate_round_questions(
                    req.round_number + 1, entry, session.get("participant_role", "Team Member"), entry
                )
                response_data["next_round"] = req.round_number + 1
                response_data["next_questions"] = next_questions
            else:
                # All 3 rounds done — compute final participant score
                await _finalize_participant(entry_id, current_user["user_id"], entry)
                # Check if all participants are done
                await _check_all_interviews_complete(entry_id, entry)
                response_data["interview_complete"] = True

        return {"success": True, "message": "Answer submitted.", "data": response_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error submitting answer: %s", e)
        raise HTTPException(status_code=500, detail="Failed to submit answer")


# ── Interview internal helpers ─────────────────────────────────

async def _generate_round_questions(round_number: int, entry: dict, participant_role: str, _entry: dict) -> list:
    """Generate questions for a given round number."""
    raw_data = prompt_manager.get_raw("contest_interview_questions")
    rounds_config = raw_data.get("rounds", [])
    r_config = next((r for r in rounds_config if r["round"] == round_number), {})
    system_prompt = r_config.get("system_prompt", "").format(
        project_name=entry.get("refined_title", entry.get("raw_project_name")),
        project_description=entry.get("refined_description", entry.get("raw_description")),
        category=entry.get("category", ""),
        tech_stack=", ".join(entry.get("tech_stack", [])),
        participant_role=participant_role,
        team_size=entry.get("team_size", 1),
        blueprint_summary=entry.get("blueprint_feedback", ""),
        demo_url=entry.get("demo_url", ""),
        github_url=entry.get("github_url", ""),
        round1_score_summary="",
        round2_score_summary="",
    )
    try:
        llm_response = await llm.generate(
            f"{system_prompt}\n\n{raw_data.get('output_instruction', 'Return JSON only.')}",
            model="gemini", temperature=0.7,
        )
        result = json.loads(_strip_json(llm_response.get("content", "{}")))
        return result.get("questions", [])
    except Exception as e:
        logger.warning("Round %d question generation failed: %s", round_number, e)
        return []


async def _finalize_round(entry_id: str, participant_user_id: str, round_number: int,
                          entry: dict, session: dict) -> None:
    """Generate and store round summary after all 8 answers."""
    raw_data = prompt_manager.get_raw("contest_interview_evaluation")
    summary_variant = next((v for v in raw_data.get("variants", []) if v["id"] == "contest_eval_round_summary"), {})

    rounds = session.get("rounds", [])
    current_round = next((r for r in rounds if r["round_number"] == round_number), {})
    evals = current_round.get("evaluations", [])
    answer_scores = [e.get("score", 0) for e in evals]
    depth_signals = [e.get("depth_signal", "") for e in evals]
    red_flags = [e.get("red_flags") for e in evals if e.get("red_flags")]

    system_prompt = summary_variant.get("system_prompt", "").format(
        project_name=entry.get("refined_title", entry.get("raw_project_name")),
        participant_role=session.get("participant_role", "Team Member"),
        round_number=round_number,
        round_name=current_round.get("round_name", ""),
        answer_scores_array=json.dumps(answer_scores),
        depth_signals_array=json.dumps(depth_signals),
        red_flags_array=json.dumps(red_flags),
    )
    try:
        llm_response = await llm.generate(
            f"{system_prompt}\n\n{raw_data.get('output_instruction', 'Return JSON only.')}",
            model="gemini", temperature=0.3,
        )
        summary = json.loads(_strip_json(llm_response.get("content", "{}")))
    except Exception as e:
        logger.warning("Round summary generation failed: %s", e)
        summary = {"round_score": sum(answer_scores) // max(len(answer_scores), 1), "consistency_rating": "mostly_consistent", "authenticity_assessment": "moderate_confidence", "knowledge_pattern": ""}

    await contest_db.store_round_summary(entry_id, participant_user_id, round_number, summary)

    # Push next round questions into the session if not round 3
    if round_number < 3:
        next_questions = await _generate_round_questions(
            round_number + 1, entry, session.get("participant_role", "Team Member"), entry
        )
        next_round_doc = {
            "round_number": round_number + 1,
            "round_name": ["Conceptual Depth", "Execution and Decision-Making", "Stress and Edge Cases"][round_number],
            "questions": next_questions,
            "answers": [], "evaluations": [],
            "round_score": None, "consistency_rating": None,
            "authenticity_assessment": None, "knowledge_pattern": None,
        }
        await contest_db.col.update_one(
            {"entry_id": entry_id, "interview_sessions.participant_user_id": participant_user_id},
            {"$push": {"interview_sessions.$[sess].rounds": next_round_doc}},
            array_filters=[{"sess.participant_user_id": participant_user_id}]
        )


async def _finalize_participant(entry_id: str, participant_user_id: str, entry: dict) -> None:
    """Compute final participant score after all 3 rounds."""
    fresh = await contest_db.get_by_id(entry_id)
    sessions = fresh.get("interview_sessions", [])
    session = next((s for s in sessions if s["participant_user_id"] == participant_user_id), {})
    rounds = session.get("rounds", [])

    raw_data = prompt_manager.get_raw("contest_interview_evaluation")
    final_variant = next((v for v in raw_data.get("variants", []) if v["id"] == "contest_eval_final_participant"), {})

    def _round_data(rn):
        r = next((x for x in rounds if x["round_number"] == rn), {})
        return r.get("round_score", 0), r.get("consistency_rating", ""), r.get("authenticity_assessment", ""), r.get("knowledge_pattern", "")

    r1s, r1c, r1a, r1k = _round_data(1)
    r2s, r2c, r2a, r2k = _round_data(2)
    r3s, r3c, r3a, r3k = _round_data(3)

    system_prompt = final_variant.get("system_prompt", "").format(
        project_name=entry.get("refined_title", entry.get("raw_project_name")),
        participant_role=session.get("participant_role", "Team Member"),
        round1_score=r1s, round1_consistency=r1c, round1_authenticity=r1a,
        round2_score=r2s, round2_consistency=r2c, round2_authenticity=r2a,
        round3_score=r3s, round3_consistency=r3c, round3_authenticity=r3a,
        round1_knowledge_pattern=r1k, round2_knowledge_pattern=r2k, round3_knowledge_pattern=r3k,
    )
    try:
        llm_response = await llm.generate(
            f"{system_prompt}\n\n{raw_data.get('output_instruction', 'Return JSON only.')}",
            model="gemini", temperature=0.3,
        )
        result = json.loads(_strip_json(llm_response.get("content", "{}")))
    except Exception as e:
        logger.warning("Final participant score failed: %s", e)
        result = {"final_score": (r1s * 25 + r2s * 40 + r3s * 35) // 100, "overall_verdict": "competent", "participant_summary": "", "anomaly_flags": [], "feedback_for_participant": ""}

    await contest_db.store_participant_final_score(entry_id, participant_user_id, result)


async def _check_all_interviews_complete(entry_id: str, entry: dict) -> None:
    """Check if all participants finished. If yes, compute team score and send emails."""
    fresh = await contest_db.get_by_id(entry_id)
    sessions = fresh.get("interview_sessions", [])
    expected_count = fresh.get("team_size", 1)
    complete_sessions = [s for s in sessions if s.get("status") == "complete"]

    if len(complete_sessions) < expected_count:
        return  # Not all done yet

    # Compute team score
    raw_data = prompt_manager.get_raw("contest_interview_evaluation")
    team_variant = next((v for v in raw_data.get("variants", []) if v["id"] == "contest_eval_team_score"), {})

    lead_session = next((s for s in complete_sessions if s["participant_user_id"] == fresh["lead_user_id"]), complete_sessions[0])
    member_sessions = [s for s in complete_sessions if s["participant_user_id"] != fresh["lead_user_id"]]

    system_prompt = team_variant.get("system_prompt", "").format(
        project_name=fresh.get("refined_title", fresh.get("raw_project_name")),
        team_size=fresh.get("team_size", 1),
        lead_score=lead_session.get("final_score", 0),
        lead_verdict=lead_session.get("overall_verdict", ""),
        lead_anomaly_flags=json.dumps(lead_session.get("anomaly_flags", [])),
        member_scores_array=json.dumps([{"participant_role": s.get("participant_role"), "score": s.get("final_score", 0), "verdict": s.get("overall_verdict", ""), "anomaly_flags": s.get("anomaly_flags", [])} for s in member_sessions]),
    )
    try:
        llm_response = await llm.generate(
            f"{system_prompt}\n\n{raw_data.get('output_instruction', 'Return JSON only.')}",
            model="gemini", temperature=0.3,
        )
        team_result = json.loads(_strip_json(llm_response.get("content", "{}")))
    except Exception as e:
        logger.warning("Team score computation failed: %s", e)
        avg = sum(s.get("final_score", 0) for s in complete_sessions) // max(len(complete_sessions), 1)
        team_result = {"team_interview_score": avg, "team_verdict": "competent", "team_strength_summary": "", "weakest_link": "", "strongest_contributor": "", "team_anomaly_flags": []}

    team_score = team_result.get("team_interview_score", 0)
    advance = team_score >= SCORE_THRESHOLDS["interview"]

    # Composite score: L1=10%, L2=20%, L3=30%, L4=40%
    composite = (
        fresh.get("idea_quality_score", 0) * 0.10 +
        fresh.get("blueprint_score", 0) * 0.20 +
        fresh.get("demo_score", 0) * 0.30 +
        team_score * 0.40
    )

    await contest_db.store_team_interview_result(entry_id, team_result, round(composite, 2), advance)

    # Build personal feedbacks map for email
    personal_feedbacks = {}
    for s in complete_sessions:
        from db import db
        user = await db.database["users"].find_one({"user_id": s["participant_user_id"]}, {"email": 1})
        if user:
            personal_feedbacks[user["email"]] = s.get("feedback_for_participant", "")

    updated = await contest_db.get_by_id(entry_id)
    recipients = await _resolve_member_registration(updated)
    await asyncio.to_thread(
        email_service.send_contest_interview_complete,
        recipients, updated, team_score, advance, personal_feedbacks
    )
    if not advance:
        feedback = team_result.get("team_strength_summary", "")
        await asyncio.to_thread(
            email_service.send_contest_eliminated, recipients, updated,
            "Level 4 — Interrogation", team_score, SCORE_THRESHOLDS["interview"], feedback
        )
