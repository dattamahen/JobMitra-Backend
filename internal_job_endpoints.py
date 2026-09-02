"""
Internal Job Postings API endpoints.
- Any verified job-seeker can post a job using their official company email (OTP verified).
- Supports manual entry, image/CSV → LLM parse → preview → post.
- Content moderation via LLM before saving.
- Auto-expires after 15 days.
- On apply: notify poster + admin.
"""

import asyncio
import logging
import os
import random
import re
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from auth_endpoints import get_current_user
from db import db
from email_service import email_service
from internal_job_db import internal_job_db
from internal_job_schemas import (
    InternalJobApplyRequest,
    InternalJobPostRequest,
    InternalJobSearchFilters,
    ParseJobFromMediaRequest,
    SendOTPRequest,
    VerifyOTPRequest,
)
from prompt_manager import prompt_manager

logger = logging.getLogger(__name__)

internal_job_router = APIRouter(prefix="/api/v1/internal-jobs", tags=["Internal Job Market"])

ADMIN_EMAIL = "renukadevi@jobmouka.com"
OTP_TTL_MINUTES = 10

# ── Blocked content patterns ──────────────────────────────────────────────────
_BLOCKED_PATTERNS = [
    r"\bsex\b", r"\bporn\b", r"\bescort\b", r"\bprostitut",
    r"\bterror", r"\bbomb\b", r"\bweapon\b", r"\btheft\b", r"\bsteal\b",
    r"\bgovernment job\b", r"\bsarkari\b", r"\bpsc\b", r"\bupsc\b",
    r"\bssc\b", r"\bbank exam\b", r"\brailway job\b",
    r"\bdrug\b", r"\bnarco", r"\bhack\b", r"\bphish",
]
_BLOCKED_RE = re.compile("|".join(_BLOCKED_PATTERNS), re.IGNORECASE)


def _is_content_safe(text: str) -> bool:
    return not bool(_BLOCKED_RE.search(text))


async def _llm_check_job_content(job: InternalJobPostRequest) -> None:
    """LLM moderation at final POST gate — blocks objectionable jobs before DB write."""
    # Fast regex pre-check first (no API cost)
    combined = f"{job.title} {job.company} {job.description} {' '.join(job.skills_required)}"
    if not _is_content_safe(combined):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Job content violates our community guidelines."
        )

    # LLM final check
    try:
        import json
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        mod_variant = prompt_manager.get_random("job_moderation")
        prompt = (
            mod_variant["system_prompt"]
            + f"\n\nJob Title: {job.title}"
            + f"\nCompany: {job.company}"
            + f"\nDescription: {job.description[:500]}"
            + f"\nSkills: {', '.join(job.skills_required)}"
            + f"\nRequirements: {'; '.join((job.requirements or [])[:3])}"
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=mod_variant.get("temperature", 0.0),
            max_tokens=mod_variant.get("max_tokens", 100)
        )
        result = json.loads(response.choices[0].message.content)
        if not result.get("safe", True):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.get("reason", "Job content violates community guidelines.")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("LLM moderation check failed, falling back to regex: %s", e)
        # If LLM fails, regex already passed above — allow through


# ── OTP helpers ───────────────────────────────────────────────────────────────

def _generate_otp() -> str:
    return "".join(secrets.choice(string.digits) for _ in range(6))


def _generate_otp_token() -> str:
    return secrets.token_urlsafe(32)


async def _store_otp(email: str, otp: str, token: str) -> None:
    expires = datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES)
    await db.database["internal_job_otps"].replace_one(
        {"email": email},
        {"email": email, "otp": otp, "token": token, "expires_at": expires, "verified": False},
        upsert=True
    )


async def _verify_otp_record(email: str, otp: str) -> Optional[str]:
    """Returns the token if OTP is valid, else None."""
    record = await db.database["internal_job_otps"].find_one({"email": email})
    if not record:
        return None
    if record.get("otp") != otp:
        return None
    if record.get("expires_at") < datetime.utcnow():
        return None
    token = record["token"]
    await db.database["internal_job_otps"].update_one(
        {"email": email}, {"$set": {"verified": True}}
    )
    return token


async def _validate_otp_token(email: str, token: str) -> bool:
    """Check that the token was issued for this email and is verified."""
    record = await db.database["internal_job_otps"].find_one(
        {"email": email, "token": token, "verified": True}
    )
    if not record:
        return False
    if record.get("expires_at") < datetime.utcnow():
        return False
    return True


def _is_official_email(email: str) -> bool:
    """Reject free/personal email providers."""
    from email_domain_validator import is_company_email
    return is_company_email(email)


# ── Subscription guard ────────────────────────────────────────────────────────

def _is_paid(user: dict) -> bool:
    plan = (user.get("user_plan") or "F").upper()
    return plan in ("P", "S", "PAID", "SUBSCRIBED", "PRO", "PREMIUM")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@internal_job_router.post("/send-otp")
async def send_otp(
    body: SendOTPRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send OTP to official company email for job-post verification."""
    if not _is_official_email(body.official_email):
        raise HTTPException(
            status_code=400,
            detail="Only official company email addresses are accepted. Personal email providers (Gmail, Yahoo, Outlook, etc.) are not allowed."
        )
    otp = _generate_otp()
    token = _generate_otp_token()
    await _store_otp(body.official_email, otp, token)

    user_name = f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip()
    subject = "JobMouka — Verify your company email to post a job"
    html = email_service._build_email(
        "Company Email Verification",
        f"""
        <p>Hi <strong>{user_name}</strong>,</p>
        <p>Use the OTP below to verify your company email and post an internal job on <strong>JobMouka</strong>.</p>
        <div class="code-box"><span class="code">{otp}</span></div>
        <p class="note">This OTP expires in {OTP_TTL_MINUTES} minutes. Do not share it with anyone.</p>
        """
    )
    await asyncio.to_thread(email_service.send_email, body.official_email, subject, html)
    logger.info("OTP sent to %s for user %s", body.official_email, current_user["user_id"])
    return {"message": "OTP sent to your company email", "email": body.official_email}


@internal_job_router.post("/verify-otp")
async def verify_otp(
    body: VerifyOTPRequest,
    current_user: dict = Depends(get_current_user)
):
    """Verify OTP and return a short-lived posting token."""
    token = await _verify_otp_record(body.official_email, body.otp)
    if not token:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return {"message": "Email verified", "otp_token": token, "official_email": body.official_email}


@internal_job_router.post("/parse-from-text")
async def parse_job_from_text(
    body: ParseJobFromMediaRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Parse job details from raw text (extracted from image/CSV) using LLM.
    Returns a structured job object for user review before posting.
    """
    if not await _validate_otp_token(body.official_email, body.otp_token):
        raise HTTPException(status_code=401, detail="Invalid or expired verification token")

    if not _is_content_safe(body.raw_text):
        raise HTTPException(status_code=422, detail="Content violates community guidelines")

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        variant = prompt_manager.get_random("job_text_parse")
        prompt = variant["system_prompt"] + f"\n\nText:\n{body.raw_text[:3000]}"

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=variant.get("temperature", 0.2),
            max_tokens=variant.get("max_tokens", 1500)
        )
        import json
        raw_content = response.choices[0].message.content or ""
        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            cleaned = raw_content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                logger.error("Text parse LLM response not valid JSON: %s", raw_content[:300])
                raise HTTPException(status_code=422, detail="Could not parse job details from the provided text. Please try manual entry.")

        if parsed.get("rejected"):
            raise HTTPException(status_code=422, detail=parsed.get("reason", "Job content violates community guidelines"))

        # Fallback regex safety net
        combined = f"{parsed.get('title','')} {parsed.get('description','')} {parsed.get('company','')}"
        if not _is_content_safe(combined):
            raise HTTPException(status_code=422, detail="Parsed content violates community guidelines")

        return {"parsed_job": parsed, "message": "Review the details below before posting"}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error("LLM parse error: %s\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to parse job details: {type(e).__name__}: {str(e)[:200]}")


@internal_job_router.post("/upload-and-parse")
async def upload_and_parse(
    file: UploadFile = File(...),
    official_email: str = Form(...),
    otp_token: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Accept image or CSV file, extract text, then parse via LLM.
    Returns structured job for preview.
    """
    if not await _validate_otp_token(official_email, otp_token):
        raise HTTPException(status_code=401, detail="Invalid or expired verification token")

    content_type = file.content_type or ""
    raw_bytes = await file.read()

    if "csv" in content_type or file.filename.endswith(".csv"):
        raw_text = raw_bytes.decode("utf-8", errors="ignore")
        if not raw_text.strip():
            raise HTTPException(status_code=422, detail="Could not extract text from the uploaded file")
        body = ParseJobFromMediaRequest(raw_text=raw_text, official_email=official_email, otp_token=otp_token)
        return await parse_job_from_text(body, current_user)

    elif "image" in content_type or file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        import base64
        import json
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        b64 = base64.b64encode(raw_bytes).decode()
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpeg"
        mime = f"image/{ext}"

        vision_variant = prompt_manager.get_random("job_image_parse")
        vision_prompt = vision_variant["system_prompt"]

        vision_resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": vision_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                ]
            }],
            temperature=vision_variant.get("temperature", 0.1),
            max_tokens=vision_variant.get("max_tokens", 1500)
        )

        raw_content = vision_resp.choices[0].message.content or ""
        if not raw_content.strip():
            raise HTTPException(status_code=422, detail="Could not extract job details from the image")

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            cleaned = raw_content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                logger.error("Vision response not valid JSON: %s", raw_content[:300])
                raise HTTPException(status_code=422, detail="Could not parse job details from the image. Please try manual entry.")

        if parsed.get("rejected"):
            raise HTTPException(status_code=422, detail=parsed.get("reason", "Image content violates community guidelines"))

        # Fallback regex safety net
        combined = f"{parsed.get('title','')} {parsed.get('description','')} {parsed.get('company','')}"
        if not _is_content_safe(combined):
            raise HTTPException(status_code=422, detail="Image content violates community guidelines")

        return {"parsed_job": parsed, "message": "Review the details below before posting"}
    else:
        raise HTTPException(status_code=400, detail="Only image (PNG/JPG) and CSV files are supported")


@internal_job_router.post("/post")
async def post_internal_job(
    job: InternalJobPostRequest,
    current_user: dict = Depends(get_current_user)
):
    """Post an internal job. Requires verified OTP token."""
    if not await _validate_otp_token(job.official_email, job.otp_token):
        raise HTTPException(status_code=401, detail="Invalid or expired verification token. Please verify your company email again.")

    await _llm_check_job_content(job)

    user_id = current_user["user_id"]
    user_email = current_user["email"]

    job_id = await internal_job_db.create(job, user_id, user_email)

    # Invalidate OTP token after use
    await db.database["internal_job_otps"].delete_one({"email": job.official_email, "token": job.otp_token})

    # Notify poster
    user_name = f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip()
    subject = f"Your job '{job.title}' is now live on JobMouka!"
    html = email_service._build_email(
        "Job Posted Successfully 🎉",
        f"""
        <p>Hi <strong>{user_name}</strong>,</p>
        <p>Your internal job posting <strong>"{job.title}"</strong> at <strong>{job.company}</strong> is now live on JobMouka's Internal Job Market.</p>
        <p>It will be automatically removed after <strong>15 days</strong>.</p>
        <p>You can view and manage it under <strong>Refer &amp; Hire</strong> in your dashboard.</p>
        <p class="note">Job ID: {job_id}</p>
        """
    )
    await asyncio.to_thread(email_service.send_email, user_email, subject, html)

    logger.info("Internal job posted: %s by %s", job_id, user_id)
    return {"message": "Job posted successfully", "internal_job_id": job_id, "expires_in_days": 15}


@internal_job_router.get("/my-applications")
async def get_my_internal_applications(
    current_user: dict = Depends(get_current_user)
):
    """Return internal job applications for the current user."""
    user = await db.database["users"].find_one({"user_id": current_user["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    applications = [
        app for app in user.get("internal_job_applications", [])
        if isinstance(app, dict)
    ]
    return {"applications": applications, "total_count": len(applications)}


@internal_job_router.get("/my-posts")
async def get_my_posts(
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Refer & Hire — jobs posted by the current user."""
    result = await internal_job_db.get_by_poster(current_user["user_id"], page, per_page)
    return result


@internal_job_router.get("/search")
async def search_internal_jobs(
    keywords: Optional[str] = None,
    location: Optional[str] = None,
    experience_level: Optional[str] = None,
    employment_type: Optional[str] = None,
    job_type: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Internal Job Market — paid feature. Search all active internal jobs."""
    if not _is_paid(current_user):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Internal Job Market requires an active subscription (₹149/month). Please subscribe to access this feature."
        )
    filters = InternalJobSearchFilters(
        keywords=keywords,
        location=location,
        experience_level=experience_level,
        employment_type=employment_type,
        job_type=job_type,
        page=page,
        per_page=per_page
    )
    return await internal_job_db.search(filters)


@internal_job_router.get("/{job_id}")
async def get_internal_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a single internal job. Paid users only (for market view)."""
    job = await internal_job_db.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or has expired")
    await internal_job_db.increment_views(job_id)
    return job


@internal_job_router.post("/apply")
async def apply_internal_job(
    body: InternalJobApplyRequest,
    current_user: dict = Depends(get_current_user)
):
    """Apply for an internal job. Paid users only."""
    if not _is_paid(current_user):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Applying to internal jobs requires an active subscription (₹149/month)."
        )

    job = await internal_job_db.get_by_id(body.internal_job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or has expired")

    if job.get("posted_by_user_id") == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="You cannot apply to your own job posting")

    if not body.force_apply:
        return {"message": "Confirm your application for this internal job?", "show_confirm": True, "success": False}

    user_name = f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip()
    success = await internal_job_db.apply(
        body.internal_job_id,
        current_user["user_id"],
        current_user["email"],
        user_name
    )

    if not success:
        raise HTTPException(status_code=400, detail="You have already applied for this job")

    # Notify job poster
    poster_email = job.get("official_email") or job.get("posted_by_email", "")
    if poster_email:
        subject = f"New application for '{job['title']}' on JobMouka"
        html = email_service._build_email(
            "New Job Application Received 📩",
            f"""
            <p>Someone applied to your internal job posting <strong>"{job['title']}"</strong>.</p>
            <table style="width:100%;font-size:14px;margin:12px 0;">
              <tr><td style="color:#6b7280;width:120px;">Applicant</td><td><strong>{user_name}</strong></td></tr>
              <tr><td style="color:#6b7280;">Email</td><td>{current_user['email']}</td></tr>
              <tr><td style="color:#6b7280;">Applied On</td><td>{datetime.utcnow().strftime('%d %b %Y, %H:%M UTC')}</td></tr>
            </table>
            <p class="note">Log in to JobMouka to view all applications under Refer &amp; Hire.</p>
            """
        )
        await asyncio.to_thread(email_service.send_email, poster_email, subject, html)

    # Always notify admin
    admin_html = email_service._build_email(
        "Internal Job Application",
        f"""
        <p><strong>Internal Job Application</strong></p>
        <p>Job: {job['title']} @ {job['company']}</p>
        <p>Applicant: {user_name} ({current_user['email']})</p>
        <p>Job ID: {body.internal_job_id}</p>
        """
    )
    await asyncio.to_thread(
        email_service.send_email, ADMIN_EMAIL,
        f"[JobMouka] Internal Job Apply — {job['title']}", admin_html
    )

    return {"message": "Application submitted successfully", "success": True}


@internal_job_router.delete("/{job_id}")
async def delete_my_post(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a job posted by the current user."""
    success = await internal_job_db.delete_by_poster(job_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or you don't have permission")
    return {"message": "Job removed successfully"}
