"""
Authentication and User Management Schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator, constr
from datetime import datetime
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from typing import Optional, Dict, Any, List, Union

# New helper models for user data
class PreviousOrganization(BaseModel):
    """Previous organization information."""
    company_name: str
    position: str
    duration: str
    description: Optional[str] = None

class Certification(BaseModel):
    """Certification information."""
    name: str
    issuer: str
    issue_date: Optional[Union[str, datetime]] = None
    expiry_date: Optional[Union[str, datetime]] = None
    credential_id: Optional[str] = None
    link: Optional[str] = None

class CommunicationSkill(BaseModel):
    """Communication skill information."""
    skill: str
    level: Literal["beginner", "intermediate", "advanced", "expert"] = "intermediate"

class RecentActivity(BaseModel):
    """Recent user activity."""
    activity_type: Literal["application", "job_application", "interview", "profile_update", "skill_assessment", "mock_interview", "resume_update"]
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SocialLinks(BaseModel):
    """Social media links."""
    github: Optional[str] = None
    youtube: Optional[str] = None
    linkedin: Optional[str] = None
    playstore: Optional[str] = None

# Authentication Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Updated user response with comprehensive fields."""
    user_id: str
    email: str
    
    # Basic Personal Information
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    
    # Professional Information
    overall_experience_years: Optional[int] = None
    highest_qualification: Optional[str] = None
    previous_organizations: List[PreviousOrganization] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    contributions: Optional[str] = None
    communication_skills: List[CommunicationSkill] = Field(default_factory=list)
    ai_tools: List[str] = Field(default_factory=list)
    
    # Social Links
    github_link: Optional[str] = None
    youtube_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    playstore_link: Optional[str] = None
    
    # Job Application Tracking
    overall_jobs_applied: List[Dict[str, Any]] = Field(default_factory=list)
    
    # User Classification
    user_type: Literal["candidate", "hire"] = "candidate"
    user_status: Literal["active", "inactive", "pending_verification"] = "active"
    user_plan: Literal["F", "P", "S"] = "F"
    
    # Feature Usage Tracking
    feature_usage_count: int = 5
    
    # Preferences
    job_preferences: List[Literal["remote", "hybrid", "on-site"]] = Field(default_factory=list)
    employment_type: List[Literal["full-time", "part-time", "freelancing", "contract"]] = Field(default_factory=list)
    
    # Timestamps
    profile_created_on: datetime
    last_active: datetime
    
    # Analytics and Metrics
    match_analysis_count: int = 0
    match_tailored_count: int = 0
    mock_interview_count: int = 0
    profile_completion_count: int = 0
    profile_visits: int = 0
    recent_activity: List[RecentActivity] = Field(default_factory=list)
    
    # Legacy compatibility
    username: Optional[str] = None
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    is_active: bool = True
    is_verified: Optional[bool] = False
    profile_completion: Optional[int] = 0
    created_at: str
    city: Optional[str] = None
    state: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class RegisterRequest(BaseModel):
    """Minimal registration request with only required fields."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    user_type: Literal["candidate", "hire"] = "candidate"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

class UserProfileResponse(BaseModel):
    """Comprehensive user profile response."""
    user_id: str
    email: str
    
    # Basic Personal Information
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    
    # Professional Information
    overall_experience_years: Optional[int] = None
    highest_qualification: Optional[str] = None
    previous_organizations: List[PreviousOrganization] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    technical_skills: List[Dict[str, Any]] = Field(default_factory=list)
    work_experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    contributions: Optional[str] = None
    communication_skills: List[CommunicationSkill] = Field(default_factory=list)
    ai_tools: List[str] = Field(default_factory=list)
    professional_summary: Optional[str] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    portfolio_link: Optional[str] = None
    desired_job_title: Optional[str] = None
    expected_salary: Optional[float] = None
    currency: Optional[str] = None
    linkedin_link: Optional[str] = None
    github_link: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    
    # Social Links
    social_links: Optional[SocialLinks] = None
    
    # Job Application Tracking
    overall_jobs_applied: List[Dict[str, Any]] = Field(default_factory=list)
    
    # User Classification
    user_type: Literal["candidate", "hire"] = "candidate"
    user_status: Literal["active", "inactive", "pending_verification"] = "active"
    user_plan: Literal["free", "subscribed", "pro"] = "free"
    
    # Preferences
    job_preferences: List[Literal["remote", "hybrid", "on-site"]] = Field(default_factory=list)
    employment_type: List[Literal["full-time", "part-time", "freelancing", "contract"]] = Field(default_factory=list)
    
    # Timestamps
    profile_created_on: datetime
    last_active: datetime
    
    # Analytics and Metrics
    match_analysis_count: int = 0
    match_tailored_count: int = 0
    mock_interview_count: int = 0
    profile_completion_count: int = 0
    profile_visits: int = 0
    recent_activity: List[RecentActivity] = Field(default_factory=list)
    
    # Legacy compatibility
    username: Optional[str] = None
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    personal_info: Optional[Dict[str, Any]] = None
    professional_info: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: bool = True
    is_verified: bool = False
    profile_completion: Optional[int] = 0
    created_at: str
    updated_at: str
    last_login: Optional[str] = None
    
    class Config:
        extra = "allow"

# User Update Models
class UserProfileUpdateRequest(BaseModel):
    """Comprehensive user profile update request."""
    # Basic Personal Information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    
    # Professional Information
    overall_experience_years: Optional[int] = Field(None, ge=0)
    highest_qualification: Optional[str] = None
    previous_organizations: Optional[List[PreviousOrganization]] = None
    skills: Optional[List[str]] = None
    technical_skills: Optional[List[Dict[str, Any]]] = None
    work_experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    contributions: Optional[str] = None
    communication_skills: Optional[List[CommunicationSkill]] = None
    ai_tools: Optional[List[str]] = None
    professional_summary: Optional[str] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    portfolio_link: Optional[str] = None
    desired_job_title: Optional[str] = None
    expected_salary: Optional[float] = None
    currency: Optional[str] = None
    linkedin_link: Optional[str] = None
    github_link: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    
    # Social Links
    github_link: Optional[str] = None
    youtube_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    playstore_link: Optional[str] = None
    
    # User Classification
    user_status: Optional[Literal["active", "inactive", "pending_verification"]] = None
    user_plan: Optional[Literal["free", "subscribed", "pro"]] = None
    
    # Preferences
    job_preferences: Optional[List[Literal["remote", "hybrid", "on-site"]]] = None
    employment_type: Optional[List[Literal["full-time", "part-time", "freelancing", "contract"]]] = None
    
    # Legacy compatibility fields
    total_experience: Optional[str] = None
    industry: Optional[str] = None
    current_salary: Optional[float] = None
    area_of_expertise: Optional[List[str]] = None
    key_contributions: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    youtube_url: Optional[str] = None
    
    @validator('certifications', pre=True)
    @classmethod
    def validate_certifications(cls, v):
        """Handle both string and Certification object formats for certifications"""
        if v is None:
            return v
        
        processed_certs = []
        for cert in v:
            if isinstance(cert, str):
                if cert in ["[object Object]", ""]:
                    continue
                processed_certs.append({
                    "name": cert,
                    "issuer": "Unknown",
                    "issue_date": None,
                    "expiry_date": None,
                    "credential_id": None
                })
            elif isinstance(cert, dict):
                processed_certs.append(cert)
            else:
                processed_certs.append(cert)
        
        return processed_certs

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class UpdateUserProfile(BaseModel):
    personal_info: Optional[Dict[str, Any]] = None
    professional_info: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

# Additional Auth Models
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: constr(min_length=8, max_length=100)  # type: ignore

class VerifyEmailRequest(BaseModel):
    token: str
