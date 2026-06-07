"""
AI Content Generation Endpoint
Unified endpoint for generating AI-powered profile content.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal
from multi_llm_service import MultiLLMService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
llm_service = MultiLLMService()

SUMMARY_SYSTEM_PROMPT = """You are a senior career strategist who has written professional summaries for executives at Google, Amazon, and Microsoft. You craft summaries that make hiring managers stop scrolling.

Write a powerful professional summary (4-6 sentences, 200-400 words) that:

1. Opens with a strong identity statement — who they are, their specialization, and years of experience
2. Highlights 3-4 of their strongest technical skills with context on HOW they've used them (not just listing)
3. Quantifies impact where possible — scale, performance improvements, team size, users served
4. Mentions their domain/industry expertise and what makes them unique
5. Closes with their career direction or the value they bring to organizations

Style rules:
- Write in FIRST PERSON
- Use active voice and strong action verbs (architected, spearheaded, optimized, scaled)
- Be specific — mention actual technologies, frameworks, and methodologies
- NO generic buzzwords: avoid "passionate", "results-driven", "team player", "self-motivated", "detail-oriented"
- NO bullet points — write in flowing paragraph form
- Make it sound human and confident, not robotic
- Tailor the tone to their experience level (junior = eager learner, senior = proven leader, mid = growing expert)
- ATS-friendly: naturally weave in keywords from their skills

Return ONLY the summary text. No quotes, no labels, no markdown, no extra formatting."""

JOB_DESCRIPTION_PROMPT = """You are a senior resume writer who specializes in writing impactful job descriptions for resumes.

Generate a compelling job description with achievements (4-6 bullet points) for the given role.

Rules:
- Write in PAST TENSE (unless it's a current role)
- Start each bullet with a strong action verb (Architected, Spearheaded, Optimized, Delivered, Led, Built, Reduced, Increased, Automated, Migrated)
- QUANTIFY impact wherever possible (percentages, numbers, scale, team size, revenue, users)
- Be specific to the technologies and skills mentioned
- Each bullet should show: Action + Context + Impact/Result
- Keep each bullet to 1-2 lines max
- Make it ATS-friendly with relevant keywords
- NO generic statements like "Responsible for..." or "Worked on..."
- Format as bullet points starting with •
- Return ONLY the bullet points, no headers or extra text"""


class GenerateAIContentRequest(BaseModel):
    type: Literal["professional_summary", "job_description"]

    # Common fields
    skills: Optional[List[str]] = []
    experience_years: Optional[int] = 0

    # Professional summary fields
    current_role: Optional[str] = ""
    current_company: Optional[str] = ""
    highest_qualification: Optional[str] = ""
    desired_job_title: Optional[str] = ""
    work_experience: Optional[List[dict]] = []
    projects: Optional[List[dict]] = []
    certifications: Optional[List[dict]] = []

    # Job description fields
    position: Optional[str] = ""
    company: Optional[str] = ""
    is_current: Optional[bool] = False


class GenerateAIContentResponse(BaseModel):
    content: str


@router.post("/profile/generate-ai-content", response_model=GenerateAIContentResponse)
async def generate_ai_content(request: GenerateAIContentRequest):
    """Unified endpoint for generating AI-powered profile content."""
    try:
        if request.type == "professional_summary":
            content = await _generate_summary(request)
        else:
            content = await _generate_job_description(request)

        if not content:
            raise HTTPException(status_code=500, detail="Failed to generate content")

        return GenerateAIContentResponse(content=content)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI content ({request.type}): {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate {request.type.replace('_', ' ')}")


async def _generate_summary(request: GenerateAIContentRequest) -> str:
    skills_str = ", ".join(request.skills) if request.skills else "Not specified"

    experience_context = ""
    if request.work_experience:
        exp_lines = []
        for exp in request.work_experience[:3]:
            company = exp.get("company", "")
            position = exp.get("position", "")
            description = exp.get("description", "")
            line = f"- {position} at {company}"
            if description:
                line += f" — {description[:150]}"
            if company or position:
                exp_lines.append(line)
        if exp_lines:
            experience_context = "\nRecent Work History:\n" + "\n".join(exp_lines)

    projects_context = ""
    if request.projects:
        proj_lines = []
        for proj in request.projects[:3]:
            name = proj.get("name", "")
            tech = proj.get("technologies", "")
            desc = proj.get("description", "")
            if name:
                line = f"- {name}"
                if tech:
                    line += f" (Tech: {tech})"
                if desc:
                    line += f" — {desc[:100]}"
                proj_lines.append(line)
        if proj_lines:
            projects_context = "\nKey Projects:\n" + "\n".join(proj_lines)

    certs_context = ""
    if request.certifications:
        cert_names = [c.get("name", "") for c in request.certifications if c.get("name")]
        if cert_names:
            certs_context = f"\nCertifications: {', '.join(cert_names[:5])}"

    exp_years = request.experience_years or 0
    if exp_years <= 2:
        level_hint = "This is a JUNIOR professional — emphasize eagerness to learn, strong foundations, and potential."
    elif exp_years <= 5:
        level_hint = "This is a MID-LEVEL professional — emphasize growing expertise, hands-on delivery, and technical depth."
    elif exp_years <= 10:
        level_hint = "This is a SENIOR professional — emphasize leadership, architecture decisions, mentoring, and business impact."
    else:
        level_hint = "This is a STAFF/PRINCIPAL level professional — emphasize strategic thinking, org-wide impact, and technical vision."

    user_prompt = f"""Generate a professional summary for this candidate:

{level_hint}

- Current Role: {request.current_role or 'Not specified'}
- Current Company: {request.current_company or 'Not specified'}
- Total Experience: {exp_years} years
- Core Technical Skills: {skills_str}
- Highest Qualification: {request.highest_qualification or 'Not specified'}
- Target Role: {request.desired_job_title or request.current_role or 'Not specified'}{experience_context}{projects_context}{certs_context}"""

    full_prompt = f"{SUMMARY_SYSTEM_PROMPT}\n\n{user_prompt}"
    ai_response = await llm_service.generate(full_prompt, "gemini")
    return ai_response.get("content", "").strip().strip('"').strip("'")


async def _generate_job_description(request: GenerateAIContentRequest) -> str:
    skills_str = ", ".join(request.skills) if request.skills else "Not specified"
    tense = "present tense (current role)" if request.is_current else "past tense"

    user_prompt = f"""Generate job description bullet points for:

- Job Title: {request.position}
- Company: {request.company or 'Not specified'}
- Relevant Skills/Technologies: {skills_str}
- Candidate's Total Experience: {request.experience_years} years
- Write in: {tense}

Generate 4-6 achievement-focused bullet points for this role."""

    full_prompt = f"{JOB_DESCRIPTION_PROMPT}\n\n{user_prompt}"
    ai_response = await llm_service.generate(full_prompt, "gemini")
    return ai_response.get("content", "").strip().strip('"').strip("'")
