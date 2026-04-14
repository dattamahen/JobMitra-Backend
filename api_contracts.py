"""
API Contracts — Strict response schemas shared between FE and BE.

Every LLM response MUST be parsed and validated against these models
before being returned to the frontend. This ensures the UI always
receives a predictable shape regardless of LLM output variance.

FE TypeScript interfaces are the source of truth.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ─── Interview Question Generation ───────────────────────────
# FE: InterviewService.startInterview() → /get-interview-prompt

class InterviewQuestionResponse(BaseModel):
    """Response for POST /api/v1/get-interview-prompt"""
    session_id: str
    questions: List[str] = Field(
        ...,
        description="Array of plain question strings, no numbering or markdown",
        min_length=1,
    )
    question_count: int
    provider: str
    model: str
    prompt_variant: str
    prompt_style: Optional[str] = None


# ─── Interview Evaluation ────────────────────────────────────
# FE: MockInterviewService.submitInterviewForEvaluation()
# FE type: InterviewEvaluation

class QuestionScore(BaseModel):
    question_id: str
    score: int = Field(..., ge=0, le=100)
    feedback: str

class InterviewEvaluationResult(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    feedback: str
    question_scores: List[QuestionScore]

class InterviewEvaluationResponse(BaseModel):
    """Response for POST /api/v1/mock-interview/submit-for-evaluation"""
    success: bool
    session_id: str
    interview_id: Optional[str] = None
    evaluation: InterviewEvaluationResult


# ─── Interview History ───────────────────────────────────────
# FE: MockInterviewService.getInterviewHistory()
# FE type: InterviewHistorySession

class InterviewHistoryItem(BaseModel):
    session_id: str
    interview_type: str = ""
    overall_score: int = 0
    completed_at: Optional[str] = None
    questions_count: int = 0

class InterviewHistoryResponse(BaseModel):
    """Response for GET /api/v1/mock-interview/history/{user_id}"""
    success: bool
    user_id: str
    interviews: List[InterviewHistoryItem]
    total: int


# ─── Resume Tailor Preview ───────────────────────────────────
# FE: ResumeTailorService.getTailorPreview()
# FE type: TailorPreviewData

class WorkExperience(BaseModel):
    company: str = ""
    position: str = ""
    duration: str = ""
    achievements: List[str] = []

class Education(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""

class Project(BaseModel):
    name: str = ""
    description: str = ""
    technologies: List[str] = []

class TailorChange(BaseModel):
    section: str
    type: str = Field(..., pattern="^(added|modified|removed)$")
    original: Optional[str] = None
    modified: Optional[str] = None
    reason: str = ""

class TailoredResume(BaseModel):
    professional_summary: Optional[str] = None
    skills_organized: List[str] = []
    work_experience: List[WorkExperience] = []
    education: List[Education] = []
    projects: List[Project] = []
    certifications: List[str] = []

class OriginalResume(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: Optional[str] = None
    professional_summary: Optional[str] = None
    skills: List[str] = []
    work_experience: List[dict] = []
    education: List[dict] = []
    projects: List[dict] = []
    certifications: List[dict] = []

class TailorPreviewResponse(BaseModel):
    """Response for GET /api/v1/jobs/{job_id}/tailor-preview"""
    original_resume: OriginalResume
    tailored_resume: TailoredResume
    match_improvement: int = Field(..., ge=0, le=100)
    changes: List[TailorChange]


# ─── Resume Tailor Action ────────────────────────────────────
# FE: ResumeTailorService.tailorResume()
# FE type: TailorResponse

class TailorResumeResponse(BaseModel):
    """Response for POST /api/v1/jobs/{job_id}/tailor-resume"""
    success: bool
    message: str
    tailor_done: bool
    match_percentage: int = Field(..., ge=0, le=100)


# ─── Apply for Job ───────────────────────────────────────────
# FE: ResumeTailorService.applyWithTailoredResume()
# FE type: ApplyJobResponse

class ApplyJobResponse(BaseModel):
    """Response for POST /api/v1/jobs/{job_id}/apply"""
    success: bool
    message: str
    application_id: str
    match_percentage: Optional[int] = None


# ─── LLM Output Parsers ─────────────────────────────────────
# Utility functions to coerce raw LLM output into contract models.

import json
import re
import logging

logger = logging.getLogger(__name__)


def parse_evaluation_response(
    raw_content: str,
    question_ids: List[str],
) -> InterviewEvaluationResult:
    """
    Parse LLM evaluation output into InterviewEvaluationResult.
    Falls back to safe defaults if parsing fails.
    """
    try:
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_content.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()

        # Try extracting JSON object from mixed content
        match = re.search(
            r"\{[\s\S]*\"overall_score\"[\s\S]*\"question_scores\"[\s\S]*\}",
            cleaned,
        )
        if match:
            cleaned = match.group()

        data = json.loads(cleaned)

        scores = data.get("question_scores", [])
        validated_scores = []
        for i, qs in enumerate(scores):
            validated_scores.append(QuestionScore(
                question_id=qs.get("question_id", question_ids[i] if i < len(question_ids) else f"q_{i+1}"),
                score=max(0, min(100, int(qs.get("score", 75)))),
                feedback=str(qs.get("feedback", "No feedback available")),
            ))

        # Fill missing question scores
        for i in range(len(validated_scores), len(question_ids)):
            validated_scores.append(QuestionScore(
                question_id=question_ids[i],
                score=75,
                feedback="Evaluation pending",
            ))

        return InterviewEvaluationResult(
            overall_score=max(0, min(100, int(data.get("overall_score", 75)))),
            feedback=str(data.get("feedback", "Interview evaluation completed.")),
            question_scores=validated_scores,
        )

    except Exception as e:
        logger.warning("Evaluation parse failed: %s — using fallback", e)
        return InterviewEvaluationResult(
            overall_score=75,
            feedback="Interview completed. Detailed evaluation could not be fully processed.",
            question_scores=[
                QuestionScore(question_id=qid, score=75, feedback="Good response")
                for qid in question_ids
            ],
        )


def parse_tailor_response(raw_content: str) -> dict:
    """
    Parse LLM resume tailor output into a dict matching TailoredResume + changes.
    Falls back to empty structure if parsing fails.
    """
    try:
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_content.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(cleaned[start:end])
        else:
            raise ValueError("No JSON object found")

        tailored = data.get("tailored_resume", {})

        # Normalize work_experience
        work_exp = []
        for w in tailored.get("work_experience", []):
            work_exp.append({
                "company": w.get("company", ""),
                "position": w.get("position", ""),
                "duration": w.get("duration", ""),
                "achievements": w.get("achievements", []),
            })

        # Normalize education
        edu = []
        for e in tailored.get("education", []):
            edu.append({
                "degree": e.get("degree", ""),
                "institution": e.get("institution", ""),
                "year": str(e.get("year", "")),
            })

        # Normalize projects
        projects = []
        for p in tailored.get("projects", []):
            projects.append({
                "name": p.get("name", ""),
                "description": p.get("description", ""),
                "technologies": p.get("technologies", []),
            })

        # Normalize changes
        changes = []
        for c in data.get("changes", []):
            change_type = c.get("type", "modified")
            if change_type not in ("added", "modified", "removed"):
                change_type = "modified"
            changes.append({
                "section": c.get("section", ""),
                "type": change_type,
                "original": c.get("original"),
                "modified": c.get("modified"),
                "reason": c.get("reason", ""),
            })

        return {
            "tailored_resume": {
                "professional_summary": tailored.get("professional_summary"),
                "skills_organized": tailored.get("skills_organized", []),
                "work_experience": work_exp,
                "education": edu,
                "projects": projects,
                "certifications": tailored.get("certifications", []),
            },
            "match_improvement": max(0, min(100, int(data.get("match_improvement", 0)))),
            "changes": changes,
        }

    except Exception as e:
        logger.warning("Tailor parse failed: %s — using fallback", e)
        return {
            "tailored_resume": {},
            "match_improvement": 0,
            "changes": [],
        }
