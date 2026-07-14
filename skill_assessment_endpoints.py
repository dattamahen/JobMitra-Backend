"""
Skill Assessment API Endpoints - Placeholder Implementation
"""

import logging
import json
import re
import uuid

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import random
from auth_endpoints import get_current_user
from auth_db import get_user_by_id
from activity_tracker import log_user_activity
from multi_llm_service import MultiLLMService
from prompt_manager import prompt_manager
from db import get_user_mock_interviews, get_learning_resources

llm_service = MultiLLMService()

router = APIRouter(prefix="/api/v1/skill-assessment", tags=["Skill Assessment"])

# Pydantic Models
class SkillLevel(BaseModel):
    skill_id: str
    skill_name: str
    current_level: int  # 0-100
    level_text: str
    category: str

class AssessmentResult(BaseModel):
    id: str
    skill_name: str
    score: int
    level: str
    completed_date: datetime
    has_certificate: bool

class MockInterviewRequest(BaseModel):
    skill_name: str
    user_id: str

class LearningResource(BaseModel):
    id: str
    title: str
    description: str
    youtube_url: str
    channel: str
    duration: str
    level: str
    skill: str
    rating: Optional[float] = None



def get_level_text(level: int) -> str:
    """Convert numeric level to text"""
    if level >= 80:
        return "Expert"
    elif level >= 60:
        return "Advanced"
    elif level >= 40:
        return "Intermediate"
    else:
        return "Beginner"

def get_experience_level(experience: str) -> int:
    """Convert experience string to numeric level"""
    exp = experience.lower()
    if "expert" in exp or "5+" in exp or "senior" in exp:
        return 85
    elif "advanced" in exp or "4+" in exp:
        return 75
    elif "intermediate" in exp or "3-5" in exp or "mid" in exp:
        return 65
    else:
        return 45

MOCK_LEARNING_RESOURCES = [
    {
        "id": "1",
        "title": "Complete JavaScript Tutorial for Beginners",
        "description": "Learn JavaScript from scratch with practical examples",
        "youtube_url": "https://www.youtube.com/watch?v=PkZNo7MFNFg",
        "channel": "freeCodeCamp",
        "duration": "3:26:42",
        "level": "beginner",
        "skill": "JavaScript",
        "rating": 4.8
    },
    {
        "id": "2",
        "title": "Python Full Course for Beginners",
        "description": "Complete Python programming course covering all fundamentals",
        "youtube_url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
        "channel": "Programming with Mosh",
        "duration": "6:14:07",
        "level": "beginner", 
        "skill": "Python",
        "rating": 4.9
    }
]

@router.get("/skills/technical")
async def get_technical_skills(current_user: dict = Depends(get_current_user)) -> List[SkillLevel]:
    """Get user's technical skills with current levels"""
    try:
        user_profile = await get_user_by_id(current_user["user_id"])
        if not user_profile:
            return []
        
        technical_skills = []
        skill_names = set()
        
        # Prioritize technical_skills (more detailed) over general skills
        if user_profile.get("technical_skills"):
            for i, tech_skill in enumerate(user_profile["technical_skills"]):
                skill_name = tech_skill["name"]
                if skill_name not in skill_names:
                    level = get_experience_level(tech_skill.get("experience", "beginner"))
                    technical_skills.append({
                        "skill_id": f"tech_{i}",
                        "skill_name": skill_name,
                        "current_level": level,
                        "level_text": get_level_text(level),
                        "category": "technical"
                    })
                    skill_names.add(skill_name)
        
        # Add remaining skills from general skills array
        if user_profile.get("skills"):
            for i, skill in enumerate(user_profile["skills"]):
                if skill not in skill_names:
                    level = random.randint(40, 85)
                    technical_skills.append({
                        "skill_id": f"skill_{i}",
                        "skill_name": skill,
                        "current_level": level,
                        "level_text": get_level_text(level),
                        "category": "technical"
                    })
                    skill_names.add(skill)
        
        return [SkillLevel(**skill) for skill in technical_skills]
    except Exception as e:
        logger.error("fetching technical skills: %s", e)
        return []

@router.get("/skills/soft")
async def get_soft_skills(current_user: dict = Depends(get_current_user)) -> List[SkillLevel]:
    """Get user's soft skills with current levels"""
    try:
        user_profile = await get_user_by_id(current_user["user_id"])
        if not user_profile:
            return []
        
        # Generate soft skills based on current role or skills
        soft_skills = []
        current_role = user_profile.get("current_role", "")
        
        soft_skills_map = {
            "frontend": ["Communication", "Creativity", "User Experience"],
            "backend": ["Problem Solving", "Analytical Thinking", "Attention to Detail"],
            "fullstack": ["Leadership", "Time Management", "Adaptability"],
            "devops": ["Critical Thinking", "Collaboration", "Process Improvement"],
            "data": ["Research Skills", "Statistical Analysis", "Data Visualization"]
        }
        
        generated_skills = set()
        if current_role:
            role_lower = current_role.lower()
            for key, skills in soft_skills_map.items():
                if key in role_lower:
                    generated_skills.update(skills)
        
        if not generated_skills:
            generated_skills = {"Communication", "Problem Solving", "Teamwork"}
        
        for i, skill in enumerate(generated_skills):
            soft_skills.append({
                "skill_id": f"soft_{i}",
                "skill_name": skill,
                "current_level": random.randint(50, 80),
                "level_text": get_level_text(random.randint(50, 80)),
                "category": "soft"
            })
        
        return [SkillLevel(**skill) for skill in soft_skills]
    except Exception as e:
        logger.error("fetching soft skills: %s", e)
        return []

@router.get("/history")
async def get_assessment_history(current_user: dict = Depends(get_current_user)) -> List[AssessmentResult]:
    """Get user's assessment history from DB"""
    try:
        interviews = await get_user_mock_interviews(current_user["user_id"])
        results = []
        for i, interview in enumerate(interviews):
            results.append(AssessmentResult(
                id=interview.get("_id", str(i)),
                skill_name=interview.get("interview_type", "General"),
                score=interview.get("overall_score", 0),
                level=get_level_text(interview.get("overall_score", 0)),
                completed_date=interview.get("completed_at", interview.get("created_at", datetime.utcnow())),
                has_certificate=interview.get("overall_score", 0) >= 70,
            ))
        return results
    except Exception as e:
        logger.error("fetching assessment history: %s", e)
        return []

@router.post("/take-test/{skill_id}")
async def take_skill_test(skill_id: str, current_user: dict = Depends(get_current_user)):
    """Start a skill assessment test"""
    test_id = f"test_{skill_id}_{random.randint(1000, 9999)}"

    await log_user_activity(
        current_user["user_id"],
        "skill_assessment",
        f"Started skill assessment for {skill_id}",
        {"skill_id": skill_id, "test_id": test_id},
    )

    return {
        "message": f"Assessment for {skill_id} started",
        "test_id": test_id,
        "questions_count": 20,
        "duration_minutes": 30
    }

@router.post("/mock-interview")
async def start_mock_interview(request: MockInterviewRequest):
    """Start a skill-focused mock interview session using LLM"""
    system_prompt = prompt_manager.get_random(
        "interview_questions", user_id=request.user_id
    ).get("system_prompt", "You are an expert technical interviewer.")

    prompt = f"""{system_prompt}

Generate exactly 10 focused interview questions specifically about "{request.skill_name}".
Questions must test deep knowledge of {request.skill_name} only — concepts, best practices, real-world usage, and problem-solving.

STRICT OUTPUT RULES:
- Return ONLY a valid JSON object
- Format: {{"questions": ["question 1", "question 2", ...]}}
- Each question must be a single concise string
- No markdown, no numbering, no extra text
- Start with {{ and end with }}"""

    try:
        ai_response = await llm_service.generate(prompt, "gemini")
        content = ai_response.get("content", "").strip()
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content).strip()
        data = json.loads(content)
        questions = data.get("questions", [])
        if not questions:
            raise ValueError("Empty questions list")
    except Exception as e:
        logger.warning("LLM question generation failed, using fallback: %s", e)
        questions = [
            f"What are the core concepts of {request.skill_name}?",
            f"How have you used {request.skill_name} in a real project?",
            f"What are common pitfalls when working with {request.skill_name}?",
        ]

    return {
        "message": f"Mock interview for {request.skill_name} started",
        "session_id": str(uuid.uuid4()),
        "questions": questions,
        "question_count": len(questions),
        "duration_minutes": 15,
        "skill": request.skill_name,
    }

@router.get("/learning-resources/{skill_name}")
async def get_skill_learning_resources(skill_name: str) -> List[LearningResource]:
    """Get learning resources for a specific skill from DB"""
    try:
        resources = await get_learning_resources(skill=skill_name)
        return [
            LearningResource(
                id=str(r.get("_id", r.get("id", ""))),
                title=r.get("title", ""),
                description=r.get("description", ""),
                youtube_url=r.get("youtube_url", r.get("url", "")),
                channel=r.get("channel", ""),
                duration=r.get("duration", str(r.get("duration_minutes", ""))),
                level=r.get("level", "beginner"),
                skill=r.get("skill", skill_name),
                rating=r.get("rating"),
            )
            for r in resources
        ]
    except Exception as e:
        logger.error("fetching learning resources: %s", e)
        return []

@router.get("/usage-status")
async def get_usage_status():
    """Get mock interview usage status"""
    return {
        "interviews_used": 2,
        "interviews_remaining": 3,
        "weekly_limit": 5,
        "next_reset": datetime.utcnow() + timedelta(days=3),
        "can_take_interview": True
    }

@router.get("/recommended-skills")
async def get_recommended_skills():
    """Get AI recommended skills for improvement"""
    return [
        {
            "id": "docker",
            "name": "Docker",
            "relevance_reason": "High demand in your target job roles"
        },
        {
            "id": "aws",
            "name": "AWS",
            "relevance_reason": "Complements your current tech stack"
        },
        {
            "id": "typescript",
            "name": "TypeScript", 
            "relevance_reason": "Natural progression from JavaScript"
        }
    ]

@router.post("/contribute-resource")
async def contribute_learning_resource(resource_data: dict):
    """Allow users to contribute learning resources"""
    return {
        "message": "Thank you for contributing! Your resource will be reviewed.",
        "contribution_id": f"contrib_{random.randint(1000, 9999)}",
        "status": "pending_review"
    }

@router.get("/certificate/{assessment_id}")
async def get_certificate(assessment_id: str):
    """Generate/download certificate for completed assessment"""
    return {
        "certificate_url": f"https://certificates.jobmitra.com/{assessment_id}.pdf",
        "certificate_id": f"CERT_{assessment_id.upper()}",
        "issued_date": datetime.utcnow().isoformat() + "Z"
    }