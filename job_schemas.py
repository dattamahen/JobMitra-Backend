"""
Pydantic schemas for job posting functionality
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


class JobType(str, Enum):
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"


class CompanySize(str, Enum):
    STARTUP = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "201-500"
    ENTERPRISE = "501-1000"
    CORPORATION = "1000+"


class Currency(str, Enum):
    INR = "INR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class SalaryPeriod(str, Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    HOURLY = "hourly"


class JobLocation(BaseModel):
    city: str
    state: str
    country: str
    is_remote: bool = False
    timezone: Optional[str] = "IST"


class SalaryInfo(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    currency: Currency = Currency.INR
    period: SalaryPeriod = SalaryPeriod.YEARLY
    is_negotiable: bool = True


class CompanyInfo(BaseModel):
    company_size: CompanySize
    industry: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None


class HRContact(BaseModel):
    name: str
    email: str
    phone: str
    title: Optional[str] = "HR Recruiter"
    department: Optional[str] = "Human Resources"


class LearningResource(BaseModel):
    id: str
    title: str
    description: str
    youtube_url: str
    duration: str
    level: str = "intermediate"
    channel: str
    skill: str
    rating: Optional[float] = 4.0


class JobPostRequest(BaseModel):
    """Schema for job posting request from HR"""
    title: str = Field(..., min_length=5, max_length=100)
    company: str = Field(..., min_length=2, max_length=100)
    location: JobLocation
    employment_type: EmploymentType
    experience_level: ExperienceLevel
    job_type: JobType
    salary: Optional[SalaryInfo] = None
    description: str = Field(..., min_length=50, max_length=2000)
    requirements: List[str] = Field(..., min_items=3, max_items=15)
    responsibilities: List[str] = Field(..., min_items=3, max_items=15)
    skills_required: List[str] = Field(..., min_items=2, max_items=10)
    skills_preferred: Optional[List[str]] = []
    benefits: Optional[List[str]] = []
    company_info: CompanyInfo
    hr_contact: HRContact
    application_deadline: Optional[datetime] = None
    external_apply_url: Optional[str] = None
    application_instructions: Optional[str] = None
    tags: Optional[List[str]] = []
    learning_resources: Optional[List[LearningResource]] = []

    @validator('requirements')
    def validate_requirements(cls, v):
        if not v or len(v) < 3:
            raise ValueError('At least 3 requirements are needed')
        return v

    @validator('responsibilities')
    def validate_responsibilities(cls, v):
        if not v or len(v) < 3:
            raise ValueError('At least 3 responsibilities are needed')
        return v

    @validator('skills_required')
    def validate_skills_required(cls, v):
        if not v or len(v) < 2:
            raise ValueError('At least 2 required skills are needed')
        return v


class JobPostResponse(BaseModel):
    """Schema for job posting response"""
    message: str
    job_id: str
    job_url: str
    created_at: datetime


class JobListing(BaseModel):
    """Schema for complete job listing (used in database and API responses)"""
    _id: Optional[str] = None
    job_id: str
    title: str
    company: str
    location: JobLocation
    employment_type: EmploymentType
    experience_level: ExperienceLevel
    job_type: JobType
    salary: Optional[SalaryInfo]
    description: str
    requirements: List[str]
    responsibilities: List[str]
    skills_required: List[str]
    skills_preferred: List[str]
    benefits: List[str]
    company_info: CompanyInfo
    hr_contact: HRContact
    application_deadline: Optional[datetime] = None
    external_apply_url: Optional[str] = None
    application_instructions: Optional[str] = None
    tags: List[str]
    learning_resources: List[LearningResource]
    
    # Metadata
    posted_date: datetime
    updated_date: datetime
    is_active: bool = True
    posted_by_hr_id: str  # Reference to HR user who posted this job
    views_count: int = 0
    applications_count: int = 0
    source: str = "internal"  # internal, external, etc.
    
    # Auto-calculated fields
    job_score: Optional[float] = None
    match_percentage: Optional[float] = None


class JobUpdateRequest(BaseModel):
    """Schema for updating existing job postings"""
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    skills_required: Optional[List[str]] = None
    skills_preferred: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    salary: Optional[SalaryInfo] = None
    application_deadline: Optional[datetime] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None


class JobSearchFilters(BaseModel):
    """Schema for job search filters"""
    keywords: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[List[EmploymentType]] = None
    experience_level: Optional[List[ExperienceLevel]] = None
    job_type: Optional[List[JobType]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    skills: Optional[List[str]] = None
    company_size: Optional[List[CompanySize]] = None
    industry: Optional[List[str]] = None
    posted_within_days: Optional[int] = None
    is_remote: Optional[bool] = None


class JobSearchResponse(BaseModel):
    """Schema for job search API response"""
    jobs: List[JobListing]
    total_count: int
    page: int
    per_page: int
    total_pages: Optional[int] = None
    has_next: Optional[bool] = None
    has_prev: Optional[bool] = None
    filters: Optional[Dict[str, Any]] = None


class HRJobListing(BaseModel):
    """Simplified schema for HR job listings view"""
    job_id: str
    title: str
    company: str
    location: str
    employment_type: str
    experience_level: str
    salary_range: Optional[Dict[str, Any]] = None
    posted_date: datetime
    application_deadline: Optional[datetime] = None
    is_active: bool = True
    applications_count: int = 0
    views_count: int = 0
    description: Optional[str] = None
    requirements: Optional[List[str]] = []
    skills: Optional[List[str]] = []


class HRJobSearchResponse(BaseModel):
    """Schema for HR job search response with simplified job listings"""
    jobs: List[HRJobListing]
    total_count: int
    page: int
    per_page: int
    total_pages: Optional[int] = None
    has_next: Optional[bool] = None
    has_prev: Optional[bool] = None


class HRJobDashboard(BaseModel):
    """Schema for HR dashboard showing their posted jobs"""
    total_jobs_posted: int
    active_jobs: int
    inactive_jobs: int
    total_applications_received: int
    jobs_expiring_soon: int
    recent_jobs: List[JobListing]


class JobApplicationStats(BaseModel):
    """Schema for job application statistics"""
    job_id: str
    job_title: str
    total_applications: int
    applications_this_week: int
    average_match_score: float
    top_skills_applied: List[str]
