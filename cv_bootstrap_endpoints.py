"""
CV Bootstrap Endpoint
Generates a sample resume preview from minimal user data (role + skills).
If the user already has work experience, it understands and upgrades their
existing roles & responsibilities calibrated to their experience level at
each company. Used immediately after signup to show value.
"""

import json
import re
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from multi_llm_service import MultiLLMService
from prompt_manager import prompt_manager
from auth_endpoints import get_current_user
from db import db

router = APIRouter(prefix="/api/v1", tags=["CV Bootstrap"])
logger = logging.getLogger(__name__)
llm_service = MultiLLMService()


class BootstrapCVRequest(BaseModel):
    desired_role: str
    skills: List[str]
    experience_years: Optional[int] = 2
    highest_qualification: Optional[str] = "bachelors"


class BootstrapCVResponse(BaseModel):
    professional_summary: str
    work_experience: List[dict]
    skills: List[str]
    projects: List[dict]
    certifications: List[dict]
    is_sample: bool = True
    message: str = "This is an AI-generated sample. Fill in your real details for an accurate resume."


def _determine_exp_level_at_company(
    company_index: int,
    total_experience_years: int,
    work_experience: list,
) -> str:
    """
    Determine the candidate's experience level when they joined a given company.
    company_index=0 is the most recent; last index is the oldest (first job).
    """
    # Accumulate years from most recent backwards to estimate level at each role
    years_at_entry = 0
    for i in range(len(work_experience) - 1, company_index, -1):
        entry = work_experience[i]
        # Try to parse duration; default 1.5 years if unknown
        try:
            start = entry.get("start_date", "")
            end = entry.get("end_date", "Present")
            if start and end and end != "Present":
                from datetime import datetime
                fmt = "%b %Y"
                s = datetime.strptime(start, fmt)
                e = datetime.strptime(end, fmt)
                years_at_entry += max(0, (e - s).days / 365)
            else:
                years_at_entry += 1.5
        except Exception:
            years_at_entry += 1.5

    if years_at_entry < 1:
        return "fresher"
    elif years_at_entry < 3:
        return "junior"
    elif years_at_entry < 6:
        return "mid"
    else:
        return "senior"


async def _generate_rr_for_experience(
    work_experience: list,
    total_experience_years: int,
    skills: list,
    desired_role: str,
) -> list:
    """
    For each work experience entry, generate 4-5 strong, calibrated R&R bullets
    using the roles_responsibilities prompt. Understands existing descriptions
    and upgrades them.
    """
    rr_prompt_variant = prompt_manager.get_random("roles_responsibilities")
    system_prompt = rr_prompt_variant.get("system_prompt", "")

    enriched_experience = []

    for idx, exp in enumerate(work_experience):
        exp_level = _determine_exp_level_at_company(idx, total_experience_years, work_experience)

        existing_desc = exp.get("description", "") or exp.get("achievements", [])
        if isinstance(existing_desc, list):
            existing_desc = "\n".join(existing_desc)

        user_prompt = f"""Generate exactly 4-5 strong roles and responsibilities bullet points for this work experience entry.

CANDIDATE CONTEXT:
- Overall experience at time of this role: {exp_level} level
- Total career experience: {total_experience_years} years
- Core skills: {', '.join(skills[:10])}
- Career goal / desired role: {desired_role}

THIS WORK EXPERIENCE ENTRY:
- Company: {exp.get('company', 'Unknown Company')}
- Role / Position: {exp.get('role', exp.get('position', desired_role))}
- Duration: {exp.get('start_date', '')} to {exp.get('end_date', 'Present')}
- Existing description (understand and upgrade this, do not discard real context):
{existing_desc if existing_desc else 'Not provided — generate based on role and skills'}

Return ONLY a JSON object:
{{
  "company": "{exp.get('company', '')}",
  "role": "{exp.get('role', exp.get('position', desired_role))}",
  "start_date": "{exp.get('start_date', '')}",
  "end_date": "{exp.get('end_date', 'Present')}",
  "responsibilities": [
    "Strong bullet 1 starting with action verb",
    "Strong bullet 2 starting with action verb",
    "Strong bullet 3 starting with action verb",
    "Strong bullet 4 starting with action verb",
    "Strong bullet 5 starting with action verb (optional but preferred)"
  ]
}}

Rules:
- Exactly 4-5 bullets. Never fewer than 4.
- Calibrate scope and language to {exp_level} level.
- Quantify with numbers/percentages where realistic.
- No generic filler. Every bullet must be specific and impactful.
- No markdown, no extra text."""

        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        try:
            ai_response = await llm_service.generate(full_prompt, "gemini")
            content = ai_response.get("content", "").strip()
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content).strip()
            entry_data = json.loads(content)
            enriched_experience.append(entry_data)
        except Exception as e:
            logger.warning("R&R generation failed for %s: %s", exp.get("company"), e)
            # Fallback: keep original with a note
            enriched_experience.append({
                "company": exp.get("company", ""),
                "role": exp.get("role", exp.get("position", desired_role)),
                "start_date": exp.get("start_date", ""),
                "end_date": exp.get("end_date", "Present"),
                "responsibilities": [
                    f"Contributed to {exp.get('role', desired_role)} responsibilities using {', '.join(skills[:3])}",
                    "Collaborated with cross-functional teams to deliver project milestones",
                    "Supported technical implementation and quality assurance processes",
                    "Participated in code reviews and knowledge-sharing sessions",
                ],
            })

    return enriched_experience


@router.post("/profile/bootstrap-cv", response_model=BootstrapCVResponse)
async def bootstrap_cv(
    request: BootstrapCVRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate a sample CV from minimal signup data.
    If the user has existing work experience, understand and upgrade their
    roles & responsibilities calibrated to their experience level at each company.
    """
    try:
        user_id = current_user.get("user_id")
        user = await db.database["users"].find_one({"user_id": user_id}) or {}

        existing_work_exp = user.get("work_experience", [])
        total_exp_years = request.experience_years or user.get("overall_experience_years", 2)
        skills = request.skills or user.get("skills", [])

        # ── Generate R&R for each work experience entry ──────────────────
        if existing_work_exp:
            enriched_experience = await _generate_rr_for_experience(
                existing_work_exp,
                total_exp_years,
                skills,
                request.desired_role,
            )
        else:
            # No real experience — generate one sample entry calibrated to fresher/junior
            exp_level = "fresher" if total_exp_years < 1 else "junior" if total_exp_years < 3 else "mid"
            enriched_experience = await _generate_rr_for_experience(
                [{
                    "company": "Sample Tech Company",
                    "role": request.desired_role,
                    "start_date": "Jan 2023",
                    "end_date": "Present",
                    "description": "",
                }],
                total_exp_years,
                skills,
                request.desired_role,
            )

        # ── Generate professional summary ─────────────────────────────────
        summary_prompt = f"""Write a compelling 3-4 sentence professional summary for:
- Role: {request.desired_role}
- Experience: {total_exp_years} years
- Skills: {', '.join(skills[:8])}
- Qualification: {request.highest_qualification}
Return ONLY the summary text, no JSON, no markdown."""

        try:
            summary_response = await llm_service.generate(summary_prompt, "gemini")
            professional_summary = summary_response.get("content", "").strip()
        except Exception:
            professional_summary = (
                f"Experienced {request.desired_role} with {total_exp_years}+ years of expertise in "
                f"{', '.join(skills[:3])}. Passionate about building scalable solutions and delivering impactful results."
            )

        # ── Projects and certifications from profile or minimal sample ────
        projects = user.get("projects", []) or [{
            "name": f"{skills[0] if skills else request.desired_role} Application",
            "technologies": ", ".join(skills[:3]),
            "description": "Built a full-stack application demonstrating core competencies",
        }]

        certifications = user.get("certifications", []) or [{
            "name": f"{skills[0] if skills else request.desired_role} Professional Certificate",
            "issuer": "Industry Leader",
        }]

        return BootstrapCVResponse(
            professional_summary=professional_summary,
            work_experience=enriched_experience,
            skills=skills,
            projects=projects,
            certifications=certifications,
            is_sample=not bool(existing_work_exp),
            message=(
                "Your existing experience has been enhanced with strong roles & responsibilities."
                if existing_work_exp
                else "This is an AI-generated sample. Fill in your real details for an accurate resume."
            ),
        )

    except Exception as e:
        logger.error("CV bootstrap error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to generate sample CV")
