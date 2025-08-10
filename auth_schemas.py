"""
Authentication and User Management Schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# Authentication Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    username: str
    first_name: str
    last_name: str
    phone: str
    city: str
    state: str
    is_active: bool
    created_at: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str
    city: str
    state: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    username: str
    personal_info: Dict[str, Any]
    professional_info: Dict[str, Any]
    preferences: Dict[str, Any]
    social_links: Optional[Dict[str, Any]] = None
    is_active: bool
    is_verified: bool
    created_at: str
    updated_at: str
    last_login: Optional[str]

# User Update Models
class UserProfileUpdateRequest(BaseModel):
    # Personal Information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    
    # Professional Information - Basic
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    total_experience: Optional[str] = None
    industry: Optional[str] = None
    skills: Optional[List[str]] = None
    current_salary: Optional[float] = None
    expected_salary: Optional[float] = None
    
    # Professional Information - Extended
    desired_job_title: Optional[str] = None
    professional_summary: Optional[str] = None
    certifications: Optional[List[str]] = None
    area_of_expertise: Optional[List[str]] = None
    key_contributions: Optional[str] = None
    
    # Social Links
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    youtube_url: Optional[str] = None

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
    new_password: str = Field(..., min_length=8)

class VerifyEmailRequest(BaseModel):
    token: str
