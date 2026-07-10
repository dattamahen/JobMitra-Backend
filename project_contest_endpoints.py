"""
Project Contest Endpoints for JobMitra Backend.
Handles project submissions, team management, payments, and subscription grants.
Collection: project_contest_entries
"""

import logging
import uuid
import re
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from db import db
from config import settings
from activity_tracker import log_user_activity
from email_service import email_service
from project_contest_schemas import (
    ProjectSubmission,
    ContestPaymentConfirm,
    PRICING,
    CONTEST_SUBSCRIPTION_BENEFITS,
    ALL_CATEGORIES,
    TECHNICAL_CATEGORIES,
    NON_TECHNICAL_CATEGORIES,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/project-contest", tags=["Project Contest"])

COLLECTION = "project_contest_entries"


# ── Helpers ──────────────────────────────────────────────────

GMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@gmail\.com$')


def _generate_project_id() -> str:
    """Generate a unique project ID with prefix and timestamp component."""
    ts = datetime.utcnow().strftime("%y%m%d")
    uid = uuid.uuid4().hex[:8]
    return f"PRJ-{ts}-{uid.upper()}"


def _validate_member_email(email: str) -> bool:
    """Validate that email is a valid Gmail address."""
    return bool(GMAIL_REGEX.match(email))


def _determine_pricing(team_size: int) -> tuple[str, float]:
    """Return (tier, amount) based on team size."""
    if team_size <= 1:
        return "solo", PRICING["solo"]
    return "team", PRICING["team"]


async def _grant_subscription(user_id: str, benefits: dict):
    """Add contest subscription benefits on top of existing credits."""
    users = db.database["users"]
    await users.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "credits.cv_downloads_remaining": benefits["cv_downloads"],
                "credits.mock_interviews_remaining": benefits["mock_interviews"],
                "credits.total_cv_downloads": benefits["cv_downloads"],
                "credits.total_mock_interviews": benefits["mock_interviews"],
            },
            "$set": {
                "user_plan": "paid",
                "updated_at": datetime.utcnow(),
            },
        },
    )


async def _grant_subscription_to_member(email: str, benefits: dict):
    """Grant subscription to a team member by email (if they have an account)."""
    users = db.database["users"]
    user = await users.find_one({"email": email})
    if user:
        await _grant_subscription(user["user_id"], benefits)
        return True
    return False


async def _send_team_member_emails(entry: dict):
    """Send notification emails to all team members after successful submission."""
    users_collection = db.database["users"]
    project_id = entry["entry_id"]
    project_title = entry["project_title"]
    project_desc = entry["project_description"][:200]
    lead_name = entry["lead_name"]
    category = entry["category"].replace("_", " ").title()
    tech_stack = ", ".join(entry.get("tech_stack", [])) or "N/A"

    for member in entry.get("team_members", []):
        email = member.get("email")
        name = member.get("full_name", "Team Member")
        if not email:
            continue

        user = await users_collection.find_one({"email": email})

        if user:
            # Existing user — share project details
            html = _build_existing_user_email(
                name, project_id, project_title, project_desc,
                lead_name, category, tech_stack
            )
            subject = f"🎉 You've been added to project: {project_title}"
        else:
            # Non-existing user — ask to create account
            html = _build_new_user_email(
                name, project_id, project_title, project_desc,
                lead_name, category, tech_stack
            )
            subject = f"🎉 You're invited to join {project_title} on JobMouka"

        try:
            email_service.send_email(email, subject, html)
        except Exception as e:
            logger.error("Failed to send contest email to %s: %s", email, e)


def _build_existing_user_email(
    name: str, project_id: str, title: str, desc: str,
    lead_name: str, category: str, tech_stack: str
) -> str:
    frontend_url = settings.FRONTEND_URL
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #4831af 0%, #7c3aed 50%, #a855f7 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .project-box {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 16px 0; }}
            .project-id {{ color: #4831af; font-weight: 700; font-size: 14px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #4831af; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏆 Project Contest</h1>
                <p>You've been added to a project!</p>
            </div>
            <div class="content">
                <p>Hi {name},</p>
                <p><strong>{lead_name}</strong> has added you as a team member in the Project Contest.</p>
                <div class="project-box">
                    <p class="project-id">Project ID: {project_id}</p>
                    <h3 style="margin: 8px 0 4px;">{title}</h3>
                    <p style="font-size: 13px; color: #666;"><strong>Category:</strong> {category}</p>
                    <p style="font-size: 13px; color: #666;"><strong>Tech Stack:</strong> {tech_stack}</p>
                    <p style="font-size: 13px; color: #555; margin-top: 12px;">{desc}...</p>
                </div>
                <p>✅ You've received <strong>+5 CV Downloads</strong> and <strong>+3 Mock Interviews</strong> as subscription benefits!</p>
                <p style="text-align: center;">
                    <a href="{frontend_url}/project-contest" class="button">View Project</a>
                </p>
            </div>
            <div class="footer">
                <p>&copy; 2024 JobMouka. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def _build_new_user_email(
    name: str, project_id: str, title: str, desc: str,
    lead_name: str, category: str, tech_stack: str
) -> str:
    frontend_url = settings.FRONTEND_URL
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #4831af 0%, #7c3aed 50%, #a855f7 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .project-box {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 16px 0; }}
            .project-id {{ color: #4831af; font-weight: 700; font-size: 14px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #4831af; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏆 Project Contest</h1>
                <p>You're invited to join a project!</p>
            </div>
            <div class="content">
                <p>Hi {name},</p>
                <p><strong>{lead_name}</strong> has added you as a team member in the Project Contest on <strong>JobMouka</strong>.</p>
                <div class="project-box">
                    <p class="project-id">Project ID: {project_id}</p>
                    <h3 style="margin: 8px 0 4px;">{title}</h3>
                    <p style="font-size: 13px; color: #666;"><strong>Category:</strong> {category}</p>
                    <p style="font-size: 13px; color: #666;"><strong>Tech Stack:</strong> {tech_stack}</p>
                    <p style="font-size: 13px; color: #555; margin-top: 12px;">{desc}...</p>
                </div>
                <p>🎁 Create your account to claim <strong>+5 CV Downloads</strong> and <strong>+3 Mock Interviews</strong> for free!</p>
                <p>JobMouka helps you find jobs, practice mock interviews, and build your career.</p>
                <p style="text-align: center;">
                    <a href="{frontend_url}/login" class="button">Sign In with Google</a>
                </p>
            </div>
            <div class="footer">
                <p>&copy; 2024 JobMouka. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


# ── Endpoints ────────────────────────────────────────────────

@router.get("/categories")
async def get_categories():
    """Return all available project categories."""
    return {
        "technical": TECHNICAL_CATEGORIES,
        "non_technical": NON_TECHNICAL_CATEGORIES,
    }


@router.get("/pricing")
async def get_pricing():
    """Return pricing tiers and subscription benefits."""
    return {
        "solo": {"members": 1, "amount": PRICING["solo"], "currency": PRICING["currency"]},
        "team": {"members": "2-4", "amount": PRICING["team"], "currency": PRICING["currency"]},
        "benefits": CONTEST_SUBSCRIPTION_BENEFITS,
    }


@router.post("/submit")
async def submit_project(req: ProjectSubmission):
    """Submit a project entry. Creates a draft entry pending payment."""
    try:
        # Validate category
        if req.category not in ALL_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {ALL_CATEGORIES}")

        # Validate team size (max 3 additional = 4 total)
        if len(req.team_members) > 3:
            raise HTTPException(status_code=400, detail="Maximum 4 team members (including lead)")

        # Get lead user info
        users = db.database["users"]
        lead_user = await users.find_one({"user_id": req.lead_user_id})
        if not lead_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate team member emails are valid Gmail
        for member in req.team_members:
            if not _validate_member_email(member.email):
                raise HTTPException(
                    status_code=400,
                    detail=f"Team member email must be a valid Gmail address: {member.email}"
                )
            if member.email == lead_user.get("email"):
                raise HTTPException(
                    status_code=400,
                    detail="Team member email cannot be the same as the team lead's email"
                )

        team_size = 1 + len(req.team_members)
        tier, amount = _determine_pricing(team_size)

        entry_id = _generate_project_id()

        entry = {
            "entry_id": entry_id,
            "lead_user_id": req.lead_user_id,
            "lead_email": lead_user.get("email", ""),
            "lead_name": f"{lead_user.get('first_name', '')} {lead_user.get('last_name', '')}".strip(),
            "project_title": req.project_title,
            "project_description": req.project_description,
            "project_type": req.project_type,
            "category": req.category,
            "tech_stack": req.tech_stack,
            "project_url": req.project_url,
            "demo_url": req.demo_url,
            "github_url": req.github_url,
            "team_size": team_size,
            "team_members": [m.model_dump() for m in req.team_members],
            "amount_paid": 0,
            "pricing_tier": tier,
            "payment_status": "pending",
            "subscription_granted": False,
            "subscription_benefits": {},
            "college_name": req.college_name,
            "graduation_year": req.graduation_year,
            "status": "draft",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        collection = db.database[COLLECTION]
        await collection.insert_one(entry)

        await log_user_activity(
            req.lead_user_id, "project_contest",
            f"Submitted project: {req.project_title}",
            {"entry_id": entry_id, "team_size": team_size}
        )

        return {
            "entry_id": entry_id,
            "pricing_tier": tier,
            "amount": amount,
            "currency": PRICING["currency"],
            "team_size": team_size,
            "message": f"Project submitted. Please pay ₹{int(amount)} to confirm entry.",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error submitting project: %s", e)
        raise HTTPException(status_code=500, detail="Failed to submit project")


@router.post("/payment/confirm")
async def confirm_contest_payment(req: ContestPaymentConfirm):
    """Confirm payment for a contest entry. Grants subscription to all team members."""
    try:
        collection = db.database[COLLECTION]
        entry = await collection.find_one({"entry_id": req.entry_id, "lead_user_id": req.user_id})

        if not entry:
            raise HTTPException(status_code=404, detail="Contest entry not found")

        if entry.get("payment_status") == "confirmed":
            raise HTTPException(status_code=400, detail="Payment already confirmed")

        # Validate amount
        _, expected_amount = _determine_pricing(entry["team_size"])
        if req.amount != expected_amount:
            raise HTTPException(status_code=400, detail=f"Amount must be ₹{int(expected_amount)}")

        benefits = CONTEST_SUBSCRIPTION_BENEFITS.copy()

        # Grant subscription to lead
        await _grant_subscription(req.user_id, benefits)

        # Grant subscription to team members (by email)
        members_granted = []
        for member in entry.get("team_members", []):
            email = member.get("email")
            if email:
                granted = await _grant_subscription_to_member(email, benefits)
                members_granted.append({"email": email, "granted": granted})

        # Send notification emails to team members
        try:
            updated_entry = {**entry, "payment_status": "confirmed"}
            await _send_team_member_emails(updated_entry)
        except Exception as e:
            logger.error("Error sending team member emails: %s", e)

        # Update entry
        await collection.update_one(
            {"entry_id": req.entry_id},
            {
                "$set": {
                    "payment_status": "confirmed",
                    "upi_transaction_id": req.upi_transaction_id,
                    "amount_paid": req.amount,
                    "subscription_granted": True,
                    "subscription_benefits": benefits,
                    "status": "submitted",
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        # Audit log
        await db.database["payments"].insert_one({
            "user_id": req.user_id,
            "type": "project_contest",
            "entry_id": req.entry_id,
            "upi_transaction_id": req.upi_transaction_id,
            "amount": req.amount,
            "currency": PRICING["currency"],
            "status": "confirmed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

        await log_user_activity(
            req.user_id, "project_contest",
            f"Payment confirmed for project contest — ₹{int(req.amount)}",
            {"entry_id": req.entry_id}
        )

        return {
            "message": "Payment confirmed. Subscription benefits granted to all team members.",
            "benefits": benefits,
            "members_granted": members_granted,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error confirming contest payment: %s", e)
        raise HTTPException(status_code=500, detail="Failed to confirm payment")


@router.get("/my-entries/{user_id}")
async def get_user_entries(user_id: str):
    """Get all contest entries for a user (as lead or team member)."""
    try:
        collection = db.database[COLLECTION]
        # Entries where user is lead
        cursor = collection.find(
            {"lead_user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1)
        entries = await cursor.to_list(length=50)

        # Serialize datetimes
        for entry in entries:
            for key in ("created_at", "updated_at"):
                if isinstance(entry.get(key), datetime):
                    entry[key] = entry[key].isoformat() + "Z"

        return {"entries": entries, "count": len(entries)}

    except Exception as e:
        logger.error("Error fetching user entries: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch entries")


@router.get("/entries")
async def list_entries(
    project_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query("submitted"),
    limit: int = Query(20, le=100),
):
    """List contest entries (public view for approved/submitted projects)."""
    try:
        collection = db.database[COLLECTION]
        query: dict = {}
        if project_type:
            query["project_type"] = project_type
        if category:
            query["category"] = category
        if status:
            query["status"] = status

        cursor = collection.find(
            query,
            {"_id": 0, "upi_transaction_id": 0, "lead_email": 0}
        ).sort("created_at", -1).limit(limit)

        entries = await cursor.to_list(length=limit)
        for entry in entries:
            for key in ("created_at", "updated_at"):
                if isinstance(entry.get(key), datetime):
                    entry[key] = entry[key].isoformat() + "Z"

        return {"entries": entries, "count": len(entries)}

    except Exception as e:
        logger.error("Error listing entries: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list entries")


@router.get("/entry/{entry_id}")
async def get_entry(entry_id: str):
    """Get a single contest entry by ID."""
    try:
        collection = db.database[COLLECTION]
        entry = await collection.find_one({"entry_id": entry_id}, {"_id": 0})
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")

        for key in ("created_at", "updated_at"):
            if isinstance(entry.get(key), datetime):
                entry[key] = entry[key].isoformat() + "Z"

        return entry

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching entry: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch entry")
