"""
MongoDB Schema Definitions for JobMitra Backend.
Defines data models and validation schemas for all collections.
"""

from datetime import datetime
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic validation."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema


# Base Models
class BaseDocument(BaseModel):
    """Base document model with common fields."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# User Management Schema
class SalaryRange(BaseModel):
    """Salary range specification."""
    min: int
    max: int
    currency: Literal["USD", "EUR", "GBP", "INR"] = "USD"
    period: Literal["yearly", "monthly", "hourly"] = "yearly"


class Location(BaseModel):
    """Location information."""
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    timezone: Optional[str] = None
    type: Literal["remote", "onsite", "hybrid"] = "remote"


class SocialLinks(BaseModel):
    """Social media and professional links."""
    github: Optional[HttpUrl] = None
    youtube: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    playstore: Optional[HttpUrl] = None


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
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    credential_id: Optional[str] = None

class CommunicationSkill(BaseModel):
    """Communication skill information."""
    skill: str
    level: Literal["beginner", "intermediate", "advanced", "expert"] = "intermediate"

class JobApplicationRecord(BaseModel):
    """Job application record in user profile."""
    job_id: str
    application_id: str
    status: Literal["applied", "under_review", "interview_scheduled", "interviewed", "offer_received", "rejected", "withdrawn"] = "applied"
    applied_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    match_analysis_done: bool = False
    match_percentage: Optional[int] = None
    tailor_resume_done: bool = False
    is_applied: bool = False

class RecentActivity(BaseModel):
    """Recent user activity."""
    activity_type: Literal["application", "interview", "profile_update", "skill_assessment", "mock_interview", "resume_update"]
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SocialLinks(BaseModel):
    """Social media and professional links."""
    github: Optional[HttpUrl] = None
    youtube: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    playstore: Optional[HttpUrl] = None

class UserProfile(BaseDocument):
    """Comprehensive user profile information."""
    # Core Identity
    user_id: str = Field(..., index=True, unique=True)
    email: EmailStr = Field(..., index=True, unique=True)
    password_hash: str = Field(..., exclude=True)  # Excluded from serialization
    
    # Basic Personal Information
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    location: Optional[Location] = None
    city: Optional[str] = None
    state: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    
    # Professional Information
    overall_experience_years: Optional[int] = Field(None, ge=0)
    highest_qualification: Optional[str] = None
    professional_summary: Optional[str] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    
    # Skills and Experience
    skills: List[str] = Field(default_factory=list)
    technical_skills: List[Dict[str, Any]] = Field(default_factory=list)
    work_experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Legacy fields
    previous_organizations: List[PreviousOrganization] = Field(default_factory=list)
    contributions: Optional[str] = None
    communication_skills: List[CommunicationSkill] = Field(default_factory=list)
    ai_tools: List[str] = Field(default_factory=list)
    
    # Additional professional fields
    linkedin_link: Optional[str] = None
    github_link: Optional[str] = None
    portfolio_link: Optional[str] = None
    desired_job_title: Optional[str] = None
    expected_salary: Optional[float] = None
    currency: Optional[str] = "USD"
    
    # Social Links
    social_links: Optional[SocialLinks] = None
    
    # Job Application Tracking
    overall_jobs_applied: List[JobApplicationRecord] = Field(default_factory=list)  # Array of application records
    
    # User Classification
    user_type: Literal["candidate", "hire"] = "candidate"
    user_status: Literal["active", "inactive"] = "active"
    user_plan: Literal["free", "subscribed", "pro"] = "free"
    
    # Preferences
    job_preferences: List[Literal["remote", "hybrid", "on-site"]] = Field(default_factory=list)
    employment_type: List[Literal["full-time", "part-time", "freelancing", "contract"]] = Field(default_factory=list)
    
    # Timestamps
    profile_created_on: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    
    # Analytics and Metrics
    match_analysis_count: int = Field(default=0, ge=0)
    match_tailored_count: int = Field(default=0, ge=0)
    mock_interview_count: int = Field(default=0, ge=0)
    profile_completion_count: int = Field(default=0, ge=0, le=100)
    profile_visits: int = Field(default=0, ge=0)
    recent_activity: List[RecentActivity] = Field(default_factory=list)
    
    # Legacy Settings (maintained for backward compatibility)
    is_active: bool = Field(default=True)
    is_public: bool = Field(default=True)
    email_notifications: bool = Field(default=True)
    profile_searchable: bool = Field(default=True)
    
    @property
    def full_name(self) -> str:
        """Computed property for full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    class Config:
        use_enum_values = True


# Company and Job Schemas
class CompanyInfo(BaseModel):
    """Company information."""
    id: str
    name: str
    industry: str
    size: str  # e.g., "50-100", "500-1000"
    website: Optional[HttpUrl] = None
    logo: Optional[HttpUrl] = None
    description: Optional[str] = None


class HRContact(BaseModel):
    """HR contact information."""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None


class JobRequirement(BaseModel):
    """Job requirement specification."""
    id: str
    description: str
    type: Literal["required", "preferred", "nice-to-have"]
    category: Literal["technical", "soft-skills", "experience", "education", "certification"]


class JobBenefit(BaseModel):
    """Job benefit information."""
    id: str
    title: str
    description: str
    category: Literal["health", "financial", "time-off", "professional", "lifestyle"]


class JobListing(BaseDocument):
    """Job listing information."""
    job_id: str = Field(..., index=True, unique=True)
    title: str = Field(..., index=True)
    company: CompanyInfo
    location: Location
    salary: Optional[SalaryRange] = None
    
    # Job Details
    description: str
    short_description: str
    requirements: List[JobRequirement] = Field(default_factory=list)
    benefits: List[JobBenefit] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list, index=True)
    
    # Job Metadata
    experience_level: Literal["entry", "mid", "senior", "lead", "executive"]
    employment_type: Literal["full-time", "part-time", "contract", "internship"]
    department: str
    hr_contact: Optional[HRContact] = None
    
    # Status and Dates
    posted_date: datetime = Field(default_factory=datetime.utcnow)
    application_deadline: Optional[datetime] = None
    is_active: bool = Field(default=True)
    
    # Tags and Classification
    tags: List[str] = Field(default_factory=list, index=True)
    industry_tags: List[str] = Field(default_factory=list)
    
    # Analytics
    view_count: int = Field(default=0, ge=0)
    application_count: int = Field(default=0, ge=0)


# Application Management
class ApplicationStatus(BaseModel):
    """Application status tracking."""
    status: Literal["draft", "submitted", "under_review", "interview_scheduled", "interview_completed", "offer_received", "accepted", "rejected", "withdrawn"]
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


class JobApplication(BaseDocument):
    """Job application tracking."""
    application_id: str = Field(..., index=True, unique=True)
    user_id: str = Field(..., index=True)
    job_id: str = Field(..., index=True)
    
    # Application Details
    cover_letter: Optional[str] = None
    resume_version: Optional[str] = None  # Reference to resume version
    custom_answers: Dict[str, str] = Field(default_factory=dict)  # Custom question responses
    
    # Status Tracking
    current_status: Literal["draft", "submitted", "under_review", "interview_scheduled", "interview_completed", "offer_received", "accepted", "rejected", "withdrawn"] = "draft"
    status_history: List[ApplicationStatus] = Field(default_factory=list)
    
    # Timeline
    submitted_at: Optional[datetime] = None
    last_status_update: datetime = Field(default_factory=datetime.utcnow)
    
    # Interview Information
    interview_dates: List[datetime] = Field(default_factory=list)
    interview_feedback: Optional[str] = None
    
    # Analytics
    response_time_hours: Optional[int] = None  # Time to get response
    match_percentage: Optional[int] = Field(None, ge=0, le=100)


# Resume Management
class ResumeSection(BaseModel):
    """Resume section content."""
    section_type: Literal["experience", "education", "skills", "projects", "certifications", "achievements"]
    content: Dict[str, Any]  # Flexible content structure
    order: int = 0


class Resume(BaseDocument):
    """Resume document."""
    resume_id: str = Field(..., index=True, unique=True)
    user_id: str = Field(..., index=True)
    
    # Resume Metadata
    title: str
    version: str = "1.0"
    is_primary: bool = Field(default=False)
    template_id: Optional[str] = None
    
    # Resume Content
    sections: List[ResumeSection] = Field(default_factory=list)
    raw_content: Optional[str] = None  # Backup of full content
    
    # File Information
    file_url: Optional[HttpUrl] = None
    file_format: Literal["pdf", "docx", "txt"] = "pdf"
    file_size_bytes: Optional[int] = None
    
    # Analytics
    download_count: int = Field(default=0, ge=0)
    view_count: int = Field(default=0, ge=0)
    last_downloaded: Optional[datetime] = None


# Mock Interview System
class MockInterviewQuestion(BaseModel):
    """Mock interview question."""
    question: str
    skill_category: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    expected_answer_points: List[str] = Field(default_factory=list)


class MockInterviewSession(BaseDocument):
    """Mock interview session."""
    session_id: str = Field(..., index=True, unique=True)
    user_id: str = Field(..., index=True)
    
    # Session Details
    skill: str
    difficulty_level: Literal["beginner", "intermediate", "advanced"]
    duration_minutes: int = 30
    
    # Questions and Responses
    questions: List[MockInterviewQuestion] = Field(default_factory=list)
    user_responses: Dict[str, str] = Field(default_factory=dict)  # question_id -> response
    
    # AI Analysis
    overall_score: Optional[int] = Field(None, ge=0, le=100)
    skill_scores: Dict[str, int] = Field(default_factory=dict)  # skill -> score
    feedback: Optional[str] = None
    improvement_suggestions: List[str] = Field(default_factory=list)
    
    # Session Status
    status: Literal["scheduled", "in_progress", "completed", "cancelled"] = "scheduled"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Learning Resources
class LearningResource(BaseDocument):
    """Learning resource for skill development."""
    resource_id: str = Field(..., index=True, unique=True)
    
    # Resource Details
    title: str = Field(..., index=True)
    description: str
    url: HttpUrl
    resource_type: Literal["video", "article", "course", "tutorial", "documentation"]
    
    # Classification
    skill: str = Field(..., index=True)
    level: Literal["beginner", "intermediate", "advanced"]
    duration_minutes: Optional[int] = None
    
    # Metadata
    provider: str  # e.g., "YouTube", "Coursera", "freeCodeCamp"
    rating: Optional[float] = Field(None, ge=0, le=5)
    language: str = "English"
    
    # Analytics
    view_count: int = Field(default=0, ge=0)
    completion_rate: Optional[float] = Field(None, ge=0, le=1)
    
    # Tags
    tags: List[str] = Field(default_factory=list, index=True)
    prerequisites: List[str] = Field(default_factory=list)


# User Progress Tracking
class SkillAssessment(BaseDocument):
    """Skill assessment results."""
    assessment_id: str = Field(..., index=True, unique=True)
    user_id: str = Field(..., index=True)
    
    # Assessment Details
    skill: str = Field(..., index=True)
    assessment_type: Literal["quiz", "coding_challenge", "project", "interview"]
    
    # Results
    score: int = Field(..., ge=0, le=100)
    max_score: int = 100
    time_taken_minutes: Optional[int] = None
    
    # Detailed Results
    question_scores: List[Dict[str, Any]] = Field(default_factory=list)
    feedback: Optional[str] = None
    areas_for_improvement: List[str] = Field(default_factory=list)
    
    # Status
    status: Literal["in_progress", "completed", "expired"] = "completed"
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class UserProgress(BaseDocument):
    """User learning and career progress."""
    user_id: str = Field(..., index=True, unique=True)
    
    # Skill Progress
    skill_levels: Dict[str, int] = Field(default_factory=dict)  # skill -> level (0-100)
    completed_resources: List[str] = Field(default_factory=list)  # resource_ids
    bookmarked_resources: List[str] = Field(default_factory=list)
    
    # Assessment History
    assessment_scores: Dict[str, int] = Field(default_factory=dict)  # skill -> latest_score
    total_assessments: int = Field(default=0, ge=0)
    
    # Learning Goals
    learning_goals: List[str] = Field(default_factory=list)
    target_skills: List[str] = Field(default_factory=list)
    career_objectives: List[str] = Field(default_factory=list)
    
    # Activity Metrics
    total_learning_hours: int = Field(default=0, ge=0)
    streak_days: int = Field(default=0, ge=0)
    last_activity: datetime = Field(default_factory=datetime.utcnow)


# Subscription Management
class SubscriptionPlan(BaseModel):
    """Subscription plan details."""
    plan_id: str
    name: str
    description: str
    price: float
    currency: Literal["USD", "EUR", "GBP", "INR"] = "USD"
    period: Literal["monthly", "yearly"] = "monthly"
    features: List[str] = Field(default_factory=list)
    
    # Limits
    mock_interviews_per_week: int = 2
    cooldown_hours: int = 24
    priority: Literal["basic", "premium", "enterprise"] = "basic"
    is_popular: bool = False


class UserSubscription(BaseDocument):
    """User subscription information."""
    user_id: str = Field(..., index=True, unique=True)
    
    # Subscription Details
    plan_id: str
    status: Literal["active", "cancelled", "expired", "trial"] = "trial"
    
    # Billing
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime
    auto_renew: bool = True
    payment_method: Optional[str] = None
    
    # Usage Tracking
    mock_interviews_used_this_week: int = Field(default=0, ge=0)
    last_interview_date: Optional[datetime] = None
    
    # Trial Information
    is_trial: bool = False
    trial_days_remaining: Optional[int] = None


# Analytics and Dashboard
class DashboardStats(BaseModel):
    """Dashboard statistics."""
    stat_id: str
    label: str
    value: int
    icon: Optional[str] = None
    color: Optional[str] = None
    trend_direction: Optional[Literal["up", "down", "neutral"]] = None
    trend_percentage: Optional[float] = None
    trend_period: Optional[str] = None


class ActivityItem(BaseModel):
    """User activity item."""
    activity_id: str
    title: str
    icon: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    activity_type: Literal["application", "interview", "assessment", "profile", "resume", "learning", "other"]
    status: Optional[Literal["completed", "pending", "in_progress", "cancelled"]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserDashboard(BaseDocument):
    """User dashboard data."""
    user_id: str = Field(..., index=True, unique=True)
    
    # Statistics
    stats: List[DashboardStats] = Field(default_factory=list)
    recent_activities: List[ActivityItem] = Field(default_factory=list)
    
    # Quick Metrics
    applications_count: int = Field(default=0, ge=0)
    interviews_scheduled: int = Field(default=0, ge=0)
    mock_interviews_completed: int = Field(default=0, ge=0)
    profile_completion: int = Field(default=0, ge=0, le=100)
    matching_jobs_count: int = Field(default=0, ge=0)
    
    # Cache Information
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    cache_expires_at: datetime = Field(default_factory=datetime.utcnow)


# System Collections
class QueryLog(BaseDocument):
    """AI query and response logging."""
    user_id: Optional[str] = None  # May be anonymous
    query: str = Field(..., index=True)
    response: str
    
    # Processing Details
    processing_time_ms: Optional[int] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    
    # Context
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    # Classification
    query_category: Optional[str] = None
    intent: Optional[str] = None
    satisfaction_score: Optional[int] = Field(None, ge=1, le=5)


class SystemConfig(BaseDocument):
    """System configuration settings."""
    config_key: str = Field(..., index=True, unique=True)
    config_value: Any
    description: Optional[str] = None
    config_type: Literal["string", "number", "boolean", "json", "array"] = "string"
    is_public: bool = False
    environment: Literal["development", "staging", "production"] = "development"


# Collection Names Constants
COLLECTION_NAMES = {
    "users": "user_profiles",
    "jobs": "job_listings", 
    "applications": "job_applications",
    "resumes": "resumes",
    "mock_interviews": "mock_interview_sessions",
    "learning_resources": "learning_resources",
    "skill_assessments": "skill_assessments",
    "user_progress": "user_progress",
    "subscriptions": "user_subscriptions",
    "dashboards": "user_dashboards",
    "query_logs": "query_logs",
    "system_config": "system_config",
}


# Index Definitions for Performance
def get_indexes():
    """Return index definitions for all collections."""
    return {
        COLLECTION_NAMES["users"]: [
            [("user_id", 1)],
            [("email", 1)],
            [("skills", 1)],
            [("location.country", 1)],
            [("is_active", 1)],
            [("last_active", -1)],
        ],
        COLLECTION_NAMES["jobs"]: [
            [("job_id", 1)],
            [("title", "text"), ("description", "text")],
            [("skills", 1)],
            [("location.country", 1), ("location.type", 1)],
            [("experience_level", 1)],
            [("employment_type", 1)],
            [("is_active", 1)],
            [("posted_date", -1)],
            [("tags", 1)],
        ],
        COLLECTION_NAMES["applications"]: [
            [("application_id", 1)],
            [("user_id", 1), ("job_id", 1)],
            [("current_status", 1)],
            [("submitted_at", -1)],
            [("last_status_update", -1)],
        ],
        COLLECTION_NAMES["mock_interviews"]: [
            [("session_id", 1)],
            [("user_id", 1)],
            [("skill", 1)],
            [("status", 1)],
            [("completed_at", -1)],
        ],
        COLLECTION_NAMES["query_logs"]: [
            [("user_id", 1)],
            [("created_at", -1)],
            [("query_category", 1)],
        ],
    }
