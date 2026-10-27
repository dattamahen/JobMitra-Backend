"""
Project Contest Schemas — 5-level AI-driven contest lifecycle.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from pydantic import BaseModel, Field, EmailStr


# ── Categories ───────────────────────────────────────────────

TECHNICAL_CATEGORIES = [
    "web_development", "mobile_app", "ai_ml", "data_science",
    "cloud_devops", "cybersecurity", "blockchain", "iot",
    "game_development", "open_source",
]

NON_TECHNICAL_CATEGORIES = [
    "business_plan", "social_impact", "design_ux", "content_marketing",
    "research_paper", "entrepreneurship",
]

ALL_CATEGORIES = TECHNICAL_CATEGORIES + NON_TECHNICAL_CATEGORIES

# ── Pricing ──────────────────────────────────────────────────
import os

_solo_fee = int(os.getenv("CONTEST_FEE_SOLO", "149"))
_team_fee = int(os.getenv("CONTEST_FEE_TEAM", "599"))

PRICING = {"solo": _solo_fee, "team": _team_fee, "currency": "INR"}

CONTEST_SUBSCRIPTION_BENEFITS = {"mock_interviews": 3, "cv_downloads": 5}

# ── Status constants ─────────────────────────────────────────

VALID_STATUSES = [
    "spark_submitted",
    "spark_confirmed",
    "blueprint_open",
    "blueprint_submitted",
    "blueprint_evaluated",
    "proof_open",
    "proof_submitted",
    "proof_evaluated",
    "interview_scheduled",
    "interview_in_progress",
    "interview_complete",
    "finalist",
    "winner",
    "eliminated",
]

# Days before each level opens after the previous gate clears
LEVEL_WAIT_DAYS = {
    "blueprint": 30,   # after spark_confirmed
    "proof": 30,       # after blueprint_evaluated
    "interview": 30,   # after proof_evaluated
}

# AI score thresholds to advance
SCORE_THRESHOLDS = {
    "idea_quality": 60,
    "blueprint": 65,
    "demo": 70,
    "interview": 72,
}


# ── Request Models ───────────────────────────────────────────

class TeamMember(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role_in_project: Optional[str] = None
    college: Optional[str] = None


class SparkSubmitRequest(BaseModel):
    """Level 1 — raw idea submission."""
    raw_project_name: str = Field(..., min_length=3, max_length=200)
    raw_description: str = Field(..., min_length=10, max_length=1000)
    project_type: Literal["technical", "non_technical"]
    category: str
    tech_stack: List[str] = Field(default_factory=list)
    team_members: List[TeamMember] = Field(default_factory=list, max_length=3)
    college_name: Optional[str] = None
    graduation_year: Optional[int] = None


class SparkConfirmRequest(BaseModel):
    """Level 1 — team confirms the LLM-refined idea."""
    entry_id: str
    confirmed: bool


class ContestPaymentConfirm(BaseModel):
    entry_id: str
    user_id: str
    upi_transaction_id: str
    amount: float


class BlueprintAnswerItem(BaseModel):
    question_number: int
    answer: str = Field(..., min_length=20)


class BlueprintSubmitRequest(BaseModel):
    """Level 2 — team submits answers to the questionnaire."""
    entry_id: str
    answers: List[BlueprintAnswerItem] = Field(..., min_length=12, max_length=12)


class ProofSubmitRequest(BaseModel):
    """Level 3 — team submits demo/proof links.
    Technical: youtube_url + github_url required.
    Non-technical: youtube_url required; github_url optional; document_url/report_url for reports.
    """
    entry_id: str
    youtube_url: str = Field(..., min_length=10)          # required for all
    github_url: Optional[str] = None                      # technical projects
    demo_url: Optional[str] = None                        # optional live demo
    document_url: Optional[str] = None                    # non-technical: Google Drive / Notion / Canva
    report_url: Optional[str] = None                      # non-technical: research paper / PDF link


class InterviewAnswerRequest(BaseModel):
    """Level 4 — participant submits one answer."""
    entry_id: str
    participant_user_id: str
    round_number: int = Field(..., ge=1, le=3)
    question_id: int = Field(..., ge=1, le=8)
    answer: str = Field(..., min_length=10)
