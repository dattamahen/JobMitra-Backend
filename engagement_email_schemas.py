"""
Pydantic models for the engagement email campaign system.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CampaignConfig(BaseModel):
    campaign_id: str = Field(..., min_length=1, max_length=100)
    enabled: bool = True
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    hour_utc: int = Field(..., ge=0, le=23)
    minute_utc: int = Field(..., ge=0, le=59)
    cooldown_days: int = Field(..., ge=1)
    description: str = ""
    profile_completion_threshold: int = Field(80, ge=1, le=100)
    mock_interview_inactive_days: int = Field(30, ge=1)
    fresher_max_experience_years: int = Field(0, ge=0)
    last_run_at: Optional[datetime] = None


class CampaignConfigUpdate(BaseModel):
    enabled: Optional[bool] = None
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    hour_utc: Optional[int] = Field(None, ge=0, le=23)
    minute_utc: Optional[int] = Field(None, ge=0, le=59)
    cooldown_days: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None
    profile_completion_threshold: Optional[int] = Field(None, ge=1, le=100)
    mock_interview_inactive_days: Optional[int] = Field(None, ge=1)
    fresher_max_experience_years: Optional[int] = Field(None, ge=0)


class SendLogEntry(BaseModel):
    campaign_id: str
    user_id: str
    email: str
    sent_at: datetime
    status: str  # "sent" | "failed" | "skipped"


class CampaignRunReport(BaseModel):
    campaign_id: str
    run_at: datetime
    eligible_count: int
    sent_count: int
    skipped_count: int
    failed_count: int
