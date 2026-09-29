"""
CV Upload Endpoint — Profile fill via document upload.
Accepts PDF or DOCX, checks for password protection, runs LLM content
moderation + ATS profile extraction, then saves to the users collection.
"""

import io
import re
import json
import logging
import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import Optional

from auth_endpoints import get_current_user
from multi_llm_service import MultiLLMService
from prompt_manager import prompt_manager
from auth_db import update_user_profile
from activity_tracker import log_user_activity

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/profile", tags=["CV Upload"])
llm = MultiLLMService()

ALLOWED_MIME = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB


# ── Text extraction helpers ──────────────────────────────────────────────────

def _extract_pdf_text(data: bytes) -> str:
    """Extract text from PDF bytes; raises ValueError if password-protected."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            if pdf.doc.is_encrypted:
                raise ValueError("password_protected")
            pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n".join(pages).strip()
    except ValueError:
        raise
    except Exception as e:
        logger.warning("pdfplumber failed, trying pypdf: %s", e)
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted:
                raise ValueError("password_protected")
            return "\n".join(
                page.extract_text() or "" for page in reader.pages
            ).strip()
        except ValueError:
            raise
        except Exception as e2:
            logger.error("PDF extraction failed: %s", e2)
            raise HTTPException(status_code=422, detail="Could not read PDF content")


def _extract_docx_text(data: bytes) -> str:
    """Extract text from DOCX bytes."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        logger.error("DOCX extraction failed: %s", e)
        raise HTTPException(status_code=422, detail="Could not read DOCX content")


# ── Field mapping helpers ────────────────────────────────────────────────────

def _build_update_payload(extracted: dict, current_user: dict) -> dict:
    """
    Map LLM-extracted fields to DB fields.
    Logged-in email, first_name, last_name always win over document values.
    Missing fields are saved as null (excluded from update to avoid overwriting).
    """
    update: dict = {}

    # Identity — logged-in user always wins
    update["first_name"] = current_user.get("first_name") or extracted.get("first_name")
    update["last_name"] = current_user.get("last_name") or extracted.get("last_name")
    update["email"] = current_user["email"]  # never overwrite

    # Scalar fields — only set if extracted value is non-null
    scalar_fields = [
        "phone", "city", "state", "current_role", "current_company",
        "overall_experience_years", "highest_qualification",
        "professional_summary", "desired_job_title",
        "linkedin_link", "github_link", "portfolio_link",
    ]
    for field in scalar_fields:
        val = extracted.get(field)
        if val is not None and val != "":
            update[field] = val

    # Array fields — only set if non-empty list
    if extracted.get("skills"):
        update["skills"] = extracted["skills"]
    if extracted.get("technical_skills"):
        update["technical_skills"] = extracted["technical_skills"]
    if extracted.get("work_experience"):
        update["work_experience"] = extracted["work_experience"]
    if extracted.get("education"):
        update["education"] = extracted["education"]
    if extracted.get("projects"):
        update["projects"] = extracted["projects"]
    if extracted.get("certifications"):
        update["certifications"] = extracted["certifications"]

    # Social links subdocument
    social: dict = {}
    if extracted.get("github_link"):
        social["github"] = extracted["github_link"]
    if extracted.get("linkedin_link"):
        social["linkedin"] = extracted["linkedin_link"]
    if extracted.get("portfolio_link"):
        social["portfolio"] = extracted["portfolio_link"]
    if social:
        update["social_links"] = social

    update["updated_at"] = datetime.utcnow()
    update["profile_setup_done"] = True
    return update


# ── Endpoint ─────────────────────────────────────────────────────────────────

class CvUploadPreviewResponse(BaseModel):
    """Returned after successful parse — caller confirms before save."""
    extracted: dict
    warnings: list[str] = []


@router.post("/upload-cv", response_model=CvUploadPreviewResponse)
async def upload_cv_preview(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a PDF or DOCX resume.
    Runs content moderation + ATS extraction via LLM.
    Returns extracted fields for preview — does NOT save yet.
    Call /upload-cv/confirm to persist.
    """
    filename = (file.filename or "").lower()
    is_pdf = filename.endswith(".pdf") or file.content_type == "application/pdf"
    is_docx = filename.endswith(".docx") or file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    if not is_pdf and not is_docx:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported.",
        )

    raw = await file.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(status_code=400, detail="File must be under 10 MB.")

    # Extract text
    try:
        if is_pdf:
            text = _extract_pdf_text(raw)
        else:
            text = _extract_docx_text(raw)
    except ValueError as e:
        if "password_protected" in str(e):
            raise HTTPException(
                status_code=422,
                detail="Password-protected files are not supported. Please upload an unlocked document.",
            )
        raise

    if len(text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Document appears to be empty or unreadable.",
        )

    # LLM moderation + extraction
    try:
        variant = prompt_manager.get_random("cv_upload_parse")
        system_prompt = variant["system_prompt"]
        user_prompt = f"Parse this resume document:\n\n{text[:12000]}"
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        ai_response = await llm.generate(full_prompt, "gemini")
        content = ai_response.get("content", "").strip()

        # Strip markdown fences
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content).strip()

        result = json.loads(content)
    except json.JSONDecodeError:
        logger.error("LLM returned non-JSON for CV upload")
        raise HTTPException(status_code=500, detail="Failed to parse document. Please try again.")
    except Exception as e:
        logger.error("LLM error during CV upload: %s", e)
        raise HTTPException(status_code=500, detail="Document analysis failed.")

    if result.get("rejected"):
        raise HTTPException(
            status_code=422,
            detail=f"Document rejected: {result.get('reason', 'Not a valid resume')}",
        )

    extracted = result.get("extracted", {})
    warnings: list[str] = []

    # Warn if identity fields differ (but logged-in values will win on confirm)
    doc_email = extracted.get("email")
    if doc_email and doc_email.lower() != current_user["email"].lower():
        warnings.append(
            "Email in document differs from your account email. Your account email will be used."
        )
    doc_first = extracted.get("first_name")
    doc_last = extracted.get("last_name")
    if doc_first and doc_first.lower() != (current_user.get("first_name") or "").lower():
        warnings.append("First name in document differs from your account. Your account name will be used.")
    if doc_last and doc_last.lower() != (current_user.get("last_name") or "").lower():
        warnings.append("Last name in document differs from your account. Your account name will be used.")

    return CvUploadPreviewResponse(extracted=extracted, warnings=warnings)


class CvUploadConfirmRequest(BaseModel):
    extracted: dict


@router.post("/upload-cv/confirm")
async def upload_cv_confirm(
    request: CvUploadConfirmRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Persist the extracted CV data to the user's profile.
    Logged-in email, first_name, last_name always override document values.
    """
    try:
        update_payload = _build_update_payload(request.extracted, current_user)
        success = await update_user_profile(current_user["user_id"], update_payload)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save profile data.")

        await log_user_activity(
            current_user["user_id"],
            "profile_update",
            "Profile filled via CV upload",
        )

        return {"success": True, "message": "Profile updated from your CV successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("CV confirm save error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to save profile.")
