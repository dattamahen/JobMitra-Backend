"""
CV tailoring by raw Job Description (paste or file upload).
Returns tailored resume data for immediate PDF download — not saved to DB.
"""
import json
import re
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from typing import Optional

from auth_endpoints import get_current_user
from db import db
from multi_llm_service import MultiLLMService

logger = logging.getLogger(__name__)
llm_service = MultiLLMService()

cv_jd_router = APIRouter(prefix="/api/v1", tags=["CV by JD"])


class TailorByJdResponse(BaseModel):
    tailored_summary: str
    tailored_skills: list[str]
    match_percentage: int
    message: str


@cv_jd_router.post("/tailor-resume-by-jd", response_model=TailorByJdResponse)
async def tailor_resume_by_jd(
    jd_text: str = Form(default=""),
    jd_file: Optional[UploadFile] = File(default=None),
    current_user: dict = Depends(get_current_user),
):
    """Tailor resume against a raw JD (paste or .txt/.pdf file). Returns tailored data for download."""
    # Resolve JD text
    resolved_jd = jd_text.strip()
    if jd_file:
        content = await jd_file.read()
        try:
            resolved_jd = content.decode("utf-8", errors="ignore").strip()
        except Exception:
            raise HTTPException(status_code=400, detail="Could not read uploaded file")

    if not resolved_jd:
        raise HTTPException(status_code=400, detail="Job description is required")

    user_id = current_user["user_id"]
    user = await db.database["users"].find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skills = user.get("skills", [])
    summary = user.get("professional_summary") or user.get("professional_info", {}).get("professional_summary", "")
    experience_years = user.get("overall_experience_years", user.get("experience_years", 0))
    current_role = user.get("current_role", "")

    prompt = f"""You are an expert resume writer. Tailor this candidate's resume for the job description below.

CANDIDATE:
- Current Role: {current_role}
- Experience: {experience_years} years
- Skills: {', '.join(skills)}
- Current Summary: {summary[:500] if summary else 'Not provided'}

JOB DESCRIPTION:
{resolved_jd[:2000]}

Rewrite the professional summary to match the JD keywords and requirements.
Reorder and filter the skills list to highlight the most relevant ones first.
Estimate a realistic match percentage (0-100).

Return ONLY a JSON object:
{{
  "tailored_summary": "<rewritten professional summary, 3-4 sentences, ATS-optimized>",
  "tailored_skills": [<skills list, most relevant first, max 15>],
  "match_percentage": <integer 0-100>
}}

No markdown, no extra text."""

    try:
        ai_response = await llm_service.generate(prompt, "gemini")
        content_str = ai_response.get("content", "").strip()
        content_str = re.sub(r"^```(?:json)?\s*", "", content_str)
        content_str = re.sub(r"\s*```$", "", content_str).strip()
        result = json.loads(content_str)

        return TailorByJdResponse(
            tailored_summary=result.get("tailored_summary", summary),
            tailored_skills=result.get("tailored_skills", skills)[:15],
            match_percentage=int(result.get("match_percentage", 0)),
            message=f"Resume tailored successfully! Estimated match: {result.get('match_percentage', 0)}%",
        )
    except Exception as e:
        logger.error("LLM tailor-by-jd failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to tailor resume. Please try again.",
        )
