"""
CV Bootstrap Endpoint
Generates a sample resume preview from minimal user data (role + skills).
Used immediately after signup to show value before user fills complete profile.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from multi_llm_service import MultiLLMService
from auth_endpoints import get_current_user
import logging

router = APIRouter(prefix="/api/v1", tags=["CV Bootstrap"])
logger = logging.getLogger(__name__)
llm_service = MultiLLMService()

BOOTSTRAP_PROMPT = """You are a professional resume writer. Given minimal information about a candidate, generate a COMPLETE sample resume content that looks impressive and realistic.

Generate the following sections as JSON:
{
  "professional_summary": "3-4 sentence compelling summary in first person",
  "work_experience": [
    {"company": "Realistic company name", "position": "Matching role title", "start_date": "Month Year", "end_date": "Present or Month Year", "description": "4-5 bullet points with • starting each line, showing achievements with numbers"}
  ],
  "skills_categorized": ["skill1", "skill2", ...],
  "projects": [
    {"name": "Relevant project name", "technologies": "tech1, tech2", "description": "2-3 lines about the project with impact"}
  ],
  "certifications": [
    {"name": "Relevant certification", "issuer": "Issuing body"}
  ]
}

Rules:
- Make it realistic and industry-appropriate for the given role
- Use the provided skills in work experience descriptions
- Generate 2 work experiences, 2 projects, 2 certifications
- Quantify achievements (percentages, numbers, scale)
- Keep it ATS-friendly
- Return ONLY valid JSON, no markdown, no extra text"""


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


@router.post("/profile/bootstrap-cv", response_model=BootstrapCVResponse)
async def bootstrap_cv(
    request: BootstrapCVRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate a sample CV from minimal signup data to show immediate value."""
    try:
        skills_str = ", ".join(request.skills)

        user_prompt = f"""Generate a sample resume for:
- Desired Role: {request.desired_role}
- Core Skills: {skills_str}
- Experience Level: {request.experience_years} years
- Qualification: {request.highest_qualification}
- Name: {current_user.get('first_name', 'John')} {current_user.get('last_name', 'Doe')}"""

        full_prompt = f"{BOOTSTRAP_PROMPT}\n\n{user_prompt}"

        ai_response = await llm_service.generate(full_prompt, "gemini")
        content = ai_response.get("content", "").strip()

        # Parse JSON response
        import json
        # Clean markdown code blocks if present
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        data = json.loads(content)

        return BootstrapCVResponse(
            professional_summary=data.get("professional_summary", ""),
            work_experience=data.get("work_experience", []),
            skills=request.skills,
            projects=data.get("projects", []),
            certifications=data.get("certifications", []),
            is_sample=True,
            message="This is an AI-generated sample. Fill in your real details for an accurate resume."
        )

    except json.JSONDecodeError:
        logger.error("Failed to parse AI response as JSON")
        # Fallback: return a basic template
        return BootstrapCVResponse(
            professional_summary=f"Experienced {request.desired_role} with {request.experience_years}+ years of expertise in {', '.join(request.skills[:3])}. Passionate about building scalable solutions and delivering impactful results.",
            work_experience=[{
                "company": "Tech Company",
                "position": request.desired_role,
                "start_date": "Jan 2022",
                "end_date": "Present",
                "description": f"• Developed solutions using {', '.join(request.skills[:3])}\n• Collaborated with cross-functional teams\n• Improved system performance by 30%"
            }],
            skills=request.skills,
            projects=[{
                "name": f"{request.skills[0]} Application",
                "technologies": ", ".join(request.skills[:3]),
                "description": "Built a full-stack application demonstrating core competencies"
            }],
            certifications=[{
                "name": f"{request.skills[0]} Professional Certificate",
                "issuer": "Industry Leader"
            }],
            is_sample=True,
            message="This is an AI-generated sample. Fill in your real details for an accurate resume."
        )
    except Exception as e:
        logger.error("CV bootstrap error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to generate sample CV")
