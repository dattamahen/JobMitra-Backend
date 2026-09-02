"""
Pydantic schemas for Internal Job Postings (Refer & Hire / Internal Job Market).
Any verified job-seeker can post a job from their company using official email OTP.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum


class InternalJobStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REMOVED = "removed"


class InternalJobPostRequest(BaseModel):
    """Payload for creating an internal job post (manual entry)."""
    title: str = Field(..., min_length=3, max_length=200)
    company: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=20, max_length=5000)
    skills_required: List[str] = Field(..., min_items=1, max_items=30)
    experience_level: str = Field(default="mid")          # entry/mid/senior/lead
    employment_type: str = Field(default="full-time")     # full-time/part-time/contract
    job_type: str = Field(default="onsite")               # remote/onsite/hybrid
    location_city: str = Field(default="India")
    location_state: str = Field(default="")
    requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    # Official company email used for OTP verification
    official_email: EmailStr
    # OTP token returned from /internal-jobs/send-otp
    otp_token: str


class InternalJobFromLLMRequest(BaseModel):
    """Payload after LLM parses image/CSV — user confirms before posting."""
    parsed_job: InternalJobPostRequest
    # same OTP token
    otp_token: str


class SendOTPRequest(BaseModel):
    official_email: EmailStr


class VerifyOTPRequest(BaseModel):
    official_email: EmailStr
    otp: str


class InternalJobListing(BaseModel):
    """Full internal job document (DB + API response)."""
    internal_job_id: str
    title: str
    company: str
    description: str
    skills_required: List[str]
    experience_level: str
    employment_type: str
    job_type: str
    location: dict                  # {city, state, country, is_remote}
    requirements: List[str]
    responsibilities: List[str]
    # Poster info
    posted_by_user_id: str
    posted_by_email: str            # personal account email
    official_email: str             # verified company email
    # Metadata
    posted_date: datetime
    expires_at: datetime            # posted_date + 15 days
    status: InternalJobStatus = InternalJobStatus.ACTIVE
    is_active: bool = True
    views_count: int = 0
    applications_count: int = 0
    # Generic defaults (no salary exposed)
    source: str = "internal_referral"


class InternalJobSearchFilters(BaseModel):
    keywords: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    job_type: Optional[str] = None
    page: int = 1
    per_page: int = 10


class InternalJobApplyRequest(BaseModel):
    internal_job_id: str
    force_apply: bool = False


class ParseJobFromMediaRequest(BaseModel):
    """Request to parse job details from image/CSV text via LLM."""
    raw_text: str = Field(..., min_length=10, description="Extracted text from image or CSV")
    official_email: EmailStr
    otp_token: str
