"""
CV tailoring by raw Job Description (paste or file upload).
Returns tailored resume data for immediate PDF download — not saved to DB.
Rewrites professional summary, skills, AND work experience R&R (4-5 bullets
per company, calibrated to experience level, aligned to JD keywords).
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
from prompt_manager import prompt_manager

logger = logging.getLogger(__name__)
llm_service = MultiLLMService()

cv_jd_router = APIRouter(prefix="/api/v1", tags=["CV by JD"])


class WorkExperienceEntry(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: str
    responsibilities: list[str]


class TailorByJdResponse(BaseModel):
    tailored_summary: str
    tailored_skills: list[str]
    tailored_work_experience: list[dict]
    match_percentage: int
    message: str


def _exp_level_label(years_at_entry: float) -> str:
    if years_at_entry < 1:
        return "fresher"
    elif years_at_entry < 3:
        return "junior"
    elif years_at_entry < 6:
        return "mid"
    return "senior"


def _estimate_years_at_entry(company_index: int, work_experience: list) -> float:
    """Estimate cumulative experience years when the candidate joined this company."""
    years = 0.0
    for i in range(len(work_experience) - 1, company_index, -1):
        entry = work_experience[i]
        try:
            from datetime import datetime
            s = datetime.strptime(entry.get("start_date", ""), "%b %Y")
            e_str = entry.get("end_date", "Present")
            e = datetime.utcnow() if e_str == "Present" else datetime.strptime(e_str, "%b %Y")
            years += max(0, (e - s).days / 365)
        except Exception:
            years += 1.5
    return years


async def _tailor_work_experience_to_jd(
    work_experience: list,
    total_experience_years: int,
    skills: list,
    jd_text: str,
) -> list:
    """
    For each work experience entry, rewrite R&R with 4-5 strong bullets
    calibrated to experience level AND aligned to JD keywords.
    """
    rr_system_prompt = prompt_manager.get_random("roles_responsibilities").get("system_prompt", "")
    tailored = []

    for idx, exp in enumerate(work_experience):
        years_at_entry = _estimate_years_at_entry(idx, work_experience)
        exp_level = _exp_level_label(years_at_entry)

        existing_desc = exp.get("description", "") or exp.get("responsibilities", []) or exp.get("achievements", [])
        if isinstance(existing_desc, list):
            existing_desc = "\n".join(existing_desc)

        user_prompt = f"""Generate exactly 4-5 strong roles and responsibilities bullet points for this work experience entry.
Align the bullets to the keywords and requirements from the Job Description below.

CANDIDATE CONTEXT:
- Experience level at this role: {exp_level}
- Total career experience: {total_experience_years} years
- Core skills: {', '.join(skills[:10])}

THIS WORK EXPERIENCE ENTRY:
- Company: {exp.get('company', '')}
- Role: {exp.get('role', exp.get('position', ''))}
- Duration: {exp.get('start_date', '')} to {exp.get('end_date', 'Present')}
- Existing description (understand and upgrade, do not discard real context):
{existing_desc if existing_desc else 'Not provided'}

JOB DESCRIPTION (align bullets to these keywords and requirements):
{jd_text[:1500]}

Return ONLY a JSON object:
{{
  "company": "{exp.get('company', '')}",
  "role": "{exp.get('role', exp.get('position', ''))}",
  "start_date": "{exp.get('start_date', '')}",
  "end_date": "{exp.get('end_date', 'Present')}",
  "responsibilities": [
    "Strong JD-aligned bullet 1",
    "Strong JD-aligned bullet 2",
    "Strong JD-aligned bullet 3",
    "Strong JD-aligned bullet 4",
    "Strong JD-aligned bullet 5"
  ]
}}

Rules:
- Exactly 4-5 bullets. Never fewer than 4.
- Calibrate scope to {exp_level} level.
- Mirror JD keywords naturally — do NOT fabricate experience.
- Quantify with numbers/percentages where realistic.
- No markdown, no extra text."""

        full_prompt = f"{rr_system_prompt}\n\n{user_prompt}"

        try:
            ai_response = await llm_service.generate(full_prompt, "gemini")
            content = ai_response.get("content", "").strip()
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content).strip()
            tailored.append(json.loads(content))
        except Exception as e:
            logger.warning("JD R&R tailoring failed for %s: %s", exp.get("company"), e)
            tailored.append({
                "company": exp.get("company", ""),
                "role": exp.get("role", exp.get("position", "")),
                "start_date": exp.get("start_date", ""),
                "end_date": exp.get("end_date", "Present"),
                "responsibilities": [
                    f"Delivered {exp.get('role', 'key')} responsibilities aligned with team objectives",
                    f"Applied {', '.join(skills[:3])} to solve technical challenges",
                    "Collaborated with cross-functional teams to meet project deadlines",
                    "Contributed to code quality through reviews and documentation",
                ],
            })

    return tailored


@cv_jd_router.post("/tailor-resume-by-jd", response_model=TailorByJdResponse)
async def tailor_resume_by_jd(
    jd_text: str = Form(default=""),
    jd_file: Optional[UploadFile] = File(default=None),
    current_user: dict = Depends(get_current_user),
):
    """
    Tailor resume against a raw JD (paste or .txt/.pdf file).
    Rewrites professional summary, reorders skills, AND rewrites work experience
    R&R with 4-5 strong bullets per company calibrated to experience level and
    aligned to JD keywords.
    """
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
    summary = (
        user.get("professional_summary")
        or user.get("professional_info", {}).get("professional_summary", "")
    )
    experience_years = user.get("overall_experience_years", user.get("experience_years", 0))
    current_role = user.get("current_role", "")
    work_experience = user.get("work_experience", [])

    import asyncio

    # ── Run summary/skills tailoring and R&R tailoring in parallel ────────
    summary_prompt = f"""You are an expert resume writer. Tailor this candidate's resume for the job description below.

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

    async def _tailor_summary():
        try:
            ai_response = await llm_service.generate(summary_prompt, "gemini")
            content_str = ai_response.get("content", "").strip()
            content_str = re.sub(r"^```(?:json)?\s*", "", content_str)
            content_str = re.sub(r"\s*```$", "", content_str).strip()
            return json.loads(content_str)
        except Exception as e:
            logger.error("Summary tailoring failed: %s", e)
            return {"tailored_summary": summary, "tailored_skills": skills, "match_percentage": 0}

    summary_task = _tailor_summary()
    rr_task = _tailor_work_experience_to_jd(work_experience, experience_years, skills, resolved_jd) if work_experience else asyncio.sleep(0)

    summary_result, tailored_work_exp = await asyncio.gather(summary_task, rr_task)

    if not work_experience:
        tailored_work_exp = []

    match_pct = int(summary_result.get("match_percentage", 0))

    return TailorByJdResponse(
        tailored_summary=summary_result.get("tailored_summary", summary),
        tailored_skills=summary_result.get("tailored_skills", skills)[:15],
        tailored_work_experience=tailored_work_exp,
        match_percentage=match_pct,
        message=f"Resume tailored successfully! Estimated match: {match_pct}%",
    )
