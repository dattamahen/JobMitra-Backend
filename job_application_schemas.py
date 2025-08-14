"""
Job Application schemas for applicant tracking
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    SHORTLISTED = "shortlisted"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    OFFER_EXTENDED = "offer_extended"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class ProfileMatchAnalysis(BaseModel):
    """Profile match analysis for job application"""
    overall_match_percentage: float = Field(..., ge=0, le=100)
    skills_match_percentage: float = Field(..., ge=0, le=100)
    experience_match_percentage: float = Field(..., ge=0, le=100)
    education_match_percentage: float = Field(..., ge=0, le=100)
    
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    
    recommendation: str = ""

class JobApplication(BaseModel):
    """Job application model"""
    application_id: str
    job_id: str
    user_id: str
    
    # Application details
    applied_date: datetime = Field(default_factory=datetime.utcnow)
    status: ApplicationStatus = ApplicationStatus.APPLIED
    cover_letter: Optional[str] = None
    
    # Profile match analysis
    profile_match: Optional[ProfileMatchAnalysis] = None
    
    # Metadata
    source: str = "internal"  # internal, external, referral
    notes: Optional[str] = None

class ApplicantProfile(BaseModel):
    """Simplified applicant profile for HR view"""
    user_id: str
    full_name: str
    email: str
    phone: Optional[str] = None
    
    # Professional info
    overall_experience_years: Optional[int] = None
    current_role: Optional[str] = None
    skills: List[str] = []
    highest_qualification: Optional[str] = None
    
    # Application specific
    application_id: str
    applied_date: datetime
    status: ApplicationStatus
    profile_match: Optional[ProfileMatchAnalysis] = None

class JobApplicationsResponse(BaseModel):
    """Response for job applications"""
    job_id: str
    job_title: str
    total_applications: int
    applications: List[ApplicantProfile]