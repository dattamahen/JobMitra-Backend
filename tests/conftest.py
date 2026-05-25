"""
Shared test fixtures and configuration for JobMitra Backend tests.
"""
import os
import sys
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment
os.environ["APP_ENV"] = "test"
os.environ["MONGO_URI"] = "mongodb://localhost:27017/jobmitra_test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["OPENAI_API_KEY"] = "test-key"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db():
    """Mock database instance."""
    with patch("db_simple.db") as mock:
        mock.fallback_mode = False
        mock.database = MagicMock()
        yield mock


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        "user_id": "test_user_001",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password_hash": "$2b$12$test_hash",
        "phone": "+1234567890",
        "skills": ["Python", "FastAPI"],
        "user_type": "candidate",
        "user_status": "active",
        "user_plan": "free",
        "feature_usage_count": 5,
        "job_preferences": ["remote"],
        "employment_type": ["full-time"],
        "profile_created_on": datetime(2024, 1, 1),
        "last_active": datetime(2024, 6, 1),
        "match_analysis_count": 0,
        "match_tailored_count": 0,
        "mock_interview_count": 0,
        "profile_completion_count": 50,
        "profile_visits": 10,
        "overall_jobs_applied": [],
        "is_active": True,
        "is_verified": False,
    }


@pytest.fixture
def sample_hr_user():
    """Sample HR user data."""
    return {
        "user_id": "hr_user_001",
        "email": "hr@company.com",
        "first_name": "HR",
        "last_name": "Manager",
        "password_hash": "$2b$12$test_hash",
        "user_type": "hire",
        "user_status": "active",
        "user_plan": "pro",
        "profile_created_on": datetime(2024, 1, 1),
        "last_active": datetime(2024, 6, 1),
        "match_analysis_count": 0,
        "match_tailored_count": 0,
        "mock_interview_count": 0,
        "profile_completion_count": 80,
        "profile_visits": 5,
        "is_active": True,
    }


@pytest.fixture
def sample_job():
    """Sample job listing data."""
    return {
        "job_id": "job_001",
        "title": "Senior Python Developer",
        "company": {"name": "TechCorp", "industry": "Technology"},
        "location": {"city": "Remote", "type": "remote"},
        "description": "Looking for a senior Python developer",
        "skills": ["Python", "FastAPI", "MongoDB"],
        "skills_required": ["Python", "FastAPI"],
        "experience_level": "senior",
        "employment_type": "full-time",
        "status": "active",
        "is_active": True,
        "posted_date": datetime(2024, 5, 1),
        "application_deadline": datetime(2024, 12, 31),
    }


@pytest.fixture
def auth_token(sample_user):
    """Generate a valid JWT token for testing."""
    from auth_utils import create_access_token
    return create_access_token({"user_id": sample_user["user_id"], "email": sample_user["email"]})


@pytest.fixture
def auth_headers(auth_token):
    """Auth headers with Bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}
