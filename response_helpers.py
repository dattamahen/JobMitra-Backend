"""
Response Helpers
Eliminates duplicated response mapping logic across endpoints.
"""

from datetime import datetime
from auth_schemas import UserResponse


def build_user_response(user: dict) -> UserResponse:
    """Build a UserResponse from a raw user dict. Single source of truth."""
    created_on = user.get("profile_created_on", datetime.utcnow())
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        first_name=user.get("first_name", ""),
        last_name=user.get("last_name", ""),
        date_of_birth=user.get("date_of_birth"),
        phone=user.get("phone"),
        overall_experience_years=user.get("overall_experience_years"),
        highest_qualification=user.get("highest_qualification"),
        skills=user.get("skills", []),
        certifications=user.get("certifications", []),
        user_type=user.get("user_type", "candidate"),
        user_status=user.get("user_status", "active"),
        user_plan=user.get("user_plan", "free"),
        feature_usage_count=user.get("feature_usage_count", 5),
        job_preferences=user.get("job_preferences", []),
        employment_type=user.get("employment_type", []),
        profile_created_on=created_on,
        last_active=user.get("last_active", datetime.utcnow()),
        match_analysis_count=user.get("match_analysis_count", 0),
        match_tailored_count=user.get("match_tailored_count", 0),
        mock_interview_count=user.get("mock_interview_count", 0),
        profile_completion_count=user.get("profile_completion_count", 0),
        profile_visits=user.get("profile_visits", 0),
        username=user.get("username"),
        full_name=f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
        company_name=user.get("company_name"),
        city=user.get("city"),
        state=user.get("state"),
        is_active=user.get("is_active", True),
        is_verified=user.get("is_verified", False),
        profile_completion=user.get("profile_completion_count", 0),
        created_at=created_on.isoformat() + "Z" if hasattr(created_on, 'isoformat') else str(created_on),
        updated_at=user.get("updated_at", created_on.isoformat() + "Z" if hasattr(created_on, 'isoformat') else str(created_on))
    )
