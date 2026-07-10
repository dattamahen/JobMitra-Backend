"""
Project Contest Schemas for JobMitra Backend.
Supports team-based project submissions with pricing tiers and subscription integration.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from pydantic import BaseModel, Field, EmailStr


# ── Category Definitions ─────────────────────────────────────

TECHNICAL_CATEGORIES = [
    "web_development",
    "mobile_development",
    "ai_ml",
    "data_science",
    "cloud_devops",
    "cybersecurity",
    "blockchain",
    "iot_embedded",
    "game_development",
    "ar_vr",
    "other_technical",
]

NON_TECHNICAL_CATEGORIES = [
    "business_plan",
    "marketing_strategy",
    "social_impact",
    "content_creation",
    "event_management",
    "finance_analytics",
    "hr_management",
    "other_non_technical",
]

ALL_CATEGORIES = TECHNICAL_CATEGORIES + NON_TECHNICAL_CATEGORIES

# ── Pricing ──────────────────────────────────────────────────

PRICING = {
    "solo": 149,       # 1 member
    "team": 599,       # 2-4 members
    "currency": "INR",
}

# ── Subscription Benefits on Purchase ────────────────────────

CONTEST_SUBSCRIPTION_BENEFITS = {
    "mock_interviews": 3,
    "cv_downloads": 5,
}


# ── Models ───────────────────────────────────────────────────

class TeamMember(BaseModel):
    """A team member (non-lead). Must have valid Gmail."""
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role_in_project: Optional[str] = None
    college: Optional[str] = None


class ProjectSubmission(BaseModel):
    """Request model for submitting a project to the contest."""
    # Lead info (from auth)
    lead_user_id: str

    # Project details
    project_title: str = Field(..., min_length=3, max_length=200)
    project_description: str = Field(..., min_length=20, max_length=5000)
    project_type: Literal["technical", "non_technical"]
    category: str  # Must be one of ALL_CATEGORIES
    tech_stack: List[str] = Field(default_factory=list)
    project_url: Optional[str] = None
    demo_url: Optional[str] = None
    github_url: Optional[str] = None

    # Team
    team_members: List[TeamMember] = Field(default_factory=list, max_length=3)

    # College / institution
    college_name: Optional[str] = None
    graduation_year: Optional[int] = None


class ProjectContestEntry(BaseModel):
    """Full contest entry stored in DB."""
    entry_id: str
    lead_user_id: str
    lead_email: str
    lead_name: str

    # Project
    project_title: str
    project_description: str
    project_type: str
    category: str
    tech_stack: List[str] = Field(default_factory=list)
    project_url: Optional[str] = None
    demo_url: Optional[str] = None
    github_url: Optional[str] = None

    # Team
    team_size: int = 1
    team_members: List[Dict[str, Any]] = Field(default_factory=list)

    # Pricing
    amount_paid: float = 0
    pricing_tier: Literal["solo", "team"] = "solo"
    payment_status: Literal["pending", "confirmed", "failed"] = "pending"
    upi_transaction_id: Optional[str] = None

    # Subscription granted
    subscription_granted: bool = False
    subscription_benefits: Dict[str, int] = Field(default_factory=dict)

    # College
    college_name: Optional[str] = None
    graduation_year: Optional[int] = None

    # Status
    status: Literal["draft", "submitted", "under_review", "approved", "rejected"] = "draft"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContestPaymentConfirm(BaseModel):
    """Payment confirmation for contest entry."""
    entry_id: str
    user_id: str
    upi_transaction_id: str
    amount: float
